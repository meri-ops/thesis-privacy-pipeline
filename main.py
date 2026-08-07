"""Entry point della pipeline.

Fasi eseguite finora:
- Fase 1: ingestion + quality assessment completo (metriche + grafici)
- Split train/test: il test set viene isolato subito e non verra' mai
  usato per la generazione sintetica (Fase 2) ne' per il training (Fase 4
  lo usera' solo in valutazione finale).
- Fase 2: generazione dati sintetici a partire dal SOLO train set.
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


def main():
    config = load_config("config.yaml")
    target_col = config["dataset"]["target_column"]

    # --- Fase 1: ingestion ---
    df = load_adult_income(config)

    # --- Fase 1: quality assessment (missing values, distribuzioni, correlazioni,
    # class imbalance, outlier) ---
    quality = compute_quality_report(df, target_col)

    # --- Fase 1: grafici (uno per ciascun aspetto richiesto dal piano di tesi) ---
    plot_paths = generate_all_plots(
        df, quality, target_col, config["report"]["output_dir"]
    )

    dataset_hash = sha256_of_file(config["dataset"]["real_data_path"])

    # --- Split train/test: stratificato sul target per preservare il class
    # imbalance in entrambi i sottoinsiemi. Da qui in poi il test set NON
    # viene piu' toccato fino alla valutazione finale in Fase 4. ---
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

    # --- Fase 2: generazione dati sintetici (addestrata SOLO sul train set) ---
    synthesizer = train_synthesizer(train_df, config)
    synthetic_df = generate_synthetic_data(synthesizer, n_rows=len(train_df), config=config)
    synthetic_hash = sha256_of_file(config["synthetic"]["output_path"])

    # --- audit trail: hash di dataset originale, split, e dataset sintetico ---
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
    print(f"Hash SHA256 dataset completo: {dataset_hash}")

    print(f"\n=== Split train/test (test_size={test_size}, seed={seed}) ===")
    print(f"  Train: {len(train_df)} righe -> {train_path} (sha256: {train_hash[:16]}...)")
    print(f"  Test:  {len(test_df)} righe -> {test_path} (sha256: {test_hash[:16]}...)")

    print(f"\n=== Fase 2 completata ===")
    print(f"  Metodo: {config['synthetic']['method']}")
    print(f"  Righe generate: {len(synthetic_df)}")
    print(f"  Hash SHA256 dataset sintetico: {synthetic_hash}")

    print(f"\nReport salvato in: {report_path}")
    print("Grafici salvati in:")
    for name, path in plot_paths.items():
        if path:
            print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()