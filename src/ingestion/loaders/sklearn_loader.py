"""Loader per dataset inclusi direttamente in scikit-learn (sklearn.datasets).
"""
from pathlib import Path
import pandas as pd

from src.ingestion.loaders.common import (
    normalize_target_column,
    ensure_parent_dir,
    load_cached_csv_if_exists,
    drop_columns,
)

# Registro dei loader bundled disponibili: nome logico -> funzione sklearn.
_SKLEARN_LOADERS = {}
try:
    from sklearn.datasets import load_breast_cancer
    _SKLEARN_LOADERS["breast_cancer"] = load_breast_cancer
except ImportError:  # pragma: no cover - scikit-learn e' comunque una dipendenza del progetto
    pass


def load(config: dict) -> pd.DataFrame:
    """Carica un dataset bundled in scikit-learn secondo config['dataset']."""
    ds_cfg = config["dataset"]
    real_path = Path(ds_cfg["real_data_path"])

    cached = load_cached_csv_if_exists(real_path)
    if cached is not None:
        return cached

    sklearn_name = ds_cfg["sklearn_dataset"]
    if sklearn_name not in _SKLEARN_LOADERS:
        raise ValueError(
            f"Dataset sklearn non registrato: '{sklearn_name}'. "
            f"Disponibili: {list(_SKLEARN_LOADERS)}"
        )

    print(f"[ingestion] Dataset '{ds_cfg['name']}' non trovato in locale: carico da scikit-learn...")
    bunch = _SKLEARN_LOADERS[sklearn_name](as_frame=True)
    df = bunch.frame.copy()

    df = drop_columns(df, ds_cfg.get("columns_to_drop"))

    target_col = ds_cfg["target_column"]
    df = normalize_target_column(df, target_col, ds_cfg.get("source_target_column"))

    ensure_parent_dir(real_path)
    df.to_csv(real_path, index=False)
    print(f"[ingestion] Dataset salvato in {real_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")

    return df
