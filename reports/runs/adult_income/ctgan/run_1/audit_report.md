\
# Report di audit — data/real/adult.csv

Generato il **2026-09-19T12:31:38.517313+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `f0aa2d5c9877feb38332ddc4cc03a4fa54712b13de827c7495b84c65327d5ddb` |
| Metodo sintetico | `ctgan` |
| Modello | `random_forest` |

**Iperparametri modello:**

- `type`: `random_forest`
- `n_estimators`: `200`
- `max_depth`: `None`
- `random_state`: `42`

---

## 2. Dataset reale

| Metrica | Valore |
|---|---|
| Percorso | `data/real/adult.csv` |
| SHA256 | `d273d956c28eba72241f69dcbb78e37e93862248503a1873fb44b9fc2a6ae00b` |
| Righe | 48842 |
| Colonne | 15 |
| Class balance (%) | {'<=50K': 76.07, '>50K': 23.93} |

**Split train/test** (test_size=0.2, seed=42)

| Set | Righe | Percorso | SHA256 |
|---|---|---|---|
| Train | 39073 | `data/real/adult_income_train.csv` | `05c231c99941a5af...` |
| Test | 9769 | `data/real/adult_income_test.csv` | `1694e1dee59c50e1...` |


**Missing values (% > 0):** `workclass`: 5.73%, `occupation`: 5.75%, `native-country`: 1.75%


**Outlier IQR (% > 0):** `age`: 0.44%, `fnlwgt`: 2.97%, `education-num`: 3.67%, `capital-gain`: 8.26%, `capital-loss`: 4.67%, `hours-per-week`: 27.63%

---

## 3. Dati sintetici

| Metrica | Valore |
|---|---|
| Metodo | `ctgan` |
| Righe generate | 39073 |
| Tempo di training del synthesizer | 732.31s |
| Tempo di generazione | 1.22s |
| Percorso | `data/synthetic/adult_synthetic.csv` |
| SHA256 | `04a6f90eb419f8a42dfc1c207e477ba7ed227a3b81b8f79b9fa41ba53bac6d76` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | 0.8811 |
| Column shapes score | 0.9046 |
| Column pair trends score | 0.8575 |
| Diagnostic score (validity/structure) | 1.0 |

**Column shapes per colonna:**

- `age`: 0.96
- `workclass`: 0.9398
- `fnlwgt`: 0.8927
- `education`: 0.9182
- `education-num`: 0.9489
- `marital-status`: 0.8679
- `occupation`: 0.8775
- `relationship`: 0.9153
- `race`: 0.9443
- `sex`: 0.9348
- `capital-gain`: 0.7461
- `capital-loss`: 0.8243
- `hours-per-week`: 0.9406
- `native-country`: 0.8681
- `class`: 0.9904

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | 0 (0.0%) |
| New Row Synthesis | 0.999 (soglia indicativa ≥ 0.8) |
| DCR Overfitting Protection | non disponibile — error: DCROverfittingProtection.compute_breakdown() missing 1 required positional argument: 'table_name'. Se l'errore riguarda i nomi dei parametri, la firma di DCROverfittingProtection.compute_breakdown potrebbe differire nella versione di sdmetrics installata: verificare con `help(DCROverfittingProtection.compute_breakdown)` e aggiornare i nomi dei kwargs in questa funzione di conseguenza. |

> Frazione di righe sintetiche che non sono quasi-duplicati di nessuna riga reale. Valore vicino a 1 = buono (righe per lo piu' 'nuove'); valore basso = molte righe sintetiche sono troppo simili a righe reali specifiche.


---

## 4. Training e valutazione (Fase 4)

| Esperimento | Righe train | Accuracy | Precision | Recall | F1 | AUC-ROC | SHA256 modello |
|---|---|---|---|---|---|---|---|
| experiment_A_real | 39073 | 0.8576 | 0.739 | 0.6262 | 0.6779 | 0.9055 | `4019fba405d981e4...` |
| experiment_B_synthetic | 39073 | 0.8323 | 0.6689 | 0.5928 | 0.6286 | 0.8711 | `f524ca1d726157e6...` |


**Delta accuracy (sintetico − reale):** -0.0253

**Target encoding** (classi, indice = posizione): ['<=50K', '>50K']

---

## 5. Grafici generati

- `target_balance` → `reports/runs/adult_income/ctgan/run_1/target_balance.png`
- `missing_values` → `reports/runs/adult_income/ctgan/run_1/missing_values.png`
- `numeric_distributions` → `reports/runs/adult_income/ctgan/run_1/numeric_distributions.png`
- `categorical_distributions` → `reports/runs/adult_income/ctgan/run_1/categorical_distributions.png`
- `correlation_heatmap` → `reports/runs/adult_income/ctgan/run_1/correlation_heatmap.png`
- `outliers_boxplot` → `reports/runs/adult_income/ctgan/run_1/outliers_boxplot.png`
- `column_shapes` → `reports/runs/adult_income/ctgan/run_1/fidelity_column_shapes.png`
- `column_pair_trends` → `reports/runs/adult_income/ctgan/run_1/fidelity_column_pair_trends.png`
- `real_vs_synthetic_distributions` → `reports/runs/adult_income/ctgan/run_1/fidelity_real_vs_synthetic.png`
- `quality_scores_summary` → `reports/runs/adult_income/ctgan/run_1/fidelity_scores_summary.png`
- `privacy_scores_summary` → `reports/runs/adult_income/ctgan/run_1/privacy_scores_summary.png`


---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `phase1_quality_report.json`.*