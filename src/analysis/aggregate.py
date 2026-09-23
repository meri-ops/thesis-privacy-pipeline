"""Fase 3 (item 9 del checklist di migrazione): livello di aggregazione
(§3.6 del piano di refactoring).

load_runs_index() legge reports/runs_index.jsonl (una riga JSON per run,
scritta da run_experiments.py::summarize_for_index) e la trasforma in un
unico DataFrame "tidy": una riga per run, con le colonne gia' pronte per
rispondere alle RQ senza dover riaprire nessun report/audit_report.md
singolo.
"""
from pathlib import Path
import json
import pandas as pd


def load_runs_index(index_path: str = "reports/runs_index.jsonl") -> pd.DataFrame:
    """Legge l'indice delle run e ritorna un DataFrame, una riga per run.

    Solleva un errore con un messaggio chiaro se l'indice non esiste
    ancora o e' vuoto, invece di un errore pandas generico.
    """
    path = Path(index_path)
    if not path.exists():
        raise FileNotFoundError(
            f"{path} non esiste: lancia prima run_experiments.py per generarlo."
        )

    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    if not rows:
        raise ValueError(f"{path} esiste ma e' vuoto: nessuna run registrata.")

    return pd.DataFrame(rows)


def summarize_by_dataset_method(df: pd.DataFrame) -> pd.DataFrame:
    """Aggrega per (dataset, method): media e deviazione standard delle
    metriche principali sulle repliche disponibili (1 per gaussian_copula,
    N per ctgan). Utile per le tabelle di sintesi in tesi; non sostituisce
    il DataFrame completo (necessario per RQ3, dove serve vedere la
    variabilita' tra singole repliche, non solo la media).
    """
    metrics = [
        "accuracy_real", "accuracy_synth", "delta_accuracy",
        "overall_quality_score", "new_row_synthesis_score", "dcr_score",
        "fit_seconds", "sample_seconds",
    ]
    return df.groupby(["dataset", "method"])[metrics].agg(["mean", "std"])


if __name__ == "__main__":
    # Uso rapido da riga di comando per un controllo veloce senza notebook:
    # python -m src.analysis.aggregate
    df = load_runs_index()
    print(f"{len(df)} run caricate da reports/runs_index.jsonl\n")
    print(df[["dataset", "method", "replica", "accuracy_real", "accuracy_synth",
              "delta_accuracy", "overall_quality_score"]].to_string(index=False))