"""Fase 3 - Grafici di validazione fedelta': confronto visivo reale vs
sintetico, per colonna e per correlazioni tra colonne.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=0.95)


def save_column_shapes_plot(quality_report, output_path: str) -> str:
    """Barplot dello score di fedelta' (0-1) per ciascuna colonna: quanto la
    distribuzione marginale della colonna sintetica assomiglia a quella reale.
    """
    details = quality_report.get_details("Column Shapes").sort_values("Score")

    fig, ax = plt.subplots(figsize=(7, max(3, 0.35 * len(details))))
    colors = ["#C44E52" if s < 0.8 else "#55A868" for s in details["Score"]]
    ax.barh(details["Column"], details["Score"], color=colors)
    ax.axvline(0.8, color="grey", linestyle="--", linewidth=1, label="soglia 0.8")
    ax.set_xlim(0, 1)
    ax.set_xlabel("Fidelity score (1 = distribuzione identica al reale)")
    ax.set_title("Fedelta' per colonna — Column Shapes", fontsize=12, fontweight="bold")
    ax.legend(loc="lower right", fontsize=8)

    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out)


def save_column_pair_trends_heatmap(quality_report, output_path: str) -> str:
    """Heatmap dello score di fedelta' delle correlazioni a coppie di colonne.

    I nomi esatti delle colonne del dettaglio (es. 'Column1' vs 'Column 1')
    cambiano tra versioni di sdmetrics, quindi li rileviamo a runtime invece
    di hardcodarli.
    """
    details = quality_report.get_details("Column Pair Trends")
    if details.empty:
        return ""

    col_name_fields = [c for c in details.columns if "Column" in c]
    if len(col_name_fields) < 2:
        print(f"[fidelity_plots] Colonne inattese in 'Column Pair Trends': {list(details.columns)}")
        return ""
    col1_field, col2_field = col_name_fields[0], col_name_fields[1]

    columns = sorted(set(details[col1_field]) | set(details[col2_field]))
    matrix = pd.DataFrame(1.0, index=columns, columns=columns)
    for _, row in details.iterrows():
        matrix.loc[row[col1_field], row[col2_field]] = row["Score"]
        matrix.loc[row[col2_field], row[col1_field]] = row["Score"]

    fig, ax = plt.subplots(figsize=(0.6 * len(columns) + 3, 0.6 * len(columns) + 2))
    sns.heatmap(matrix, annot=True, fmt=".2f", cmap="RdYlGn", vmin=0, vmax=1,
                square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})
    ax.set_title("Fedelta' delle correlazioni — Column Pair Trends", fontsize=12, fontweight="bold")

    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out)


def save_real_vs_synthetic_distributions(
    real_df: pd.DataFrame, synthetic_df: pd.DataFrame, numeric_cols: list, output_path: str
) -> str:
    """Sovrappone gli istogrammi reale vs sintetico per ciascuna variabile
    numerica: il modo piu' diretto per "vedere ad occhio" la fedelta'.
    """
    if not numeric_cols:
        return ""

    n = len(numeric_cols)
    n_rows_grid = (n + 2) // 3
    fig, axes = plt.subplots(n_rows_grid, 3, figsize=(13, 3.8 * n_rows_grid))
    axes = np.array(axes).flatten()

    for i, col in enumerate(numeric_cols):
        sns.kdeplot(real_df[col].dropna(), ax=axes[i], color="#4C72B0", label="Reale", fill=True, alpha=0.3)
        sns.kdeplot(synthetic_df[col].dropna(), ax=axes[i], color="#DD8452", label="Sintetico", fill=True, alpha=0.3)
        axes[i].set_title(col, fontsize=11, fontweight="bold")
        axes[i].set_xlabel("")
        if i == 0:
            axes[i].legend(fontsize=8)
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")

    fig.suptitle("Distribuzioni: Reale vs Sintetico", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out)


def save_quality_scores_summary_plot(summary: dict, output_path: str) -> str:
    """Barplot riassuntivo dei punteggi principali: overall quality, column
    shapes, column pair trends, e diagnostic (validity/structure)."""
    labels, values = [], []

    labels.append("Overall Quality")
    values.append(summary["overall_quality_score"])

    labels.append("Column Shapes")
    values.append(summary["column_shapes_score"])

    if summary.get("column_pair_trends_score") is not None:
        labels.append("Column Pair Trends")
        values.append(summary["column_pair_trends_score"])

    diagnostic = summary.get("diagnostic", {})
    if diagnostic.get("overall_diagnostic_score") is not None:
        labels.append("Diagnostic (validity)")
        values.append(diagnostic["overall_diagnostic_score"])

    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ["#C44E52" if v < 0.8 else "#55A868" for v in values]
    bars = ax.bar(labels, values, color=colors)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.set_title("Riepilogo score — Fase 3", fontsize=12, fontweight="bold")
    plt.xticks(rotation=15, ha="right")

    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out)


def generate_all_fidelity_plots(
    quality_report, real_df: pd.DataFrame, synthetic_df: pd.DataFrame,
    numeric_cols: list, summary: dict, output_dir: str
) -> dict:
    """Orchestratore: genera tutti i grafici della Fase 3.

    Ogni grafico e' avvolto in un try/except: se una singola funzione fallisce
    per un'incompatibilita' di versione non ancora vista, la pipeline non si
    interrompe del tutto — stampa un avviso e prosegue con gli altri grafici.
    """
    out_dir = Path(output_dir)
    plots = {}

    steps = [
        ("column_shapes", lambda: save_column_shapes_plot(quality_report, out_dir / "fidelity_column_shapes.png")),
        ("column_pair_trends", lambda: save_column_pair_trends_heatmap(quality_report, out_dir / "fidelity_column_pair_trends.png")),
        ("real_vs_synthetic_distributions", lambda: save_real_vs_synthetic_distributions(
            real_df, synthetic_df, numeric_cols, out_dir / "fidelity_real_vs_synthetic.png"
        )),
        ("quality_scores_summary", lambda: save_quality_scores_summary_plot(summary, out_dir / "fidelity_scores_summary.png")),
    ]

    for name, fn in steps:
        try:
            plots[name] = fn()
        except Exception as e:
            print(f"[fidelity_plots] Grafico '{name}' saltato per errore: {e}")
            plots[name] = ""

    return plots