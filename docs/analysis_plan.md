# Analysis Plan

Corpus frozen 30 August 2026.

The canonical analytical corpus contains **12,820 comments** spanning
2016-01-04 to 2025-04-30.

Corpus membership SHA-256:

`99b6cfc1203f70949d3707615dbceb7d57e6c789632a67b594d114122c6d3e81`

All primary analysis must use this frozen snapshot.

## Primary estimand

All longitudinal outcomes will be **share-based rather than count-based**.

Sampling intensity is uneven by design. A saturated query can contribute at most
48 sampled posts:

- 10 annual blocks x 3 posts
- 9 January-June supplementary blocks x 2 posts

An unsaturated query can contribute up to 100 posts in one study-window job.

High-volume query-subreddit pairs are therefore deliberately sampled less densely
than low-volume pairs.

Comment capture is also strongly dependent on Reddit-reported thread size:

| Reddit-reported thread size | Corrected capture rate |
|---|---:|
| 1-5 | 91.8% |
| 6-15 | 96.5% |
| 16-50 | 48.7% |
| 51-200 | 14.4% |
| 201-1000 | 3.8% |
| 1000+ | 0.7% |

The corrected overall raw capture rate is **9.379%**.

For capture-rate auditing, the denominator for each sampled thread is defined
conservatively as:

`max(commentsCount, unique comments captured)`

This prevents estimated capture exceeding 100% where Reddit's stored
`commentsCount` is smaller than the number of unique comments actually returned.

Raw comment and post counts are therefore functions of the sampling configuration
and must not be interpreted as measures of Reddit discourse volume.

The primary annual outcome will be:

`concern share = comments classified as concern / analysable comments`

The numerator and denominator will be reported alongside each share so that annual
sample size remains visible without treating sample size as discourse volume.

## Temporal analysis

The primary longitudinal resolution is **annual**.

Complete calendar years:

- 2016-2024

Partial year:

- 2025 covers 1 January to 30 April only

The primary longitudinal trend analysis will therefore use **2016-2024**.

The 2025 result will be reported explicitly as a partial-year observation and will
not be treated as directly equivalent to a complete calendar year in the primary
trend test.

Primary longitudinal tests:

- Mann-Kendall trend test
- Sen's slope

Additional analyses such as changepoint detection will be considered exploratory
and used only if their assumptions and value are justified by the resulting annual
series.

## Sampling-position drift

The original annual-block collection was measurably biased toward later positions
within each calendar year because the scraper searches newest-first and stops at
the configured post cap.

On the complete pre-C2 annual frame:

- n = 738 posts
- mean within-year position = 0.73
- slope = +0.0256/year
- p = 0.0075

C2 added nine January-June supplementary blocks for each of the 33 saturated
query-subreddit pairs.

Annual/supplementary overlaps are deduplicated in the primary C2 diagnostic because
repeat retrieval of the same Reddit post is not an independent sampling event.

After C2:

- effective n = 1,062 posts
- mean within-year position = 0.62
- slope = +0.0133/year
- p = 0.0209

C2 reduced the slope magnitude by approximately **48%**, but residual drift remains
statistically distinguishable from zero.

The raw-overlap sensitivity result was:

- slope = +0.0190/year
- p = 0.0098

C2 therefore mitigated but did not eliminate the temporal sampling defect.

The original 181-post diagnostic that triggered C2 measured:

- slope = +0.044/year
- p = 0.0055

Relative to the complete annual-frame estimate of +0.0256/year, the original
diagnostic overstated the slope magnitude by roughly 70%. It remains part of the
audit trail because it correctly identified the direction of the defect and
triggered C2, but it is not the final pre-C2 estimate.

## Planned sensitivity analyses

### 1. Seasonality

Concern share will be compared between:

- H1: January-June
- H2: July-December

for complete calendar years 2016-2024.

The residual post-C2 within-year sampling-position drift is +0.0133/year,
corresponding to an approximately 0.10-year shift across the study span, roughly
five weeks.

Residual sampling drift can materially bias the longitudinal estimate only if
concern prevalence itself varies materially within the year.

If the H1-H2 concern difference is small relative to the observed longitudinal
effect, the residual drift will be described as statistically detectable but
unlikely to materially explain the annual trend.

If the H1-H2 difference is material, seasonality will remain an explicit limitation
and an additional sensitivity analysis will be applied.

This decision rule is specified before concern-classification results are known.

### 2. Word-count threshold

The primary preprocessing pipeline applies a minimum **20-word** comment threshold.

The study-window filter retained 22,115 comments. The 20-word floor reduced this
to 12,820 comments, a reduction of approximately **42%**, making it the largest
single preprocessing filter.

The headline longitudinal result will therefore be checked using alternative
minimum comment lengths of:

- 15 words
- 25 words

The comparison will examine:

- annual concern-share trend
- tier composition
- year composition
- whether the substantive longitudinal conclusion changes

These alternative datasets are sensitivity analyses only. The frozen 20-word
corpus remains the primary analytical corpus.

### 3. Tier stratification

Pooled results will be accompanied by tier-stratified results.

Temporal coverage is uneven for several subreddits:

- r/RealTesla has no surviving comments in 2016
- r/cybersecurity has no surviving comments in 2016 or 2017
- r/waymo has no surviving comments in 2016 or 2017

These subreddits cannot independently support a complete 2016-2024 longitudinal
series covering the entire primary period.

Subreddit-specific trend claims must therefore respect the years actually
observed.

## Classification

Classification will be performed on the frozen corpus.

The final model-selection and validation procedure will be documented before
longitudinal classification results are interpreted.

The analysis must distinguish between:

1. classification-model performance
2. production classification output
3. longitudinal statistical inference

Candidate approaches may include zero-shot and task-specific fine-tuned transformer
models, but no model is designated as the final classifier until its suitability
has been evaluated.

Any manual annotation protocol, inter-rater reliability procedure or prevalence
correction method will be added only after its methodological role and feasibility
have been established.

Classification thresholds, labels and codebook definitions must not be changed in
response to whether the resulting longitudinal trend is statistically significant.

## Multiple testing

Where multiple subsystem-specific hypotheses form one inferential family, an
appropriate multiple-comparison procedure such as Holm-Bonferroni will be used.

The family of tests will be defined before statistical significance is interpreted.

## Reproducibility

Canonical analytical artefact:

`data/clean/corpus.parquet`

Parquet SHA-256:

`358679eaf5ef71c0d643c7c359e6e2b1683a56edb9c832e594baa6ebe06f0526`

Corpus membership SHA-256:

`99b6cfc1203f70949d3707615dbceb7d57e6c789632a67b594d114122c6d3e81`

Authoritative collection and preprocessing audit:

`docs/corpus_manifest.md`

All subsequent primary analytical scripts must read the frozen analytical corpus
rather than rebuilding or modifying the production collection frame.