# Sincronizzazione v4 — fix target 'class' di german_credit

- configs/datasets/german_credit.yaml: target_column class -> credit_risk
  (era una parola riservata Python, rompeva NewRowSynthesis).
- src/ingestion/loaders/openml_loader.py: normalize_target_column ora
  applicata anche sul path cache (prima solo su download fresco) — se hai
  gia' un data/real/german_credit.csv locale con la vecchia colonna
  'class', CANCELLALO prima di rilanciare in locale (su Kaggle ripartira'
  pulito, non l'ho incluso nello zip).
