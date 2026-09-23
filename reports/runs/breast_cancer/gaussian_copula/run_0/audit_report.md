\
# Report di audit — data/real/breast_cancer.csv

Generato il **2026-09-19T21:26:29.775859+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `67401c6b395d14b51f235a796223803b085a69aacef29a57ab1e05dde5b95611` |
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
| Percorso | `data/real/breast_cancer.csv` |
| SHA256 | `75a1d74a59df9cb0a78ecc0a36085bf8a85239557f178d3b8d758e88b26416e1` |
| Righe | 569 |
| Colonne | 31 |
| Class balance (%) | {1: 62.74, 0: 37.26} |

**Split train/test** (test_size=0.2, seed=42)

| Set | Righe | Percorso | SHA256 |
|---|---|---|---|
| Train | 455 | `data/real/breast_cancer_train.csv` | `1a3d4eb5ffa80df7...` |
| Test | 114 | `data/real/breast_cancer_test.csv` | `209a811a89e2c0d1...` |


**Missing values (% > 0):** nessuno


**Outlier IQR (% > 0):** `mean radius`: 2.46%, `mean texture`: 1.23%, `mean perimeter`: 2.28%, `mean area`: 4.39%, `mean smoothness`: 1.05%, `mean compactness`: 2.81%, `mean concavity`: 3.16%, `mean concave points`: 1.76%, `mean symmetry`: 2.64%, `mean fractal dimension`: 2.64%, `radius error`: 6.68%, `texture error`: 3.51%, `perimeter error`: 6.68%, `area error`: 11.42%, `smoothness error`: 5.27%, `compactness error`: 4.92%, `concavity error`: 3.87%, `concave points error`: 3.34%, `symmetry error`: 4.75%, `fractal dimension error`: 4.92%, `worst radius`: 2.99%, `worst texture`: 0.88%, `worst perimeter`: 2.64%, `worst area`: 6.15%, `worst smoothness`: 1.23%, `worst compactness`: 2.81%, `worst concavity`: 2.11%, `worst symmetry`: 4.04%, `worst fractal dimension`: 4.22%

---

## 3. Dati sintetici

| Metrica | Valore |
|---|---|
| Metodo | `gaussian_copula` |
| Righe generate | 455 |
| Tempo di training del synthesizer | 2.45s |
| Tempo di generazione | 0.19s |
| Percorso | `data/synthetic/breast_cancer_synthetic.csv` |
| SHA256 | `3a2d4a5c70ab5b4b14d20fbdca7e3030e717401e3af79fb82fcdac2dc94a70cd` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | 0.897 |
| Column shapes score | 0.8749 |
| Column pair trends score | 0.9191 |
| Diagnostic score (validity/structure) | 1.0 |

**Column shapes per colonna:**

- `mean radius`: 0.9341
- `mean texture`: 0.9538
- `mean perimeter`: 0.9165
- `mean area`: 0.9077
- `mean smoothness`: 0.8879
- `mean compactness`: 0.9143
- `mean concavity`: 0.8747
- `mean concave points`: 0.8747
- `mean symmetry`: 0.8571
- `mean fractal dimension`: 0.0044
- `radius error`: 0.8945
- `texture error`: 0.9407
- `perimeter error`: 0.8681
- `area error`: 0.8352
- `smoothness error`: 0.9319
- `compactness error`: 0.9121
- `concavity error`: 0.9055
- `concave points error`: 0.9011
- `symmetry error`: 0.9033
- `fractal dimension error`: 0.9055
- `worst radius`: 0.9143
- `worst texture`: 0.9473
- `worst perimeter`: 0.9121
- `worst area`: 0.8132
- `worst smoothness`: 0.9077
- `worst compactness`: 0.9099
- `worst concavity`: 0.9604
- `worst concave points`: 0.8659
- `worst symmetry`: 0.8989
- `worst fractal dimension`: 0.9055
- `target`: 0.9626

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
| experiment_A_real | 455 | 0.9561 | 0.9589 | 0.9722 | 0.9655 | 0.9931 | `4b1dd4981c0778a1...` |
| experiment_B_synthetic | 455 | 0.8772 | 0.9143 | 0.8889 | 0.9014 | 0.9649 | `e766fda497f03b1b...` |


**Delta accuracy (sintetico − reale):** -0.0789

**Target encoding** (classi, indice = posizione): [0, 1]

---

## 5. Grafici generati

- `target_balance` → `reports/runs/breast_cancer/gaussian_copula/run_0/target_balance.png`
- `numeric_distributions` → `reports/runs/breast_cancer/gaussian_copula/run_0/numeric_distributions.png`
- `correlation_heatmap` → `reports/runs/breast_cancer/gaussian_copula/run_0/correlation_heatmap.png`
- `outliers_boxplot` → `reports/runs/breast_cancer/gaussian_copula/run_0/outliers_boxplot.png`
- `column_shapes` → `reports/runs/breast_cancer/gaussian_copula/run_0/fidelity_column_shapes.png`
- `column_pair_trends` → `reports/runs/breast_cancer/gaussian_copula/run_0/fidelity_column_pair_trends.png`
- `real_vs_synthetic_distributions` → `reports/runs/breast_cancer/gaussian_copula/run_0/fidelity_real_vs_synthetic.png`
- `quality_scores_summary` → `reports/runs/breast_cancer/gaussian_copula/run_0/fidelity_scores_summary.png`
- `privacy_scores_summary` → `reports/runs/breast_cancer/gaussian_copula/run_0/privacy_scores_summary.png`


---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `phase1_quality_report.json`.*