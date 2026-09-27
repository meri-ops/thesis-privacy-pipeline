\
# Report di audit — data/real/german_credit.csv

Generato il **2026-09-26T18:36:38.293928+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `f2b32e59989b8459e7fcbdb9435e4c630cbf60be50229136c3da7bef1beb8fe0` |
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
| SHA256 | `227c102de4573201e32befb869189bf001e9b0e341cbbb2b5b9236203cef2b22` |
| Righe | 1000 |
| Colonne | 21 |
| Class balance (%) | {'good': 70.0, 'bad': 30.0} |

**Split train/test** (test_size=0.2, seed=42)

| Set | Righe | Percorso | SHA256 |
|---|---|---|---|
| Train | 800 | `data/real/german_credit_train.csv` | `05025f0f6fb3119f...` |
| Test | 200 | `data/real/german_credit_test.csv` | `2866e3bb5ef470b4...` |


**Missing values (% > 0):** nessuno


**Outlier IQR (% > 0):** `duration`: 7.0%, `credit_amount`: 7.2%, `age`: 2.3%, `existing_credits`: 0.6%, `num_dependents`: 15.5%

---

## 3. Dati sintetici

| Metrica | Valore |
|---|---|
| Metodo | `ctgan` |
| Righe generate | 800 |
| Tempo di training del synthesizer | 14.73s |
| Tempo di generazione | 0.11s |
| Percorso | `data/synthetic/german_credit_synthetic.csv` |
| SHA256 | `dbbff4ac305d247d7968301e5f6767ac5dfa86dfcb671ac0070016d75824ff63` |

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
- `credit_risk`: 0.9688

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | 0 (0.0%) |
| New Row Synthesis | 1.0 (soglia indicativa ≥ 0.8) |
| DCR Overfitting Protection | 0.91 (migliore = 1.0, peggiore = 0.0) |

> Frazione di righe sintetiche che non sono quasi-duplicati di nessuna riga reale. Valore vicino a 1 = buono (righe per lo piu' 'nuove'); valore basso = molte righe sintetiche sono troppo simili a righe reali specifiche.
> Score vicino a 1.0 = il sintetico non e' mai (o quasi) piu' vicino al train che all'holdout: nessuna evidenza di memorizzazione, buon segnale di privacy. Score vicino a 0.0 = il sintetico e' sistematicamente piu' vicino al train: possibile overfitting del synthesizer sui dati di training, con rischio di leakage di record reali. Fonte: SDMetrics DCROverfittingProtection docs.

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