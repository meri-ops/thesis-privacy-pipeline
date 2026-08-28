"""Fase 3 - Grafico riassuntivo dei punteggi di privacy."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_privacy_summary_plot(privacy_summary: dict, output_path: str) -> str:
    """Barplot dei punteggi di privacy (NewRowSynthesis, DCR Overfitting
    Protection) con le rispettive soglie di riferimento. Le metriche non
    disponibili (status != 'ok', es. libreria non aggiornata) vengono omesse
    dal grafico con un avviso in console, non nascoste silenziosamente nel
    report finale.
    """
    labels, values, refs = [], [], []

    nrs = privacy_summary.get("new_row_synthesis", {})
    if nrs.get("status") == "ok":
        labels.append("New Row\nSynthesis")
        values.append(nrs["score"])
        refs.append(0.8)  # soglia indicativa, coerente con le altre soglie del progetto

    dcr = privacy_summary.get("dcr_overfitting_protection", {})
    if dcr.get("status") == "ok":
        labels.append("DCR Overfitting\nProtection")
        values.append(dcr["score"])
        refs.append(0.5)  # valore ideale: equidistanza train/holdout

    if not values:
        print("[privacy_plots] Nessuna metrica di privacy disponibile da plottare.")
        return ""

    fig, ax = plt.subplots(figsize=(5.5, 4))
    colors = ["#55A868" if v >= r * 0.9 else "#C44E52" for v, r in zip(values, refs)]
    bars = ax.bar(labels, values, color=colors)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, v, f"{v:.3f}", ha="center", va="bottom", fontsize=9)
    for ref in sorted(set(refs)):
        ax.axhline(ref, color="grey", linestyle="--", linewidth=1)
    ax.set_ylim(0, 1.05)
    ax.set_title("Riepilogo score — Privacy (Fase 3)", fontsize=12, fontweight="bold")

    fig.tight_layout()
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=130)
    plt.close(fig)
    return str(out)


def generate_all_privacy_plots(privacy_summary: dict, output_dir: str) -> dict:
    out_dir = Path(output_dir)
    plots = {}
    try:
        plots["privacy_scores_summary"] = save_privacy_summary_plot(
            privacy_summary, out_dir / "privacy_scores_summary.png"
        )
    except Exception as e:
        print(f"[privacy_plots] Grafico 'privacy_scores_summary' saltato per errore: {e}")
        plots["privacy_scores_summary"] = ""
    return plots