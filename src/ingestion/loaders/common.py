"""Utility condivise tra i loader di dataset. Eventualmente piu' facile aggiungere in
futuro un terzo tipo di loader senza riscrivere questa logica."""
from pathlib import Path
from typing import Optional
import pandas as pd


def normalize_target_column(
    df: pd.DataFrame, target_column: str, source_target_column: Optional[str] = None
) -> pd.DataFrame:
    """Rinomina la colonna target originale nel nome canonico atteso dal
    resto della pipeline (quello dichiarato in config['dataset']['target_column']).
    """
    if target_column in df.columns:
        return df

    candidate = source_target_column or "class"
    if candidate in df.columns:
        return df.rename(columns={candidate: target_column})

    raise KeyError(
        f"Colonna target '{target_column}' non trovata (ne' come '{candidate}'). "
        f"Colonne disponibili: {list(df.columns)}"
    )


def drop_columns(df: pd.DataFrame, columns_to_drop: Optional[list] = None) -> pd.DataFrame:
    """Rimuove le colonne indicate (se presenti) prima che il resto della
    pipeline le veda: identificativi senza valore predittivo (rischio di
    leakage/overfitting se lasciati dentro), o colonne con missing values
    troppo estesi per essere utili senza un'imputazione dedicata.

    No-op se columns_to_drop e' None o vuoto: adult_income non lo usa,
    resta invariato.
    """
    if not columns_to_drop:
        return df
    existing = [c for c in columns_to_drop if c in df.columns]
    return df.drop(columns=existing)


def binarize_target_column(
    df: pd.DataFrame, target_column: str, positive_values: Optional[list] = None
) -> pd.DataFrame:
    """Rimappa un target a piu' di 2 classi in binario: 1 se il valore
    originale e' in positive_values, 0 altrimenti.

    Necessario perche' il resto della pipeline (src/training/evaluate.py)
    assume esplicitamente un target a 2 classi (precision/recall/f1 in
    modalita' 'binary', AUC-ROC con predict_proba[:, 1]): un target a 3+
    classi lascito cosi' com'e' o solleva un errore in fase di valutazione,
    o (peggio) produce un AUC-ROC silenziosamente sbagliato.

    No-op se positive_values e' None: adult_income e' gia' binario di suo,
    resta invariato.
    """
    if not positive_values:
        return df
    df = df.copy()
    df[target_column] = df[target_column].isin(positive_values).astype(int)
    return df


def ensure_parent_dir(path) -> Path:
    """Crea la cartella padre di `path` se non esiste e ritorna il Path."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def load_cached_csv_if_exists(real_path: Path) -> Optional[pd.DataFrame]:
    """Se il CSV locale esiste gia' lo carica e lo ritorna (garantisce
    riproducibilita': stesso file, stesso hash, ad ogni run). Altrimenti
    ritorna None, segnalando al chiamante di scaricare/generare i dati."""
    if real_path.exists():
        print(f"[ingestion] Dataset gia' presente, carico da {real_path}")
        return pd.read_csv(real_path)
    return None