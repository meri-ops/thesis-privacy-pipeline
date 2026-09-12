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