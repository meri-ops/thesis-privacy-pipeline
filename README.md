# Progettazione e valutazione di una pipeline privacy-preserving per sistemi AI

Tesi triennale — Ingegneria Informatica. Pipeline modulare che integra
generazione di dati sintetici, addestramento di modelli, validazione della
privacy/fedeltà e auditabilità end-to-end.

## Stato di avanzamento

- [x] Struttura progetto
- [x] Fase 1 — Ingestion + Quality Assessment dataset reale
- [x] Split train/test stratificato (con hash SHA256 di entrambi i file)
- [x] Fase 2 — Generazione dati sintetici (GaussianCopula / CTGAN, selezionabile da config)
- [x] Fase 3 — Validazione fedeltà (SDMetrics: Column Shapes, Column Pair Trends, Diagnostic Report)
- [x] Fase 3 — Validazione privacy (duplicati esatti, NewRowSynthesis, DCR Overfitting Protection train-vs-holdout)
- [x] Fase 4 — Training e valutazione modello (Esperimento A: reale, Esperimento B: sintetico, stesso test set reale)
- [x] Fase 5 — Audit trail completo (report JSON + Markdown, hash SHA256 di dataset/train/test/sintetico/modello/config)
- [ ] Confronto automatico GaussianCopula vs CTGAN nello stesso report (oggi richiede due esecuzioni manuali)
- [ ] Test automatici (pytest)
- [ ] Detection Score (SDMetrics) come metrica di fedeltà aggiuntiva

## Setup

```bash
# 1. Crea l'ambiente virtuale (Python 3.10 o 3.11)
py -3.11 -m venv .venv

# 2. Attivalo (PowerShell)
.venv\Scripts\Activate.ps1

# 3. Installa le dipendenze
pip install -r requirements.txt
```

## Esecuzione

```bash
python main.py
```

Alla prima esecuzione scarica il dataset Adult Income da OpenML (serve
connessione internet) e lo salva in `data/real/adult.csv`. Alle esecuzioni
successive legge il CSV locale.

Il metodo di generazione sintetica (`gaussian_copula` o `ctgan`) e il tipo
di modello (`random_forest` o `logistic_regression`) si scelgono in
`config.yaml`, non da riga di comando. **Nota:** eseguire di nuovo la
pipeline sovrascrive il contenuto di `reports/` — per confrontare più
metodi, salvare manualmente i report tra un'esecuzione e l'altra.

Al termine, la pipeline produce:

- `reports/phase1_quality_report.json` — report completo machine-readable
- `reports/audit_report.md` — stesso contenuto, leggibile, con hash SHA256
  di dataset, train/test split, dataset sintetico, modelli e config
- grafici di quality assessment, fedeltà e privacy in `reports/*.png`
- modelli serializzati in `reports/models/*.pkl`

## Struttura del progetto

```text
thesis-project/
├── data/
│   ├── real/            # dataset reale + split train/test (non versionati)
│   └── synthetic/       # dataset sintetico generato (non versionato)
├── src/
│   ├── ingestion/       # caricamento dati (Fase 1)
│   ├── preprocessing/   # encoding feature per il training
│   ├── synthetic/       # generazione dati sintetici (Fase 2)
│   ├── training/        # training/valutazione modello (Fase 4)
│   ├── audit/           # quality/fidelity/privacy metrics + report generator (Fasi 1, 3, 5)
│   └── utils/           # config loader, hashing SHA256
├── reports/             # report e grafici generati automaticamente
├── notebooks/           # analisi esplorativa (non ancora popolata)
├── config.yaml          # unico punto di configurazione dell'esperimento
├── requirements.txt
└── main.py              # entry point della pipeline (Fasi 1→5)
```

## Limiti noti

- Il seed globale non è propagato al training di CTGAN (solo a split e
  modelli scikit-learn): la generazione sintetica con CTGAN non è quindi
  perfettamente riproducibile bit-per-bit tra esecuzioni.
- Un solo dataset (Adult Income), come da scope definito in fase di
  pianificazione.
- `max_depth: null` per RandomForest produce modelli molto pesanti
  (~200 MB ciascuno) e potenzialmente overfit; da rivedere prima
  dell'analisi finale dei risultati.
git