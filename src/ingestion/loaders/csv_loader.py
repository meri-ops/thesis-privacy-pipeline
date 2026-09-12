"""Loader generico per dataset gia' distribuiti come CSV 

Se config['dataset']['csv_url'] e' presente, il loader prova a scaricare
il file la prima volta; altrimenti si aspetta che il CSV sia gia' in
real_data_path (scaricato manualmente) e solleva un errore chiaro se manca,
invece di fallire piu' avanti nella pipeline con un errore meno leggibile.
"""
from pathlib import Path
import pandas as pd

from src.ingestion.loaders.common import (
    normalize_target_column,
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

    target_col = ds_cfg["target_column"]
    df = normalize_target_column(df, target_col, ds_cfg.get("source_target_column"))

    return df