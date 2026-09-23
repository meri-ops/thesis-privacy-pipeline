\
# Report di audit — data/real/german_credit.csv

Generato il **2026-09-19T21:52:43.689725+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `c0b77a41c982037055a969c2651069c56c30891a1d970cd59875167d19ca27dd` |
| Metodo sintetico | `gaussian_copula` |
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
| Metodo | `gaussian_copula` |
| Righe generate | 800 |
| Tempo di training del synthesizer | 2.2s |
| Tempo di generazione | 0.22s |
| Percorso | `data/synthetic/german_credit_synthetic.csv` |
| SHA256 | `01815ca6894184c8c77f7683b7bb19d4fec1ceff0a0a8205f64339b8db2babf8` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | 0.7992 |
| Column shapes score | 0.8607 |
| Column pair trends score | 0.7377 |
| Diagnostic score (validity/structure) | 1.0 |

**Column shapes per colonna:**

- `checking_status`: 0.88
- `duration`: 0.855
- `credit_history`: 0.6525
- `purpose`: 0.8488
- `credit_amount`: 0.9338
- `savings_status`: 0.6162
- `employment`: 0.7862
- `installment_commitment`: 0.9712
- `personal_status`: 0.6488
- `other_parties`: 0.93
- `residence_since`: 0.975
- `property_magnitude`: 0.8838
- `age`: 0.98
- `other_payment_plans`: 0.9512
- `housing`: 0.8338
- `existing_credits`: 0.9838
- `job`: 0.8312
- `num_dependents`: 0.9662
- `own_telephone`: 0.5988
- `foreign_worker`: 0.965
- `class`: 0.9825

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | 0 (0.0%) |
| New Row Synthesis | non disponibile — error: Python keyword not valid identifier in numexpr query (<unknown>, line 1) |
| DCR Overfitting Protection | non disponibile — error: DCROverfittingProtection.compute_breakdown() missing 1 required positional argument: 'table_name'. Se l'errore riguarda i nomi dei parametri, la firma di DCROverfittingProtection.compute_breakdown potrebbe differire nella versione di sdmetrics installata: verificare con `help(DCROverfittingProtection.compute_breakdown)` e aggiornare i nomi dei kwargs in questa funzione di conseguenza. |




---

## 4. Training e valutazione (Fase 4)

| Esperimento | Righe train | Accuracy | Precision | Recall | F1 | AUC-ROC | SHA256 modello |
|---|---|---|---|---|---|---|---|
| experiment_A_real | 800 | 0.745 | 0.7834 | 0.8786 | 0.8283 | 0.7832 | `62c1a0cdb088833b...` |
| experiment_B_synthetic | 800 | 0.695 | 0.709 | 0.9571 | 0.8146 | 0.6255 | `e5af1f285b3ab932...` |


**Delta accuracy (sintetico − reale):** -0.05

**Target encoding** (classi, indice = posizione): ['bad', 'good']

---

## 5. Grafici generati

- `target_balance` → `reports/runs/german_credit/gaussian_copula/run_0/target_balance.png`
- `numeric_distributions` → `reports/runs/german_credit/gaussian_copula/run_0/numeric_distributions.png`
- `categorical_distributions` → `reports/runs/german_credit/gaussian_copula/run_0/categorical_distributions.png`
- `correlation_heatmap` → `reports/runs/german_credit/gaussian_copula/run_0/correlation_heatmap.png`
- `outliers_boxplot` → `reports/runs/german_credit/gaussian_copula/run_0/outliers_boxplot.png`
- `column_shapes` → `reports/runs/german_credit/gaussian_copula/run_0/fidelity_column_shapes.png`
- `column_pair_trends` → `reports/runs/german_credit/gaussian_copula/run_0/fidelity_column_pair_trends.png`
- `real_vs_synthetic_distributions` → `reports/runs/german_credit/gaussian_copula/run_0/fidelity_real_vs_synthetic.png`
- `quality_scores_summary` → `reports/runs/german_credit/gaussian_copula/run_0/fidelity_scores_summary.png`


---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `phase1_quality_report.json`.*