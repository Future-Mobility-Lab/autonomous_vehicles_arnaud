# CAV Reddit Corpus Manifest

## Frozen analysis corpus

Canonical analytical artefact:

`data/clean/corpus.parquet`

This manifest contains aggregate dataset metadata only. It contains no Reddit
usernames, author identifiers, comment text or raw Reddit comment IDs.

- Final corpus rows: 12,820
- Observed date range: 2016-01-04 to 2025-04-30
- Top-level raw JSON files read by preprocessing: 694
- Parquet file SHA-256: `358679eaf5ef71c0d643c7c359e6e2b1683a56edb9c832e594baa6ebe06f0526`
- Corpus membership SHA-256: `99b6cfc1203f70949d3707615dbceb7d57e6c789632a67b594d114122c6d3e81`

The two hashes serve different purposes.

The **Parquet file SHA-256** identifies the exact stored artefact. It may change
if the same logical dataset is serialised under a different Parquet/PyArrow
environment.

The **Corpus membership SHA-256** is calculated from the sorted final Reddit
comment IDs. It therefore identifies comment membership independently of row
order and Parquet serialisation. It does not detect changes to other fields when
the comment-ID membership remains unchanged.

## Sampling configuration at freeze

- `PROBE_MAX_POSTS = 100`
- `COLLECT_MAX_POSTS = 100`
- `MAX_POSTS_PER_BLOCK = 3`
- `MAX_POSTS_PER_SUPP_BLOCK = 2`
- `MAX_COMMENTS_PER_POST = 15`
- `MAX_COMMENTS_PER_RUN = 1500`
- `BLOCKING_MODE = "annual"`
- Study window: `2016-01-01` to `2025-04-30`

### Sampling intensity is uneven by design

A saturated query receives at most 48 posts (10 annual blocks x 3, plus 9
supplementary blocks x 2). An unsaturated query receives up to 100 posts in a
single window. High-volume query-subreddit pairs are therefore sampled less
densely than low-volume ones.

All longitudinal estimands must consequently be share-based. Comment and post
counts are a function of the sampling configuration and must not be interpreted as
measures of discourse volume.

## Comment capture rate

Reddit's `commentsCount` field stored on each sampled post provides a
Reddit-reported measure of thread size. It is not treated as an exact
ground-truth count of retrievable comments.

For each sampled thread, the capture denominator is defined conservatively as:

`max(commentsCount, unique comments captured)`

This guarantees that estimated capture cannot exceed 100% for an individual
thread while making the smallest correction supported directly by the observed
data.

- Sampled threads with a post record: **2,237**
- Reddit-reported `commentsCount` total: **250,781**
- Effective denominator after correction: **250,909**
- Denominator adjustment: **128 comments**
- Unique comments captured from those threads: **23,534**
- Original uncorrected capture rate: **9.384%**
- Corrected overall capture rate: **9.379%**

### Denominator consistency check

On **95 of 2,237 threads
(4.2%)**, the number of unique comments
actually captured exceeded the stored `commentsCount`.

The total excess was **128 comments**, with a
maximum excess of **4 comments on any one
thread**.

Those inconsistent threads contained
**133 `[deleted]`** and
**13 `[removed]`** comments. In
**95 of
95 threads**, the number of
deleted/removed comments was sufficient to numerically cover the observed excess.
The remaining unexplained excess after allowing for deletion/removal status was
**0 comments**.

This is consistent with Reddit's treatment of deleted and removed comment nodes
contributing to the discrepancy, but it does not establish Reddit's exact internal
counting semantics.

The reported capture rate is therefore a slight **overestimate** of true capture
against a complete denominator: the denominator undercounts the retrievable set,
so the ratio is inflated.

This discrepancy is detectable only where capture approaches 100%, which is why
the effective and reported denominators differ solely in the 1-5 and 6-15 thread
buckets. On a thread where 0.7% of comments are retrieved, an undercounted
denominator cannot be observed at all. The
**4.2%** figure is therefore a **lower
bound** on how often `commentsCount` is unreliable, not an estimate of it.


### Capture rate by Reddit-reported thread size

| Reddit-reported thread size (`commentsCount`) | Threads | Reported comments | Effective denominator | Unique comments captured | Capture rate |
|---|---:|---:|---:|---:|---:|
| 0 | 191 | 0 | 0 | 0 | n/a |
| 1-5 | 414 | 1,066 | 1,096 | 1,006 | 91.8% |
| 6-15 | 360 | 3,496 | 3,594 | 3,469 | 96.5% |
| 16-50 | 474 | 14,548 | 14,548 | 7,089 | 48.7% |
| 51-200 | 525 | 54,519 | 54,519 | 7,875 | 14.4% |
| 201-1000 | 234 | 91,707 | 91,707 | 3,510 | 3.8% |
| 1000+ | 39 | 85,445 | 85,445 | 585 | 0.7% |

Thread-size categories are based on Reddit's reported `commentsCount`, while the
capture denominator within each category uses the conservative corrected value
defined above.

Capture falls sharply as Reddit-reported thread size increases because
`MAX_COMMENTS_PER_POST = 15` limits comments retrieved
from each thread per scraper run. The same strong size-dependent pattern was
reproduced on the complete collection frame.

This provides direct evidence that collected comment counts are a function of the
sampling configuration and must not be interpreted as measures of discourse
volume. Longitudinal estimands are therefore share-based rather than count-based.

## Corpus composition by tier

| Tier | Comments |
|---|---:|
| Tier 1 | 6,652 |
| Tier 2 | 5,603 |
| Tier 3 | 565 |

## Corpus composition by year

| Year | Comments |
|---|---:|
| 2016 | 724 |
| 2017 | 816 |
| 2018 | 1,042 |
| 2019 | 1,305 |
| 2020 | 1,236 |
| 2021 | 1,353 |
| 2022 | 1,300 |
| 2023 | 1,415 |
| 2024 | 2,308 |
| 2025 | 1,321 |

## Subreddit temporal coverage

| Subreddit | Comments | First | Last | Missing study years |
|---|---:|---|---|---|
| r/Futurology | 1,447 | 2016-01-09 | 2025-04-27 | none |
| r/RealTesla | 1,189 | 2017-11-07 | 2025-04-30 | 2016 |
| r/SelfDrivingCars | 2,143 | 2016-01-07 | 2025-04-30 | none |
| r/cars | 1,471 | 2016-02-11 | 2025-04-29 | none |
| r/cybersecurity | 193 | 2018-11-08 | 2025-04-13 | 2016,2017 |
| r/electricvehicles | 1,758 | 2016-01-27 | 2025-04-30 | none |
| r/privacy | 372 | 2016-07-21 | 2025-04-22 | none |
| r/technology | 927 | 2016-01-04 | 2025-04-30 | none |
| r/teslamotors | 2,436 | 2016-01-16 | 2025-04-27 | none |
| r/waymo | 884 | 2018-05-29 | 2025-04-30 | 2016,2017 |

A subreddit with no surviving comments in one or more study years cannot
independently support a complete 2016-2025 annual longitudinal series. The study
window itself ends on 30 April 2025, so 2025 is a partial calendar year by design.

## Preprocessing

`02_preprocess.py` reads the non-recursive glob:

`data/raw/*.json`

The following diagnostic and archive directories are therefore outside the
analytical input:

- `data/raw/_archive_tier3_v1/`
- `data/raw/_failed_backfill/`
- `data/raw/_direct_test/`
- `data/raw/_phrase_test/`
- `data/raw/_probe/`
- `data/raw/_archive_skeleton_test/`

The skeleton test file was moved into `_archive_skeleton_test` before the final
preprocessing run. Its records were dated in July 2026 and had already been
removed by the study-window filter, so this archival move changed the raw-input
count but did not change the final 2016-2025 corpus.

The final analytical corpus contains no Reddit author-name or author-ID columns.

Duplicate Reddit comment IDs after preprocessing: **0**

### Preprocessing funnel

| Stage | Comments retained |
|---|---:|
| raw items | 29,649 |
| comments | 27,126 |
| after dedup | 23,534 |
| after body-deleted removed | 22,291 |
| after bot filter | 22,181 |
| after timestamp parse | 22,181 |
| after study window | 22,115 |
| after >= 20-word floor | 12,820 |
| after English filter | 12,820 |

The **20-word floor is the largest single filter** in the frozen preprocessing
run. The English filter is effectively inert in this corpus: all comments that
reached that stage were retained. `langdetect` runs only on comments that have
already cleared the 20-word floor, where language identification is more reliable,
so the English filter should not be presented as a material source of attrition.

Raw-union maximum unique comments per Reddit thread: **16**

Raw-union threads exceeding 15 unique comments: **1**

Final maximum surviving comments per Reddit thread: **15**

Final threads exceeding 15 surviving comments: **0**

The 15-comment collection cap applied per scraper run, not globally to a Reddit
thread. Overlapping search jobs can therefore produce more than 15 unique raw
comments for one thread. The final thread count is measured after cross-file
deduplication, body/deletion filtering, bot filtering, the study-window filter,
the 20-word floor and the English-language filter. Any final maximum of 15 or
less is therefore an observed preprocessing outcome rather than a globally
enforced collection constraint.

The raw-union maximum was only **16 unique comments per thread**,
with only **1 thread** exceeding 15, despite
**143 duplicate post retrievals during C2**. This is
evidence that repeat crawls of the same Reddit thread returned a near-identical
set of comments rather than accumulating substantially different comment samples.

## Excluded collection: Tier 3 v1

535 comments collected under five multi-word Tier 3 search terms were archived to
`data/raw/_archive_tier3_v1/` and excluded from the analytical corpus.

Measured cause: the scraper does not phrase-match unquoted search terms of three
or more tokens. Across 78 collected files, 0% of posts returned by 3-token terms
contained the search phrase and 7% of those returned by 4-token terms did, against
87-98% for 1-2 token terms. The retrieved posts were consequently off-topic.

Controlled test, 16 August 2026, USD 0.16: quotation marks are passed to Reddit's
search endpoint verbatim, and a quoted 2-token search returned 25 posts at 100%
phrase precision. Tier 3 was redesigned so the subreddit carries the privacy and
security framing while the search term carries only the CAV framing.

Files retained for audit. Logged expenditure USD 7.02.

## Historical collection-cap note

`job_path()` encodes subreddit, search term and date range but does not encode
collection caps. A filename therefore does not, by itself, identify the cap that
was in force when that file was originally collected.

`COLLECT_MAX_POSTS` was raised from 60 to 100 on 16 August 2026.

The ten production files originally collected under the former 60-post cap were:

- `selfdrivingcars__robotaxi__2016-01-01_2025-04-30.json`
- `waymo__waymo__2016-01-01_2025-04-30.json`
- `waymo__autonomous-vehicle__2016-01-01_2025-04-30.json`
- `teslamotors__lidar__2016-01-01_2025-04-30.json`
- `teslamotors__robotaxi__2016-01-01_2025-04-30.json`
- `futurology__lidar__2016-01-01_2025-04-30.json`
- `futurology__robotaxi__2016-01-01_2025-04-30.json`
- `cars__autonomous-vehicle__2016-01-01_2025-04-30.json`
- `electricvehicles__autonomous-vehicle__2016-01-01_2025-04-30.json`
- `electricvehicles__robotaxi__2016-01-01_2025-04-30.json`

Their known probe/production discrepancy was subsequently addressed through the
documented direct URL recovery workflow. The original cap setting remains part
of the corpus audit history.

### MAX_COMMENTS_PER_POST 25 -> 15 verification

`MAX_COMMENTS_PER_POST` was changed from 25 to 15 on 3 August 2026. The frozen
raw files were checked directly using their record-level `crawledAt` timestamps
rather than assuming that the new cap predated production.

No parsed `crawledAt` timestamp in the top-level production/recovery files predates the calendar date **3 August 2026**.

The earliest observed `crawledAt` timestamp was `2026-08-03T11:23:46.859000+00:00`.

However, **10 file(s)** contain at least one `crawledAt` timestamp dated 3 August itself. Because the exact clock time of the configuration change is not encoded in this audit, same-day `crawledAt` values cannot establish whether those particular crawls occurred before or after the 25-to-15 edit.

**110 empty top-level file(s)** contain no records and therefore cannot be independently dated using `crawledAt`.

## Current frame versus scrape log

The final current production frame generated by `build_jobs()` contains
**684 jobs**.

`scrape_log.csv` contains **750 rows** because it is an append-only
execution and expenditure record, not a corpus manifest.

The audited log composition is:

| Log component | Rows |
|---|---:|
| Current standard frame before C2 | 387 |
| Tier 3 v1, subsequently archived | 55 |
| C2 supplementary sampling | 297 |
| Direct URL recovery | 10 |
| Failed date-tail backfill | 1 |
| **Total** | **750** |

The difference between **750 log rows** and **684 current jobs** is therefore
intentional.

## Collection expenditure

- Logged collection expenditure: **USD 80.25**
- Approximate probe and diagnostic expenditure outside `scrape_log.csv`:
  **~USD 13.00**
- Approximate true collection-stage expenditure:
  **~USD 93.25**
- Logged expenditure attributable to archived or failed work:
  **USD 7.07**
- Configured safety ceiling:
  **USD 110.00**

The budget cap was a safety ceiling, not a spending target.

## C2 supplementary sampling

C2 added nine January-June supplementary blocks for each of the 33 saturated
query pairs, producing 297 supplementary jobs.

The supplementary cap was two posts per block. C2 collected 467 posts and 5,600
comments, 6,067 items in total, at a logged cost of USD 18.07 against a pre-run
prediction of USD 18.30.

On the complete current annual-block frame, the pre-C2 within-year
sampling-position slope was **+0.0256/year (p = 0.0075)**.

After C2, using the deduplicated effective sample, the slope was
**+0.0133/year (p = 0.0209)**.

C2 therefore reduced the slope magnitude by approximately **48%**, but the
residual drift remained statistically distinguishable from zero.

The earlier 181-post diagnostic that triggered C2 measured **+0.044/year
(p = 0.0055)**. Relative to the complete annual-frame value of +0.0256/year, the
subsample overstated the slope magnitude by roughly 70%. The temporal defect was
real, but materially less severe than the original diagnostic indicated.

Annual/supplementary overlaps are deduplicated in the primary C2 diagnostic
because duplicate retrieval of the same Reddit thread is not an independent
sampling event and identical Reddit comment IDs are deduplicated by
`02_preprocess.py`. This deduplication rule was selected on methodological
grounds before its effect on the drift estimate was known.

The raw-overlap sensitivity result was **+0.0190/year (p = 0.0098)**.

The final within-year sample remains boundary-weighted rather than uniform.
Accordingly, the sampling design supports annual longitudinal analysis and does
not support quarterly-resolution claims.

## Planned seasonality sensitivity check

After concern classification is complete, concern share will be compared between
H1 (January-June) and H2 (July-December) for the complete calendar years
2016-2024.

The residual sampling-position slope corresponds to an approximately 0.10-year
shift across the study span, roughly five weeks later in the calendar in later
years.

This can bias the longitudinal concern estimate only if concern itself varies
materially by season.

If the H1-H2 concern difference is small relative to the observed longitudinal
effect, the residual sampling drift will be bounded as unlikely to be materially
consequential despite its statistical significance.

If a material H1-H2 difference exists, seasonality will remain an explicit
limitation and an additional sensitivity analysis will be applied to the
longitudinal result.
