"""Loader generico per dataset gia' distribuiti come CSV

"""
from pathlib import Path
import pandas as pd

from src.ingestion.loaders.common import (
    normalize_target_column,
    binarize_target_column,
    drop_columns,
    ensure_parent_dir,
    load_cached_csv_if_exists,
)


def load(config: dict) -> pd.DataFrame:
    ds_cfg = config["dataset"]
    real_path = Path(ds_cfg["real_data_path"])

    df = load_cached_csv_if_exists(real_path)

    if df is None:
        csv_url = ds_cfg.get("csv_url")
        if not csv_url:
            raise FileNotFoundError(
                f"Dataset '{ds_cfg['name']}' non trovato in {real_path.resolve()} e "
                "nessun 'csv_url' specificato in config per scaricarlo automaticamente. "
                "Scarica il CSV manualmente e posizionalo in quel path."
            )
        print(f"[ingestion] Dataset '{ds_cfg['name']}' non trovato in locale: scarico da {csv_url}...")
        df = pd.read_csv(csv_url)
        ensure_parent_dir(real_path)
        df.to_csv(real_path, index=False)
        print(f"[ingestion] Dataset salvato in {real_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")

    df = drop_columns(df, ds_cfg.get("columns_to_drop"))

    target_col = ds_cfg["target_column"]
    df = normalize_target_column(df, target_col, ds_cfg.get("source_target_column"))
    df = binarize_target_column(df, target_col, ds_cfg.get("target_positive_values"))

    return df