"""Fase 4 - Training del modello.

Il modello (tipo e iperparametri) e' interamente definito in config.yaml
(sezione `model`), coerentemente con la filosofia "un solo config, nessun
parametro hardcoded" della pipeline.
"""
import pickle
from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression


def build_model(config: dict):
    """Istanzia (senza addestrare) il modello indicato in config.yaml."""
    model_cfg = config["model"]
    model_type = model_cfg["type"]

    if model_type == "random_forest":
        return RandomForestClassifier(
            n_estimators=model_cfg.get("n_estimators", 200),
            max_depth=model_cfg.get("max_depth"),
            random_state=model_cfg.get("random_state", 42),
        )
    elif model_type == "logistic_regression":
        return LogisticRegression(
            max_iter=1000,
            random_state=model_cfg.get("random_state", 42),
        )
    else:
        raise ValueError(
            f"Modello non supportato: '{model_type}'. "
            "Valori validi: 'random_forest', 'logistic_regression'."
        )


def train_model(X_train, y_train, config: dict):
    """Addestra il modello indicato in config.yaml su (X_train, y_train)."""
    model = build_model(config)
    print(f"[training] Addestro '{config['model']['type']}' su {X_train.shape[0]} righe...")
    model.fit(X_train, y_train)
    print("[training] Training completato.")
    return model


def save_model(model, output_path) -> str:
    """Serializza il modello su disco (pickle) per l'audit trail (Fase 5):
    l'hash SHA256 del file .pkl garantisce che il modello valutato sia
    esattamente identificabile/riproducibile a posteriori."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(model, f)
    return str(path)