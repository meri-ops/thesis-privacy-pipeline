"""Fase 2: enerazione di dati sintetici a partire dal train set reale.

Possono essere selezionati due metodi di sintesi, uno statistico (gaussian_copula) e uno basato su reti generative (ctgan). 
Il metodo viene scelto in config.yaml
-gaussian_copula: modello statistico, veloce, buona baseline per dati misti
numerici/categorici. 
-ctgan: rete generativa (GAN), cattura meglio distribuzioni multimodali e
correlazioni complesse, ma il training e' molto piu' lento (ventina di minuti sul mio hardware. da specificare meglio)

Il sintetizzatore viene addestrato ESCLUSIVAMENTE sul train set
"""
import time
from pathlib import Path
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer


def _build_metadata(df: pd.DataFrame) -> SingleTableMetadata:
    """rileva automaticamente i tipi di colonna (numerica, categorica, id, ecc.)
    a partire dal dataframe. SDV usa questi metadati per decidere come
    modellare statisticamente ogni colonna e poi nella Fase 3 li riusa per
    confrontare correttamente reale vs sintetico.
    """
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    return metadata


def train_synthesizer(train_df: pd.DataFrame, config: dict):
    """istanzia e addestra il synthesizer indicato in config.yaml

    ritorna una tupla con il synthesizer addestrato, 
    e il tempo di training in secondi
    """
    synth_cfg = config["synthetic"]
    method = synth_cfg["method"]

    metadata = _build_metadata(train_df)

    if method == "gaussian_copula":
        synthesizer = GaussianCopulaSynthesizer(metadata)
    elif method == "ctgan":
        synthesizer = CTGANSynthesizer(
            metadata,
            epochs=synth_cfg.get("ctgan_epochs", 100),
            cuda=False,  # CPU-only, coerente con l'ambiente di sviluppo attuale
        )
    else:
        raise ValueError(
            f"Metodo di sintesi non supportato: '{method}'. "
            "Valori validi: 'gaussian_copula', 'ctgan'."
        )

    print(f"[synthetic] Addestro '{method}' su {len(train_df)} righe (train set)...")
    t0 = time.perf_counter()
    synthesizer.fit(train_df)
    fit_seconds = round(time.perf_counter() - t0, 2)
    print(f"[synthetic] Training completato in {fit_seconds}s.")

    return synthesizer, metadata, fit_seconds


def generate_synthetic_data(synthesizer, n_rows: int, config: dict):
    """genera n_rows record sintetici e li salva su disco.

    args:
        synthesizer: oggetto restituito da train_synthesizer.
        n_rows: numero di righe sintetiche da generare (di norma = len(train_df),
            per avere un confronto 1:1 nella Fase 3 di validazione).
        config: configurazione globale dell'esperimento.

    ritorna:
        tupla (synthetic_df, sample_seconds).
    """
    print(f"[synthetic] Genero {n_rows} righe sintetiche...")
    t0 = time.perf_counter()
    synthetic_df = synthesizer.sample(num_rows=n_rows)
    sample_seconds = round(time.perf_counter() - t0, 2)

    output_path = Path(config["synthetic"]["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    synthetic_df.to_csv(output_path, index=False)
    print(f"[synthetic] Dataset sintetico salvato in {output_path} ({sample_seconds}s)")

    return synthetic_df, sample_seconds