# Progettazione e valutazione di una pipeline privacy-preserving per sistemi AI

Tesi triennale — Ingegneria Informatica. Pipeline modulare che integra
generazione di dati sintetici, addestramento di modelli, validazione della
privacy e auditabilita'.

## Stato di avanzamento

- [x] Struttura progetto
- [x] Fase 1 — Ingestion + Quality Assessment dataset reale
- [ ] Fase 2 — Generazione dati sintetici (GaussianCopula / CTGAN)
- [ ] Fase 3 — Validazione privacy/fedeltà (SDMetrics)
- [ ] Fase 4 — Training e valutazione modello
- [ ] Fase 5 — Audit trail completo

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
successive legge il CSV locale. Il report di quality assessment viene
salvato in `reports/phase1_quality_report.json`, insieme a un grafico
delle distribuzioni in `reports/distributions.png`.

## Struttura del progetto

```
thesis-project/
├── data/
│   ├── real/          # dataset reale (non versionato, generato da main.py)
│   └── synthetic/      # dataset sintetico (Fase 2, non ancora implementata)
├── src/
│   ├── ingestion/       # caricamento dati
│   ├── preprocessing/   # pulizia dati (Fase 2)
│   ├── synthetic/        # generazione dati sintetici (Fase 2)
│   ├── training/         # training/valutazione modello (Fase 4)
│   ├── audit/             # metriche di qualita' e audit trail
│   └── utils/             # config loader, hashing
├── reports/             # report generati automaticamente
├── notebooks/           # analisi esplorativa
├── config.yaml          # unico punto di configurazione dell'esperimento
├── requirements.txt
└── main.py              # entry point della pipeline
```
