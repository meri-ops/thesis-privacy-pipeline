"""Loader generico per dataset disponibili su OpenML.
"""
from pathlib import Path
import pandas as pd

from src.ingestion.loaders.common import (
    normalize_target_column,
    ensure_parent_dir,
    load_cached_csv_if_exists,
    drop_columns,
    sanitize_reserved_keyword_values,
)


def load(config: dict) -> pd.DataFrame:
    """Carica un dataset OpenML secondo i parametri in config['dataset']
    """
    ds_cfg = config["dataset"]
    real_path = Path(ds_cfg["real_data_path"])

    cached = load_cached_csv_if_exists(real_path)
    if cached is not None:
        # Anche sulla cache: se target_column e' cambiato in config dopo che
        # il CSV era gia' stato salvato (es. rinominata una colonna target),
        # normalize_target_column e' un no-op se gia' a posto, altrimenti
        # rinomina - evita un KeyError a valle su un CSV ormai disallineato
        # dalla config attuale (bug gia' visto una volta con diabetes_130us).
        target_col = ds_cfg["target_column"]
        cached = normalize_target_column(cached, target_col, ds_cfg.get("source_target_column"))
        return sanitize_reserved_keyword_values(cached)

    print(f"[ingestion] Dataset '{ds_cfg['name']}' non trovato in locale: scarico da OpenML...")
    from sklearn.datasets import fetch_openml

    # OpenML puo' avere piu' dataset con lo stesso nome caricati da utenti
    # diversi: 'openml_data_id' (l'ID numerico univoco) e' il modo piu'
    # specifico e non ambiguo per identificare un dataset esatto, quindi ha
    # precedenza su nome+versione se presente in config.
    if "openml_data_id" in ds_cfg:
        bunch = fetch_openml(
            data_id=ds_cfg["openml_data_id"],
            as_frame=True,
            parser="auto",
        )
    else:
        bunch = fetch_openml(
            name=ds_cfg["openml_name"],
            version=ds_cfg.get("openml_version", "active"),
            as_frame=True,
            parser="auto",
        )
    df = bunch.frame
    df = drop_columns(df, ds_cfg.get("columns_to_drop"))

    target_col = ds_cfg["target_column"]
    df = normalize_target_column(df, target_col, ds_cfg.get("source_target_column"))
    df = sanitize_reserved_keyword_values(df)

    ensure_parent_dir(real_path)
    df.to_csv(real_path, index=False)
    print(f"[ingestion] Dataset salvato in {real_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")

    return df