"""Funzioni di hashing usate dall'audit trail per garantire tracciabilita'
e integrita' di dataset, config e modelli"""
import hashlib
import json
from pathlib import Path


def sha256_of_file(path: str, chunk_size: int = 8192) -> str:
    """Calcola l'hash SHA256 di un file leggendolo a blocchi
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File non trovato: {file_path.resolve()}")

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def sha256_of_dict(data: dict) -> str:
    """Calcola l'hash SHA256 di un dizionario di configurazione, dopo averlo
    serializzato in modo deterministico (chiavi ordinate, nessuna ambiguita'
    di whitespace). Necessario ora che la config e' risolta a runtime da piu'
    file (base.yaml + dataset.yaml [+ eventuali override da experiment_grid,
    Fase 3]) e non esiste piu' un unico file config.yaml da hashare
    direttamente.
    """
    serialized = json.dumps(data, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()