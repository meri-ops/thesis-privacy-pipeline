"""Fase 2 - Generazione di dati sintetici a partire dal train set reale.

Supporta due synthesizer, selezionabili da config.yaml (synthetic.method):
- gaussian_copula: modello statistico, veloce, buona baseline per dati misti
  numerici/categorici. E' il default consigliato per iniziare.
- ctgan: rete generativa (GAN), cattura meglio distribuzioni multimodali e
  correlazioni complesse, ma il training e' molto piu' lento (minuti anziche'
  secondi anche su dataset di media dimensione).

Il synthesizer viene addestrato ESCLUSIVAMENTE sul train set: il test set
non deve mai essere usato in questa fase (verra' usato solo in Fase 4 per
la valutazione finale dei modelli).
"""
from pathlib import Path
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer


def _build_metadata(df: pd.DataFrame) -> SingleTableMetadata:
    """Rileva automaticamente i tipi di colonna (numerica, categorica, id, ecc.)
    a partire dal dataframe. SDV usa questi metadati per decidere come
    modellare statisticamente ogni colonna, e la Fase 3 li riusa per
    confrontare correttamente reale vs sintetico.
    """
    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df)
    return metadata


def train_synthesizer(train_df: pd.DataFrame, config: dict):
    """Istanzia e addestra il synthesizer indicato in config.yaml.

    Args:
        train_df: SOLO il train set (mai il test set, mai il dataset completo).
        config: configurazione globale dell'esperimento.

    Returns:
        Tupla (synthesizer, metadata): il synthesizer addestrato e i metadata
        usati per addestrarlo (servono anche in Fase 3 per la validazione).
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
    synthesizer.fit(train_df)
    print("[synthetic] Training completato.")

    return synthesizer, metadata


def generate_synthetic_data(synthesizer, n_rows: int, config: dict) -> pd.DataFrame:
    """Genera n_rows record sintetici e li salva su disco.

    Args:
        synthesizer: oggetto restituito da train_synthesizer.
        n_rows: numero di righe sintetiche da generare (di norma = len(train_df),
            per avere un confronto 1:1 nella Fase 3 di validazione).
        config: configurazione globale dell'esperimento.

    Returns:
        Il DataFrame sintetico generato.
    """
    print(f"[synthetic] Genero {n_rows} righe sintetiche...")
    synthetic_df = synthesizer.sample(num_rows=n_rows)

    output_path = Path(config["synthetic"]["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    synthetic_df.to_csv(output_path, index=False)
    print(f"[synthetic] Dataset sintetico salvato in {output_path}")

    return synthetic_df