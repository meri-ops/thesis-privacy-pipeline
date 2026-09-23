# Sincronizzazione v2 — fix DCR + repeats_for_reproducibility

Aggiunta rispetto al pacchetto precedente (sync-package.zip). Sovrascrivi:

- `requirements.txt`: sdmetrics>=0.16 -> sdmetrics>=0.18 (la versione vecchia
  non espone DCROverfittingProtection, per questo era sempre null nei tuoi
  risultati).
- `src/pipeline.py`: aggiunta stampa di ATTENZIONE quando una metrica
  privacy (DCR o NewRowSynthesis) non riesce a calcolarsi, invece di
  fallire in silenzio (lo scoprivi solo aprendo runs_index.jsonl a run
  finita).
- `configs/experiment_grid.yaml`: repeats_for_reproducibility 3 -> 1
  (la riproducibilita' di CTGAN e' gia' dimostrata dai dati che hai, non
  serve riprovarla in questo rilancio - vedi commento nel file).

Con questo, la griglia di default adesso fa 6 run totali (3 dataset x
1 gaussian_copula + 1 ctgan) invece di 12: puoi rilanciare tutto in UN
notebook solo, non serve piu' spezzare per dataset.
