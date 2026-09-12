"""Caricamento centralizzato della configurazione dell'esperimento"""
from pathlib import Path
import copy
import yaml


def load_config(config_path: str) -> dict:
    """Carica un singolo file YAML e lo restituisce come dizionario
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Config non trovata in {path.resolve()}. "
            "Esegui gli script dalla root del progetto (thesis-project/)."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_and_merge_config(
    dataset_name: str,
    base_path: str = "configs/base.yaml",
    datasets_dir: str = "configs/datasets",
) -> dict:
    """Unisce configs/base.yaml + configs/datasets/<dataset_name>.yaml in
    un'unica configurazione risolta pronta per run_pipeline

    Il merge e' a livello di sezione top-level (es. 'dataset', 'synthetic'):
    le chiavi del file specifico del dataset aggiornano/estendono quelle
    della sezione omonima in base.yaml, invece di sostituirla per intero
    (es. synthetic.output_path del dataset convive con synthetic.method e
    synthetic.ctgan_epochs di base.yaml)
    """
    base = load_config(base_path)
    dataset_cfg = load_config(str(Path(datasets_dir) / f"{dataset_name}.yaml"))

    merged = copy.deepcopy(base)
    for section, values in dataset_cfg.items():
        if section in merged and isinstance(merged[section], dict) and isinstance(values, dict):
            merged[section].update(values)
        else:
            merged[section] = values
    return merged