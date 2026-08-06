"""Funzioni di hashing usate dall'audit trail per garantire tracciabilita'
e integrita' di dataset, config e modelli (vedi Fase 5 del piano di tesi)."""
import hashlib
from pathlib import Path


def sha256_of_file(path: str, chunk_size: int = 8192) -> str:
    """Calcola l'hash SHA256 di un file, leggendolo a blocchi (funziona
    anche su file grandi senza caricarli tutti in memoria).
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File non trovato: {file_path.resolve()}")

    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
