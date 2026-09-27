"""Registro centrale dei dataset disponibili per la pipeline.

Aggiungere un nuovo dataset = una riga in LOADERS + un file di config in
configs/datasets
"""
from src.ingestion.loaders import openml_loader, csv_loader, sklearn_loader

LOADERS = {
    "adult_income": openml_loader.load,
    "diabetes_130us": csv_loader.load,
    "breast_cancer": sklearn_loader.load,
    "german_credit": openml_loader.load,
}


def load_dataset(config: dict):
    """Carica il dataset indicato da config['dataset']['name'] usando il
    loader registrato corrispondente

    ValueError se il nome del dataset non e' registrato in LOADERS
    """
    name = config["dataset"]["name"]
    if name not in LOADERS:
        raise ValueError(f"Dataset non registrato: '{name}'. Disponibili: {list(LOADERS)}")
    return LOADERS[name](config)