"""Entry point della pipeline.

Fasi eseguite finora:
- Fase 1: ingestion + quality assessment completo (metriche + grafici)
- Split train/test: il test set viene isolato subito e non verra' mai
  usato per la generazione sintetica (Fase 2) ne' per il training (Fase 4
  lo usera' solo in valutazione finale).
- Fase 2: generazione dati sintetici a partire dal SOLO train set.
- Fase 3: validazione fedelta' (SDMetrics) e controllo privacy di base
  (duplicati esatti + synthesis score) del sintetico vs il train set.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from sklearn.model_selection import train_test_split

from src.utils.config import load_config
from src.utils.hashing import sha256_of_file
from src.ingestion.load_data import load_adult_income
from src.audit.quality_metrics import compute_quality_report
from src.audit.quality_plots import generate_all_plots
from src.synthetic.generate import train_synthesizer, generate_synthetic_data
from src.audit.fidelity_metrics import generate_reports, extract_fidelity_summary
from src.audit.fidelity_plots import generate_all_fidelity_plots


def main():
    config = load_config("config.yaml")
    target_col = config["dataset"]["target_column"]

    # --- Fase 1: ingestion ---
    df = load_adult_income(config)

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

    train_path = Path(config["dataset"]["real_data_path"]).parent / "adult_train.csv"
    test_path = Path(config["dataset"]["real_data_path"]).parent / "adult_test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    train_hash = sha256_of_file(train_path)
    test_hash = sha256_of_file(test_path)

    # --- Fase 2: generazione dati sintetici ---
    synthesizer, metadata = train_synthesizer(train_df, config)
    synthetic_df = generate_synthetic_data(synthesizer, n_rows=len(train_df), config=config)
    synthetic_hash = sha256_of_file(config["synthetic"]["output_path"])

    # --- Fase 3: validazione fedelta' + privacy di base ---
    quality_report, diagnostic_report = generate_reports(train_df, synthetic_df, metadata)
    fidelity_summary = extract_fidelity_summary(quality_report, diagnostic_report, train_df, synthetic_df)
    fidelity_plot_paths = generate_all_fidelity_plots(
        quality_report, train_df, synthetic_df, quality["numeric_columns"],
        fidelity_summary, config["report"]["output_dir"]
    )

    # --- audit trail completo ---
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_used": config,
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
        },
        "fidelity": fidelity_summary,
        "plots": {**plot_paths, **fidelity_plot_paths},
    }

    out_dir = Path(config["report"]["output_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "phase1_quality_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # --- riepilogo leggibile in console ---
    print("\n=== Fase 1 completata ===")
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
    print(f"  Hash SHA256 dataset sintetico: {synthetic_hash}")

    print(f"\n=== Fase 3 completata ===")
    print(f"  Overall quality score: {fidelity_summary['overall_quality_score']}")
    print(f"  Column shapes score: {fidelity_summary['column_shapes_score']}")
    print(f"  Column pair trends score: {fidelity_summary['column_pair_trends_score']}")
    print(f"  Diagnostic score (validity/structure): {fidelity_summary['diagnostic']['overall_diagnostic_score']}")
    dup = fidelity_summary["privacy_basic_check"]
    print(f"  Duplicati esatti reale/sintetico: {dup['n_exact_duplicates']} ({dup['pct_exact_duplicates_over_synthetic']}%)")

    print(f"\nReport salvato in: {report_path}")
    print("Grafici salvati in:")
    for name, path in {**plot_paths, **fidelity_plot_paths}.items():
        if path:
            print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()