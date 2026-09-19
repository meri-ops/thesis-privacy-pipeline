"""Entry point della pipeline per il lancio di un singolo dataset
(debug/lancio manuale di UN dataset alla volta).

La logica delle fasi 1-5 vive in src/pipeline.py::run_pipeline, cosi' da
poter essere richiamata anche da run_experiments.py (Fase 3 del
refactoring) per la campagna sperimentale multi-dataset, con un
output_dir isolato per ogni run.

Configurazione: risolta da configs/base.yaml + configs/datasets/<nome>.yaml
(vedi src/utils/config.py::load_and_merge_config). Il dataset si sceglie
con --dataset da riga di comando (default: adult_income).
"""
import argparse

from src.utils.config import load_and_merge_config
from src.pipeline import run_pipeline


def print_summary(report: dict) -> None:
    """Riepilogo leggibile in console, ricostruito dal dict ritornato da
    run_pipeline (nessun dato calcolato qui: solo formattazione)."""
    dataset_name = report["config_used"]["dataset"]["name"]
    target_col = report["config_used"]["dataset"]["target_column"]
    quality = report["dataset"]["quality_assessment"]
    split = report["split"]
    synthetic = report["synthetic"]
    fidelity = report["fidelity"]
    privacy = report["privacy"]
    experiments = report["experiments"]

    print(f"\n=== Fase 1 completata (dataset: {dataset_name}) ===")
    print(f"Dataset: {quality['n_rows']} righe, {quality['n_cols']} colonne")
    print(f"Target '{target_col}' - class balance: {quality['class_balance_pct']}")

    missing_nonzero = {k: v for k, v in quality["missing_values_pct"].items() if v > 0}
    print(f"Colonne con missing values: {missing_nonzero if missing_nonzero else 'nessuna'}")

    outliers_summary = {
        col: info["pct_outliers"] for col, info in quality["outliers"].items() if info["pct_outliers"] > 0
    }
    print(f"Colonne con outlier (IQR): {outliers_summary if outliers_summary else 'nessuna'}")
    print(f"Hash SHA256 dataset completo: {report['dataset']['sha256']}")

    print(f"\n=== Split train/test (test_size={split['test_size']}, seed={split['seed']}) ===")
    print(f"  Train: {split['train_n_rows']} righe -> {split['train_path']} (sha256: {split['train_sha256'][:16]}...)")
    print(f"  Test:  {split['test_n_rows']} righe -> {split['test_path']} (sha256: {split['test_sha256'][:16]}...)")

    print(f"\n=== Fase 2 completata ===")
    print(f"  Metodo: {synthetic['method']}")
    print(f"  Righe generate: {synthetic['n_rows']}")
    print(f"  Tempo training: {synthetic['fit_seconds']}s, tempo generazione: {synthetic['sample_seconds']}s")
    print(f"  Hash SHA256 dataset sintetico: {synthetic['sha256']}")

    print(f"\n=== Fase 3 completata (fedelta') ===")
    print(f"  Overall quality score: {fidelity['overall_quality_score']}")
    print(f"  Column shapes score: {fidelity['column_shapes_score']}")
    print(f"  Column pair trends score: {fidelity['column_pair_trends_score']}")
    print(f"  Diagnostic score (validity/structure): {fidelity['diagnostic']['overall_diagnostic_score']}")

    print(f"\n=== Fase 3 completata (privacy) ===")
    dup = privacy["exact_duplicates"]
    print(f"  Duplicati esatti reale/sintetico: {dup['n_exact_duplicates']} ({dup['pct_exact_duplicates_over_synthetic']}%)")

    nrs = privacy["new_row_synthesis"]
    if nrs.get("status") == "ok":
        print(f"  New Row Synthesis score: {nrs['score']} (soglia indicativa >= 0.8)")
    else:
        print(f"  New Row Synthesis: {nrs.get('status')} - {nrs.get('reason')}")

    dcr = privacy["dcr_overfitting_protection"]
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
    print(f"  Report JSON:     {report['report_paths']['json']}")
    print(f"  Report Markdown: {report['report_paths']['markdown']}")
    print(f"  SHA256 config risolta: {report['config_sha256']}")

    print("\nGrafici salvati in:")
    for name, path in report["plots"].items():
        if path:
            print(f"  - {name}: {path}")


def main(dataset_name: str = "adult_income") -> dict:
    config = load_and_merge_config(dataset_name)
    report = run_pipeline(config)
    print_summary(report)
    return report


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