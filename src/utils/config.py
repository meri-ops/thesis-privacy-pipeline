"""Caricamento centralizzato della configurazione dell'esperimento."""
from pathlib import Path
import yaml


def load_config(config_path: str = "config.yaml") -> dict:
    """Carica config.yaml e lo restituisce come dizionario Python.

    Args:
        config_path: path al file di configurazione (relativo alla root del progetto).

    Returns:
        dict con tutti i parametri dell'esperimento.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config non trovata in {path.resolve()}. "
            "Esegui gli script dalla root del progetto (thesis-project/)."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
