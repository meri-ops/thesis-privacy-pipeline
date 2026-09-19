"""Fase 3 del refactoring: orchestratore della campagna sperimentale
multi-dataset (item 5 del checklist di migrazione).

Legge configs/experiment_grid.yaml e, per ogni combinazione
(dataset, metodo, replica), costruisce la config risolta con un output_dir
isolato (reports/runs/{dataset}/{metodo}/run_{replica_id}/) e chiama
run_pipeline(config, output_dir=...). Ogni run scrive il proprio report
completo nella propria cartella (nessuna run sovrascrive un'altra); in piu'
un indice leggero (reports/runs_index.jsonl) raccoglie una riga per run coi
soli campi utili all'aggregazione finale (src/analysis/aggregate.py,
item 9 - non ancora scritto).

Punto unico da cui decidere "cosa confrontare": configs/experiment_grid.yaml.
Questo script non va toccato per aggiungere/togliere dataset o metodi.
"""
import argparse
import json
import time
from pathlib import Path

from src.utils.config import load_config, load_and_merge_config
from src.pipeline import run_pipeline


def build_run_config(dataset_name: str, method: str, model_type: str) -> dict:
    """Config risolta (base + dataset) con metodo sintetico e tipo di
    modello sovrascritti dalla griglia (variabili indipendenti/di
    controllo dell'esperimento, non piu' quelle di default in base.yaml).
    """
    config = load_and_merge_config(dataset_name)
    config["synthetic"]["method"] = method
    config["model"]["type"] = model_type
    return config


def build_run_dir(dataset_name: str, method: str, replica_id: int) -> str:
    return str(Path("reports") / "runs" / dataset_name / method / f"run_{replica_id}")


def summarize_for_index(
    report: dict, dataset_name: str, method: str, replica_id: int, run_dir: str, elapsed_seconds: float
) -> dict:
    """Estrae dal report completo solo i campi utili all'aggregazione
    finale (§3.6), cosi' runs_index.jsonl resta leggero e non serve
    riaprire ogni singolo audit_report.md per costruire il DataFrame tidy.
    """
    quality = report["dataset"]["quality_assessment"]
    experiments = report["experiments"]
    nrs = report["privacy"]["new_row_synthesis"]
    dcr = report["privacy"]["dcr_overfitting_protection"]

    acc_real = experiments["experiment_A_real"]["metrics"]["accuracy"]
    acc_synth = experiments["experiment_B_synthetic"]["metrics"]["accuracy"]

    return {
        "dataset": dataset_name,
        "method": method,
        "replica": replica_id,
        "run_dir": run_dir,
        "timestamp": report["timestamp"],
        "elapsed_seconds": round(elapsed_seconds, 2),
        "n_rows": quality["n_rows"],
        "n_features": quality["n_cols"],
        "class_balance_pct": quality["class_balance_pct"],
        "accuracy_real": acc_real,
        "accuracy_synth": acc_synth,
        "delta_accuracy": round(acc_synth - acc_real, 4),
        "overall_quality_score": report["fidelity"]["overall_quality_score"],
        "new_row_synthesis_score": nrs.get("score") if nrs.get("status") == "ok" else None,
        "dcr_score": dcr.get("score") if dcr.get("status") == "ok" else None,
        "synthetic_sha256": report["synthetic"]["sha256"],
        "fit_seconds": report["synthetic"]["fit_seconds"],
        "sample_seconds": report["synthetic"]["sample_seconds"],
        "config_sha256": report["config_sha256"],
    }


def append_to_index(entry: dict, index_path: Path) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with open(index_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def run_grid(grid_path: str = "configs/experiment_grid.yaml") -> None:
    grid = load_config(grid_path)
    index_path = Path("reports") / "runs_index.jsonl"

    combinations = []
    for dataset_name in grid["datasets"]:
        for method in grid["synthetic_methods"]:
            n_replicas = grid.get("repeats_for_reproducibility", 1) if method == "ctgan" else 1
            for replica_id in range(n_replicas):
                combinations.append((dataset_name, method, replica_id))

    print(f"=== Campagna sperimentale: {len(combinations)} run da eseguire ===")
    for dataset_name, method, replica_id in combinations:
        print(f"  - {dataset_name} / {method} / run_{replica_id}")

    campaign_t0 = time.perf_counter()

    for i, (dataset_name, method, replica_id) in enumerate(combinations, start=1):
        run_dir = build_run_dir(dataset_name, method, replica_id)
        print(f"\n[{i}/{len(combinations)}] === {dataset_name} / {method} / run_{replica_id} -> {run_dir} ===")

        run_t0 = time.perf_counter()
        config = build_run_config(dataset_name, method, grid["model"]["type"])
        report = run_pipeline(config, output_dir=run_dir)
        elapsed = time.perf_counter() - run_t0

        entry = summarize_for_index(report, dataset_name, method, replica_id, run_dir, elapsed)
        append_to_index(entry, index_path)
        print(f"  Completata in {entry['elapsed_seconds']}s")

    campaign_elapsed = time.perf_counter() - campaign_t0
    print(f"\n=== Campagna completata in {round(campaign_elapsed, 2)}s ({round(campaign_elapsed / 60, 1)} min) ===")
    print(f"Indice run: {index_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Esegue la griglia di esperimenti (dataset x metodo x replica) "
                     "definita in configs/experiment_grid.yaml."
    )
    parser.add_argument(
        "--grid", default="configs/experiment_grid.yaml",
        help="Path del file YAML della griglia."
    )
    args = parser.parse_args()

    run_grid(grid_path=args.grid)