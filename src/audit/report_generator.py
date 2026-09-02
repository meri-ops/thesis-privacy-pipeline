"""Fase 5: Audit trail: rendering del report JSON in un documento Markdown
Il report JSON (main.py) resta la fonte dati machine-readable e completa;
questo modulo NON ricalcola nulla, pura riformattazione
"""
from pathlib import Path
from jinja2 import Template

_TEMPLATE = Template(r"""\
# Report di audit — {{ report.dataset.path | default("dataset") }}

Generato il **{{ report.timestamp }}** · seed = `{{ report.split.seed }}`

---

## 1. Configurazione

| Campo | Valore |
|---|---|
| File di config | `config.yaml` |
| SHA256 `config.yaml` | `{{ report.config_sha256 }}` |
| Metodo sintetico | `{{ report.synthetic.method }}` |
| Modello | `{{ report.config_used.model.type }}` |

**Iperparametri modello:**
{% for k, v in report.config_used.model.items() %}
- `{{ k }}`: `{{ v }}`
{%- endfor %}

---

## 2. Dataset reale

| Metrica | Valore |
|---|---|
| Percorso | `{{ report.dataset.path }}` |
| SHA256 | `{{ report.dataset.sha256 }}` |
| Righe | {{ report.dataset.quality_assessment.n_rows }} |
| Colonne | {{ report.dataset.quality_assessment.n_cols }} |
| Class balance (%) | {{ report.dataset.quality_assessment.class_balance_pct }} |

**Split train/test** (test_size={{ report.split.test_size }}, seed={{ report.split.seed }})

| Set | Righe | Percorso | SHA256 |
|---|---|---|---|
| Train | {{ report.split.train_n_rows }} | `{{ report.split.train_path }}` | `{{ report.split.train_sha256[:16] }}...` |
| Test | {{ report.split.test_n_rows }} | `{{ report.split.test_path }}` | `{{ report.split.test_sha256[:16] }}...` |

{% set missing = report.dataset.quality_assessment.missing_values_pct.items() | selectattr("1", "gt", 0) | list %}
**Missing values (% > 0):** {% if missing %}{% for k, v in missing %}`{{ k }}`: {{ v }}%{{ ", " if not loop.last }}{% endfor %}{% else %}nessuno{% endif %}

{% set outliers = report.dataset.quality_assessment.outliers.items() | selectattr("1.pct_outliers", "gt", 0) | list %}
**Outlier IQR (% > 0):** {% if outliers %}{% for k, v in outliers %}`{{ k }}`: {{ v.pct_outliers }}%{{ ", " if not loop.last }}{% endfor %}{% else %}nessuno{% endif %}

---

## 3. Dati sintetici

| Metrica | Valore |
|---|---|
| Metodo | `{{ report.synthetic.method }}` |
| Righe generate | {{ report.synthetic.n_rows }} |
| Tempo di training del synthesizer | {{ report.synthetic.fit_seconds }}s |
| Tempo di generazione | {{ report.synthetic.sample_seconds }}s |
| Percorso | `{{ report.synthetic.output_path }}` |
| SHA256 | `{{ report.synthetic.sha256 }}` |

### 3.1 Fedeltà (SDMetrics)

| Metrica | Score |
|---|---|
| Overall quality score | {{ report.fidelity.overall_quality_score }} |
| Column shapes score | {{ report.fidelity.column_shapes_score }} |
| Column pair trends score | {{ report.fidelity.column_pair_trends_score }} |
| Diagnostic score (validity/structure) | {{ report.fidelity.diagnostic.overall_diagnostic_score }} |

**Column shapes per colonna:**
{% for col, score in report.fidelity.column_shapes_per_column.items() %}
- `{{ col }}`: {{ score }}
{%- endfor %}

### 3.2 Privacy

| Controllo | Esito |
|---|---|
| Duplicati esatti | {{ report.privacy.exact_duplicates.n_exact_duplicates }} ({{ report.privacy.exact_duplicates.pct_exact_duplicates_over_synthetic }}%) |
{% set nrs = report.privacy.new_row_synthesis -%}
| New Row Synthesis | {% if nrs.status == "ok" %}{{ nrs.score }} (soglia indicativa ≥ 0.8){% else %}non disponibile — {{ nrs.status }}: {{ nrs.reason }}{% endif %} |
{% set dcr = report.privacy.dcr_overfitting_protection -%}
| DCR Overfitting Protection | {% if dcr.status == "ok" %}{{ dcr.score }} (migliore = 1.0, peggiore = 0.0){% else %}non disponibile — {{ dcr.status }}: {{ dcr.reason }}{% endif %} |

{% if nrs.status == "ok" %}> {{ nrs.interpretation }}{% endif %}
{% if dcr.status == "ok" %}> Score vicino a 1.0 = il sintetico non e' mai (o quasi) piu' vicino al train che all'holdout: nessuna evidenza di memorizzazione, buon segnale di privacy. Score vicino a 0.0 = il sintetico e' sistematicamente piu' vicino al train: possibile overfitting del synthesizer sui dati di training, con rischio di leakage di record reali. Fonte: SDMetrics DCROverfittingProtection docs.{% endif %}

---

## 4. Training e valutazione (Fase 4)

| Esperimento | Righe train | Accuracy | Precision | Recall | F1 | AUC-ROC | SHA256 modello |
|---|---|---|---|---|---|---|---|
{% for name, exp in report.experiments.items() -%}
| {{ name }} | {{ exp.train_n_rows }} | {{ exp.metrics.accuracy }} | {{ exp.metrics.precision }} | {{ exp.metrics.recall }} | {{ exp.metrics.f1 }} | {{ exp.metrics.auc_roc }} | `{{ exp.model_sha256[:16] }}...` |
{% endfor %}

{% set acc_a = report.experiments.experiment_A_real.metrics.accuracy -%}
{% set acc_b = report.experiments.experiment_B_synthetic.metrics.accuracy -%}
**Delta accuracy (sintetico − reale):** {{ (acc_b - acc_a) | round(4) }}

**Target encoding** (classi, indice = posizione): {{ report.target_encoding.classes }}

---

## 5. Grafici generati

{% for name, path in report.plots.items() -%}
{% if path %}- `{{ name }}` → `{{ path }}`
{% endif -%}
{% endfor %}

---
*Report generato automaticamente da `src/audit/report_generator.py`. La fonte dati completa e machine-readable è `{{ json_filename }}`.*
""")


def render_markdown_report(report: dict, output_path: str, json_filename: str = "phase1_quality_report.json") -> str:
    """Renderizza `report` 
    """
    markdown = _TEMPLATE.render(report=report, json_filename=json_filename)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markdown, encoding="utf-8")
    return str(out)