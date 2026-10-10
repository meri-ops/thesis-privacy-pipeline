# Privacy-preserving pipeline for synthetic tabular data

Bachelor's thesis in Computer Engineering. A modular pipeline that generates synthetic tabular data (GaussianCopula, CTGAN via SDV), validates fidelity and privacy risk indicators (SDMetrics), trains a Random Forest on real and synthetic data, and writes an audit report with SHA-256 hashes.

Thesis version: tag `v1.0-tesi`.

## Structure

configs/      base.yaml, experiment_grid.yaml, datasets/*.yaml
src/          ingestion, preprocessing, synthetic, training, audit, analysis, utils, pipeline.py
notebooks/    one notebook per research question (RQ1-RQ3)
reports/      runs/{dataset}/{method}/run_{n}/ and runs_index.jsonl
run_experiments.py   runs the full grid
main.py              runs a single dataset (debug)

## Setup

python -m venv .venv
source .venv/bin/activate      #Windows:venv\Scripts\Activate ps1
pip install -r requirements.txt

Campaigns were run on Kaggle (CPU-only, Python 3.12). Installed versions are listed in the thesis (Appendix A).

## Usage

python run_experiments.py                  # full grid: 3
datasets x 2 methods
python main.py --dataset german_credit     # single run

Each run writes in reports/runs/{dataset}/{method}/run_{n}/ the JSON and
Markdown audit reports, plots and models, and appends a row to
reports/runs_index.jsonl. The index is append-only: relaunching the full grid
duplicates rows.

## Datasets

Adult Income and German Credit (OpenML), Breast Cancer Wisconsin (scikit-learn).
Downloaded at execution time, not redistributed here.

## Known limitations

- Bit-for-bit reproducibility holds within a single session only.
- NewRowSynthesis returns no score for GaussianCopula on Adult Income and German Credit.
- The configuration hash includes the output folder.
- Per-phase timings are not saved in the JSON report.
- Results rely on a single seed (42).
