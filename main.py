"""Entry point della pipeline.

Al momento esegue la Fase 1 (ingestion + quality assessment completo) e
genera un primo audit report. Le fasi successive (synthetic, training,
audit completo) verranno agganciate qui via via che vengono implementate,
cosi' che main.py resti sempre il punto unico di esecuzione dell'esperimento.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from src.utils.config import load_config
from src.utils.hashing import sha256_of_file
from src.ingestion.load_data import load_adult_income
from src.audit.metrics import compute_quality_report, generate_all_plots


def main():
    config = load_config("config.yaml")

    # --- Fase 1: ingestion ---
    df = load_adult_income(config)

    # --- Fase 1: quality assessment (missing values, distribuzioni, correlazioni,
    # class imbalance, outlier) ---
    target_col = config["dataset"]["target_column"]
    quality = compute_quality_report(df, target_col)

    # --- Fase 1: grafici (uno per ciascun aspetto richiesto dal piano di tesi) ---
    plot_paths = generate_all_plots(
        df, quality, target_col, config["report"]["output_dir"]
    )

    # --- inizio audit trail: hash del dataset reale usato ---
    dataset_hash = sha256_of_file(config["dataset"]["real_data_path"])

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_used": config,
        "dataset": {
            "path": config["dataset"]["real_data_path"],
            "sha256": dataset_hash,
            "quality_assessment": quality,
        },
        "plots": plot_paths,
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
        col: info["pct_outliers"]
        for col, info in quality["outliers"].items()
        if info["pct_outliers"] > 0
    }
    print(f"Colonne con outlier (IQR): {outliers_summary if outliers_summary else 'nessuna'}")

    print(f"Hash SHA256 dataset: {dataset_hash}")
    print(f"Report salvato in: {report_path}")
    print("Grafici salvati in:")
    for name, path in plot_paths.items():
        if path:
            print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()