\
# Report di audit — data/real/adult.csv

Generato il **2026-09-26T17:21:55.932820+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `439403b745a20da622d3bc7b8bbf7600504c20d10501266814043ee5ebb45f24` |
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
| Percorso | `data/real/adult.csv` |
| SHA256 | `740de363e8d615339f3d39374a61e92b406af52efd01791f5557129e640beea8` |
| Righe | 48842 |
| Colonne | 15 |
| Class balance (%) | {'<=50K': 76.07, '>50K': 23.93} |

**Split train/test** (test_size=0.2, seed=42)

| Set | Righe | Percorso | SHA256 |
|---|---|---|---|
| Train | 39073 | `data/real/adult_income_train.csv` | `f2fa7033555060fd...` |
| Test | 9769 | `data/real/adult_income_test.csv` | `ecaa0cdd62696590...` |


**Missing values (% > 0):** `workclass`: 5.73%, `occupation`: 5.75%, `native-country`: 1.75%


**Outlier IQR (% > 0):** `age`: 0.44%, `fnlwgt`: 2.97%, `education-num`: 3.67%, `capital-gain`: 8.26%, `capital-loss`: 4.67%, `hours-per-week`: 27.63%

---

## 3. Dati sintetici

| Metrica | Valore |
|---|---|
| Metodo | `gaussian_copula` |
| Righe generate | 39073 |
| Tempo di training del synthesizer | 10.72s |
| Tempo di generazione | 1.09s |
| Percorso | `data/synthetic/adult_synthetic.csv` |
| SHA256 | `48d67a647e1339ea980f02727ea6a5876076dcb275c3d523b5bcd73dca9a7896` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | 0.6156 |
| Column shapes score | 0.6856 |
| Column pair trends score | 0.5455 |
| Diagnostic score (validity/structure) | 1.0 |

**Column shapes per colonna:**

- `age`: 0.9795
- `workclass`: 0.1771
- `fnlwgt`: 0.925
- `education`: 0.67
- `education-num`: 0.8566
- `marital-status`: 0.5545
- `occupation`: 0.8874
- `relationship`: 0.7837
- `race`: 0.8978
- `sex`: 0.7167
- `capital-gain`: 0.0885
- `capital-loss`: 0.3205
- `hours-per-week`: 0.7719
- `native-country`: 0.6598
- `target`: 0.9953

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | 0 (0.0%) |
| New Row Synthesis | non disponibile — error: Python keyword not valid identifier in numexpr query (<unknown>, line 1) |
| DCR Overfitting Protection | 0.9496 (migliore = 1.0, peggiore = 0.0) |


> Score vicino a 1.0 = il sintetico non e' mai (o quasi) piu' vicino al train che all'holdout: nessuna evidenza di memorizzazione, buon segnale di privacy. Score vicino a 0.0 = il sintetico e' sistematicamente piu' vicino al train: possibile overfitting del synthesizer sui dati di training, con rischio di leakage di record reali. Fonte: SDMetrics DCROverfittingProtection docs.

---

## 4. Training e valutazione (Fase 4)

| Esperimento | Righe train | Accuracy | Precision | Recall | F1 | AUC-ROC | SHA256 modello |
|---|---|---|---|---|---|---|---|
| experiment_A_real | 39073 | 0.8576 | 0.739 | 0.6262 | 0.6779 | 0.9055 | `4019fba405d981e4...` |
| experiment_B_synthetic | 39073 | 0.7621 | 1.0 | 0.006 | 0.0119 | 0.762 | `def59254de7989b7...` |


**Delta accuracy (sintetico − reale):** -0.0955

**Target encoding** (classi, indice = posizione): ['<=50K', '>50K']

---

## 5. Grafici generati

- `target_balance` → `reports/runs/adult_income/gaussian_copula/run_0/target_balance.png`
- `missing_values` → `reports/runs/adult_income/gaussian_copula/run_0/missing_values.png`
- `numeric_distributions` → `reports/runs/adult_income/gaussian_copula/run_0/numeric_distributions.png`
- `categorical_distributions` → `reports/runs/adult_income/gaussian_copula/run_0/categorical_distributions.png`
- `correlation_heatmap` → `reports/runs/adult_income/gaussian_copula/run_0/correlation_heatmap.png`
- `outliers_boxplot` → `reports/runs/adult_income/gaussian_copula/run_0/outliers_boxplot.png`
- `column_shapes` → `reports/runs/adult_income/gaussian_copula/run_0/fidelity_column_shapes.png`
- `column_pair_trends` → `reports/runs/adult_income/gaussian_copula/run_0/fidelity_column_pair_trends.png`
- `real_vs_synthetic_distributions` → `reports/runs/adult_income/gaussian_copula/run_0/fidelity_real_vs_synthetic.png`
- `quality_scores_summary` → `reports/runs/adult_income/gaussian_copula/run_0/fidelity_scores_summary.png`
- `privacy_scores_summary` → `reports/runs/adult_income/gaussian_copula/run_0/privacy_scores_summary.png`


---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `phase1_quality_report.json`.*