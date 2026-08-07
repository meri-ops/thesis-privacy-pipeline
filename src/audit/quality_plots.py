"""Fase 1 - Quality Assessment del dataset reale: solo grafici.

Ogni funzione save_*_plot produce una figura del report visuale (PNG).
Il calcolo delle metriche (compute_quality_report) vive in audit/quality_metrics.py:
questo modulo si occupa solo di visualizzazione, cosi' le due responsabilita'
restano separate e ognuna resta leggibile da sola.
"""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend non interattivo: nessuna finestra grafica richiesta
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=0.95)


def _save_fig(fig, output_path) -> str:
    """Boilerplate comune a ogni save_*_plot: crea la cartella se manca,
    salva il PNG e chiude la figura per non accumulare memoria.
    Centralizzato qui invece che ripetuto in ogni funzione."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out)


def save_target_balance_plot(df: pd.DataFrame, target_column: str, output_path: str) -> str:
    """Barplot della distribuzione delle classi del target: rende immediatamente
    visibile lo sbilanciamento delle classi, rilevante per la Fase 4 (training)."""
    counts = df[target_column].value_counts()
    pct = (counts / counts.sum() * 100).round(1)

    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(counts.index.astype(str), counts.values, color=["#4C72B0", "#DD8452"])
    for bar, p in zip(bars, pct):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{p}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title(f"Class balance — '{target_column}'", fontsize=12, fontweight="bold")
    ax.set_ylabel("Numero di record")
    fig.tight_layout()

    return _save_fig(fig, output_path)


def save_missing_values_plot(df: pd.DataFrame, output_path: str) -> str:
    """Barplot dei missing values per colonna (solo colonne con missing > 0).
    Se non ci sono missing values, non genera nulla e ritorna stringa vuota."""
    missing_pct = (df.isnull().mean() * 100).round(2)
    missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=True)

    if missing_pct.empty:
        return ""

    fig, ax = plt.subplots(figsize=(6, max(2.5, 0.4 * len(missing_pct))))
    ax.barh(missing_pct.index, missing_pct.values, color="#C44E52")
    for i, v in enumerate(missing_pct.values):
        ax.text(v, i, f" {v}%", va="center", fontsize=9)
    ax.set_title("Missing values per colonna (%)", fontsize=12, fontweight="bold")
    ax.set_xlabel("% valori mancanti")
    fig.tight_layout()

    return _save_fig(fig, output_path)


def save_numeric_distributions_plot(df: pd.DataFrame, numeric_cols: list, output_path: str) -> str:
    """Istogrammi con KDE per tutte le variabili numeriche (non limitato a 6:
    se sono tante, la griglia si adatta)."""
    if not numeric_cols:
        return ""

    n = len(numeric_cols)
    n_rows_grid = (n + 2) // 3
    fig, axes = plt.subplots(n_rows_grid, 3, figsize=(13, 3.8 * n_rows_grid))
    axes = np.array(axes).flatten()

    for i, col in enumerate(numeric_cols):
        sns.histplot(df[col].dropna(), bins=30, kde=True, color="#4C72B0", ax=axes[i])
        axes[i].set_title(col, fontsize=11, fontweight="bold")
        axes[i].set_xlabel("")
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    fig.suptitle("Distribuzioni delle variabili numeriche", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    return _save_fig(fig, output_path)


def save_categorical_distributions_plot(df: pd.DataFrame, categorical_cols: list,
                                          output_path: str, top_n: int = 8) -> str:
    """Barplot delle categorie piu' frequenti per ciascuna variabile categorica
    (limitate a top_n per leggibilita' su colonne ad alta cardinalita')."""
    if not categorical_cols:
        return ""

    n = len(categorical_cols)
    n_rows_grid = (n + 1) // 2
    fig, axes = plt.subplots(n_rows_grid, 2, figsize=(13, 3.8 * n_rows_grid))
    axes = np.array(axes).flatten()

    for i, col in enumerate(categorical_cols):
        counts = df[col].value_counts().head(top_n)
        axes[i].barh(counts.index.astype(str)[::-1], counts.values[::-1], color="#55A868")
        axes[i].set_title(f"{col} (top {min(top_n, len(counts))})", fontsize=11, fontweight="bold")
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    fig.suptitle("Distribuzioni delle variabili categoriche", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    return _save_fig(fig, output_path)


def save_correlation_heatmap(df: pd.DataFrame, numeric_cols: list, output_path: str) -> str:
    """Heatmap delle correlazioni (Pearson) tra le variabili numeriche."""
    if len(numeric_cols) < 2:
        return ""

    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(0.9 * len(numeric_cols) + 2, 0.9 * len(numeric_cols) + 1))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Correlazioni tra variabili numeriche", fontsize=12, fontweight="bold")
    fig.tight_layout()

    return _save_fig(fig, output_path)


def save_outliers_boxplot(df: pd.DataFrame, numeric_cols: list, output_path: str) -> str:
    """Boxplot per variabile numerica: rende visibile la presenza di outlier
    (i punti oltre i baffi), coerente con il rilevamento IQR di quality_metrics.py."""
    if not numeric_cols:
        return ""

    n = len(numeric_cols)
    n_rows_grid = (n + 2) // 3
    fig, axes = plt.subplots(n_rows_grid, 3, figsize=(13, 3.5 * n_rows_grid))
    axes = np.array(axes).flatten()

    for i, col in enumerate(numeric_cols):
        sns.boxplot(y=df[col].dropna(), color="#8172B2", ax=axes[i])
        axes[i].set_title(col, fontsize=11, fontweight="bold")
        axes[i].set_ylabel("")
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    fig.suptitle("Boxplot — rilevamento outlier", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])

    return _save_fig(fig, output_path)


def generate_all_plots(df: pd.DataFrame, quality: dict, target_column: str, output_dir: str) -> dict:
    """Orchestratore: genera tutti i grafici della Fase 1 e restituisce
    un dizionario {nome_grafico: path} da inserire nel report di audit."""
    out_dir = Path(output_dir)
    numeric_cols = quality["numeric_columns"]
    categorical_cols = quality["categorical_columns"]

    return {
        "target_balance": save_target_balance_plot(df, target_column, out_dir / "target_balance.png"),
        "missing_values": save_missing_values_plot(df, out_dir / "missing_values.png"),
        "numeric_distributions": save_numeric_distributions_plot(df, numeric_cols, out_dir / "numeric_distributions.png"),
        "categorical_distributions": save_categorical_distributions_plot(df, categorical_cols, out_dir / "categorical_distributions.png"),
        "correlation_heatmap": save_correlation_heatmap(df, numeric_cols, out_dir / "correlation_heatmap.png"),
        "outliers_boxplot": save_outliers_boxplot(df, numeric_cols, out_dir / "outliers_boxplot.png"),
    }