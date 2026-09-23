# Sincronizzazione v3 — fix firma DCROverfittingProtection.compute_breakdown

Un solo file: src/audit/privacy_metrics.py

Aggiunto parametro table_name="table" alla chiamata di
DCROverfittingProtection.compute_breakdown(), richiesto dalla versione di
sdmetrics installata su Kaggle (errore: "missing 1 required positional
argument: 'table_name'"). Non testato in un ambiente locale con sdmetrics
installato: se il prossimo run da un errore diverso, va aggiustato ancora.
