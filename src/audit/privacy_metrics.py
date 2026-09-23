"""Fase 3: validazione privacy del dataset sintetico rispetto ai dati reali

Tre controlli complementari in ordine di rigore crescente:

1. Duplicati esatti: quante righe sintetiche sono identiche, colonna per
   colonna, a una riga del train reale. Controllo elementare ma economico
   e indipendente da SDMetrics: rileva il caso peggiore (memorizzazione
   letterale di record).

2. 2. NewRowSynthesis (SDMetrics): percentuale di righe sintetiche 
che non risultano troppo simili, entro una determinata tolleranza, 
ad alcuna riga reale del training set. La metrica quantifica la novelty 
dei record sintetici.

3. DCR Overfitting Protection (SDMetrics): confronta la Distance 
to Closest Record (DCR) dei dati sintetici rispetto al TRAIN, 
utilizzato per addestrare il synthesizer, e rispetto a un HOLDOUT 
reale mai osservato dal modello (qui: il test set). Se i record 
sintetici risultano sistematicamente più vicini al TRAIN rispetto 
all'HOLDOUT, ciò costituisce un'evidenza di possibile overfitting o 
memorization del training data, anziché di semplice 
generalizzazione della distribuzione sottostante.

"""
import pandas as pd


def _metadata_as_dict(metadata):
    """
    normalizzo il metadata in dict per compatibilita' con SDMetrics
    """
    return metadata.to_dict() if hasattr(metadata, "to_dict") else metadata


def check_exact_duplicates(real_df: pd.DataFrame, synthetic_df: pd.DataFrame) -> dict:
    """righe sintetiche identiche, colonna per colonna, a una riga reale."""
    merged = synthetic_df.merge(real_df.drop_duplicates(), how="inner")
    n_exact_duplicates = len(merged)
    return {
        "n_exact_duplicates": int(n_exact_duplicates),
        "pct_exact_duplicates_over_synthetic": round(
            n_exact_duplicates / len(synthetic_df) * 100, 3
        ) if len(synthetic_df) else 0.0,
    }


def check_new_row_synthesis(
    real_df: pd.DataFrame, synthetic_df: pd.DataFrame, metadata,
    numerical_match_tolerance: float = 0.01, sample_size: int = 10_000,
) -> dict:
    """Percentuale di righe sintetiche 'nuove' (non troppo simili a nessuna
    riga reale). Score vicino a 1 = sintetico prevalentemente novel = meno
    rischio di aver riprodotto record reali quasi identici.
    """
    try:
        from sdmetrics.single_table import NewRowSynthesis
    except ImportError as e:
        return {"status": "skipped", "reason": f"sdmetrics non espone NewRowSynthesis: {e}"}

    try:
        synthetic_sample_size = min(len(synthetic_df), sample_size)
        score = NewRowSynthesis.compute(
            real_data=real_df,
            synthetic_data=synthetic_df,
            metadata=_metadata_as_dict(metadata),
            numerical_match_tolerance=numerical_match_tolerance,
            synthetic_sample_size=synthetic_sample_size,
        )
        return {
            "status": "ok",
            "score": round(float(score), 4),
            "numerical_match_tolerance": numerical_match_tolerance,
            "synthetic_sample_size": synthetic_sample_size,
            "interpretation": (
                "Frazione di righe sintetiche che non sono quasi-duplicati di "
                "nessuna riga reale. Valore vicino a 1 = buono (righe per lo "
                "piu' 'nuove'); valore basso = molte righe sintetiche sono "
                "troppo simili a righe reali specifiche."
            ),
        }
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def check_dcr_overfitting_protection(
    train_df: pd.DataFrame, test_df: pd.DataFrame, synthetic_df: pd.DataFrame,
    metadata, sample_size: int = 5_000, table_name: str = "table",
) -> dict:
    """Confronta la Distance to Closest Record (DCR) del sintetico rispetto
    al train (usato per generare i dati) e rispetto a un holdout reale (qui:
    il test set, mai visto dal synthesizer).

    table_name: alcune versioni di sdmetrics (>=0.18 circa) richiedono un
    nome di tabella per compute_breakdown, coerente col formato metadata
    multi-table {'tables': {table_name: {...}}} introdotto in quelle
    versioni. Con una sola tabella il nome e' arbitrario, non deve
    corrispondere a nulla di specifico nel dataset.
    """
    try:
        from sdmetrics.single_table import DCROverfittingProtection
    except ImportError as e:
        return {"status": "skipped", "reason": f"sdmetrics non espone DCROverfittingProtection: {e}"}

    try:
        num_rows_subsample = min(len(train_df), len(test_df), sample_size)
        breakdown = DCROverfittingProtection.compute_breakdown(
            real_training_data=train_df,
            real_validation_data=test_df,
            synthetic_data=synthetic_df,
            metadata=_metadata_as_dict(metadata),
            num_rows_subsample=num_rows_subsample,
            num_iterations=1,
            table_name=table_name,
        )
        # NB: compute_breakdown NON restituisce "median_DCR_to_*_data" (quelle
        # chiavi non esistono nella risposta di SDMetrics: prima venivano
        # cercate per errore e finivano sempre null nel report). La chiave
        # corretta e' "synthetic_data_percentages", con le due frazioni di
        # righe sintetiche piu' vicine al train vs. all'holdout.
        percentages = breakdown.get("synthetic_data_percentages", {})
        return {
            "status": "ok",
            "score": round(float(breakdown["score"]), 4),
            "pct_synthetic_closer_to_training": percentages.get("closer_to_training"),
            "pct_synthetic_closer_to_holdout": percentages.get("closer_to_holdout"),
            "num_rows_subsample": num_rows_subsample,
            "interpretation": (
                "Score vicino a 1.0 = il sintetico non e' mai (o quasi) piu' "
                "vicino al train che all'holdout: nessuna evidenza di "
                "memorizzazione, buon segnale di privacy. Score vicino a 0.0 "
                "= il sintetico e' sistematicamente piu' vicino al train: "
                "possibile overfitting del synthesizer sui dati di training, "
                "con rischio di leakage di record reali. (0.5 non e' il "
                "valore ideale: e' gia' una zona di attenzione, non neutra.)"
            ),
        }
    except Exception as e:
        return {
            "status": "error",
            "reason": (
                f"{e}. Se l'errore riguarda i nomi dei parametri, la firma di "
                "DCROverfittingProtection.compute_breakdown potrebbe differire "
                "nella versione di sdmetrics installata: verificare con "
                "`help(DCROverfittingProtection.compute_breakdown)` e aggiornare "
                "i nomi dei kwargs in questa funzione di conseguenza."
            ),
        }


def build_privacy_summary(
    train_df: pd.DataFrame, test_df: pd.DataFrame, synthetic_df: pd.DataFrame,
    metadata, config: dict,
) -> dict:
    """Orchestratore Fase 3 - privacy: esegue i tre controlli e li aggrega
    in un unico dizionario JSON-serializzabile per il report di audit.
    """
    privacy_cfg = config.get("privacy", {})

    print("[privacy] Controllo duplicati esatti...")
    exact_duplicates = check_exact_duplicates(train_df, synthetic_df)

    print("[privacy] Controllo NewRowSynthesis (novita' rispetto al reale)...")
    new_row_synthesis = check_new_row_synthesis(
        train_df, synthetic_df, metadata,
        numerical_match_tolerance=privacy_cfg.get("new_row_synthesis_tolerance", 0.01),
        sample_size=privacy_cfg.get("new_row_synthesis_sample_size", 10_000),
    )

    print("[privacy] Controllo DCR Overfitting Protection (train vs holdout)...")
    dcr_overfitting = check_dcr_overfitting_protection(
        train_df, test_df, synthetic_df, metadata,
        sample_size=privacy_cfg.get("dcr_overfitting_sample_size", 5_000),
    )

    return {
        "exact_duplicates": exact_duplicates,
        "new_row_synthesis": new_row_synthesis,
        "dcr_overfitting_protection": dcr_overfitting,
    }