# autonomous_vehicles_arnaud
# CAV Concern — Longitudinal Reddit Analysis

Longitudinal analysis of public concern about CAV data infrastructure in Reddit
discourse. Pipeline: Apify scrape → Python preprocessing → transformer sentiment
+ zero-shot subsystem coding → Python time-series analysis.

## Environment
- Python 3.12
- `python -m venv .venv` then activate, then `pip install -r requirements.txt`
- Exact versions are pinned in `requirements.txt` (generated with `pip freeze`).

## Run order
1. `python 01_scrape.py`       # Apify two-stage collection → data/raw/
2. `python 02_preprocess.py`   # clean, filter, dedup → data/clean/corpus.parquet
3. `03_classify.ipynb` (Colab) # sentiment + subsystem labels → data/labelled/
4. `python 04_analysis.py`     # aggregate, Mann–Kendall, changepoints, plots → outputs/

## Data
Raw and cleaned corpora are NOT in this repo (size + Reddit usernames).
See data/README for the manifest: counts, date range, snapshot hash.

## Scope
Purposive, non-representative sample. Analysis window 2016-01-01 to 2025-04-30.
