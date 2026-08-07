"""Fase 1 - Quality Assessment del dataset reale: solo calcolo.

Copre tutti i punti richiesti dal piano di tesi:
- valori mancanti per colonna
- statistiche descrittive delle variabili numeriche
- correlazioni tra feature numeriche
- class imbalance del target
- outlier (rilevati con il metodo IQR)

Nessuna dipendenza da matplotlib/seaborn qui: questo modulo produce solo
strutture dati (dict), che finiscono nel report JSON di audit. La
generazione dei grafici vive in audit/plots.py.
"""
import pandas as pd


def _detect_outliers_iqr(series: pd.Series) -> dict:
    """Rileva gli outlier di una colonna numerica con il metodo IQR (1.5 * IQR),
    lo standard de-facto per un quality assessment esplorativo (non serve
    reinventare metodi più sofisticati per questo scopo)."""
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    n_outliers = int(((series < lower) | (series > upper)).sum())
    return {
        "n_outliers": n_outliers,
        "pct_outliers": round(n_outliers / len(series) * 100, 2),
        "lower_bound": round(float(lower), 2),
        "upper_bound": round(float(upper), 2),
    }


def compute_quality_report(df: pd.DataFrame, target_column: str) -> dict:
    """Calcola tutte le metriche di qualita' richieste dalla Fase 1.

    Returns:
        dict con: shape, missing values, class imbalance, colonne numeriche/
        categoriche, statistiche descrittive, outlier per colonna numerica,
        matrice di correlazione tra le variabili numeriche.
    """
    n_rows, n_cols = df.shape

    missing_pct = (df.isnull().mean() * 100).round(2).to_dict()

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = [c for c in df.columns if c not in numeric_cols]

    class_counts = df[target_column].value_counts()
    class_balance = (class_counts / class_counts.sum() * 100).round(2).to_dict()

    outliers = {
        col: _detect_outliers_iqr(df[col].dropna())
        for col in numeric_cols
    }

    correlation_matrix = (
        df[numeric_cols].corr().round(3).to_dict() if len(numeric_cols) > 1 else {}
    )

    report = {
        "n_rows": n_rows,
        "n_cols": n_cols,
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "missing_values_pct": missing_pct,
        "target_column": target_column,
        "class_balance_pct": class_balance,
        "numeric_summary": df[numeric_cols].describe().round(2).to_dict() if numeric_cols else {},
        "outliers": outliers,
        "correlation_matrix": correlation_matrix,
    }
    return report