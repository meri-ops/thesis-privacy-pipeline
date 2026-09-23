\
# Report di audit — data/real/german_credit.csv

Generato il **2026-09-19T21:53:37.499625+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `30c485001b721562c9648d10e8a89e10a40a27d153ca35061ac9a7a318d204da` |
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
| Percorso | `data/real/german_credit.csv` |
| SHA256 | `38b6dbf6fb4b0311a3ffc005730f42623128591fb36473ab3c22d270c0467632` |
| Righe | 1000 |
| Colonne | 21 |
| Class balance (%) | {'good': 70.0, 'bad': 30.0} |

**Split train/test** (test_size=0.2, seed=42)

| Set | Righe | Percorso | SHA256 |
|---|---|---|---|
| Train | 800 | `data/real/german_credit_train.csv` | `72d0854ae9a9409f...` |
| Test | 200 | `data/real/german_credit_test.csv` | `a81103bc4c1be0ac...` |


**Missing values (% > 0):** nessuno


**Outlier IQR (% > 0):** `duration`: 7.0%, `credit_amount`: 7.2%, `age`: 2.3%, `existing_credits`: 0.6%, `num_dependents`: 15.5%

---

## 3. Dati sintetici

| Metrica | Valore |
|---|---|
| Metodo | `ctgan` |
| Righe generate | 800 |
| Tempo di training del synthesizer | 24.95s |
| Tempo di generazione | 0.24s |
| Percorso | `data/synthetic/german_credit_synthetic.csv` |
| SHA256 | `8c31664d53999d66e5597e5e6c8d371b841d90752bebd7ed48e9b0857d0c5727` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | 0.8514 |
| Column shapes score | 0.9202 |
| Column pair trends score | 0.7826 |
| Diagnostic score (validity/structure) | 1.0 |

**Column shapes per colonna:**

- `checking_status`: 0.8875
- `duration`: 0.8012
- `credit_history`: 0.9425
- `purpose`: 0.8112
- `credit_amount`: 0.81
- `savings_status`: 0.985
- `employment`: 0.9125
- `installment_commitment`: 0.8988
- `personal_status`: 0.8288
- `other_parties`: 0.9662
- `residence_since`: 0.9075
- `property_magnitude`: 0.9525
- `age`: 0.89
- `other_payment_plans`: 0.9812
- `housing`: 0.9625
- `existing_credits`: 0.9225
- `job`: 0.9325
- `num_dependents`: 0.9812
- `own_telephone`: 0.9975
- `foreign_worker`: 0.985
- `class`: 0.9688

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | 0 (0.0%) |
| New Row Synthesis | 1.0 (soglia indicativa ≥ 0.8) |
| DCR Overfitting Protection | non disponibile — error: DCROverfittingProtection.compute_breakdown() missing 1 required positional argument: 'table_name'. Se l'errore riguarda i nomi dei parametri, la firma di DCROverfittingProtection.compute_breakdown potrebbe differire nella versione di sdmetrics installata: verificare con `help(DCROverfittingProtection.compute_breakdown)` e aggiornare i nomi dei kwargs in questa funzione di conseguenza. |

> Frazione di righe sintetiche che non sono quasi-duplicati di nessuna riga reale. Valore vicino a 1 = buono (righe per lo piu' 'nuove'); valore basso = molte righe sintetiche sono troppo simili a righe reali specifiche.


---

## 4. Training e valutazione (Fase 4)

| Esperimento | Righe train | Accuracy | Precision | Recall | F1 | AUC-ROC | SHA256 modello |
|---|---|---|---|---|---|---|---|
| experiment_A_real | 800 | 0.745 | 0.7834 | 0.8786 | 0.8283 | 0.7832 | `62c1a0cdb088833b...` |
| experiment_B_synthetic | 800 | 0.705 | 0.7056 | 0.9929 | 0.8249 | 0.527 | `c4ba9c3f34fc9b15...` |


**Delta accuracy (sintetico − reale):** -0.04

**Target encoding** (classi, indice = posizione): ['bad', 'good']

---

## 5. Grafici generati

- `target_balance` → `reports/runs/german_credit/ctgan/run_0/target_balance.png`
- `numeric_distributions` → `reports/runs/german_credit/ctgan/run_0/numeric_distributions.png`
- `categorical_distributions` → `reports/runs/german_credit/ctgan/run_0/categorical_distributions.png`
- `correlation_heatmap` → `reports/runs/german_credit/ctgan/run_0/correlation_heatmap.png`
- `outliers_boxplot` → `reports/runs/german_credit/ctgan/run_0/outliers_boxplot.png`
- `column_shapes` → `reports/runs/german_credit/ctgan/run_0/fidelity_column_shapes.png`
- `column_pair_trends` → `reports/runs/german_credit/ctgan/run_0/fidelity_column_pair_trends.png`
- `real_vs_synthetic_distributions` → `reports/runs/german_credit/ctgan/run_0/fidelity_real_vs_synthetic.png`
- `quality_scores_summary` → `reports/runs/german_credit/ctgan/run_0/fidelity_scores_summary.png`
- `privacy_scores_summary` → `reports/runs/german_credit/ctgan/run_0/privacy_scores_summary.png`


---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `phase1_quality_report.json`.*