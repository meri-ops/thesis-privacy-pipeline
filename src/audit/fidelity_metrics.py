"""Fase 3 - Validazione fedelta' (fidelity) e controllo privacy di base
del dataset sintetico rispetto al train set reale.

Fedelta': quanto il sintetico riproduce statisticamente il reale
(distribuzioni per colonna, correlazioni tra colonne) - misurata con SDMetrics
tramite il wrapper sdv.evaluation.single_table (QualityReport).

Diagnostica strutturale: validita' dei valori generati (Data Validity: es.
nessun valore fuori range/categoria) e coerenza strutturale con lo schema
originale (Data Structure) - misurata con DiagnosticReport.

Privacy (controllo di base, non esaustivo): quante righe sintetiche sono
copie esatte di righe reali. Metriche di privacy piu' rigorose (distance to
closest record, membership inference) sono rimandate a una fase successiva
se il piano di tesi lo richiede.
"""
import pandas as pd
from sdv.evaluation.single_table import evaluate_quality, run_diagnostic


def generate_reports(real_df: pd.DataFrame, synthetic_df: pd.DataFrame, metadata):
    """Esegue le valutazioni SDMetrics (una sola volta: sono computazionalmente
    non banali su dataset di decine di migliaia di righe).

    Returns:
        Tupla (quality_report, diagnostic_report): oggetti SDV, riusati sia
        per estrarre le metriche numeriche sia per generare i grafici.
    """
    print("[fidelity] Calcolo quality report (fedelta' statistica)...")
    quality_report = evaluate_quality(real_df, synthetic_df, metadata, verbose=False)

    print("[fidelity] Calcolo diagnostic report (validity/structure)...")
    diagnostic_report = run_diagnostic(real_df, synthetic_df, metadata, verbose=False)

    return quality_report, diagnostic_report


def extract_fidelity_summary(
    quality_report, diagnostic_report, real_df: pd.DataFrame, synthetic_df: pd.DataFrame
) -> dict:
    """Estrae dai report SDV un dizionario JSON-serializzabile con tutte le
    metriche rilevanti per la Fase 3.
    """
    column_shapes = quality_report.get_details("Column Shapes")
    column_pair_trends = quality_report.get_details("Column Pair Trends")

    data_validity = diagnostic_report.get_details("Data Validity")
    data_structure = diagnostic_report.get_details("Data Structure")

    # Duplicati esatti: righe sintetiche identiche, colonna per colonna, a una
    # riga del train reale. Un valore alto e' un campanello d'allarme forte di
    # privacy leakage (il synthesizer ha "memorizzato" record reali invece di
    # generalizzare la distribuzione). Questo e' il nostro controllo privacy
    # di base, indipendente dalla libreria SDV.
    merged = synthetic_df.merge(real_df.drop_duplicates(), how="inner")
    n_exact_duplicates = len(merged)

    summary = {
        "overall_quality_score": round(float(quality_report.get_score()), 4),
        "column_shapes_score": round(float(column_shapes["Score"].mean()), 4),
        "column_shapes_per_column": dict(
            zip(column_shapes["Column"], column_shapes["Score"].round(4))
        ),
        "column_pair_trends_score": (
            round(float(column_pair_trends["Score"].mean()), 4)
            if not column_pair_trends.empty else None
        ),
        "diagnostic": {
            "overall_diagnostic_score": round(float(diagnostic_report.get_score()), 4),
            "data_validity_score": (
                round(float(data_validity["Score"].mean()), 4)
                if not data_validity.empty else None
            ),
            "data_validity_per_column": (
                dict(zip(data_validity["Column"], data_validity["Score"].round(4)))
                if not data_validity.empty else {}
            ),
            "data_structure_score": (
                round(float(data_structure["Score"].mean()), 4)
                if not data_structure.empty else None
            ),
        },
        "privacy_basic_check": {
            "n_exact_duplicates": int(n_exact_duplicates),
            "pct_exact_duplicates_over_synthetic": round(
                n_exact_duplicates / len(synthetic_df) * 100, 3
            ),
        },
    }
    return summary