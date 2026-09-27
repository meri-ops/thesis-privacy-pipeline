"""pipeline eseguibile come funzione riusabile.

`run_pipeline(config, output_dir=None)` esegue le fasi 1-5 su una config
gia' risolta (base.yaml + dataset yaml [+ eventuali override futuri da
experiment_grid.yaml, Fase 3]) e ritorna il dict del report finale (lo
stesso oggi serializzato in JSON + Markdown).

Estratto da main.py per essere richiamabile da run_experiments.py (Fase 3)
una volta per ogni combinazione (dataset, metodo, replica), con un
output_dir isolato per ogni run.

Instrumentazione di timing per fase (non richiesta dal documento di
refactoring, aggiunta per diagnosticare i tempi di esecuzione lunghi
osservati durante la campagna sperimentale): ogni fase viene cronometrata
con _timed() e il risultato finisce sia stampato a console in tempo reale
sia salvato in report["phase_timings"].

I tre controlli di privacy (duplicati esatti, NewRowSynthesis, DCR
Overfitting Protection) sono cronometrati separatamente, chiamando le
funzioni di src/audit/privacy_metrics.py direttamente invece che tramite
il suo build_privacy_summary: questo evita di modificare quel file (resta
nella lista dei moduli di dominio da non toccare) pur ottenendo il
dettaglio di quale dei tre controlli domina il tempo totale. Il dict
risultante ("privacy_summary") ha esattamente la stessa struttura che
build_privacy_summary avrebbe prodotto.
"""
import copy
import json
import random
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from sklearn.model_selection import train_test_split

from src.utils.hashing import sha256_of_file, sha256_of_dict
from src.ingestion.registry import load_dataset
from src.audit.quality_metrics import compute_quality_report
from src.audit.quality_plots import generate_all_plots
from src.synthetic.generate import train_synthesizer, generate_synthetic_data
from src.audit.fidelity_metrics import generate_reports, extract_fidelity_summary
from src.audit.fidelity_plots import generate_all_fidelity_plots
from src.audit.privacy_metrics import (
    check_exact_duplicates,
    check_new_row_synthesis,
    check_dcr_overfitting_protection,
)
from src.audit.privacy_plots import generate_all_privacy_plots
from src.audit.report_generator import render_markdown_report
from src.preprocessing.clean_data import split_features_target, build_preprocessor, encode_target
from src.training.train import train_model, save_model
from src.training.evaluate import evaluate_model


def set_global_seed(seed: int) -> None:
    """Fissa il seed per tutte le fonti di casualita' usate dalla pipeline
    (split, sampling di GaussianCopula, training/sampling di CTGAN, modelli
    scikit-learn). Va chiamata PRIMA di istanziare qualunque synthesizer

    Effetto atteso: GaussianCopula riproducibile al 100% (stesso hash a
    ogni run, salvo un rischio residuo trascurabile legato a eventuale
    multi-threading). CTGAN: varianza molto ridotta rispetto a prima del fix,
    ma non azzerata (training stocastico + possibili operazioni floating
    point multi-thread non associative, amplificate su centinaia di step)
    . Possibile limite del metodo
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


@contextmanager
def _timed(label: str, sink: dict):
    """Cronometra il blocco 'with', stampa il risultato a console e lo
    accumula in sink[label] (in sec)"""
    t0 = time.perf_counter()
    yield
    elapsed = round(time.perf_counter() - t0, 2)
    sink[label] = elapsed
    print(f"[timing] {label}: {elapsed}s")


def run_pipeline(config: dict, output_dir: Optional[str] = None) -> dict:
    """Esegue le fasi 1-5 su una config gia' risolta e ritorna il dict del
    report finale.

    Args:
        config: configurazione risolta (es. da load_and_merge_config).
            Non viene modificata: internamente si lavora su una copia.
        output_dir: se specificato, sovrascrive config["report"]["output_dir"]
            per isolare l'output di questa run (usato da run_experiments.py,
            Fase 3, per lo schema reports/runs/{dataset}/{metodo}/run_{n}/).
            Se None, si usa il valore gia' presente in config (comportamento
            "legacy" di main.py per il lancio di un singolo dataset).

    Returns:
        dict: il report completo (config usata, hash SHA256 di dataset/
        train/test/sintetico/modelli/config, metriche di fedelta', privacy
        ed esperimenti A/B, path dei plot e dei report JSON/Markdown
        scritti su disco, e phase_timings con il tempo di ogni fase).
    """
    pipeline_t0 = time.perf_counter()
    phase_timings = {}

    resolved_config = copy.deepcopy(config)
    if output_dir is not None:
        resolved_config["report"]["output_dir"] = output_dir

    set_global_seed(resolved_config["seed"])

    dataset_name = resolved_config["dataset"]["name"]
    target_col = resolved_config["dataset"]["target_column"]
    config_hash = sha256_of_dict(resolved_config)
    out_dir = Path(resolved_config["report"]["output_dir"])

    # --- Fase 1: ingestion ---
    with _timed("ingestion", phase_timings):
        df = load_dataset(resolved_config)

    # --- Fase 1: quality assessment ---
    with _timed("quality_assessment", phase_timings):
        quality = compute_quality_report(df, target_col)
        plot_paths = generate_all_plots(df, quality, target_col, str(out_dir))
        dataset_hash = sha256_of_file(resolved_config["dataset"]["real_data_path"])

    # --- Split train/test ---
    with _timed("train_test_split", phase_timings):
        test_size = resolved_config["dataset"]["test_size"]
        seed = resolved_config["seed"]

        train_df, test_df = train_test_split(
            df, test_size=test_size, random_state=seed, stratify=df[target_col]
        )

        train_path = Path(resolved_config["dataset"]["real_data_path"]).parent / f"{dataset_name}_train.csv"
        test_path = Path(resolved_config["dataset"]["real_data_path"]).parent / f"{dataset_name}_test.csv"
        train_df.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)

        train_hash = sha256_of_file(train_path)
        test_hash = sha256_of_file(test_path)

    # --- Fase 2: generazione dati sintetici ---
    with _timed("synthetic_generation", phase_timings):
        synthesizer, metadata, fit_seconds = train_synthesizer(train_df, resolved_config)
        synthetic_df, sample_seconds = generate_synthetic_data(
            synthesizer, n_rows=len(train_df), config=resolved_config
        )
        synthetic_hash = sha256_of_file(resolved_config["synthetic"]["output_path"])

    # --- Fase 3: validazione fedelta' ---
    with _timed("fidelity_validation", phase_timings):
        quality_report, diagnostic_report = generate_reports(train_df, synthetic_df, metadata)
        fidelity_summary = extract_fidelity_summary(quality_report, diagnostic_report, train_df, synthetic_df)
        fidelity_plot_paths = generate_all_fidelity_plots(
            quality_report, train_df, synthetic_df, quality["numeric_columns"],
            fidelity_summary, str(out_dir)
        )

    # --- Fase 3: validazione privacy (3 controlli cronometrati separatamente) ---
    privacy_cfg = resolved_config.get("privacy", {})

    with _timed("privacy_exact_duplicates", phase_timings):
        print("[privacy] Controllo duplicati esatti...")
        exact_duplicates = check_exact_duplicates(train_df, synthetic_df)

    with _timed("privacy_new_row_synthesis", phase_timings):
        print("[privacy] Controllo NewRowSynthesis (novita' rispetto al reale)...")
        new_row_synthesis = check_new_row_synthesis(
            train_df, synthetic_df, metadata,
            numerical_match_tolerance=privacy_cfg.get("new_row_synthesis_tolerance", 0.01),
            sample_size=privacy_cfg.get("new_row_synthesis_sample_size", 10_000),
        )

    with _timed("privacy_dcr_overfitting", phase_timings):
        print("[privacy] Controllo DCR Overfitting Protection (train vs holdout)...")
        dcr_overfitting = check_dcr_overfitting_protection(
            train_df, test_df, synthetic_df, metadata,
            sample_size=privacy_cfg.get("dcr_overfitting_sample_size", 5_000),
        )
        if dcr_overfitting.get("status") != "ok":
            print(
                f"[privacy][ATTENZIONE] DCR Overfitting Protection non calcolato "
                f"(status={dcr_overfitting.get('status')}, reason={dcr_overfitting.get('reason')})"
            )

    if new_row_synthesis.get("status") != "ok":
        print(
            f"[privacy][ATTENZIONE] NewRowSynthesis non calcolato "
            f"(status={new_row_synthesis.get('status')}, reason={new_row_synthesis.get('reason')})"
        )

    privacy_summary = {
        "exact_duplicates": exact_duplicates,
        "new_row_synthesis": new_row_synthesis,
        "dcr_overfitting_protection": dcr_overfitting,
    }

    with _timed("privacy_plots", phase_timings):
        privacy_plot_paths = generate_all_privacy_plots(privacy_summary, str(out_dir))

    # --- Fase 4: training e valutazione (Esperimento A: reale, B: sintetico) ---
    numeric_cols = [c for c in quality["numeric_columns"] if c != target_col]
    categorical_cols = [c for c in quality["categorical_columns"] if c != target_col]

    with _timed("target_encoding", phase_timings):
        X_train_real, y_train_real_raw = split_features_target(train_df, target_col)
        X_test_real, y_test_raw = split_features_target(test_df, target_col)
        X_train_synth, y_train_synth_raw = split_features_target(synthetic_df, target_col)

        y_train_real, (y_test, y_train_synth), target_encoder = encode_target(
            y_train_real_raw, y_test_raw, y_train_synth_raw
        )

    experiments = {}
    models_dir = out_dir / "models"

    for exp_name, X_train, y_train in [
        ("experiment_A_real", X_train_real, y_train_real),
        ("experiment_B_synthetic", X_train_synth, y_train_synth),
    ]:
        with _timed(f"training_{exp_name}", phase_timings):
            print(f"\n=== {exp_name}: preprocessing + training + evaluation ===")
            preprocessor = build_preprocessor(numeric_cols, categorical_cols)
            X_train_enc = preprocessor.fit_transform(X_train)
            X_test_enc = preprocessor.transform(X_test_real)

            model = train_model(X_train_enc, y_train, resolved_config)
            model_path = save_model(model, models_dir / f"{exp_name}.pkl")
            model_hash = sha256_of_file(model_path)

            metrics = evaluate_model(model, X_test_enc, y_test)

            experiments[exp_name] = {
                "train_n_rows": int(X_train.shape[0]),
                "model_type": resolved_config["model"]["type"],
                "model_path": model_path,
                "model_sha256": model_hash,
                "metrics": metrics,
            }
            print(f"  Metriche: {metrics}")

    # --- Fase 5: audit trail completo ---
    with _timed("audit_trail_writing", phase_timings):
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config_used": resolved_config,
            "config_sha256": config_hash,
            "config_sources": {
                "base_yaml_sha256": sha256_of_file("configs/base.yaml"),
                "dataset_yaml_sha256": sha256_of_file(f"configs/datasets/{dataset_name}.yaml"),
            },
            "dataset": {
                "path": resolved_config["dataset"]["real_data_path"],
                "sha256": dataset_hash,
                "quality_assessment": quality,
            },
            "split": {
                "test_size": test_size,
                "seed": seed,
                "train_path": str(train_path),
                "train_sha256": train_hash,
                "train_n_rows": len(train_df),
                "test_path": str(test_path),
                "test_sha256": test_hash,
                "test_n_rows": len(test_df),
            },
            "synthetic": {
                "method": resolved_config["synthetic"]["method"],
                "output_path": resolved_config["synthetic"]["output_path"],
                "sha256": synthetic_hash,
                "n_rows": len(synthetic_df),
                "fit_seconds": fit_seconds,
                "sample_seconds": sample_seconds,
            },
            "fidelity": fidelity_summary,
            "privacy": privacy_summary,
            "target_encoding": {
                "classes": target_encoder.classes_.tolist(),
            },
            "experiments": experiments,
            "plots": {**plot_paths, **fidelity_plot_paths, **privacy_plot_paths},
        }

        out_dir.mkdir(parents=True, exist_ok=True)

        report_path = out_dir / "phase1_quality_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        md_report_path = render_markdown_report(report, out_dir / "audit_report.md", json_filename=report_path.name)

    phase_timings["total"] = round(time.perf_counter() - pipeline_t0, 2)
    print(f"[timing] total: {phase_timings['total']}s")

    # Path dei report scritti su disco, utili al chiamante (main.py legacy
    # o run_experiments.py) senza dover ricostruire out_dir da soli.
    report["report_paths"] = {
        "json": str(report_path),
        "markdown": str(md_report_path),
    }
    report["phase_timings"] = phase_timings

    return report