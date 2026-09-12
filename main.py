"""Entry point della pipeline.

Fasi eseguite:
- Fase 1: ingestion + quality assessment completo (metriche + grafici)
- Split train/test: il test set viene isolato subito e non verra' mai
  usato per la generazione sintetica (Fase 2) ne' per il training (Fase 4
  lo usa solo in valutazione finale).
- Fase 2: generazione dati sintetici a partire dal SOLO train set.
- Fase 3: validazione fedelta' (SDMetrics: column shapes, column pair
  trends, diagnostic) e validazione privacy (duplicati esatti,
  NewRowSynthesis, DCR Overfitting Protection train-vs-holdout) del
  sintetico vs il train set.
- Fase 4: training e valutazione modello, due esperimenti:
    Esperimento A: train su dati reali, test su dati reali
    Esperimento B: train su dati sintetici, test sugli STESSI dati reali
  In entrambi i casi il preprocessing (encoding) e' fit SOLO sul training
  set di quell'esperimento e poi applicato, invariato, al test set reale.
- Fase 5: audit trail. Report JSON completo (machine-readable) + report
  Markdown leggibile (report_generator.py), entrambi con hash SHA256 di
  dataset/train/test/sintetico/modello/config.

Configurazione: risolta da configs/base.yaml + configs/datasets/<nome>.yaml
(vedi src/utils/config.py::load_and_merge_config). Il dataset si sceglie
con --dataset da riga di comando (default: adult_income). Questo script e'
pensato per il debug/lancio di UN dataset alla volta; la campagna
sperimentale completa (N dataset x 2 metodi) sara' gestita da
run_experiments.py (Fase 3 del refactoring).
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from sklearn.model_selection import train_test_split

from src.utils.config import load_and_merge_config
from src.utils.hashing import sha256_of_file, sha256_of_dict
from src.ingestion.registry import load_dataset
from src.audit.quality_metrics import compute_quality_report
from src.audit.quality_plots import generate_all_plots
from src.synthetic.generate import train_synthesizer, generate_synthetic_data
from src.audit.fidelity_metrics import generate_reports, extract_fidelity_summary
from src.audit.fidelity_plots import generate_all_fidelity_plots
from src.audit.privacy_metrics import build_privacy_summary
from src.audit.privacy_plots import generate_all_privacy_plots
from src.audit.report_generator import render_markdown_report
from src.preprocessing.clean_data import split_features_target, build_preprocessor, encode_target
from src.training.train import train_model, save_model
from src.training.evaluate import evaluate_model


def main(dataset_name: str = "adult_income"):
    config = load_and_merge_config(dataset_name)
    config_hash = sha256_of_dict(config)
    target_col = config["dataset"]["target_column"]

    # --- Fase 1: ingestion ---
    df = load_dataset(config)

    # --- Fase 1: quality assessment ---
    quality = compute_quality_report(df, target_col)
    plot_paths = generate_all_plots(df, quality, target_col, config["report"]["output_dir"])
    dataset_hash = sha256_of_file(config["dataset"]["real_data_path"])

    # --- Split train/test ---
    test_size = config["dataset"]["test_size"]
    seed = config["seed"]

    train_df, test_df = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df[target_col]
    )

    train_path = Path(config["dataset"]["real_data_path"]).parent / f"{dataset_name}_train.csv"
    test_path = Path(config["dataset"]["real_data_path"]).parent / f"{dataset_name}_test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    train_hash = sha256_of_file(train_path)
    test_hash = sha256_of_file(test_path)

    # --- Fase 2: generazione dati sintetici ---
    synthesizer, metadata, fit_seconds = train_synthesizer(train_df, config)
    synthetic_df, sample_seconds = generate_synthetic_data(synthesizer, n_rows=len(train_df), config=config)
    synthetic_hash = sha256_of_file(config["synthetic"]["output_path"])

    # --- Fase 3: validazione fedelta' ---
    quality_report, diagnostic_report = generate_reports(train_df, synthetic_df, metadata)
    fidelity_summary = extract_fidelity_summary(quality_report, diagnostic_report, train_df, synthetic_df)
    fidelity_plot_paths = generate_all_fidelity_plots(
        quality_report, train_df, synthetic_df, quality["numeric_columns"],
        fidelity_summary, config["report"]["output_dir"]
    )

    # --- Fase 3: validazione privacy ---
    privacy_summary = build_privacy_summary(train_df, test_df, synthetic_df, metadata, config)
    privacy_plot_paths = generate_all_privacy_plots(privacy_summary, config["report"]["output_dir"])

    # --- Fase 4: training e valutazione (Esperimento A: reale, B: sintetico) ---
    numeric_cols = quality["numeric_columns"]
    categorical_cols = [c for c in quality["categorical_columns"] if c != target_col]

    X_train_real, y_train_real_raw = split_features_target(train_df, target_col)
    X_test_real, y_test_raw = split_features_target(test_df, target_col)
    X_train_synth, y_train_synth_raw = split_features_target(synthetic_df, target_col)

    y_train_real, (y_test, y_train_synth), target_encoder = encode_target(
        y_train_real_raw, y_test_raw, y_train_synth_raw
    )

    experiments = {}
    models_dir = Path(config["report"]["output_dir"]) / "models"

    for exp_name, X_train, y_train in [
        ("experiment_A_real", X_train_real, y_train_real),
        ("experiment_B_synthetic", X_train_synth, y_train_synth),
    ]:
        print(f"\n=== {exp_name}: preprocessing + training + evaluation ===")
        preprocessor = build_preprocessor(numeric_cols, categorical_cols)
        X_train_enc = preprocessor.fit_transform(X_train)
        X_test_enc = preprocessor.transform(X_test_real)

        model = train_model(X_train_enc, y_train, config)
        model_path = save_model(model, models_dir / f"{exp_name}.pkl")
        model_hash = sha256_of_file(model_path)

        metrics = evaluate_model(model, X_test_enc, y_test)

        experiments[exp_name] = {
            "train_n_rows": int(X_train.shape[0]),
            "model_type": config["model"]["type"],
            "model_path": model_path,
            "model_sha256": model_hash,
            "metrics": metrics,
        }
        print(f"  Metriche: {metrics}")

    # --- Fase 5: audit trail completo ---
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_used": config,
        "config_sha256": config_hash,
        "config_sources": {
            "base_yaml_sha256": sha256_of_file("configs/base.yaml"),
            "dataset_yaml_sha256": sha256_of_file(f"configs/datasets/{dataset_name}.yaml"),
        },
        "dataset": {
            "path": config["dataset"]["real_data_path"],
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
            "method": config["synthetic"]["method"],
            "output_path": config["synthetic"]["output_path"],
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

    out_dir = Path(config["report"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    report_path = out_dir / "phase1_quality_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    md_report_path = render_markdown_report(report, out_dir / "audit_report.md", json_filename=report_path.name)

    # --- riepilogo leggibile in console ---
    print(f"\n=== Fase 1 completata (dataset: {dataset_name}) ===")
    print(f"Dataset: {quality['n_rows']} righe, {quality['n_cols']} colonne")
    print(f"Target '{target_col}' - class balance: {quality['class_balance_pct']}")

    missing_nonzero = {k: v for k, v in quality["missing_values_pct"].items() if v > 0}
    print(f"Colonne con missing values: {missing_nonzero if missing_nonzero else 'nessuna'}")

    outliers_summary = {
        col: info["pct_outliers"] for col, info in quality["outliers"].items() if info["pct_outliers"] > 0
    }
    print(f"Colonne con outlier (IQR): {outliers_summary if outliers_summary else 'nessuna'}")
    print(f"Hash SHA256 dataset completo: {dataset_hash}")

    print(f"\n=== Split train/test (test_size={test_size}, seed={seed}) ===")
    print(f"  Train: {len(train_df)} righe -> {train_path} (sha256: {train_hash[:16]}...)")
    print(f"  Test:  {len(test_df)} righe -> {test_path} (sha256: {test_hash[:16]}...)")

    print(f"\n=== Fase 2 completata ===")
    print(f"  Metodo: {config['synthetic']['method']}")
    print(f"  Righe generate: {len(synthetic_df)}")
    print(f"  Tempo training: {fit_seconds}s, tempo generazione: {sample_seconds}s")
    print(f"  Hash SHA256 dataset sintetico: {synthetic_hash}")

    print(f"\n=== Fase 3 completata (fedelta') ===")
    print(f"  Overall quality score: {fidelity_summary['overall_quality_score']}")
    print(f"  Column shapes score: {fidelity_summary['column_shapes_score']}")
    print(f"  Column pair trends score: {fidelity_summary['column_pair_trends_score']}")
    print(f"  Diagnostic score (validity/structure): {fidelity_summary['diagnostic']['overall_diagnostic_score']}")

    print(f"\n=== Fase 3 completata (privacy) ===")
    dup = privacy_summary["exact_duplicates"]
    print(f"  Duplicati esatti reale/sintetico: {dup['n_exact_duplicates']} ({dup['pct_exact_duplicates_over_synthetic']}%)")

    nrs = privacy_summary["new_row_synthesis"]
    if nrs.get("status") == "ok":
        print(f"  New Row Synthesis score: {nrs['score']} (soglia indicativa >= 0.8)")
    else:
        print(f"  New Row Synthesis: {nrs.get('status')} - {nrs.get('reason')}")

    dcr = privacy_summary["dcr_overfitting_protection"]
    if dcr.get("status") == "ok":
        print(f"  DCR Overfitting Protection score: {dcr['score']} (ideale ~0.5)")
    else:
        print(f"  DCR Overfitting Protection: {dcr.get('status')} - {dcr.get('reason')}")

    print(f"\n=== Fase 4 completata ===")
    for exp_name, exp in experiments.items():
        print(f"  {exp_name} ({exp['train_n_rows']} righe train): {exp['metrics']}")
    acc_a = experiments["experiment_A_real"]["metrics"]["accuracy"]
    acc_b = experiments["experiment_B_synthetic"]["metrics"]["accuracy"]
    print(f"  Delta accuracy (sintetico - reale): {round(acc_b - acc_a, 4)}")

    print(f"\n=== Fase 5 completata (audit trail) ===")
    print(f"  Report JSON:     {report_path}")
    print(f"  Report Markdown: {md_report_path}")
    print(f"  SHA256 config risolta: {config_hash}")

    print("\nGrafici salvati in:")
    for name, path in {**plot_paths, **fidelity_plot_paths, **privacy_plot_paths}.items():
        if path:
            print(f"  - {name}: {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esegue la pipeline su un singolo dataset (per debug/lancio isolato; "
                     "per la campagna multi-dataset usare run_experiments.py)."
    )
    parser.add_argument(
        "--dataset", default="adult_income",
        help="Nome del dataset: deve esistere configs/datasets/<nome>.yaml"
    )
    args = parser.parse_args()

    main(dataset_name=args.dataset)