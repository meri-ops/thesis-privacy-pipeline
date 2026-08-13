"""Fase 4 - Valutazione del modello.

Metriche richieste dal piano di tesi: Accuracy, Precision, Recall, F1,
AUC-ROC. Precision/Recall/F1 sono calcolate come "binary": il target e'
sempre a 2 classi per costruzione (vedi preprocessing.clean_data.encode_target),
quindi pos_label=1 di default va bene.
"""
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
)


def evaluate_model(model, X_test, y_test) -> dict:
    """Calcola le metriche di valutazione standard su un test set gia'
    preprocessato (stesso preprocessor/target-encoder usato in training).

    Returns:
        dict con accuracy, precision, recall, f1, auc_roc (auc_roc None se
        il modello non supporta predict_proba).
    """
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred)), 4),
        "recall": round(float(recall_score(y_test, y_pred)), 4),
        "f1": round(float(f1_score(y_test, y_pred)), 4),
    }

    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)[:, 1]
        metrics["auc_roc"] = round(float(roc_auc_score(y_test, y_proba)), 4)
    else:
        metrics["auc_roc"] = None

    return metrics