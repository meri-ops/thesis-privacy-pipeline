\
# Report di audit — data/real/breast_cancer.csv

Generato il **2026-09-26T18:34:44.874110+00:00** · seed = `42`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `43092e960aad2063f04cd27d1eb67ce90a1e7f128d7f7cdfb0edcb931431e470` |
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
| Metodo | `ctgan` |
| Righe generate | 455 |
| Tempo di training del synthesizer | 14.72s |
| Tempo di generazione | 0.24s |
| Percorso | `data/synthetic/breast_cancer_synthetic.csv` |
| SHA256 | `610b3cccea85da85f3fe1fa0b4eccb37ab46f5237bbfcea61aec79c3739272c0` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | 0.6447 |
| Column shapes score | 0.6562 |
| Column pair trends score | 0.6333 |
| Diagnostic score (validity/structure) | 1.0 |

**Column shapes per colonna:**

- `mean radius`: 0.8901
- `mean texture`: 0.7099
- `mean perimeter`: 0.5648
- `mean area`: 0.4681
- `mean smoothness`: 0.767
- `mean compactness`: 0.8396
- `mean concavity`: 0.6571
- `mean concave points`: 0.7385
- `mean symmetry`: 0.4725
- `mean fractal dimension`: 0.4418
- `radius error`: 0.7473
- `texture error`: 0.7692
- `perimeter error`: 0.789
- `area error`: 0.7736
- `smoothness error`: 0.3692
- `compactness error`: 0.6879
- `concavity error`: 0.767
- `concave points error`: 0.4923
- `symmetry error`: 0.7297
- `fractal dimension error`: 0.3473
- `worst radius`: 0.5341
- `worst texture`: 0.5187
- `worst perimeter`: 0.7912
- `worst area`: 0.4791
- `worst smoothness`: 0.5099
- `worst compactness`: 0.6198
- `worst concavity`: 0.9033
- `worst concave points`: 0.9297
- `worst symmetry`: 0.611
- `worst fractal dimension`: 0.5253
- `target`: 0.8967

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | 0 (0.0%) |
| New Row Synthesis | 1.0 (soglia indicativa ≥ 0.8) |
| DCR Overfitting Protection | 0.7018 (migliore = 1.0, peggiore = 0.0) |

> Frazione di righe sintetiche che non sono quasi-duplicati di nessuna riga reale. Valore vicino a 1 = buono (righe per lo piu' 'nuove'); valore basso = molte righe sintetiche sono troppo simili a righe reali specifiche.
> Score vicino a 1.0 = il sintetico non e' mai (o quasi) piu' vicino al train che all'holdout: nessuna evidenza di memorizzazione, buon segnale di privacy. Score vicino a 0.0 = il sintetico e' sistematicamente piu' vicino al train: possibile overfitting del synthesizer sui dati di training, con rischio di leakage di record reali. Fonte: SDMetrics DCROverfittingProtection docs.

---

## 4. Training e valutazione (Fase 4)

| Esperimento | Righe train | Accuracy | Precision | Recall | F1 | AUC-ROC | SHA256 modello |
|---|---|---|---|---|---|---|---|
| experiment_A_real | 455 | 0.9561 | 0.9589 | 0.9722 | 0.9655 | 0.9931 | `4b1dd4981c0778a1...` |
| experiment_B_synthetic | 455 | 0.7632 | 0.8571 | 0.75 | 0.8 | 0.8499 | `db7963508ab63635...` |


**Delta accuracy (sintetico − reale):** -0.1929

**Target encoding** (classi, indice = posizione): [0, 1]

---

## 5. Grafici generati

- `target_balance` → `reports/runs/breast_cancer/ctgan/run_1/target_balance.png`
- `numeric_distributions` → `reports/runs/breast_cancer/ctgan/run_1/numeric_distributions.png`
- `correlation_heatmap` → `reports/runs/breast_cancer/ctgan/run_1/correlation_heatmap.png`
- `outliers_boxplot` → `reports/runs/breast_cancer/ctgan/run_1/outliers_boxplot.png`
- `column_shapes` → `reports/runs/breast_cancer/ctgan/run_1/fidelity_column_shapes.png`
- `column_pair_trends` → `reports/runs/breast_cancer/ctgan/run_1/fidelity_column_pair_trends.png`
- `real_vs_synthetic_distributions` → `reports/runs/breast_cancer/ctgan/run_1/fidelity_real_vs_synthetic.png`
- `quality_scores_summary` → `reports/runs/breast_cancer/ctgan/run_1/fidelity_scores_summary.png`
- `privacy_scores_summary` → `reports/runs/breast_cancer/ctgan/run_1/privacy_scores_summary.png`


---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `phase1_quality_report.json`.*