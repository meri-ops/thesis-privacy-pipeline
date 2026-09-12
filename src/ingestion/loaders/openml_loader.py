"""Loader generico per dataset disponibili su OpenML.

Alla prima esecuzione scarica da OpenML
e salva un CSV locale alle esecuzioni successive legge solo il
CSV per garantire riproducibilita' (stesso file, stesso hash, Fase 5 audit).
"""
from pathlib import Path
import pandas as pd

from src.ingestion.loaders.common import (
    normalize_target_column,
    ensure_parent_dir,
    load_cached_csv_if_exists,
)


def load(config: dict) -> pd.DataFrame:
    """Carica un dataset OpenML secondo i parametri in config['dataset']
    """
    ds_cfg = config["dataset"]
    real_path = Path(ds_cfg["real_data_path"])

    cached = load_cached_csv_if_exists(real_path)
    if cached is not None:
        return cached

    print(f"[ingestion] Dataset '{ds_cfg['name']}' non trovato in locale: scarico da OpenML...")
    from sklearn.datasets import fetch_openml

    bunch = fetch_openml(
        name=ds_cfg["openml_name"],
        version=ds_cfg.get("openml_version", "active"),
        as_frame=True,
        parser="auto",
    )
    df = bunch.frame

    target_col = ds_cfg["target_column"]
    df = normalize_target_column(df, target_col, ds_cfg.get("source_target_column"))

    ensure_parent_dir(real_path)
    df.to_csv(real_path, index=False)
    print(f"[ingestion] Dataset salvato in {real_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")

    return df