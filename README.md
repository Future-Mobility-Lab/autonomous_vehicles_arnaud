# Concern about connected and autonomous vehicles in Reddit comments, 2016-2025

Capstone project (UTS 41030). It measures how the share of expressed concern about
connected and autonomous vehicles (CAVs) changes across 2016-2025 in ten Reddit
communities, which vehicle subsystems that concern names, how zero-shot and
fine-tuned classifiers compare on the task, and how much of what keyword search
retrieves is about CAVs at all. The analysis was pre-registered: every rule a result
could depend on was committed before the data it governs existed, and every later
change is recorded as a dated deviation.

## Research questions

- **RQ1.** How does the share of expressed concern about CAVs change across
  2016-2025 in the sampled Reddit discourse?
- **RQ2.** Which CAV subsystems appear in expressed concern, and how do their shares
  develop over time?
- **RQ3.** How do zero-shot and fine-tuned classification approaches compare on this
  domain, in classification accuracy and in cost?
- **RQ4.** What proportion of search-retrieved Reddit comments are about CAVs, and
  what does that imply for search-based corpus construction?

## Where to start

| File | What it holds |
|---|---|
| `docs/analysis_preregistration.md` | The analysis plan: rules R1-R5 and the dated deviations from them. Binding for every analysis. |
| `docs/decision_register.md` | Dated record of decisions, script commits and runs, with the SHA-256 of every input and output. |
| `docs/corpus_manifest.md` | How the corpus was collected and filtered (written for corpus v1; later figures are in the register and in `results/corpus_report.md`). |
| `docs/annotation_codebook.md`, `docs/codebook_reference_labels.csv` | The annotation rules and the 60 worked examples (text column removed). |
| `docs/calibration_instructions.md`, `docs/subsystem_retrofit_instructions.md` | The calibration round and the subsystem labelling instructions. |
| `docs/analysis_plan.md` | The analysis plan. Where it and the pre-registration differ, the pre-registration governs. |
| `MODEL_NOTES.md` | The classifiers of record and their settings. |
| `results/` | The results files of record, each written by a committed script (below). |

## Results of record

| File | Written by |
|---|---|
| `results/sample_results.json`, `results/sample_report.md` | `analysis_01_sample.py`: the annotated sample (prevalence, RQ4, reliability, error rates, the temporal calibration check) |
| `results/corpus_results.json`, `results/corpus_report.md` | `analysis_02_corpus.py`: the corpus description and the thread-size join |
| `results/series_results.json`, `results/series_report.md`, `results/series_values.csv`, `results/series_figures/` | `analysis_03_series.py`: the series analyses (RQ1, RQ2, R3, R4, the sensitivity analyses) |
| `results/report_tables/`, `results/report_figures/` | `analysis_04_tables.py`: the report's data tables and figures, read from the files above |

`results/*_report.md` gives the main figures in readable form; the `.json` files hold
every figure with its counts.

## Pipeline

The analysis-stage scripts (tranche 2 onwards) were each committed before they ran
on the data of record. They check their inputs against the SHA-256 values recorded
in the register and stop if any differs, and their outputs are hashed and recorded
there.

1. **Collection.** `01_scrape.py` retrieves Reddit posts and comments through Apify,
   by search term and time window, into `data/raw/` (694 files). `00_probe.py` and
   `01b_backfill_truncation.py` are collection-stage probes and supplements, and
   `01c_recover_probe_posts.py` recovers the posts that the original 60-post cap
   left out. Shared settings are in `config.py`.
2. **Preprocessing.** `02_preprocess.py` (with `preprocess_content_filters.py`)
   applies the cleaning, bot and duplicate filters, a 20-word floor and an
   English-language filter, giving corpus v2.2 (`data/clean_v2_2/corpus.parquet`:
   12,776 comments, 2016-01-04 to 2025-04-30, in three tiers of subreddits; Tier 3
   is analysed qualitatively). `check_final_corpus.py` is the final quality check and
   freeze manifest; `verify_v2_membership.py` checks the corpus membership.
3. **Sampling frame and draws.** `emit_frozen_frame.py` regenerates the draw frame
   (12,166 Tier 1+2 comments) and verifies it against the recorded values.
   `draw_calibration.py` and `draw_tranche1.py` draw the calibration items and
   tranche 1. The `tranche2_*.py` scripts are the tranche 2 pipeline: the input
   export, the pre-filter scoring, the allocation and its gate (with
   `tranche2_gate_null_simulation.py`), the boosted draw (`tranche2_04_draw.py`, not
   run after the gate failed) and the natural draw that replaced it
   (`tranche2_05_draw_natural.py`). `build_subsystem_retrofit.py` builds the
   subsystem labelling workbooks.
4. **Annotation.** Two natural, era-stratified tranches of 500 comments each were
   annotated by three annotators for relevance (Stage 1), stance (Stage 2: CONCERN,
   ENDORSEMENT, OTHER) and primary subsystem. Gold labels are formed by the committed
   rules (`models_01_prepare.py`). The fold assignments are in `splits/`.
5. **Model comparison** (RQ3). `models_01_prepare.py` to `models_05_evaluate.py`:
   five Stage 2 classifiers under two label schemas and two Stage 1 candidates,
   evaluated by cross-validation on the 1,000 annotated items. The configuration is
   frozen in `models_config.py`; helpers are in `models_common.py`. See
   `MODEL_NOTES.md`.
6. **Corpus runs.** `models_06_deploy.py`: the deployed Stage 1 classifier over all
   12,776 comments, then the Stage 2 classifier and the subsystem classifier over the
   6,503 Tier 1+2 comments classified relevant.
7. **Analyses.** `analysis_01_sample.py`, `analysis_02_corpus.py`,
   `analysis_03_series.py` and `analysis_04_tables.py`, in that order (see the
   results table above).

## Diagnostics and audits

These scripts measured the collection and the corpus; their findings are recorded in
`docs/corpus_manifest.md` and the register. They change no file of record.

- `99_phrase_test.py`: whether the collection actor phrase-matches multi-word search
  terms (the Tier 3 redesign).
- `check_truncation_band.py`: a further check of the collection.
- `check_capture_rate.py`: captured comments against Reddit's reported thread sizes.
- `check_c2_audit.py`: the within-year sampling position before and after the
  supplementary collection (C2).
- `diagnose_bot_authors.py`, `reconcile_bot_filters.py`: checks of the bot filters.

## Superseded

- `skeleton_pipeline.py` and `outputs/`: the walking-skeleton proof of concept from
  the proposal stage (41029). Not part of the analysis.
- `lit_search/superseded/`: superseded literature-search exports and logs.

## Literature search

`literature_search_manifest.md` documents the structured literature search; its
exports, screening workbooks and PRISMA log are in `lit_search/`.

## Environment

- Python 3.12. Create a virtual environment, activate it, then
  `pip install -r requirements.txt`. Exact versions are pinned there.
- The fine-tuning and the Stage 1 corpus run need a GPU (Google Colab); their library
  versions are fixed in `models_config.py` (transformers 5.19.0, scikit-learn 1.9.0).
- The Stage 2 and subsystem runs use the Anthropic API (`anthropic` 1.13.0) and read
  the key from the environment variable `ANTHROPIC_API_KEY`.

## Data

Nothing under `data/` is committed: the raw files and the corpus contain Reddit
usernames and comment text. The register records the SHA-256 of every data file that
an analysis reads, so that a copy can be checked against the record. The corpus is
identified by the SHA-256 of its sorted comment ids (R5).

## Scope

A purposive, non-representative sample of ten subreddits; analysis window 2016-01-01
to 2025-04-30. Claims are about the sampled discourse, at the resolution the
pre-registration allows.
