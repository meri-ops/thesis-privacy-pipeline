"""Fase 1 - Ingestion: carica il dataset Adult Income.

Alla prima esecuzione scarica il dataset da OpenML (serve connessione
internet) e lo salva in data/real/adult.csv. Alle esecuzioni successive
legge direttamente il CSV locale: questo garantisce riproducibilita'
(stesso file, stesso hash, ad ogni run) come richiesto in Fase 5 (audit).
"""
from pathlib import Path
import pandas as pd


def load_adult_income(config: dict) -> pd.DataFrame:
    """Carica il dataset Adult Income secondo i parametri in config.yaml.

    Args:
        config: dizionario di configurazione (vedi src/utils/config.py).

    Returns:
        DataFrame con feature + colonna target.
    """
    ds_cfg = config["dataset"]
    real_path = Path(ds_cfg["real_data_path"])

    if real_path.exists():
        print(f"[ingestion] Dataset gia' presente, carico da {real_path}")
        return pd.read_csv(real_path)

    print("[ingestion] Dataset non trovato in locale: scarico da OpenML...")
    # fetch_openml scarica (e mette in cache) il dataset 'adult' (Adult Income,
    # noto anche come 'Census Income'), lo stesso usato in letteratura sulla
    # generazione di dati sintetici tabellari.
    from sklearn.datasets import fetch_openml

    bunch = fetch_openml(
        name=ds_cfg["openml_name"],
        version=ds_cfg["openml_version"],
        as_frame=True,
        parser="auto",
    )
    df = bunch.frame

    # Normalizziamo il nome della colonna target per essere coerenti con config.yaml
    target_col = ds_cfg["target_column"]
    if target_col not in df.columns and "class" in df.columns:
        df = df.rename(columns={"class": target_col})

    real_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(real_path, index=False)
    print(f"[ingestion] Dataset salvato in {real_path} ({df.shape[0]} righe, {df.shape[1]} colonne)")

    return df


if __name__ == "__main__":
    # Permette di testare il modulo in isolamento: python -m src.ingestion.load_data
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from src.utils.config import load_config

    cfg = load_config("config.yaml")
    data = load_adult_income(cfg)
    print(data.head())
