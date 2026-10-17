"""Series analyses of record (on the PC): the analyses of the corpus runs that Deviation 13 of
docs/analysis_preregistration.md assigns to "the series analyses", with the subsystem classifier's validation, the
comparison of the two Stage 2 runs on the tranche items and the Tier 3 figures.

From the repository folder, with the virtual environment active (no GPU, no internet):
    python analysis_03_series.py --preflight
        Before the commit. Checks every input against the record, then runs every analysis once as a dry run on the
        real comments with the labels of the three runs replaced by labels drawn at random from fixed made-up
        distributions (rule 17), so that the code is exercised on the structure of the real data while no label of a
        corpus run enters any figure (Deviation 13). The result, its report and its figures are discarded unseen. It
        writes no output (Python and matplotlib may refresh their caches).
    python analysis_03_series.py --confirm-committed
        After this file is committed and its SHA-256 recorded. The run of record. It runs once: it refuses to start
        if this file's results already exist (the SHA-256 is that of the file with LF line endings, as the register
        records script hashes).

Inputs, each checked against the record: the inputs of the sample analyses of record, read and checked by
analysis_01_sample.load_all (the files of record of both tranches, the gold labels, the predictions of the evaluation
of record, the evaluation output, corpus v2.2 and the frame); corpus v2.2 again, against its file SHA-256 of record
(each comment's creation time, subreddit, tier, thread, word count and text); the three prediction files of the
corpus runs (data/models/deploy/: stage1_corpus_predictions.csv, stage2_predictions.csv, subsystem_predictions.csv);
and thread_sizes.csv, the commentsCount join of the corpus-description run of record. It runs no model.

What it computes (exploratory figures are labelled so, as R5 requires for Family C)
  1. The corpus runs: the comments each covers, refusals and unclassified comments by quarter, the Tier 3 share of
     the comments classified relevant (Deviation 13, "Tier 3"), and the Tier 3 comments classified relevant written
     out for the author's reading.
  2. The Stage 2 labels of the corpus run against those of the evaluation run on the tranche items both cover, a
     refusal being a fourth value; the subsystem classifier against the gold primary subsystems of both tranches, per
     value, for each tranche and both, with and without the three adjudicated items (Deviation 13).
  3. The error rates: the rates of record recomputed and checked; the block rates of the temporal calibration check
     and the three-class rates M_ij, as the sample analyses compute them; the item resamples, checked against the
     SHA-256 of record.
  4. The reweighting of R3 as Deviation 13 fixes it: the target shares, the retained and left-out subreddit-years,
     every weight, the largest weight and each quarter's effective sample size.
  5. The temporal calibration check's rule: the block-specific series against the primary series by R3's criteria,
     and the 95% interval of the difference in Sen's slope; whether the effect is material, and if so how it is
     qualified.
  6. RQ1: the primary series (the corrected reweighted concern share by quarter, 2016 Q1 to 2024 Q4, and the same
     by half-year and by year), its trend statistics (Sen's slope, the Gilbert interval, Mann-Kendall, Hamed-Rao),
     the changepoints of Deviation 12, the STL decomposition and the exploratory GLM; beside it the block-specific,
     companion, pooled, tier-level and three-class series, each with its statistics and, where Deviation 13 says so,
     R3's two criteria; every corrected share with its bootstrap interval.
  7. R4: the thread-size decomposition (C, T, the ratio a common trend would produce, the trend net of C, the
     size-stratified series), with its outcome.
  8. The relevance-error series (low and high), with the two figures of the annotated sample that place the series
     between them.
  9. The sensitivity analyses (Family C): seasonality (half-years, and the month-of-year decomposition C_m with its
     outcome), the word floor of 25, and the tier strata.
 10. RQ2 (Deviations 9 and 13): the sparsity rule; pi_s, C_s and E_s corrected for Stage 2 error and as classified;
     Family A with Holm-Bonferroni; V2X and the unclassified comments as counts.
 11. Added with this file, after the corpus runs' counts had been seen (description): the share of comments
     classified relevant at Stage 1 in the corpus beside the design-weighted shares on the annotated sample, and the
     corpus run's Stage 1 labels on the tranche items against their gold labels.
 12. Figures for the report, with the three events of Deviation 12 as markers.

Rules fixed with this file (where the committed text is silent, or to say how a committed rule is applied)
  1. Inputs. Each prediction file must be the file of record and hold exactly the comments its run covers: Stage 1,
     every comment of corpus v2.2 with N or Y; Stage 2, the Tier 1+2 comments classified Y, each with a class or,
     with the status refusal, none; the subsystem run, those comments and the tranche items relevant in the gold set
     and not among them (marked validation_only), each with one of the seven values or, with the status
     unclassified, none. thread_sizes.csv must give every comment of corpus v2.2 its thread as the corpus does, and
     a bucket that follows from its count by the buckets of R4. clean_wordcount must be a whole number of at least 20
     equal to the number of words of clean_body separated by white space (02_preprocess.py computes it so). Any
     departure stops the script.
  2. Periods are calendar quarters, half-years (January to June, July to December) and years of the creation time in
     UTC. The trend span is 2016 Q1 to 2024 Q4 (36 quarters, nine years). The quarters 2025 Q1 and Q2 (January to
     April) are computed and plotted and enter no statistic; no half-year or year of 2025 is formed, except the year
     2025 of RQ2, shown descriptively. A period's era is that of its calendar year.
  3. The population of the series is the Tier 1+2 comments classified relevant at Stage 1. Retention and the weights
     are those of Deviation 13, computed for each year 2016-2025 (2025 on its four months, with the 2016-2024
     target). The companion series uses the subreddits retained in every year 2016-2024. The word-floor series keeps
     the primary target and recomputes retention and weights on the comments with clean_wordcount of 25 or more.
     Every figure is computed in double precision from the comments' labels and weights.
  4. Correction: corrected = (x - FPR) / (TPR - FPR), with no value when TPR = FPR. In the block-specific series
     the early-block rates apply to every period up to 2021 and the late-block rates from 2022. A value, an interval
     limit or a series is clipped to [0, 1] only for display; statistics use the values before clipping (Deviation
     13), except the relevance-error series.
  5. Trend statistics. Positions are the quarter number (2016 Q1 = 0) or the year, so that a gap keeps the true
     distance in time; the slope per year of a quarterly series and its limits are four times those per quarter.
     A series with fewer than two values has no statistic. For fewer than ten values, the exact two-sided p-value is
     the share of the n! orderings of the values (equal values in different positions counted as different
     orderings) whose |S| is at least the observed |S|, and significance is decided by it. Hamed-Rao is computed for
     the primary series only (Deviation 13); the autocorrelation reported is the library's, of the ranks of the values
     less the library's Sen line. R3's two criteria compare another series' 36 quarterly values before clipping with
     the primary's: (1) the two Sen's slopes have the same sign (zero agrees only with zero) and the two tests are
     both significant or both not; (2) the other Sen's slope lies within the primary Gilbert interval, limits
     included.
  6. Changepoints. For each penalty the number of changepoints k (0 to 8) minimises the cost plus the penalty times
     k, an exact tie going to the smaller k; for each k the segmentation is ruptures.Dynp's. A changepoint is the
     index of the first quarter of a new segment. In the BIC comparison a residual sum of squares of zero has a
     logarithm of minus infinity. A changepoint supported at 2021 Q4, 2022 Q1 or 2022 Q2 keeps the label only if the
     same quarter is supported on the block-specific series, which is searched only then.
  7. Bootstrap. Resample k (1 to 2,000) uses row k of the item index arrays (checked against the SHA-256 of record)
     and of the comment index arrays. The threads of a quarter are the distinct parsedPostId of its population
     comments, sorted as strings; a quarter with none draws nothing; the SHA-256 of the comment index arrays
     (little-endian 64-bit integers, row-major, the quarters in time order) is recorded. A statistic formed from
     several values (a slope, a difference, a mean, a sum) has no value in a resample in which one of them has none.
     A value that a rule of Deviation 13 leaves undefined on the full corpus (pi_s when the sum of the A_s is not
     positive, E_s when C is not positive) is undefined in a resample in the same way, and that resample is left out
     for it.
     Intervals are analysis_01_sample.percentile_interval's (numpy.nanpercentile, its default method; none when more
     than 100 resamples lack a value). In the size-stratified series a bucket with no comment in a year of a
     resample is left out of that year and the others rescaled, as on the full corpus.
  8. R4. The cut-points are applied as R4 writes them: |C| < 0.20 x |T|, non-consequential; 0.20 x |T| <= |C| <
     0.50 x |T|, a material limitation; |C| >= 0.50 x |T|, the size-stratified series is reported first as the result
     for RQ1. They are applied only if the primary series' Mann-Kendall test is significant (Deviation 13). The same
     rule decides the outcome of C_m against 0.20 x |T| (sensitivity 1), with months in UTC; there T is that of the
     comments C_m is formed from. The ratio a common straight-line trend would produce is reported beside C / T, from
     each bucket's (each month's) weighted mean year over 2016-2024.
  9. Three-class correction: the equations sum_i p_i M_ij = q_j are solved by Cramer's rule; with a determinant of
     zero they have no solution. For display, negative components are set to zero and the others rescaled to sum to
     one; with no positive component the display has no value.
 10. RQ2. The values s are the seven primary values and the unclassified comments. The sparsity rule is applied to
     the median of the 36 quarterly and of the nine annual unweighted counts. A value analysed at quarterly or annual
     resolution has pi_s and C_s as a series at that resolution, and pi_s, C_s and E_s over 2016-2024; a value the
     rule reports as counts only, V2X and the unclassified comments are reported as counts (their unweighted counts
     by quarter and year, and their weighted counts and A_s over 2016-2024; R5, Deviations 9 and 13); `none` is
     described and not tested. Holm-Bonferroni adjusted p-values are step-down, made monotone and capped at 1. The
     measures as classified carry intervals like the corrected ones (Deviation 13: "each reported value"). RQ2's 2025
     values are descriptive; at annual resolution 2025 is labelled as January to April.
 11. Subsystem validation, on the tranche items with a gold primary subsystem: the share of the items of each gold
     value given that value, and the share of the items given a value whose gold value it is, with Wilson 95%
     intervals on the counts; an unclassified item is a column of the table and counts as a disagreement; overall
     agreement is the share of items given their gold value. Without the adjudicated items: those with
     subsystem_adjudicated in gold_labels.csv.
 12. GLM (exploratory): intercept, year - 2020 and indicators of seven subreddits, r/teslamotors the reference;
     an indicator with no comment would be left out, and the terms are listed with the result;
     statsmodels GLM with the binomial family and its default logit link, fitted with cov_type="cluster" and the
     thread as the group, every other setting the library's default; the year odds ratio exp(b) and its Wald 95%
     interval from conf_int(alpha=0.05).
 13. STL: statsmodels.tsa.seasonal.STL(values, period=4, seasonal=7, trend=9, low_pass=5, seasonal_deg=1,
     trend_deg=1, low_pass_deg=1, robust=True, seasonal_jump=1, trend_jump=1, low_pass_jump=1).fit(inner_iter=2,
     outer_iter=15).
 14. Added with this file after the corpus runs' counts had been seen, as description: the share of comments
     classified relevant at Stage 1 among the Tier 1+2 comments and among the frame comments (overall and by era),
     beside the design-weighted share classified relevant by the cross-validated predictions and the gold relevance
     rate on the annotated sample (Deviation 3 intervals); and the corpus run's Stage 1 labels on the tranche items
     against their gold labels, which the retrained model had seen; with them, the counts classified relevant by tier
     and the Tier 3 comments classified relevant by subreddit and year.
 15. Figures (matplotlib, Agg backend): the shares as displayed (clipped), with their 95% intervals; the three events
     of Deviation 12 as vertical lines at the start of 2018 Q1, 2023 Q4 and 2024 Q4; the quarters of 2025 drawn apart
     from the trend span. They show figures that the results file holds and decide nothing.
 16. Outputs. The results file gives every figure rounded to six decimals, except the p-values, Sen's slopes and
     Gilbert limits, which are written unrounded so that each can be set against the decision it led to; the report
     formats every figure from its unrounded value, so that no figure is rounded twice.
 17. The preflight's dry run: every comment keeps its real attributes; Stage 1 labels are Y with probability 0.53;
     each comment of the dry population (Tier 1+2, Y) gets CONCERN, ENDORSEMENT, OTHER or a refusal with
     probabilities 0.45, 0.25, 0.295 and 0.005; those comments and the tranche items relevant in the gold set and not
     among them get a primary subsystem with the probabilities in DRY_RUN; the generators are
     numpy.random.default_rng([24916660, 3, 96]) for the labels and ([24916660, 3, 97]) for the comment resamples.

Writes, in data/analysis/series/run_<first 12 hex digits of this file's SHA-256>/ (data/ is not committed):
  series_results.json             every figure (no timestamp: a rerun on the same inputs gives the same bytes)
  series_report.md                the main figures, as tables
  series_values.csv               every period value of every series, one row each (for the report's figures)
  figures/*.pdf, figures/*.png    the figures
  tier3_relevant_comments.csv     the Tier 3 comments classified relevant, with their text (for the author's reading)
  series_manifest.json            time, versions, and the SHA-256 of every input file and of the files above
  PASTE_series_block.txt          the register lines (hashes only)
After the run, series_results.json, series_report.md, series_values.csv and the figures are copied to results/ and
committed with the register lines, so that every figure is in a results file committed to the repository
(Deviation 13). tier3_relevant_comments.csv holds comment text and is not committed.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import itertools
import json
import math
import os
import re
import shutil
import time
from collections import Counter
from fractions import Fraction
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
import pandas as pd

import analysis_01_sample as sample
import models_01_prepare as prep
import models_05_evaluate as ev
import models_common as mc
import models_config as cfg

# =============================================================================
# THE RECORD
# =============================================================================
SCRIPT = "analysis_03_series.py"
REPORT = "Report this message before going further."
MODULES_OF_RECORD = {                             # SHA-256 with LF line endings: the files at 1397cc9 (= 8d9c0d1)
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
    "models_05_evaluate.py": "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734",
    "analysis_01_sample.py": "95f7a48c7509c58eca11330814be32fef0a8c1e430447790fdccfa5da6fdd952",
}
LIBRARIES = {"scipy": "1.18.0", "pymannkendall": "1.4.3", "ruptures": "1.1.10", "statsmodels": "0.15.0",
             "matplotlib": "3.11.2"}                # SciPy too: the Gilbert interval is its theilslopes
OUT_ROOT = cfg.REPO / "data" / "analysis" / "series"
CORPUS = sample.CORPUS                            # data/clean_v2_2/corpus.parquet
CORPUS_FILE_SHA256 = "958f480ec13d469dbf285714e2601e5035cf05e10126a7f9b598e32e4b33b39d"   # register, 14 October 2026
DEPLOY_DIR = cfg.MODELS_DIR / "deploy"
PREDICTIONS = {                                   # register, 15 October 2026
    "stage1": (DEPLOY_DIR / "stage1_corpus_predictions.csv",
               "087e1e58ff3f9c36efa307e7735ead27e997a918452dbad993b085d119513cdf"),
    "stage2": (DEPLOY_DIR / "stage2_predictions.csv",
               "472ed550d1260ee0b032ca834a47ed605839ce74705c9a3806d2a0260d4a9389"),
    "subsystem": (DEPLOY_DIR / "subsystem_predictions.csv",
                  "538fa8ac682b6113d634eba65cef3f804a1d223ddd5d25210ee8c1306a8669ac"),
}
THREAD_SIZES = cfg.REPO / "data" / "analysis" / "corpus" / "run_f2240bdd7354" / "thread_sizes.csv"
THREAD_SIZES_SHA256 = "65c4557d6a46ce68b0b14500434ca327ee7a373fbb0c033680f67151f1e832c0"   # register, 17 October 2026
ITEM_ARRAYS_SHA256 = "5e3eea48169360cb9e8f85c2826373d4bf92a0d85759a3c3b41ed4eaa35da394"     # register, 14 October 2026
STAGE1_COLUMNS = ["id", "pred", "p_N", "p_Y"]
RUN_COLUMNS = ["status", "attempts", "input_tokens", "output_tokens", "answer_1", "answer_2", "request_ids",
               "api_rejections"]
SIZE_COLUMNS = ["id", "thread", "comments_count", "bucket", "status"]
SIZE_STATUSES = ["joined", "no post record", "no reported count", "reported count of zero"]
SIZE_BUCKETS = [("1-5", 1, 5), ("6-15", 6, 15), ("16-50", 16, 50), ("51-200", 51, 200), ("201-1000", 201, 1000),
                ("1000+", 1001, None)]           # R4 (docs/corpus_manifest.md); "1000+" is more than 1,000
SIZE_NAMES = [b[0] for b in SIZE_BUCKETS]
WINDOW = (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2025-05-01", tz="UTC"))   # 02_preprocess.py
WORD_FLOOR, WORD_FLOOR_SENSITIVITY = 20, 25       # 02_preprocess.py; Deviation 13, sensitivity 2

TIER12 = ("Tier 1", "Tier 2")
SUBREDDITS = list(sample.SUBREDDITS)              # the eight Tier 1+2 subreddits, in R5's order
TIER3_SUBREDDITS = ["privacy", "cybersecurity"]
CLASSES = list(sample.CLASSES)                    # CONCERN, ENDORSEMENT, OTHER
SUBSYSTEMS = list(sample.SUBSYSTEMS)              # the seven primary values, in models_config's order
UNCLASSIFIED = "unclassified"
VALUES8 = SUBSYSTEMS + [UNCLASSIFIED]
FAMILY_A = ["sensing", "in_vehicle_networks", "cybersecurity", "privacy", "data_governance"]   # Deviation 9
COUNTS_ONLY = ["v2x", UNCLASSIFIED]               # R5, Deviations 9 and 13
ERA_ORDER = list(sample.ERA_ORDER)
YEARS = list(range(2016, 2026))
TREND_YEARS = list(range(2016, 2025))
QUARTERS = [(y, q) for y in YEARS for q in (1, 2, 3, 4)][:-2]   # 2016 Q1 to 2025 Q2
TREND_Q = 36                                      # 2016 Q1 to 2024 Q4: the first 36 of QUARTERS
HALVES = [(y, h) for y in TREND_YEARS for h in (1, 2)]
SPAN_INTERVALS = 8                                # 2016-2024: nine year-points, eight intervals (R4)
RETENTION_FLOOR = 10                              # Deviation 13 (R3's sparse cell)
TIER_FLOOR = 10                                   # Deviation 13: tier-level series and tier strata
SPARSITY = 50                                     # Deviation 9
ALPHA = 0.05
PENALTIES = [1, 2, 3, 4, 6, 8, 12, 16]            # Deviation 12 as Deviation 13 fixes it
SUPPORT_PENALTIES = [4, 6, 8, 12, 16]
MAX_CHANGEPOINTS, MIN_SEGMENT = 8, 4
NEAR_BOUNDARY = [(2021, 4), (2022, 1), (2022, 2)]
EVENTS = [("Uber ATG fatality, Tempe", (2018, 1)), ("Cruise robotaxi suspension", (2023, 4)),
          ("Tesla Cybercab unveil", (2024, 4))]   # Deviation 12: markers on the plots only
N_RESAMPLES = sample.N_RESAMPLES                  # 2,000
R = N_RESAMPLES + 1                               # row 0: the full corpus; rows 1 to 2,000: the resamples
COMMENT_GENERATOR = [cfg.SEED, 3, 2]              # Deviation 13: numpy.random.default_rng([24916660, 3, 2])
DRY_RUN_GENERATORS = {"labels": [cfg.SEED, 3, 96], "comments": [cfg.SEED, 3, 97]}    # the preflight's dry run only
EXPLORATORY = sample.EXPLORATORY
UNROUNDED = {"p", "p_pymannkendall", "p_exact", "holm_adjusted_p", "sen_slope", "gilbert95_low", "gilbert95_high",
             "sen_slope_per_year", "gilbert95_low_per_year", "gilbert95_high_per_year"}         # rule 16
ADDED = "added with analysis_03_series.py after the corpus runs' counts had been seen (description; rule 14)"
STL_SETTINGS = {"period": 4, "seasonal": 7, "trend": 9, "low_pass": 5, "seasonal_deg": 1, "trend_deg": 1,
                "low_pass_deg": 1, "robust": True, "seasonal_jump": 1, "trend_jump": 1, "low_pass_jump": 1}
STL_FIT = {"inner_iter": 2, "outer_iter": 15}


# =============================================================================
# helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


def own_sha256() -> str:
    return ev.text_sha256(Path(__file__).resolve())


def run_folder(me: str) -> Path:
    return OUT_ROOT / f"run_{me[:12]}"


def qlabel(p) -> str:
    return f"{p[0]} Q{p[1]}"


def hlabel(p) -> str:
    return f"{p[0]} H{p[1]}"


def era_of_year(year: int) -> str:
    return sample.era_of_year(int(year))


def subreddit_key(s) -> str:
    return re.sub(r"^/?r/", "", str(s).strip()).lower()


def size_bucket(n: int) -> str:
    for name, low, high in SIZE_BUCKETS:
        if n >= low and (high is None or n <= high):
            return name
    stop(f"no thread-size bucket for {n}. {REPORT}")


def num(x):
    """A float, or None for a missing, infinite or NaN value."""
    if x is None:
        return None
    x = float(x)
    return None if (math.isnan(x) or math.isinf(x)) else x


def clip01(x):
    x = num(x)
    return None if x is None else min(max(x, 0.0), 1.0)


def nan_to_none(a) -> list:
    return [num(v) for v in np.asarray(a, dtype=float)]


def interval(values: np.ndarray) -> dict:
    """analysis_01_sample.percentile_interval (Deviation 13), unrounded."""
    values = np.asarray(values, dtype=float)
    undefined = int(np.isnan(values).sum())
    if undefined > sample.MAX_UNDEFINED or undefined == len(values):
        return {"low": None, "high": None, "resamples_without_value": undefined}
    low, high = np.nanpercentile(values, [2.5, 97.5])
    return {"low": float(low), "high": float(high), "resamples_without_value": undefined}


def share_interval(values: np.ndarray) -> dict:
    out = interval(values)
    out["low_displayed"], out["high_displayed"] = clip01(out["low"]), clip01(out["high"])
    return out


def div(a, b):
    """a / b elementwise; NaN where b is 0 or either is NaN."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(b != 0, a / np.where(b != 0, b, 1.0), np.nan)


def correct(x, tpr, fpr):
    """(x - FPR) / (TPR - FPR) elementwise; NaN where TPR = FPR. tpr and fpr broadcast against x."""
    x = np.asarray(x, dtype=float)
    return div(x - fpr, tpr - fpr)


def count_share(k: int, n: int) -> dict:
    """A count and its share, for figures that are counts of the corpus or of the tranche items (no interval)."""
    return {"k": int(k), "n": int(n), "share": (int(k) / int(n)) if n else None}


def wilson(k: int, n: int) -> dict:
    """models_05_evaluate.wilson's interval, unrounded (rule 16)."""
    k, n = int(k), int(n)
    if n == 0:
        return {"k": 0, "n": 0, "share": None, "wilson95_low": None, "wilson95_high": None}
    phat, z = k / n, ev.Z95
    den = 1 + z * z / n
    centre = (phat + z * z / (2 * n)) / den
    half = z * math.sqrt(phat * (1 - phat) / n + z * z / (4 * n * n)) / den
    return {"k": k, "n": n, "share": phat, "wilson95_low": centre - half, "wilson95_high": centre + half}


def check_file(path: Path, want: str, what: str) -> str:
    if not path.exists():
        stop(f"{what} not found at {path}")
    got = mc.sha256_file(path)
    if got != want:
        stop(f"{what} is not the file of record (SHA-256 {got[:16]}..., recorded {want[:16]}...). {REPORT}")
    return got


def rounded(x, keep: bool = False):
    """The results as written: floats rounded to six decimals (rule 16: the decision values in UNROUNDED are kept as
    computed); NaN and infinities as null."""
    if isinstance(x, dict):
        return {str(k): rounded(v, keep=str(k) in UNROUNDED) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [rounded(v, keep=keep) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return num(x) if keep else sample.fl(x)
    if x is None or isinstance(x, str):
        return x
    raise TypeError(f"a result of type {type(x).__name__} cannot be written: {REPORT}")


# =============================================================================
# inputs (rule 1)
# =============================================================================
def check_modules() -> dict:
    out = {}
    for module in (cfg, mc, prep, ev, sample):
        path = Path(module.__file__).resolve()
        want = MODULES_OF_RECORD.get(path.name)
        got = ev.text_sha256(path)
        if got != want:
            stop(f"{path.name} is not the file in the repository at 1397cc9 (SHA-256 {got[:16]}..., recorded "
                 f"{(want or 'none')[:16]}...). {REPORT}")
        out[path.name] = got
    return out


def check_libraries() -> dict:
    found = {}
    for name in LIBRARIES:
        try:
            found[name] = package_version(name)
        except PackageNotFoundError:
            found[name] = "not installed"
    if found != LIBRARIES:
        pins = " ".join(f"{n}=={v}" for n, v in LIBRARIES.items())
        stop(f"the series analyses use {', '.join(f'{n} {v}' for n, v in LIBRARIES.items())}; found "
             f"{', '.join(f'{n} {v}' for n, v in found.items())}.\n  Install them with:  python -m pip install {pins}")
    return found


def load_corpus() -> tuple[pd.DataFrame, dict]:
    if not CORPUS.exists():
        stop(f"corpus v2.2 not found at {CORPUS}")
    got = mc.sha256_file(CORPUS)
    if got != CORPUS_FILE_SHA256:
        stop(f"corpus.parquet is not the file of record (SHA-256 {got[:16]}..., recorded {CORPUS_FILE_SHA256[:16]}...). "
             f"{REPORT}")
    cols = ["id", "created", "year", "subreddit", "tier", "parsedPostId", "clean_wordcount", "clean_body"]
    try:
        c = pd.read_parquet(CORPUS, columns=cols)
    except Exception as e:                                  # noqa: BLE001 - reported, not handled
        stop(f"corpus v2.2 could not be read with the columns {', '.join(cols)} ({e})")
    c["id"] = c["id"].astype(str)
    if len(c) != sample.CORPUS_ROWS or c["id"].duplicated().any() \
            or mc.ids_sha256(c["id"]) != sample.CORPUS_MEMBERSHIP_SHA256:
        stop(f"corpus v2.2: the membership does not match R5 (SHA-256 of the sorted ids). {REPORT}")
    sub = c["subreddit"].map(subreddit_key)
    tier = c["tier"].astype(str)
    if dict(Counter(sub)) != sample.R5_SUBREDDIT_COUNTS or dict(Counter(tier)) != sample.R5_TIER_COUNTS:
        stop(f"corpus v2.2: the counts by subreddit or by tier differ from R5. {REPORT}")
    t12 = tier.isin(TIER12)
    if not set(sub[t12]) <= set(SUBREDDITS) or not set(sub[~t12]) <= set(TIER3_SUBREDDITS):
        stop(f"corpus v2.2: a Tier 1+2 comment is not in one of the eight subreddits of R3, or a Tier 3 comment is not "
             f"in r/privacy or r/cybersecurity. {REPORT}")
    created = pd.to_datetime(c["created"], utc=True, errors="coerce")
    if created.isna().any() or (created < WINDOW[0]).any() or (created >= WINDOW[1]).any():
        stop(f"corpus v2.2: a comment has no creation time in the study window. {REPORT}")
    year = pd.to_numeric(c["year"], errors="coerce")
    if year.isna().any() or (year.astype(int) != created.dt.year).any():
        stop(f"corpus v2.2: a comment's year is not the UTC calendar year of its creation time. {REPORT}")
    thread = c["parsedPostId"].astype(object).map(lambda x: "" if pd.isna(x) else str(x).strip())
    if (thread == "").any():
        stop(f"corpus v2.2: {int((thread == '').sum())} comments have no thread id (parsedPostId). {REPORT}")
    if c["clean_body"].isna().any():
        stop(f"corpus v2.2: a comment has no text. {REPORT}")
    words = c["clean_body"].astype(str).str.split().map(len)
    wc = pd.to_numeric(c["clean_wordcount"], errors="coerce")
    if wc.isna().any() or (wc != wc.round()).any() or (wc.astype("int64") != words).any() or (words < WORD_FLOOR).any():
        stop(f"corpus v2.2: clean_wordcount is not the number of words of clean_body for every comment, or a comment "
             f"has fewer than {WORD_FLOOR} words (rule 1). {REPORT}")
    df = pd.DataFrame({"id": c["id"].values, "created": created.values, "year": year.astype(int).values,
                       "quarter": created.dt.quarter.astype(int).values, "month": created.dt.month.astype(int).values,
                       "sub": sub.values, "tier": tier.values, "thread": thread.values,
                       "words": words.astype(int).values, "text": c["clean_body"].astype(str).values})
    df = df.sort_values("id").reset_index(drop=True)
    return df, {"rows": int(len(df)), "membership_sha256": sample.CORPUS_MEMBERSHIP_SHA256, "file_sha256": got}


def read_run(kind: str, label: str, expected: list, extra: list | None = None) -> tuple[pd.DataFrame, str]:
    path, want = PREDICTIONS[kind]
    sha = check_file(path, want, path.name)
    df = ev.read_csv(path)
    cols = ["id", label] + RUN_COLUMNS + (extra or [])
    if list(df.columns) != cols:
        stop(f"{path.name} must have the columns {cols} (models_06_deploy.py writes them). {REPORT}")
    if df["id"].tolist() != sorted(expected):
        stop(f"{path.name} does not hold exactly the comments its run covers, in id order (rule 1). {REPORT}")
    return df.set_index("id"), sha


def load_runs(corpus: pd.DataFrame, data: dict) -> dict:
    """The three prediction files of the corpus runs (rule 1)."""
    path, want = PREDICTIONS["stage1"]
    s1_sha = check_file(path, want, path.name)
    s1 = ev.read_csv(path)
    if list(s1.columns) != STAGE1_COLUMNS or s1["id"].duplicated().any() or set(s1["id"]) != set(corpus["id"]) \
            or not set(s1["pred"]) <= {"N", "Y"}:
        stop(f"{path.name} must give N or Y for every comment of corpus v2.2 (models_06_deploy.py). {REPORT}")
    s1 = s1.set_index("id")["pred"].reindex(corpus["id"]).to_numpy(dtype=object)
    in_pop = corpus["tier"].isin(TIER12).to_numpy() & (s1 == "Y")
    pop_ids = sorted(corpus["id"].to_numpy(dtype=object)[in_pop])
    s2, s2_sha = read_run("stage2", "pred_class", pop_ids)
    ok = (s2["status"] == "ok") & s2["pred_class"].isin(CLASSES)
    refused = (s2["status"] == "refusal") & (s2["pred_class"] == "")
    if not (ok | refused).all():
        stop(f"stage2_predictions.csv: a comment has neither a class with the status ok nor the status refusal with "
             f"no class (rule 1). {REPORT}")
    gold_rel = {data["ids"][j] for j in np.nonzero(data["rel"])[0]}
    validation = sorted(gold_rel - set(pop_ids))
    sub, sub_sha = read_run("subsystem", "subsystem", sorted(set(pop_ids) | set(validation)), ["validation_only"])
    ok = (sub["status"] == "ok") & sub["subsystem"].isin(SUBSYSTEMS)
    uncl = (sub["status"] == UNCLASSIFIED) & (sub["subsystem"] == "")
    if not (ok | uncl).all():
        stop(f"subsystem_predictions.csv: a comment has neither one of the seven values with the status ok nor the "
             f"status unclassified with no value (rule 1). {REPORT}")
    flagged = sorted(sub.index[sub["validation_only"] == "yes"])
    if flagged != validation or not sub["validation_only"].isin(["yes", ""]).all():
        stop(f"subsystem_predictions.csv: validation_only does not mark exactly the tranche items relevant in the gold "
             f"set and not classified relevant at Stage 1. {REPORT}")
    return {"stage1": s1, "stage2": s2, "subsystem": sub, "validation_only": validation,
            "shas": {"stage1_corpus_predictions.csv": s1_sha, "stage2_predictions.csv": s2_sha,
                     "subsystem_predictions.csv": sub_sha}}


def load_thread_sizes(corpus: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    sha = check_file(THREAD_SIZES, THREAD_SIZES_SHA256, "thread_sizes.csv")
    t = ev.read_csv(THREAD_SIZES)
    if list(t.columns) != SIZE_COLUMNS or t["id"].tolist() != corpus["id"].tolist():
        stop(f"thread_sizes.csv must have the columns {SIZE_COLUMNS} and one row for each comment of corpus v2.2 in id "
             f"order (analysis_02_corpus.py writes it so). {REPORT}")
    if (t["thread"].to_numpy() != corpus["thread"].to_numpy()).any() or not t["status"].isin(SIZE_STATUSES).all():
        stop(f"thread_sizes.csv: a comment's thread differs from corpus v2.2, or a status is not one of "
             f"{SIZE_STATUSES}. {REPORT}")
    for s, c, b in zip(t["status"], t["comments_count"], t["bucket"]):
        if s == "joined":
            good = c.isdigit() and int(c) > 0 and b == size_bucket(int(c))
        elif s == "reported count of zero":
            good = c == "0" and b == ""
        else:
            good = c == "" and b == ""
        if not good:
            stop(f"thread_sizes.csv: a row with status {s!r} has the count {c!r} and the bucket {b!r} (rule 1). {REPORT}")
    return t, sha


def load_frame_ids() -> set:
    """The frame list, checked against R5 again (analysis_01_sample.load_all has checked it once)."""
    frame = [x for x in sample.FRAME_IDS.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n") if x]
    if len(frame) != sample.FRAME_ROWS or mc.ids_sha256(frame) != sample.FRAME_MEMBERSHIP_SHA256:
        stop(f"draw_frame_ids.txt: the membership does not match R5. {REPORT}")
    return set(frame)


# =============================================================================
# the comments and their labels
# =============================================================================
def assemble(corpus: pd.DataFrame, runs: dict, sizes: pd.DataFrame, frame: set, data: dict) -> dict:
    """One row per comment of corpus v2.2, in id order, with its labels from the three runs."""
    ids = corpus["id"].to_numpy(dtype=object)
    s1 = runs["stage1"]
    pop = corpus["tier"].isin(TIER12).to_numpy() & (s1 == "Y")
    s2 = np.full(len(ids), "", dtype=object)
    lab = runs["stage2"]
    s2[pop] = [("refusal" if lab.at[i, "status"] == "refusal" else lab.at[i, "pred_class"]) for i in ids[pop]]
    sub = runs["subsystem"]
    subsys = np.full(len(ids), "", dtype=object)
    covered = np.isin(ids, sub.index.to_numpy(dtype=object))
    subsys[covered] = [(UNCLASSIFIED if sub.at[i, "status"] == UNCLASSIFIED else sub.at[i, "subsystem"])
                       for i in ids[covered]]
    qidx = np.array([QUARTERS.index((int(y), int(q))) for y, q in zip(corpus["year"], corpus["quarter"])])
    return {
        "ids": ids, "year": corpus["year"].to_numpy(dtype=int), "quarter": corpus["quarter"].to_numpy(dtype=int),
        "month": corpus["month"].to_numpy(dtype=int), "qidx": qidx, "created": corpus["created"].to_numpy(),
        "sub": corpus["sub"].to_numpy(dtype=object), "tier": corpus["tier"].to_numpy(dtype=object),
        "thread": corpus["thread"].to_numpy(dtype=object), "words": corpus["words"].to_numpy(dtype=int),
        "text": corpus["text"].to_numpy(dtype=object), "frame": np.isin(ids, list(frame)),
        "size_status": sizes["status"].to_numpy(dtype=object), "size_bucket": sizes["bucket"].to_numpy(dtype=object),
        "s1": s1, "pop": pop, "s2": s2, "subsys": subsys, "validation_only": set(runs["validation_only"]),
        "position": {i: k for k, i in enumerate(ids)},
    }


DRY_RUN = {"stage1_y": 0.53,                     # rule 17: made-up label distributions for the preflight's dry run
           "stage2": (["CONCERN", "ENDORSEMENT", "OTHER", "refusal"], [0.45, 0.25, 0.295, 0.005]),
           "subsystem": (VALUES8, [0.30, 0.08, 0.03, 0.01, 0.03, 0.02, 0.525, 0.005])}


def dry_run_labels(D: dict, data: dict) -> dict:
    """The preflight's dry run (rule 17): the labels of the three runs are replaced by labels drawn at random from the
    made-up distributions of DRY_RUN, so that no label of a corpus run enters it; every attribute of the comments
    (creation time, subreddit, tier, thread, word count, thread size, frame membership) is real."""
    rng = np.random.default_rng(DRY_RUN_GENERATORS["labels"])
    n = len(D["ids"])
    s1 = np.where(rng.random(n) < DRY_RUN["stage1_y"], "Y", "N").astype(object)
    pop = np.isin(D["tier"], TIER12) & (s1 == "Y")
    s2 = np.full(n, "", dtype=object)
    names, p = DRY_RUN["stage2"]
    s2[pop] = rng.choice(np.array(names, dtype=object), size=int(pop.sum()), p=p)
    gold_rel = {data["ids"][j] for j in np.nonzero(data["rel"])[0]}
    validation = gold_rel - set(D["ids"][pop])
    covered = pop | np.isin(D["ids"], sorted(validation))
    subsys = np.full(n, "", dtype=object)
    names, p = DRY_RUN["subsystem"]
    subsys[covered] = rng.choice(np.array(names, dtype=object), size=int(covered.sum()), p=p)
    return {**D, "s1": s1, "pop": pop, "s2": s2, "subsys": subsys, "validation_only": validation}


# =============================================================================
# error rates and the item resamples (Deviation 13)
# =============================================================================
def resampled_rate(data: dict, strata: dict, counts: dict, num_ok: np.ndarray, den_ok: np.ndarray) -> np.ndarray:
    """As analysis_01_sample.resampled_block_rates: each drawn copy of an item carries its era's pooled design weight;
    NaN where the denominator is empty."""
    pos_of = {data["ids"][j]: j for j in range(len(data["ids"]))}
    idx = {e: [pos_of[i] for i in strata[e]] for e in ERA_ORDER}
    nm = np.zeros(N_RESAMPLES)
    dn = np.zeros(N_RESAMPLES)
    for e in ERA_ORDER:
        w = float(Fraction(*sample.ERAS[e]))
        nm += w * (counts[e] @ num_ok[idx[e]].astype(np.float64))
        dn += w * (counts[e] @ den_ok[idx[e]].astype(np.float64))
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(dn > 0, nm / np.where(dn > 0, dn, 1.0), np.nan)


def exact_matrix(data: dict) -> list:
    """M_ij (Deviation 13) as fractions, as analysis_01_sample.three_class_matrix computes it."""
    sel = data["prim"]
    pred = np.where(np.isin(data["s2"], CLASSES), data["s2"], "OTHER")
    w = data["w"]
    M = []
    for a in CLASSES:
        ga = sel & (data["g2"] == a)
        den = sum(w[ga], Fraction(0))
        M.append([sum(w[ga & (pred == b)], Fraction(0)) / den if den else None for b in CLASSES])
    return M


def item_side(data: dict) -> dict:
    """The rates as rows of R: row 0 the rates of record (exact, as floats), rows 1 to 2,000 the item resamples."""
    every = np.ones(len(data["ids"]), bool)
    overall = sample.concern_rates(data, every)
    tpr, fpr = overall["_tpr"], overall["_fpr"]
    rec = sample.RATES_OF_RECORD
    if (sample.fl(tpr), sample.fl(fpr), sample.fr(tpr - fpr)) != (rec["tpr"], rec["fpr"], rec["tpr_minus_fpr_exact"]):
        stop(f"the CONCERN rates recomputed from the predictions of record are not the rates of record. {REPORT}")
    blocks = {b: sample.concern_rates(data, data["block"] == b) for b in ("early", "late")}
    M = exact_matrix(data)
    if any(x is None for row in M for x in row):
        stop(f"a gold class has no item on the primary item set: the three-class rates are not defined. {REPORT}")
    strata = sample.primary_strata(data)
    arrays, sha = sample.item_index_arrays(strata)
    if sha != ITEM_ARRAYS_SHA256:
        stop(f"the item index arrays are not those of record (SHA-256 {sha[:16]}..., recorded "
             f"{ITEM_ARRAYS_SHA256[:16]}...). {REPORT}")
    counts = sample.resample_counts(arrays, strata)
    pos = data["g2"] == "CONCERN"
    hit = data["s2"] == "CONCERN"
    prim = data["prim"]

    def row(exact, boot):
        return np.concatenate([[float(exact) if exact is not None else np.nan], boot])

    rates = {"tpr": row(tpr, resampled_rate(data, strata, counts, prim & pos & hit, prim & pos)),
             "fpr": row(fpr, resampled_rate(data, strata, counts, prim & ~pos & hit, prim & ~pos))}
    boot_blocks = sample.resampled_block_rates(data, strata, counts)
    for b in ("early", "late"):
        rates[f"tpr_{b}"] = row(blocks[b]["_tpr"], boot_blocks[("both tranches", b, "tpr")])
        rates[f"fpr_{b}"] = row(blocks[b]["_fpr"], boot_blocks[("both tranches", b, "fpr")])
    pred = np.where(np.isin(data["s2"], CLASSES), data["s2"], "OTHER")
    Mr = np.zeros((R, 3, 3))
    for i, a in enumerate(CLASSES):
        ga = prim & (data["g2"] == a)
        for j, b in enumerate(CLASSES):
            Mr[:, i, j] = row(M[i][j], resampled_rate(data, strata, counts, ga & (pred == b), ga))
    temporal = sample.temporal_check(data, boot_blocks)
    return {"rates": rates, "M": Mr, "M_exact": M, "overall": overall, "blocks": blocks, "temporal": temporal,
            "strata_sizes": {e: len(strata[e]) for e in ERA_ORDER}, "index_arrays_sha256": sha}


# =============================================================================
# reweighting (R3, Deviation 13)
# =============================================================================
def target_shares(D: dict) -> dict:
    sel = D["pop"] & (D["year"] <= 2024)
    n = Counter(D["sub"][sel])
    total = sum(n.values())
    if total == 0:
        stop(f"no comment is classified relevant in 2016-2024. {REPORT}")
    return {g: n[g] / total for g in SUBREDDITS}


def make_weights(D: dict, mask: np.ndarray, target: dict, keep: set | None = None) -> tuple[np.ndarray, dict]:
    """Deviation 13: in year y a comment of subreddit g, retained in y (ten or more comments of the mask), has weight
    t(g, y) / s(g, y), t the target renormalised over the retained subreddits and s g's share of their comments.
    keep limits the subreddits that may be retained (the companion series)."""
    w = np.zeros(len(D["ids"]))
    table = {}
    for y in YEARS:
        my = mask & (D["year"] == y)
        n = Counter(D["sub"][my])
        kept = [g for g in SUBREDDITS if n[g] >= RETENTION_FLOOR and (keep is None or g in keep)]
        t_sum = sum(target[g] for g in kept)
        n_sum = sum(n[g] for g in kept)
        wy = {}
        if t_sum > 0 and n_sum > 0:
            for g in kept:
                wy[g] = (target[g] / t_sum) / (n[g] / n_sum)
                w[my & (D["sub"] == g)] = wy[g]
        table[str(y)] = {"comments": {g: int(n[g]) for g in SUBREDDITS}, "retained": kept,
                         "left_out": {g: int(n[g]) for g in SUBREDDITS if n[g] and g not in kept}, "weights": wy}
    return w, table


def reweighting(D: dict) -> dict:
    pop = D["pop"]
    target = target_shares(D)
    w, table = make_weights(D, pop, target)
    every = [g for g in SUBREDDITS if all(g in table[str(y)]["retained"] for y in TREND_YEARS)]
    wc, table_c = make_weights(D, pop, {g: (target[g] if g in every else 0.0) for g in SUBREDDITS}, keep=set(every))
    floor = pop & (D["words"] >= WORD_FLOOR_SENSITIVITY)
    wu, table_u = make_weights(D, floor, target)
    return {"target": target, "w": w, "table": table, "companion_subreddits": every, "wc": wc, "table_c": table_c,
            "wu": wu, "table_u": table_u, "floor_mask": floor}


# =============================================================================
# the comment resamples (Deviation 13): aggregates by quarter, rows of R
# =============================================================================
FEATURES = (["w", "wc", "wE", "wO", "v", "vc", "n1", "c1", "n2", "c2", "u", "uc"]
            + [f"{k}_{b}" for b in SIZE_NAMES for k in ("bw", "bwc")]
            + [f"{k}_{j}" for j in range(3) for k in ("mw", "mwc")]
            + [f"{k}_{s}" for s in VALUES8 for k in ("sw", "swc")])
F = {name: i for i, name in enumerate(FEATURES)}


def comment_features(D: dict, RW: dict) -> np.ndarray:
    """Per comment of the population: its weights times its indicators (rule 3)."""
    c = (D["s2"] == "CONCERN").astype(float)
    e = (D["s2"] == "ENDORSEMENT").astype(float)
    o = ((D["s2"] == "OTHER") | (D["s2"] == "refusal")).astype(float)       # a refusal counts as OTHER
    w, v, u = RW["w"], RW["wc"], RW["wu"]
    t1 = (D["tier"] == "Tier 1").astype(float)
    t2 = (D["tier"] == "Tier 2").astype(float)
    span = (D["year"] <= 2024).astype(float)
    X = np.zeros((len(D["ids"]), len(FEATURES)))
    X[:, F["w"]], X[:, F["wc"]], X[:, F["wE"]], X[:, F["wO"]] = w, w * c, w * e, w * o
    X[:, F["v"]], X[:, F["vc"]] = v, v * c
    X[:, F["n1"]], X[:, F["c1"]], X[:, F["n2"]], X[:, F["c2"]] = t1, t1 * c, t2, t2 * c
    X[:, F["u"]], X[:, F["uc"]] = u, u * c
    joined = (D["size_status"] == "joined").astype(float) * span
    for b in SIZE_NAMES:
        ind = joined * (D["size_bucket"] == b)
        X[:, F[f"bw_{b}"]], X[:, F[f"bwc_{b}"]] = w * ind, w * ind * c
    offset = (D["month"] - 1) % 3
    for j in range(3):
        ind = span * (offset == j)
        X[:, F[f"mw_{j}"]], X[:, F[f"mwc_{j}"]] = w * ind, w * ind * c
    for s in VALUES8:
        ind = (D["subsys"] == s).astype(float)
        X[:, F[f"sw_{s}"]], X[:, F[f"swc_{s}"]] = w * ind, w * ind * c
    return X


def aggregates(D: dict, X: np.ndarray, generator: list) -> tuple[np.ndarray, dict]:
    """A[r, q, f]: feature f summed over the population comments of quarter q; row 0 over every comment, row k over
    the threads drawn in resample k (each drawn copy of a thread bringing its comments of that quarter)."""
    rng = np.random.default_rng(generator)
    h = hashlib.sha256()
    A = np.zeros((R, len(QUARTERS), len(FEATURES)))
    threads_by_quarter = {}
    for qi, period in enumerate(QUARTERS):
        sel = np.nonzero(D["pop"] & (D["qidx"] == qi))[0]
        threads = sorted({str(t) for t in D["thread"][sel]})
        m = len(threads)
        threads_by_quarter[qlabel(period)] = {"threads": m, "comments": int(len(sel))}
        if m == 0:
            continue
        code = {t: k for k, t in enumerate(threads)}
        Fq = np.zeros((m, len(FEATURES)))
        np.add.at(Fq, np.array([code[str(t)] for t in D["thread"][sel]]), X[sel])
        idx = rng.integers(0, m, size=(N_RESAMPLES, m))
        h.update(np.ascontiguousarray(idx, dtype="<i8").tobytes(order="C"))
        cnt = np.bincount((idx + m * np.arange(N_RESAMPLES)[:, None]).ravel(),
                          minlength=N_RESAMPLES * m).reshape(N_RESAMPLES, m).astype(np.float64)
        A[0, qi] = Fq.sum(axis=0)
        A[1:, qi] = cnt @ Fq
    return A, {"generator": f"numpy.random.default_rng({list(generator)})", "resamples": N_RESAMPLES,
               "quarters": [qlabel(p) for p in QUARTERS], "threads_by_quarter": threads_by_quarter,
               "index_arrays_sha256": h.hexdigest(),
               "hash_rule": "each quarter's array as little-endian 64-bit integers in row-major order, the quarters "
                            "joined in time order"}


def period_sum(A: np.ndarray, quarters: list, feature: str) -> np.ndarray:
    """Feature summed over the quarters given (indices of QUARTERS): one value per row of R."""
    return A[:, quarters, F[feature]].sum(axis=1)


QI = {p: i for i, p in enumerate(QUARTERS)}
HALF_Q = {p: [QI[(p[0], 2 * p[1] - 1)], QI[(p[0], 2 * p[1])]] for p in HALVES}
YEAR_Q = {y: [QI[(y, q)] for q in (1, 2, 3, 4)] for y in TREND_YEARS}
YEAR_Q_ALL = {**YEAR_Q, 2025: [QI[(2025, 1)], QI[(2025, 2)]]}


# =============================================================================
# trend statistics (R3, Deviation 13; rule 5)
# =============================================================================
_PERMUTATIONS: dict = {}


def mk_s(v: np.ndarray) -> int:
    i, j = np.triu_indices(len(v), 1)
    return int(np.sign(v[j] - v[i]).sum())


def exact_mk_p(v: np.ndarray) -> float:
    """Rule 5: the share of the n! orderings of the values whose |S| is at least the observed |S|."""
    v = np.asarray(v, dtype=float)
    n = len(v)
    if n < 2:
        return 1.0
    if n not in _PERMUTATIONS:
        _PERMUTATIONS[n] = np.array(list(itertools.permutations(range(n))), dtype=np.int8)
    ranks = np.unique(v, return_inverse=True)[1].astype(np.int8)     # equal values share a rank
    perms = ranks[_PERMUTATIONS[n]]
    S = np.zeros(len(perms), dtype=np.int16)
    for a in range(n - 1):
        for b in range(a + 1, n):
            S += np.sign(perms[:, b] - perms[:, a]).astype(np.int16)
    s_obs = abs(mk_s(v))
    return float(Fraction(int((np.abs(S) >= s_obs).sum()), len(perms)))


def sen_rows(Y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Sen's slope of each row of Y against positions x (the median of the pairwise slopes, as
    scipy.stats.theilslopes computes it); NaN for a row with a missing value."""
    i, j = np.triu_indices(len(x), 1)
    slopes = (Y[:, j] - Y[:, i]) / (x[j] - x[i])
    return np.median(slopes, axis=1)


def trend(values: list, positions: list, per_year: float, hamed_rao: bool = False) -> dict:
    """Sen's slope with the Gilbert interval (scipy.stats.theilslopes, alpha=0.95) on the periods with a value, and the
    two-sided Mann-Kendall test (pymannkendall.original_test; the exact test below ten values)."""
    import pymannkendall as mk
    from scipy import stats
    from scipy.stats import norm, rankdata
    v = np.array([np.nan if x is None else float(x) for x in values])
    x = np.asarray(positions, dtype=float)
    keep = ~np.isnan(v)
    n = int(keep.sum())
    out = {"values": n, "periods_without_value": int((~keep).sum())}
    if n < 2:
        return {**out, "sen_slope": None, "note": "fewer than two values: no statistic (rule 5)"}
    ts = stats.theilslopes(v[keep], x[keep], alpha=0.95)
    slope, low, high = float(ts.slope), float(ts.low_slope), float(ts.high_slope)
    test = mk.original_test(v)                          # values without one are left out (Deviation 13)
    out.update({"sen_slope": slope, "gilbert95_low": low, "gilbert95_high": high,
                "sen_slope_per_year": slope * per_year, "gilbert95_low_per_year": low * per_year,
                "gilbert95_high_per_year": high * per_year, "sen_intercept": float(ts.intercept),
                "mann_kendall": {"s": int(test.s), "var_s": float(test.var_s), "z": float(test.z),
                                 "tau": float(test.Tau), "p_pymannkendall": float(test.p)}})
    if n < 10:
        p = exact_mk_p(v[keep])
        out["mann_kendall"]["p_exact"] = p
        out["test"] = "exact permutation test (fewer than ten values; Deviation 13)"
    else:
        p = float(test.p)
        out["test"] = "pymannkendall.original_test"
    out["p"] = p
    out["significant"] = bool(p < ALPHA)
    if hamed_rao:
        if out["periods_without_value"]:
            out["hamed_rao"] = {"computed": False, "note": "not computed for a series with a gap (Deviation 13)"}
        else:
            hr = mk.hamed_rao_modification_test(v, lag=1)
            lib_slope = float(mk.sens_slope(v).slope)
            ranks = rankdata(v - np.arange(1, n + 1) * lib_slope)
            dev = ranks - ranks.mean()
            acf1 = float((dev[:-1] * dev[1:]).sum() / (dev * dev).sum())
            bound = float(norm.ppf(1 - ALPHA / 2) / math.sqrt(n))
            var_c = float(hr.var_s)
            ok = math.isfinite(var_c) and var_c > 0
            out["hamed_rao"] = {"computed": True, "lag": 1, "autocorrelation_lag1": acf1, "bound": bound,
                                "variance_changed": bool(abs(acf1) > bound), "var_s": var_c,
                                "z": float(hr.z) if ok else None, "p": float(hr.p) if ok else None,
                                "significant": bool(hr.p < ALPHA) if ok else None,
                                "computable": ok, "note": None if ok else "the corrected variance is not positive: "
                                                                          "not computable (Deviation 13)"}
    return out


def criteria(other: dict, primary: dict) -> dict | None:
    """R3's two criteria (rule 5)."""
    if other.get("sen_slope") is None or primary.get("sen_slope") is None:
        return None
    a, b = other["sen_slope"], primary["sen_slope"]
    same_sign = bool(np.sign(a) == np.sign(b))
    same_sig = bool(other["significant"] == primary["significant"])
    c2 = bool(primary["gilbert95_low"] <= a <= primary["gilbert95_high"])
    return {"criterion1_agreement_of_conclusion": same_sign and same_sig, "same_sign": same_sign,
            "same_significance": same_sig, "criterion2_overlap_of_estimate": c2,
            "both_hold": bool(same_sign and same_sig and c2)}


def holm(pvals: dict) -> dict:
    """Holm-Bonferroni adjusted p-values (rule 10)."""
    order = sorted(pvals, key=lambda k: (pvals[k], FAMILY_A.index(k)))
    m, running, out = len(order), 0.0, {}
    for rank, k in enumerate(order):
        running = max(running, min(1.0, (m - rank) * pvals[k]))
        out[k] = running
    return out


# =============================================================================
# changepoints, STL and the GLM (Deviation 12 as Deviation 13 fixes it; rules 6, 12 and 13)
# =============================================================================
def sse(z: np.ndarray, bkps: list) -> float:
    total, start = 0.0, 0
    for end in bkps:
        seg = z[start:end]
        total += float(((seg - seg.mean()) ** 2).sum())
        start = end
    return total


def changepoints(values: list) -> dict:
    import ruptures as rpt
    v = np.array([np.nan if x is None else float(x) for x in values])
    if len(v) != TREND_Q or np.isnan(v).any():
        return {"computed": False, "note": "not computed for a series with a gap (Deviation 13)"}
    if float(v.max() - v.min()) == 0:
        return {"computed": False, "note": "the series is constant"}
    sd = float(v.std())
    z = (v - v.mean()) / sd                                  # divisor 36
    algo = rpt.Dynp(model="l2", min_size=MIN_SEGMENT, jump=1).fit(z.reshape(-1, 1))
    segs = {k: algo.predict(n_bkps=k) for k in range(MAX_CHANGEPOINTS + 1)}
    cost = {k: sse(z, segs[k]) for k in segs}
    at = {}
    by_penalty = {}
    for pen in PENALTIES:
        k = min(segs, key=lambda kk: (cost[kk] + pen * kk, kk))
        at[pen] = segs[k][:-1]
        by_penalty[str(pen)] = {"changepoints": [qlabel(QUARTERS[b]) for b in at[pen]], "number": k,
                                "cost": cost[k], "penalised_cost": cost[k] + pen * k}
    t = np.arange(TREND_Q, dtype=float)
    coef = np.polyfit(t, z, 1)
    rss_line = float(((z - np.polyval(coef, t)) ** 2).sum())

    def bic(rss, k):
        return (-math.inf if rss <= 0 else TREND_Q * math.log(rss / TREND_Q)) + k * math.log(TREND_Q)

    found = []
    for b in sorted({b for pen in PENALTIES for b in at[pen]}):
        appears = [pen for pen in PENALTIES if b in at[pen]]
        rss_step = sse(z, [b, TREND_Q])
        every = all(pen in appears for pen in SUPPORT_PENALTIES)
        better = bic(rss_step, 3) < bic(rss_line, 2)
        found.append({"quarter": qlabel(QUARTERS[b]), "index": int(b), "year": QUARTERS[b][0],
                      "grid_values": appears, "number_of_grid_values": len(appears),
                      "returned_at_every_penalty_4_to_16": every, "rss_step": rss_step, "rss_line": rss_line,
                      "bic_step": bic(rss_step, 3), "bic_line": bic(rss_line, 2), "step_better_than_line_by_bic": better,
                      "supported": bool(every and better),
                      "statement": "supported (a description, with no error rate)" if (every and better) else
                      "the series does not distinguish a step here from a steady trend or from noise (Deviation 13)"})
    return {"computed": True, "standardised_with": {"mean": float(v.mean()), "sd_divisor_36": sd},
            "segmentations": {str(k): {"changepoints": [qlabel(QUARTERS[b]) for b in segs[k][:-1]], "cost": cost[k]}
                              for k in segs},
            "by_penalty": by_penalty, "changepoints": found,
            "supported": [c["quarter"] for c in found if c["supported"]]}


def stl(values: list) -> dict:
    from statsmodels.tsa.seasonal import STL
    v = np.array([np.nan if x is None else float(x) for x in values])
    if np.isnan(v).any():
        return {"computed": False, "note": "not computed for a series with a gap (Deviation 13)"}
    res = STL(v, **STL_SETTINGS).fit(**STL_FIT)
    return {"computed": True, "settings": {**STL_SETTINGS, **STL_FIT}, "quarters": [qlabel(p) for p in QUARTERS[:TREND_Q]],
            "observed": nan_to_none(v), "trend": nan_to_none(res.trend), "seasonal": nan_to_none(res.seasonal),
            "residual": nan_to_none(res.resid), "robustness_weights": nan_to_none(res.weights)}


def glm(D: dict) -> dict:
    import statsmodels.api as sm
    sel = D["pop"] & (D["year"] <= 2024)
    y = (D["s2"][sel] == "CONCERN").astype(float)
    subs = D["sub"][sel]
    cols = [np.ones(int(sel.sum())), (D["year"][sel] - 2020).astype(float)]
    names = ["intercept", "year - 2020"]
    for g in SUBREDDITS[1:]:
        ind = (subs == g).astype(float)
        if ind.any():
            cols.append(ind)
            names.append(f"r/{g}")
    X = np.column_stack(cols)
    groups = pd.factorize(pd.Series(D["thread"][sel].astype(str)), sort=True)[0]
    res = sm.GLM(y, X, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups})
    b, se = float(res.params[1]), float(res.bse[1])
    ci = res.conf_int(alpha=0.05)[1]
    return {"label": EXPLORATORY, "comments": int(sel.sum()), "threads": int(groups.max() + 1),
            "terms": names, "reference_subreddit": f"r/{SUBREDDITS[0]}", "year_coefficient": b, "year_se": se,
            "year_odds_ratio": math.exp(b), "year_odds_ratio_wald95_low": math.exp(float(ci[0])),
            "year_odds_ratio_wald95_high": math.exp(float(ci[1])), "use_t": bool(res.use_t),
            "converged": bool(getattr(res, "converged", True)),
            "note": "classified labels, not corrected for classifier error (Deviation 13); unweighted; standard "
                    "errors clustered on thread"}


# =============================================================================
# series from the aggregates (rows of R)
# =============================================================================
def fixed(stat: np.ndarray) -> np.ndarray:
    """Deviation 13: the periods that have a value are fixed on the full corpus (row 0)."""
    stat = np.array(stat, dtype=float)
    stat[:, np.isnan(stat[0])] = np.nan
    return stat


def rows(stat: np.ndarray, labels: list, share: bool = True, interval_rows: bool = True) -> list:
    out = []
    for p, label in enumerate(labels):
        v = num(stat[0, p])
        row = {"period": label, "value": v}
        if share:
            row["value_displayed"] = clip01(v)
            row["clipped"] = None if v is None else bool(v != clip01(v))
        if interval_rows:
            row["interval95"] = None if v is None else (share_interval(stat[1:, p]) if share else interval(stat[1:, p]))
        out.append(row)
    return out


def values(stat: np.ndarray, n: int | None = None) -> list:
    v = nan_to_none(stat[0])
    return v if n is None else v[:n]


QPOS = np.arange(len(QUARTERS), dtype=float)
YPOS = np.array(TREND_YEARS, dtype=float)
QLABELS = [qlabel(p) for p in QUARTERS]
HLABELS = [hlabel(p) for p in HALVES]
YLABELS = [str(y) for y in TREND_YEARS]


def qtrend(stat: np.ndarray, hamed_rao: bool = False) -> dict:
    return trend(values(stat, TREND_Q), list(QPOS[:TREND_Q]), 4.0, hamed_rao=hamed_rao)


def three_class(A: np.ndarray, M: np.ndarray, quarters: list) -> np.ndarray:
    """The raw solution p (R, quarters, 3) of sum_i p_i M_ij = q_j by Cramer's rule (rule 9); NaN without one."""
    w = A[:, quarters, F["w"]]
    q = np.stack([div(A[:, quarters, F["wc"]], w), div(A[:, quarters, F["wE"]], w), div(A[:, quarters, F["wO"]], w)],
                 axis=2)                                                   # (R, Q, 3), order CONCERN, ENDORSEMENT, OTHER
    MT = np.swapaxes(M, 1, 2)                                             # equation j: sum_i M[i, j] p_i = q_j
    det = np.linalg.det(MT)
    P = np.full(q.shape, np.nan)
    for i in range(3):
        Mi = np.repeat(MT[:, None, :, :], len(quarters), axis=1)
        Mi[:, :, :, i] = q
        with np.errstate(divide="ignore", invalid="ignore"):
            P[:, :, i] = np.where(det[:, None] != 0, np.linalg.det(Mi) / np.where(det[:, None] != 0, det[:, None], 1.0),
                                  np.nan)
    return P


def displayed_three_class(p: np.ndarray) -> list | None:
    if np.isnan(p).any():
        return None
    q = np.clip(p, 0.0, None)
    return None if q.sum() <= 0 else [float(x) for x in q / q.sum()]


def quarterly_series(A: np.ndarray, rates: dict, M: np.ndarray, v1: float) -> dict:
    allq = list(range(len(QUARTERS)))
    tpr, fpr = rates["tpr"][:, None], rates["fpr"][:, None]
    x = fixed(div(A[:, :, F["wc"]], A[:, :, F["w"]]))
    early = np.array([p[0] <= 2021 for p in QUARTERS])[None, :]
    tb = np.where(early, rates["tpr_early"][:, None], rates["tpr_late"][:, None])
    fb = np.where(early, rates["fpr_early"][:, None], rates["fpr_late"][:, None])
    n1, c1, n2, c2 = (A[:, :, F[k]] for k in ("n1", "c1", "n2", "c2"))
    tier_ok = (A[0, :, F["n1"]] >= TIER_FLOOR) & (A[0, :, F["n2"]] >= TIER_FLOOR)
    xt = v1 * div(c1, n1) + (1 - v1) * div(c2, n2)
    xt[:, ~tier_ok] = np.nan
    x1 = div(c1, n1)
    x1[:, A[0, :, F["n1"]] < TIER_FLOOR] = np.nan
    x2 = div(c2, n2)
    x2[:, A[0, :, F["n2"]] < TIER_FLOOR] = np.nan
    P3 = three_class(A, M, allq)
    out = {
        "classified": x,
        "primary": fixed(correct(x, tpr, fpr)),
        "block_specific": fixed(correct(x, tb, fb)),
        "companion": fixed(correct(fixed(div(A[:, :, F["vc"]], A[:, :, F["v"]])), tpr, fpr)),
        "pooled": fixed(correct(fixed(div(c1 + c2, n1 + n2)), tpr, fpr)),
        "tier_level": fixed(correct(fixed(xt), tpr, fpr)),
        "three_class_concern": fixed(P3[:, :, 0]),
        "word_floor_25": fixed(correct(fixed(div(A[:, :, F["uc"]], A[:, :, F["u"]])), tpr, fpr)),
        "tier1": fixed(correct(fixed(x1), tpr, fpr)),
        "tier2": fixed(correct(fixed(x2), tpr, fpr)),
    }
    out["_three_class_raw"] = P3
    return out


def grouped_primary(A: np.ndarray, rates: dict, groups: list) -> tuple[np.ndarray, np.ndarray]:
    """The classified and corrected primary shares of periods formed from their comments (Deviation 13)."""
    x = np.stack([div(period_sum(A, g, "wc"), period_sum(A, g, "w")) for g in groups], axis=1)
    x = fixed(x)
    return x, fixed(correct(x, rates["tpr"][:, None], rates["fpr"][:, None]))


# =============================================================================
# R4 and the month-of-year decomposition (rule 8)
# =============================================================================
def decomposition(W: np.ndarray, K: np.ndarray) -> dict:
    """W, K: (R, 9, B) weights and weighted CONCERN of the comments by year and bucket (or month). Returns the
    synthetic series S, the observed series O and the bucket mix, with the weighted mean year of each bucket."""
    Wy, Ky = W.sum(axis=2), K.sum(axis=2)
    a = div(W, Wy[:, :, None])
    r = div(K.sum(axis=1), W.sum(axis=1))                                 # pooled over 2016-2024
    S = np.where(a > 0, a * r[:, None, :], 0.0).sum(axis=2)
    S[np.isnan(a).any(axis=2)] = np.nan
    O = div(Ky, Wy)
    totals = W[0].sum(axis=0)
    mean_year = [float((YPOS * W[0, :, b]).sum() / totals[b]) if totals[b] > 0 else None for b in range(W.shape[2])]
    mix_year = np.array([sum(a[0, y, b] * mean_year[b] for b in range(W.shape[2]) if mean_year[b] is not None)
                         for y in range(len(TREND_YEARS))])
    return {"S": S, "O": O, "a": a, "r": r, "mean_year": mean_year, "mix_mean_year": mix_year}


def sen9(series: list) -> float | None:
    t = trend(series, list(YPOS), 1.0)
    return t.get("sen_slope")


def cut_point_outcome(C, T, significant: bool, gap: float) -> dict:
    out = {"abs_C": None if C is None else abs(C), "0.20_x_abs_T": None if T is None else 0.2 * abs(T),
           "0.50_x_abs_T": None if T is None else 0.5 * abs(T),
           "C_over_T": None if (C is None or not T) else C / T,
           "T_minus_C": None if None in (C, T) else T - C,
           "T_minus_C_corrected_scale": None if None in (C, T) else (T - C) / gap,
           "abs_C_corrected_scale": None if C is None else abs(C) / gap}
    if None in (C, T):
        out["outcome"] = "not computed"
    elif not significant:
        out["outcome"] = ("not applied: the primary series' Mann-Kendall test is not significant, so T cannot be told "
                          "from zero (Deviation 13); |C| / (TPR - FPR) is reported as a change in corrected share")
    elif abs(C) < 0.2 * abs(T):
        out["outcome"] = "non-consequential: |C| < 0.20 x |T|"
    elif abs(C) < 0.5 * abs(T):
        out["outcome"] = "material limitation: C is reported and the trend is stated net of it (T - C)"
    else:
        out["outcome"] = ("|C| >= 0.50 x |T|: the size-stratified series is reported first as the result for RQ1, with "
                          "the primary series beside it (R4 as Deviation 13 reads it)")
    return out


def thread_size(A: np.ndarray, rates: dict, D: dict, RW: dict, significant: bool, gap: float) -> dict:
    W = np.stack([np.stack([period_sum(A, YEAR_Q[y], f"bw_{b}") for y in TREND_YEARS], axis=1) for b in SIZE_NAMES],
                 axis=2)
    K = np.stack([np.stack([period_sum(A, YEAR_Q[y], f"bwc_{b}") for y in TREND_YEARS], axis=1) for b in SIZE_NAMES],
                 axis=2)
    dec = decomposition(W, K)
    S, O = values(dec["S"]), values(dec["O"])
    s_slope, o_slope = sen9(S), sen9(O)
    C = None if s_slope is None else SPAN_INTERVALS * s_slope
    T = None if o_slope is None else SPAN_INTERVALS * o_slope
    common = sen9([float(v) for v in dec["mix_mean_year"]])
    # the size-stratified series (rescaled over the buckets present in each year, in each row)
    ab = div(W.sum(axis=1), W.sum(axis=(1, 2))[:, None])                    # (R, B)
    rby = div(K, W)                                                         # (R, 9, B)
    present = W > 0
    num_ = np.where(present, ab[:, None, :] * np.nan_to_num(rby), 0.0).sum(axis=2)
    den_ = np.where(present, ab[:, None, :], 0.0).sum(axis=2)
    Z = fixed(div(num_, den_))
    Zc = fixed(correct(Z, rates["tpr"][:, None], rates["fpr"][:, None]))
    z_trend = trend(values(Zc), list(YPOS), 1.0)
    span = D["pop"] & (D["year"] <= 2024) & (RW["w"] > 0)
    left = {s: int((span & (D["size_status"] == s)).sum()) for s in SIZE_STATUSES[1:]}
    return {
        "comments": {"retained_2016_2024": int(span.sum()),
                     "joined": int((span & (D["size_status"] == "joined")).sum()), "left_out_by_status": left},
        "buckets": SIZE_NAMES,
        "weighted_comments_by_year_and_bucket": {YLABELS[y]: {b: float(W[0, y, i]) for i, b in enumerate(SIZE_NAMES)}
                                                 for y in range(len(TREND_YEARS))},
        "comments_by_year_and_bucket": {
            str(y): {b: int((span & (D["year"] == y) & (D["size_status"] == "joined") & (D["size_bucket"] == b)).sum())
                     for b in SIZE_NAMES} for y in TREND_YEARS},
        "bucket_share_by_year_a": {YLABELS[y]: {b: num(dec["a"][0, y, i]) for i, b in enumerate(SIZE_NAMES)}
                                   for y in range(len(TREND_YEARS))},
        "bucket_concern_share_pooled_r": {b: num(dec["r"][0, i]) for i, b in enumerate(SIZE_NAMES)},
        "bucket_mean_year": dict(zip(SIZE_NAMES, dec["mean_year"])),
        "synthetic_series_S": dict(zip(YLABELS, S)), "observed_series_O": dict(zip(YLABELS, O)),
        "sen_slope_S": s_slope, "sen_slope_O": o_slope, "C": C, "T": T,
        "ratio_a_common_trend_would_produce": common,
        **cut_point_outcome(C, T, significant, gap),
        "size_stratified_series": {"rows": rows(Zc, YLABELS), "classified": values(Z), "trend": z_trend,
                                   "trend_8_x_sen_slope": None if z_trend.get("sen_slope") is None
                                   else SPAN_INTERVALS * z_trend["sen_slope"]},
        "labels": "classified labels (R4); the size-stratified series is corrected (Deviation 13)",
    }


def month_decomposition(A: np.ndarray, significant: bool, gap: float) -> dict:
    W = np.zeros((R, len(TREND_YEARS), 12))
    K = np.zeros((R, len(TREND_YEARS), 12))
    for yi, y in enumerate(TREND_YEARS):
        for q in (1, 2, 3, 4):
            for j in range(3):
                W[:, yi, 3 * (q - 1) + j] = A[:, QI[(y, q)], F[f"mw_{j}"]]
                K[:, yi, 3 * (q - 1) + j] = A[:, QI[(y, q)], F[f"mwc_{j}"]]
    dec = decomposition(W, K)
    S, O = values(dec["S"]), values(dec["O"])
    s_slope, o_slope = sen9(S), sen9(O)
    C = None if s_slope is None else SPAN_INTERVALS * s_slope
    T = None if o_slope is None else SPAN_INTERVALS * o_slope
    if None in (C, T):
        outcome = "not computed"
    elif not significant:
        outcome = ("not applied: the primary series' Mann-Kendall test is not significant (Deviation 13); "
                   "|C_m| / (TPR - FPR) is reported")
    elif abs(C) < 0.2 * abs(T):
        outcome = "the drift is not consequential: |C_m| < 0.20 x |T| (Deviation 13, sensitivity 1)"
    else:
        outcome = "the drift is a material limitation: |C_m| >= 0.20 x |T|; the trend is also stated net of C_m (T - C_m)"
    return {"label": EXPLORATORY, "months": list(range(1, 13)),
            "month_share_by_year": {YLABELS[y]: [num(dec["a"][0, y, m]) for m in range(12)]
                                    for y in range(len(TREND_YEARS))},
            "month_concern_share_pooled": [num(dec["r"][0, m]) for m in range(12)],
            "month_mean_year": dec["mean_year"],
            "synthetic_series_S_m": dict(zip(YLABELS, S)), "observed_series_O": dict(zip(YLABELS, O)),
            "sen_slope_S_m": s_slope, "sen_slope_O": o_slope, "C_m": C, "T": T,
            "ratio_a_common_trend_would_produce": sen9([float(v) for v in dec["mix_mean_year"]]),
            "abs_C_m": None if C is None else abs(C), "0.20_x_abs_T": None if T is None else 0.2 * abs(T),
            "C_m_over_T": None if (C is None or not T) else C / T,
            "T_minus_C_m": None if None in (C, T) else T - C,
            "T_minus_C_m_corrected_scale": None if None in (C, T) else (T - C) / gap,
            "abs_C_m_corrected_scale": None if C is None else abs(C) / gap, "outcome": outcome}


# =============================================================================
# the relevance-error series (Deviation 13)
# =============================================================================
def relevance_error_series(D: dict, RW: dict, x0: np.ndarray, data: dict, rates: dict) -> dict:
    err = sample.relevance_error(data)
    def share_of(x):
        return Fraction(x["k"], x["n"]) if x["n"] else None

    e = {era: (share_of(err["by_era"][era]["e_in"]), share_of(err["by_era"][era]["e_out"])) for era in ERA_ORDER}
    retained = np.zeros(len(D["ids"]), bool)
    for y in YEARS:
        kept = RW["table"][str(y)]["retained"]
        retained |= (D["year"] == y) & np.isin(D["sub"], kept)
    t12 = np.isin(D["tier"], TIER12)
    tpr, fpr = float(rates["tpr"][0]), float(rates["fpr"][0])
    low, high, table = [], [], []
    for qi, p in enumerate(QUARTERS):
        inq = (D["qidx"] == qi) & retained & t12
        n_in = int((inq & D["pop"]).sum())
        n_out = int((inq & (D["s1"] == "N")).sum())
        ei, eo = (None if v is None else float(v) for v in e[era_of_year(p[0])])
        x = num(x0[qi])
        lo = hi = None
        den = None if None in (ei, eo) else n_in - ei * n_in + eo * n_out
        if x is not None and den is not None and den > 0 and ei < 1:
            p_lo = clip01((max(x - ei, 0.0) / (1 - ei) - fpr) / (tpr - fpr))
            p_hi = clip01((min(x, 1 - ei) / (1 - ei) - fpr) / (tpr - fpr))
            lo = p_lo * (n_in - ei * n_in) / den
            hi = (p_hi * (n_in - ei * n_in) + eo * n_out) / den
        low.append(lo)
        high.append(hi)
        table.append({"period": qlabel(p), "n_in": n_in, "n_out": n_out, "e_in": ei, "e_out": eo,
                      "classified_share_x": x, "low": lo, "high": hi})
    return {"rows": table,
            "e_in_e_out_by_era": {era: {"e_in": num(e[era][0]), "e_in_exact": sample.fr(e[era][0]),
                                        "e_out": num(e[era][1]), "e_out_exact": sample.fr(e[era][1])}
                                  for era in ERA_ORDER},
            "low_sen_slope": trend(low[:TREND_Q], list(QPOS[:TREND_Q]), 4.0),
            "high_sen_slope": trend(high[:TREND_Q], list(QPOS[:TREND_Q]), 4.0),
            "wrongly_included_classified_concern_by_stage2": err["wrongly_included_classified_concern_by_stage2"],
            "wrongly_left_out_gold_concern": err["wrongly_left_out_gold_concern"],
            "note": "no interval; the slopes are not bounds on the slope; p_lo and p_hi are clipped as written and the "
                    "slopes are taken on the values so formed; e_in and e_out are applied to every comment of a "
                    "quarter, the tranche items included, although their Stage 1 predictions in the corpus run are "
                    "in-sample (Deviation 13)"}


# =============================================================================
# RQ2 (Deviations 9 and 13; rule 10)
# =============================================================================
def sparsity(D: dict) -> dict:
    pop = D["pop"]
    out = {}
    for s in VALUES8:
        q = [int((pop & (D["qidx"] == qi) & (D["subsys"] == s)).sum()) for qi in range(TREND_Q)]
        y = [int((pop & (D["year"] == yr) & (D["subsys"] == s)).sum()) for yr in TREND_YEARS]
        mq, my = float(np.median(q)), float(np.median(y))
        res = "quarterly" if mq >= SPARSITY else "annual" if my >= SPARSITY else "counts only"
        if s in COUNTS_ONLY:
            shown = "counts (R5)" if s == "v2x" else "counts (Deviation 13: reported and never tested)"
        else:
            shown = res
        out[s] = {"median_quarterly_count": mq, "median_annual_count": my, "resolution_by_the_rule": res,
                  "reported_as": shown}
    return out


def rq2_measures(A: np.ndarray, rates: dict, groups: list) -> dict:
    tpr, fpr = rates["tpr"][:, None], rates["fpr"][:, None]
    N = {s: np.stack([period_sum(A, g, f"sw_{s}") for g in groups], axis=1) for s in VALUES8}
    K = {s: np.stack([period_sum(A, g, f"swc_{s}") for g in groups], axis=1) for s in VALUES8}
    Ac = {s: div(K[s] - fpr * N[s], np.broadcast_to(tpr - fpr, N[s].shape)) for s in VALUES8}
    sA, sN, sK = sum(Ac.values()), sum(N.values()), sum(K.values())
    C = div(sA, sN)
    Cc = div(sK, sN)
    out = {"N": N, "K": K, "A": Ac, "C": fixed(C), "C_classified": fixed(Cc)}
    out["pi"] = {s: fixed(np.where(sA > 0, div(Ac[s], sA), np.nan)) for s in VALUES8}
    out["Cs"] = {s: fixed(div(Ac[s], N[s])) for s in VALUES8}
    out["E"] = {s: fixed(np.where(C > 0, div(out["Cs"][s], C), np.nan)) for s in VALUES8}
    out["pi_classified"] = {s: fixed(div(K[s], sK)) for s in VALUES8}
    out["Cs_classified"] = {s: fixed(div(K[s], N[s])) for s in VALUES8}
    out["E_classified"] = {s: fixed(np.where(Cc > 0, div(out["Cs_classified"][s], Cc), np.nan)) for s in VALUES8}
    return out


def rq2(A: np.ndarray, rates: dict, D: dict) -> dict:
    sp = sparsity(D)
    pop = D["pop"]
    span = rq2_measures(A, rates, [list(range(TREND_Q))])
    quarters = rq2_measures(A, rates, [[qi] for qi in range(len(QUARTERS))])
    years = rq2_measures(A, rates, [YEAR_Q_ALL[y] for y in YEARS])
    year_labels = [str(y) for y in TREND_YEARS] + ["2025 (January-April, descriptive)"]
    values_out, tests = {}, {}
    for s in VALUES8:
        entry = {"sparsity": sp[s],
                 "counts": {"classified_relevant_by_quarter": {QLABELS[qi]: int((pop & (D["qidx"] == qi)
                                                                                 & (D["subsys"] == s)).sum())
                                                               for qi in range(len(QUARTERS))},
                            "classified_concern_by_quarter": {QLABELS[qi]: int((pop & (D["qidx"] == qi) & (D["subsys"] == s)
                                                                                & (D["s2"] == "CONCERN")).sum())
                                                              for qi in range(len(QUARTERS))},
                            "classified_relevant_by_year": {str(y): int((pop & (D["year"] == y) & (D["subsys"] == s)).sum())
                                                            for y in YEARS},
                            "classified_concern_by_year": {str(y): int((pop & (D["year"] == y) & (D["subsys"] == s)
                                                                        & (D["s2"] == "CONCERN")).sum()) for y in YEARS},
                            "weighted_N_2016_2024": num(span["N"][s][0, 0]),
                            "weighted_K_2016_2024": num(span["K"][s][0, 0]),
                            "A_2016_2024": num(span["A"][s][0, 0])}}
        shares = s not in COUNTS_ONLY and sp[s]["resolution_by_the_rule"] != "counts only"
        if shares:
            entry["over_2016_2024"] = {
                "pi_s": rows(span["pi"][s], ["2016-2024"])[0], "C_s": rows(span["Cs"][s], ["2016-2024"])[0],
                "E_s": rows(span["E"][s], ["2016-2024"], share=False)[0],
                "as_classified": {"pi_s": rows(span["pi_classified"][s], ["2016-2024"])[0],
                                  "C_s": rows(span["Cs_classified"][s], ["2016-2024"])[0],
                                  "E_s": rows(span["E_classified"][s], ["2016-2024"], share=False)[0]}}
            if sp[s]["resolution_by_the_rule"] == "quarterly":
                src, labels, pos, n_trend, per_year = quarters, QLABELS, list(QPOS[:TREND_Q]), TREND_Q, 4.0
            else:
                src, labels, pos, n_trend, per_year = years, year_labels, list(YPOS), len(TREND_YEARS), 1.0
            entry["series"] = {"resolution": sp[s]["resolution_by_the_rule"], "pi_s": rows(src["pi"][s], labels),
                               "C_s": rows(src["Cs"][s], labels),
                               "pi_s_as_classified": rows(src["pi_classified"][s], labels),
                               "C_s_as_classified": rows(src["Cs_classified"][s], labels)}
            if s in FAMILY_A:
                t = trend(values(src["pi"][s], n_trend), pos, per_year)
                entry["family_A_test"] = t
                if t.get("sen_slope") is not None:
                    tests[s] = t["p"]
        values_out[s] = entry
    adjusted = holm(tests) if tests else {}
    for s, p in adjusted.items():
        values_out[s]["family_A_test"]["holm_adjusted_p"] = p
        values_out[s]["family_A_test"]["significant_after_holm"] = bool(p < ALPHA)
    return {"values": values_out,
            "family_A": {"tests": [s for s in FAMILY_A if s in tests], "size": len(tests),
                         "holm_adjusted_p": adjusted,
                         "note": "one two-sided Mann-Kendall test with Sen's slope on pi_s for each of the five "
                                 "subsystems that meets the sparsity rule, at its resolution; Holm-Bonferroni within "
                                 "the family (Deviations 9 and 13)"},
            "concern_share_C_2016_2024": rows(span["C"], ["2016-2024"])[0],
            "concern_share_C_2016_2024_as_classified": rows(span["C_classified"], ["2016-2024"])[0],
            "note": "corrected for Stage 2 error with the rates of record, assuming equal rates in every subsystem; not "
                    "corrected for the subsystem classifier's error (Deviations 9 and 13); 2025 is descriptive"}


# =============================================================================
# the corpus runs on the tranche items; Tier 3; the Stage 1 shares (rules 11 and 14)
# =============================================================================
def subsystem_validation(D: dict, data: dict, dry: bool) -> dict:
    ids = data["ids"]
    pred = []
    for j, i in enumerate(ids):
        v = D["subsys"][D["position"][i]]
        if v == "" and data["rel"][j] and not dry:
            stop(f"the subsystem run has no label for a tranche item relevant in the gold set. {REPORT}")
        pred.append(v or UNCLASSIFIED)
    pred = np.array(pred, dtype=object)
    has = np.isin(data["gsub"], SUBSYSTEMS)
    out = {"items_with_a_gold_subsystem": int(has.sum()),
           "relevant_items_without_a_gold_subsystem": int((data["rel"] & ~has).sum()),
           "adjudicated_items": int((has & data["subadj"]).sum())}
    for scope, tmask in (("both tranches", np.ones(len(ids), bool)), ("tranche 1", data["tranche"] == 1),
                         ("tranche 2", data["tranche"] == 2)):
        for form, amask in (("all items", np.ones(len(ids), bool)), ("without the adjudicated items", ~data["subadj"])):
            sel = has & tmask & amask
            g, p = data["gsub"][sel], pred[sel]
            table = {a: {b: int(((g == a) & (p == b)).sum()) for b in VALUES8} for a in SUBSYSTEMS}
            per = {}
            for s in SUBSYSTEMS:
                per[s] = {"recall": wilson(table[s][s], sum(table[s].values())),
                          "precision": wilson(table[s][s], sum(table[a][s] for a in SUBSYSTEMS))}
            out[f"{scope}, {form}"] = {"items": int(sel.sum()), "gold_by_classified": table, "by_value": per,
                                       "overall_agreement": wilson(int((g == p).sum()), int(sel.sum()))}
    return out


def stage2_runs_compared(D: dict, data: dict) -> dict:
    labels = CLASSES + ["refusal"]
    pairs = []
    for j, i in enumerate(data["ids"]):
        corpus = D["s2"][D["position"][i]]
        if corpus == "":
            continue                                         # not classified relevant in the corpus run
        evaluation = data["s2"][j] if data["s2"][j] in CLASSES else "refusal"
        pairs.append((evaluation, corpus))
    table = {a: {b: sum(1 for x in pairs if x == (a, b)) for b in labels} for a in labels}
    same = sum(1 for a, b in pairs if a == b)
    return {"items_both_runs_cover": len(pairs), "evaluation_by_corpus_run": table,
            "same_label": count_share(same, len(pairs)),
            "note": "rows: the evaluation run of record; columns: the corpus run; a refusal is a fourth value "
                    "(Deviation 13). The error rates of record are not re-estimated."}


def stage1_shares(D: dict, data: dict) -> dict:
    t12 = np.isin(D["tier"], TIER12)
    y = D["s1"] == "Y"
    era = np.array([era_of_year(v) for v in D["year"]], dtype=object)
    frame = D["frame"]
    corpus = {"tier_1_and_2": count_share(int((t12 & y).sum()), int(t12.sum())),
              "frame_comments": {"overall": count_share(int((frame & y).sum()), int(frame.sum())),
                                 **{e: count_share(int((frame & y & (era == e)).sum()), int((frame & (era == e)).sum()))
                                    for e in ERA_ORDER}}}
    s = data["has1"]
    ones = np.ones(int(s.sum()), dtype=np.int64)
    cv = sample.rates_by_era((data["s1"] == "Y")[s], ones, data["era"][s], sample.N_FRAME)
    gold = sample.rates_by_era(data["rel"][s], ones, data["era"][s], sample.N_FRAME)
    def unrounded(v):
        return {"estimate": None if v["_r"] is None else float(v["_r"]), "low": v["_low"], "high": v["_high"],
                "items": v["items"], "numerator_items": v["numerator_items"]}
    in_sample = {}
    for a in ("Y", "N"):
        for b in ("Y", "N"):
            in_sample[f"gold {a}, corpus run {b}"] = int(sum(1 for j, i in enumerate(data["ids"]) if s[j]
                                                             and data["g1"][j] == a and D["s1"][D["position"][i]] == b))
    agree = in_sample["gold Y, corpus run Y"] + in_sample["gold N, corpus run N"]
    return {"label": ADDED,
            "corpus_share_classified_relevant": corpus,
            "sample_design_weighted": {
                "classified_relevant_by_the_cross_validated_prediction": {k: unrounded(v) for k, v in cv.items()},
                "gold_relevance_rate": {k: unrounded(v) for k, v in gold.items()}},
            "corpus_run_stage1_on_the_tranche_items": {"table": in_sample, "agreement": count_share(agree, int(s.sum())),
                                                       "note": "in-sample: the retrained model had seen these labels"}}


def tier3(D: dict) -> tuple[dict, list]:
    t3 = D["tier"] == "Tier 3"
    y = D["s1"] == "Y"
    rows_out = [[D["ids"][k], D["sub"][k], pd.Timestamp(D["created"][k]).isoformat(), int(D["year"][k]),
                 D["thread"][k], int(D["words"][k]), D["text"][k]]
                for k in sorted(np.nonzero(t3 & y)[0], key=lambda k: (pd.Timestamp(D["created"][k]), D["ids"][k]))]
    return {"share_of_all_comments_classified_relevant": count_share(int((t3 & y).sum()), int(y.sum())),
            "tier3_comments": int(t3.sum()), "tier3_classified_relevant": int((t3 & y).sum()),
            "classified_relevant_by_subreddit_and_year": {
                g: {str(yr): int((t3 & y & (D["sub"] == g) & (D["year"] == yr)).sum()) for yr in YEARS}
                for g in TIER3_SUBREDDITS},
            "note": "descriptive: the classifier's accuracy on Tier 3 is unmeasured (Deviation 13); the comments are "
                    "written to tier3_relevant_comments.csv for the author's reading"}, rows_out


def run_counts(D: dict, runs_info: dict) -> dict:
    pop = D["pop"]
    return {"comments": int(len(D["ids"])), "classified_relevant": int((D["s1"] == "Y").sum()),
            "classified_relevant_by_tier": {t: int(((D["s1"] == "Y") & (D["tier"] == t)).sum())
                                            for t in ("Tier 1", "Tier 2", "Tier 3")},
            "population_tier_1_and_2_classified_relevant": int(pop.sum()),
            "stage2_refusals": int((pop & (D["s2"] == "refusal")).sum()),
            "subsystem_unclassified": int((pop & (D["subsys"] == UNCLASSIFIED)).sum()),
            "subsystem_validation_only": runs_info,
            "stage2_refusals_by_quarter": {QLABELS[qi]: int((pop & (D["qidx"] == qi) & (D["s2"] == "refusal")).sum())
                                           for qi in range(len(QUARTERS))},
            "subsystem_unclassified_by_quarter": {QLABELS[qi]: int((pop & (D["qidx"] == qi)
                                                                    & (D["subsys"] == UNCLASSIFIED)).sum())
                                                  for qi in range(len(QUARTERS))}}


# =============================================================================
# the temporal calibration check's rule (Deviation 13)
# =============================================================================
def slope_rows(stat: np.ndarray) -> np.ndarray:
    """Sen's slope per quarter of the 36 trend-span values of each resample row (rows 1 to 2,000), over the quarters
    that have a value on the full corpus; NaN in a row that lacks one of them (rule 7)."""
    Y = stat[1:, :TREND_Q]
    keep = ~np.isnan(stat[0, :TREND_Q])
    return sen_rows(Y[:, keep], QPOS[:TREND_Q][keep])


def temporal_rule(series: dict, primary: dict, block: dict) -> dict:
    crit = criteria(block, primary)
    d = slope_rows(series["block_specific"]) - slope_rows(series["primary"])
    iv = interval(d * 4.0)                                   # per year (four times the slope per quarter)
    material = None if crit is None else not crit["both_hold"]
    diff = None if None in (block.get("sen_slope"), primary.get("sen_slope")) else 4.0 * (block["sen_slope"]
                                                                                          - primary["sen_slope"])
    if not material:
        established = None
        qualification = "not applied: Deviation 13 qualifies a material effect only"
    elif iv["low"] is None:
        established = None
        qualification = "no interval: more than 100 resamples lack a value"
    else:
        established = bool(iv["low"] > 0 or iv["high"] < 0)
        qualification = ("established: the interval excludes zero" if established else
                         "not distinguishable from sampling error in the block rates: the interval includes zero")
    if material is None:
        text = "The rule could not be applied: a series has no Sen's slope."
    elif not material:
        text = ("The block-specific series agrees with the primary series by R3's two criteria: the temporal effect is "
                "not material, and the primary series is the result.")
    else:
        failed = [n for n, k in (("1 (agreement of conclusion)", "criterion1_agreement_of_conclusion"),
                                 ("2 (overlap of estimate)", "criterion2_overlap_of_estimate")) if not crit[k]]
        text = (f"The block-specific series fails R3's criterion {' and '.join(failed)} against the primary series: the "
                f"temporal effect is material. The conclusion drawn from the primary series holds only under error "
                f"rates that are stable over time; the effect is {qualification}. The primary series keeps the overall "
                f"rates, and the finding is carried into the discussion and the limitations (Deviation 13).")
    return {"criteria_block_specific_against_primary": crit, "material": material,
            "difference_in_sen_slope_per_year_block_specific_minus_primary": diff,
            "difference_interval95_per_year": iv, "difference_interval95_per_quarter": interval(d),
            "established": established, "qualification": qualification,
            "statement": text}


def r3_statement(name: str, crit: dict | None, consequence: str) -> str:
    if crit is None:
        return f"{name}: the criteria could not be applied (a series has no Sen's slope)."
    if crit["both_hold"]:
        return f"{name}: both of R3's criteria hold; the series agrees with the primary series."
    failed = [n for n, k in (("1", "criterion1_agreement_of_conclusion"), ("2", "criterion2_overlap_of_estimate"))
              if not crit[k]]
    return f"{name}: R3's criterion {' and '.join(failed)} fails. {consequence}"


# =============================================================================
# the analyses
# =============================================================================
def weights_summary(D: dict, RW: dict) -> dict:
    pop = D["pop"]
    w = RW["w"]
    left = [{"subreddit": g, "year": y, "comments": n} for y in YEARS for g, n in RW["table"][str(y)]["left_out"].items()]
    ess = {}
    for qi, p in enumerate(QUARTERS):
        sel = pop & (D["qidx"] == qi) & (w > 0)
        sw, sw2 = float(w[sel].sum()), float((w[sel] ** 2).sum())
        ess[qlabel(p)] = {"comments": int((pop & (D["qidx"] == qi)).sum()), "retained": int(sel.sum()),
                          "sum_of_weights": sw, "effective_sample_size": (sw * sw / sw2) if sw2 > 0 else None}
    largest = max(((wy, g, y) for y in YEARS for g, wy in RW["table"][str(y)]["weights"].items()), default=None)
    return {"population": int(pop.sum()), "target_shares_2016_2024": RW["target"],
            "by_year": RW["table"], "left_out": left,
            "left_out_comments": {"2016-2024": sum(x["comments"] for x in left if x["year"] <= 2024),
                                  "2025": sum(x["comments"] for x in left if x["year"] == 2025)},
            "largest_weight": None if largest is None else {"weight": largest[0], "subreddit": largest[1],
                                                            "year": largest[2]},
            "quarters": ess,
            "companion_subreddits_retained_in_every_year_2016_2024": RW["companion_subreddits"],
            "companion_by_year": {y: {"retained": RW["table_c"][y]["retained"], "weights": RW["table_c"][y]["weights"]}
                                  for y in RW["table_c"]},
            "word_floor_25": {"comments": int(RW["floor_mask"].sum()),
                              "by_year": {y: {"retained": RW["table_u"][y]["retained"],
                                              "left_out": RW["table_u"][y]["left_out"],
                                              "weights": RW["table_u"][y]["weights"]} for y in RW["table_u"]}}}


def series_block(stat: np.ndarray, labels: list = QLABELS, hamed_rao: bool = False) -> dict:
    return {"rows": rows(stat, labels), "trend": qtrend(stat, hamed_rao=hamed_rao)}


def analyse(data: dict, D: dict, item: dict, comment_generator: list, dry: bool = False) -> tuple[dict, dict]:
    rates, M = item["rates"], item["M"]
    gap = float(rates["tpr"][0] - rates["fpr"][0])
    RW = reweighting(D)
    X = comment_features(D, RW)
    A, comment_info = aggregates(D, X, comment_generator)
    in_span = D["pop"] & (D["year"] <= 2024)
    v1 = float((in_span & (D["tier"] == "Tier 1")).sum() / in_span.sum())
    S = quarterly_series(A, rates, M, v1)
    primary = series_block(S["primary"], hamed_rao=True)
    pt = primary["trend"]
    significant = bool(pt.get("significant"))
    block = series_block(S["block_specific"])
    comp = {name: series_block(S[name]) for name in ("companion", "pooled", "tier_level", "three_class_concern",
                                                      "word_floor_25", "tier1", "tier2")}
    for name in ("companion", "pooled", "three_class_concern", "word_floor_25"):
        comp[name]["criteria"] = criteria(comp[name]["trend"], pt)
    P3 = S["_three_class_raw"]
    comp["three_class_concern"]["components"] = [
        {"period": QLABELS[qi], "raw": {c: num(P3[0, qi, k]) for k, c in enumerate(CLASSES)},
         "displayed": None if displayed_three_class(P3[0, qi]) is None
         else dict(zip(CLASSES, displayed_three_class(P3[0, qi])))} for qi in range(len(QUARTERS))]
    hx, hc = grouped_primary(A, rates, [HALF_Q[p] for p in HALVES])
    yx, yc = grouped_primary(A, rates, [YEAR_Q[y] for y in TREND_YEARS])
    cps = changepoints(values(S["primary"], TREND_Q))
    near = [c for c in cps.get("changepoints", []) if c["supported"] and QUARTERS[c["index"]] in NEAR_BOUNDARY]
    if near:
        cpb = changepoints(values(S["block_specific"], TREND_Q))
        held = set(cpb.get("supported", []))
        for c in near:
            c["near_the_block_boundary"] = True
            c["supported_on_the_block_specific_series"] = c["quarter"] in held
            c["keeps_the_label"] = c["quarter"] in held
            if not c["keeps_the_label"]:
                c["statement"] = ("supported on the primary series but not on the block-specific series, so it does not "
                                  "keep the label: the series does not distinguish a step here from a steady trend or "
                                  "from noise (Deviation 13)")
            c["note"] = ("a difference in error rates between the two blocks of the temporal calibration check would put "
                         "a step near the boundary (Deviation 13)")
        cps["block_specific_search"] = cpb
    kept = [c for c in cps.get("changepoints", []) if c["supported"] and c.get("keeps_the_label", True)]
    cps["supported_after_the_boundary_rule"] = [c["quarter"] for c in kept]
    cps["statement"] = (f"Supported changepoint(s), described by year: {', '.join(str(c['year']) for c in kept)}."
                        if kept else "The series does not distinguish a step from a steady trend or from noise "
                                     "(Deviation 13).")
    diff_h = hc[:, 0::2] - hc[:, 1::2]
    mean_h = diff_h.mean(axis=1)
    mean_h[np.isnan(diff_h).any(axis=1)] = np.nan
    temporal = temporal_rule(S, pt, block["trend"])
    results = {
        "corpus_runs": run_counts(D, len(D["validation_only"])),
        "stage1_shares": stage1_shares(D, data),
        "stage2_runs_compared_on_the_tranche_items": stage2_runs_compared(D, data),
        "subsystem_classifier_validation": subsystem_validation(D, data, dry),
        "error_rates": {
            "rates_of_record": {"tpr": float(rates["tpr"][0]), "fpr": float(rates["fpr"][0]),
                                "tpr_exact": sample.fr(item["overall"]["_tpr"]),
                                "fpr_exact": sample.fr(item["overall"]["_fpr"]), "tpr_minus_fpr": gap,
                                "reproduced": True,
                                "tpr_minus_fpr_at_least_0_25": bool(gap >= 0.25),
                                "note": "Deviation 12, success criterion 6: below 0.25 the uncorrected series would be "
                                        "reported beside the corrected one; the classified shares are in the primary "
                                        "series' rows in either case"},
            "block_rates_both_tranches": {
                **{b: {"tpr": float(rates[f"tpr_{b}"][0]), "fpr": float(rates[f"fpr_{b}"][0]),
                       "tpr_exact": sample.fr(item["blocks"][b]["_tpr"]), "fpr_exact": sample.fr(item["blocks"][b]["_fpr"]),
                       "tpr_interval95": interval(rates[f"tpr_{b}"][1:]), "fpr_interval95": interval(rates[f"fpr_{b}"][1:])}
                   for b in ("early", "late")},
                **{f"{k}_late_minus_early": {"difference": float(rates[f"{k}_late"][0] - rates[f"{k}_early"][0]),
                                             "interval95": interval(rates[f"{k}_late"][1:] - rates[f"{k}_early"][1:])}
                   for k in ("tpr", "fpr")}},
            "temporal_calibration_check_as_the_sample_analyses_report_it": item["temporal"],
            "three_class_rates_M": {a: {b: float(item["M_exact"][i][j]) for j, b in enumerate(CLASSES)}
                                    for i, a in enumerate(CLASSES)},
            "three_class_rates_M_exact": {a: {b: sample.fr(item["M_exact"][i][j]) for j, b in enumerate(CLASSES)}
                                          for i, a in enumerate(CLASSES)},
            "item_resamples": {"resamples": N_RESAMPLES, "generator": "numpy.random.default_rng([24916660, 3, 1])",
                               "strata_sizes": item["strata_sizes"], "index_arrays_sha256": item["index_arrays_sha256"],
                               "same_as_the_register": item["index_arrays_sha256"] == ITEM_ARRAYS_SHA256}},
        "reweighting": weights_summary(D, RW),
        "temporal_calibration_check_rule": temporal,
        "rq1": {
            "primary_series": {
                "rows": [{**r, "classified_share": num(S["classified"][0, qi]),
                          **{k: v for k, v in weights_summary_row(D, RW, qi).items()}}
                         for qi, r in enumerate(primary["rows"])],
                "trend": pt, "half_years": {"rows": rows(hc, HLABELS), "classified": dict(zip(HLABELS, values(hx)))},
                "years": {"rows": rows(yc, YLABELS), "classified": dict(zip(YLABELS, values(yx)))},
                "changepoints": cps, "stl": stl(values(S["primary"], TREND_Q)), "glm": glm(D),
                "notes": ["2025 Q1 and Q2 are in this file for the quarterly plot only and enter no statistic and no "
                          "annual table (R3, Deviation 13).",
                          "The corrected values are clipped to [0, 1] for display only; every statistic uses them "
                          "before clipping (Deviation 13).",
                          "The Stage 1 predictions of the 1,000 tranche items, about 8% of the Tier 1+2 corpus, are "
                          "in-sample: the retrained model had seen their labels (Deviation 13).",
                          "The items that chose the deployed Stage 2 classifier also supply its error rates, so the "
                          "rates are somewhat optimistic (Deviations 12 and 13)."]},
            "block_specific_series": block,
            "companion_series": {**comp["companion"], "subreddits": RW["companion_subreddits"],
                                 "statement": r3_statement("Companion series", comp["companion"]["criteria"],
                                                           "Both series are reported in full, and the difference is stated "
                                                           "as the effect of leaving out the subreddits not retained in "
                                                           "every year (Deviation 13).")},
            "pooled_series": {**comp["pooled"],
                              "statement": r3_statement("Pooled series (R3)", comp["pooled"]["criteria"],
                                                        "Both series are reported in full and the divergence is stated in "
                                                        "the results, the discussion and the limitations, with subreddit "
                                                        "composition named as the mechanism (R3).")},
            "tier_level_series": {**comp["tier_level"], "tier_shares_v_2016_2024": {"Tier 1": v1, "Tier 2": 1 - v1},
                                  "note": "the robustness check R3 names; no criterion is applied"},
            "three_class_correction": {**comp["three_class_concern"], "label": EXPLORATORY,
                                       "statement": r3_statement("Three-class correction (CONCERN component)",
                                                                 comp["three_class_concern"]["criteria"],
                                                                 "Exploratory (Family C): the primary series is "
                                                                 "unchanged.")},
        },
        "thread_size_R4": thread_size(A, rates, D, RW, significant, gap),
        "relevance_error_series": relevance_error_series(D, RW, S["classified"][0], data, rates),
        "sensitivities": {
            "seasonality": {"label": EXPLORATORY, "half_years": rows(hc, HLABELS),
                            "mean_H1_minus_H2_2016_2024": {"value": num(mean_h[0]), "interval95": interval(mean_h[1:])},
                            "month_of_year_decomposition": month_decomposition(A, significant, gap)},
            "word_floor_25": {**comp["word_floor_25"], "label": EXPLORATORY,
                              "statement": r3_statement("Word floor of 25", comp["word_floor_25"]["criteria"],
                                                        "Exploratory (Family C): the primary series is unchanged.")},
            "tier_strata": {"label": EXPLORATORY, "tier1": comp["tier1"], "tier2": comp["tier2"],
                            "note": "each tier's comments weighted equally; no criterion is applied"},
        },
        "rq2": rq2(A, rates, D),
        "comment_resamples": comment_info,
    }
    results["rq2"]["temporal_condition"] = (
        "The temporal effect is material: the corrected subsystem measures, like the primary series, hold only under "
        f"error rates that are stable over time; the effect is {temporal['qualification']} (Deviation 13)."
        if temporal["material"] else
        "The temporal effect is not material: the temporal calibration check puts no condition on the corrected "
        "subsystem measures (Deviation 13).")
    t3, t3_rows = tier3(D)
    results["tier3"] = t3
    extra = {"tier3_rows": t3_rows, "S": S, "hc": hc, "yc": yc}
    return results, extra


def weights_summary_row(D: dict, RW: dict, qi: int) -> dict:
    pop = D["pop"]
    w = RW["w"]
    sel = pop & (D["qidx"] == qi) & (w > 0)
    sw, sw2 = float(w[sel].sum()), float((w[sel] ** 2).sum())
    return {"comments": int((pop & (D["qidx"] == qi)).sum()), "retained": int(sel.sum()),
            "effective_sample_size": (sw * sw / sw2) if sw2 > 0 else None}


# =============================================================================
# the values file and the figures (rule 15)
# =============================================================================
VALUE_COLUMNS = ["series", "period", "value", "value_displayed", "low", "high", "low_displayed", "high_displayed",
                 "resamples_without_value"]


def value_rows(results: dict) -> list:
    out = []

    def add(name, rws):
        for r in rws:
            iv = r.get("interval95") or {}
            out.append([name, r["period"], r.get("value"), r.get("value_displayed"), iv.get("low"), iv.get("high"),
                        iv.get("low_displayed"), iv.get("high_displayed"), iv.get("resamples_without_value")])

    q = results["rq1"]
    add("primary (quarter)", q["primary_series"]["rows"])
    add("primary (half-year)", q["primary_series"]["half_years"]["rows"])
    add("primary (year)", q["primary_series"]["years"]["rows"])
    add("primary, classified share (quarter)", [{"period": r["period"], "value": r["classified_share"]}
                                                for r in q["primary_series"]["rows"]])
    for key, name in (("block_specific_series", "block-specific"), ("companion_series", "companion"),
                      ("pooled_series", "pooled"), ("tier_level_series", "tier-level"),
                      ("three_class_correction", "three-class CONCERN component")):
        add(f"{name} (quarter)", q[key]["rows"])
    sens = results["sensitivities"]
    add("word floor 25 (quarter)", sens["word_floor_25"]["rows"])
    add("Tier 1 (quarter)", sens["tier_strata"]["tier1"]["rows"])
    add("Tier 2 (quarter)", sens["tier_strata"]["tier2"]["rows"])
    re_ = results["relevance_error_series"]["rows"]
    add("relevance error, low (quarter)", [{"period": r["period"], "value": r["low"]} for r in re_])
    add("relevance error, high (quarter)", [{"period": r["period"], "value": r["high"]} for r in re_])
    r4 = results["thread_size_R4"]
    add("size-stratified, corrected (year)", r4["size_stratified_series"]["rows"])
    add("size-stratified, classified (year)", [{"period": k, "value": v}
                                               for k, v in zip(YLABELS, r4["size_stratified_series"]["classified"])])
    add("R4 synthetic series S, classified (year)", [{"period": k, "value": v} for k, v in r4["synthetic_series_S"].items()])
    add("R4 observed series O, classified (year)", [{"period": k, "value": v} for k, v in r4["observed_series_O"].items()])
    mo = sens["seasonality"]["month_of_year_decomposition"]
    add("month-of-year synthetic series S_m, classified (year)",
        [{"period": k, "value": v} for k, v in mo["synthetic_series_S_m"].items()])
    add("month-of-year observed series O, classified (year)",
        [{"period": k, "value": v} for k, v in mo["observed_series_O"].items()])
    comps = q["three_class_correction"]["components"]
    for c in CLASSES:
        add(f"three-class {c} component, raw and displayed (quarter)",
            [{"period": x["period"], "value": x["raw"][c],
              "value_displayed": None if x["displayed"] is None else x["displayed"][c]} for x in comps])
    st = q["primary_series"]["stl"]
    if st.get("computed"):
        for k in ("trend", "seasonal", "residual"):
            add(f"STL {k} of the primary series (quarter)", [{"period": p, "value": v} for p, v in zip(st["quarters"], st[k])])
    for s, e in results["rq2"]["values"].items():
        if "series" in e:
            add(f"pi_s {s} ({e['series']['resolution']})", e["series"]["pi_s"])
            add(f"C_s {s} ({e['series']['resolution']})", e["series"]["C_s"])
            add(f"pi_s {s}, as classified ({e['series']['resolution']})", e["series"]["pi_s_as_classified"])
            add(f"C_s {s}, as classified ({e['series']['resolution']})", e["series"]["C_s_as_classified"])
    return [[(sample.fl(v) if isinstance(v, float) else ("" if v is None else v)) for v in r] for r in out]


def make_figures(results: dict) -> dict:
    """Each figure as PDF and PNG bytes (deterministic: no creation date)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "legend.frameon": False, "savefig.dpi": 200})
    files = {}
    grey, blue, red, green, purple, orange = "#9a9a9a", "#1f4e79", "#b03a2e", "#2e7d32", "#6a1b9a", "#e65100"

    def save(fig, name):
        for fmt in ("pdf", "png"):
            buf = io.BytesIO()
            fig.savefig(buf, format=fmt, bbox_inches="tight",
                        metadata={"CreationDate": None} if fmt == "pdf" else {"Software": None})
            files[f"{name}.{fmt}"] = buf.getvalue()
        plt.close(fig)

    def below(ax, ncol=3):
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=ncol)

    def axes_quarters(ax, events=True, ylabel="Concern share (corrected)", compact=False):
        ax.set_xticks([4 * k for k in range(10)])
        ax.set_xticklabels([("" if compact and k % 2 else str(2016 + k)) for k in range(10)])
        ax.set_xlim(-1, len(QUARTERS))
        if ylabel:
            ax.set_ylabel(ylabel)
        if events:
            top = ax.get_ylim()[1]
            for name, p in EVENTS:
                ax.axvline(QI[p] - 0.5, color=grey, lw=0.8, ls="--")
                ax.text(QI[p] - 0.4, top, name, rotation=90, va="top", ha="left", fontsize=6, color="#555555")

    def interval_of(r, key):
        i = r.get("interval95") or {}
        v = i.get(key)
        return np.nan if v is None else v

    def draw(ax, rws, color, label, band=True, ls="-", marker="o", offset=0.0):
        pts = [(qi, r) for qi, r in enumerate(rws) if r.get("value") is not None]
        trend_part = [p for p in pts if p[0] < TREND_Q]
        later = [p for p in pts if p[0] >= TREND_Q]
        for part, filled in ((trend_part, True), (later, False)):
            if not part:
                continue
            x = np.array([p[0] for p in part], dtype=float) + offset
            y = np.array([p[1].get("value_displayed", p[1]["value"]) for p in part], dtype=float)
            if band:
                lo = np.array([interval_of(p[1], "low_displayed") for p in part])
                hi = np.array([interval_of(p[1], "high_displayed") for p in part])
                ok = ~np.isnan(lo) & ~np.isnan(hi)
                ax.vlines(x[ok], lo[ok], hi[ok], color=color, lw=0.7, alpha=0.6)
            if filled:
                ax.plot(x, y, ls=ls, marker=marker, ms=2.5, lw=1.0, color=color, label=label)
            else:
                ax.plot(x, y, ls="none", marker=marker, ms=3, mfc="white", color=color,
                        label=None if trend_part else label)

    def annual(ax, rws, pos, colour, label, marker="o"):
        pts = [(p, r) for p, r in zip(pos, rws) if r["value"] is not None]
        if not pts:
            return
        x = np.array([p for p, _ in pts], dtype=float)
        y = np.array([r["value_displayed"] for _, r in pts], dtype=float)
        lo = np.array([interval_of(r, "low_displayed") for _, r in pts])
        hi = np.array([interval_of(r, "high_displayed") for _, r in pts])
        ok = ~np.isnan(lo) & ~np.isnan(hi)
        ax.vlines(x[ok], lo[ok], hi[ok], color=colour, lw=0.7, alpha=0.6)
        span = x < 2025
        ax.plot(x[span], y[span], marker=marker, ms=3, lw=1.0, color=colour, label=label)
        if (~span).any():                                    # 2025, descriptive
            ax.plot(x[~span], y[~span], ls="none", marker=marker, ms=3, mfc="white", color=colour)

    def years_axis(ax, years):
        ax.set_xticks(years)
        ax.set_xticklabels([str(y) for y in years], rotation=45)

    q = results["rq1"]
    prim = q["primary_series"]["rows"]
    pt = q["primary_series"]["trend"]

    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    draw(ax, prim, blue, "Primary series, with 95% interval (2025: hollow, plotted only)")
    if pt.get("sen_slope") is not None:
        t = np.arange(TREND_Q)
        ax.plot(t, pt["sen_intercept"] + pt["sen_slope"] * t, color=red, lw=0.9, ls=":", label="Sen's slope")
    ax.set_ylim(0, 1)
    axes_quarters(ax)
    below(ax, 2)
    save(fig, "fig1_primary_series")

    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    draw(ax, prim, blue, "Primary series (overall rates)", offset=-0.15)
    draw(ax, q["block_specific_series"]["rows"], red, "Block-specific series (block rates)", offset=0.15)
    ax.axvline(QI[(2022, 1)] - 0.5, color="black", lw=0.8)
    ax.set_ylim(0, 1)
    axes_quarters(ax, events=False)
    below(ax, 2)
    save(fig, "fig2_block_specific")

    fig, axs = plt.subplots(2, 2, figsize=(7.5, 5.2), sharex=True, sharey=True)
    for ax, (key, name, colour) in zip(axs.ravel(), (("companion_series", "Companion series", green),
                                                    ("pooled_series", "Pooled series", red),
                                                    ("tier_level_series", "Tier-level series", purple),
                                                    ("three_class_correction", "Three-class correction, CONCERN",
                                                     orange))):
        draw(ax, prim, grey, None, band=False)
        draw(ax, q[key]["rows"], colour, None)
        ax.set_title(f"{name} (grey: primary series)", fontsize=8)
        ax.set_ylim(0, 1)
        axes_quarters(ax, events=False, ylabel="Concern share (corrected)" if ax in axs[:, 0] else None, compact=True)
    save(fig, "fig3_comparison_series")

    sens = results["sensitivities"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
    draw(axs[0], prim, grey, "Primary series", band=False)
    draw(axs[0], sens["word_floor_25"]["rows"], green, "Word floor of 25")
    draw(axs[1], prim, grey, "Primary series", band=False)
    draw(axs[1], sens["tier_strata"]["tier1"]["rows"], blue, "Tier 1", offset=-0.15)
    draw(axs[1], sens["tier_strata"]["tier2"]["rows"], red, "Tier 2", offset=0.15)
    for k, ax in enumerate(axs):
        ax.set_ylim(0, 1)
        axes_quarters(ax, events=False, ylabel=None if k else "Concern share (corrected)", compact=True)
        below(ax, 3)
    save(fig, "fig4_sensitivities")

    rel = results["relevance_error_series"]["rows"]
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    draw(ax, prim, blue, "Primary series")
    for key, colour, name in (("low", green, "Low series"), ("high", red, "High series")):
        draw(ax, [{"value": r[key], "value_displayed": r[key]} for r in rel], colour, name, band=False, ls="--",
             marker=".")
    ax.set_ylim(0, 1)
    axes_quarters(ax, events=False)
    below(ax, 3)
    save(fig, "fig5_relevance_error")

    fig, axs = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
    yrs = q["primary_series"]["years"]["rows"]
    halves = q["primary_series"]["half_years"]["rows"]
    annual(axs[0], yrs, TREND_YEARS, blue, "Primary series by year")
    annual(axs[0], halves[0::2], [y - 0.15 for y in TREND_YEARS], green, "January-June", marker="^")
    annual(axs[0], halves[1::2], [y + 0.15 for y in TREND_YEARS], red, "July-December", marker="v")
    annual(axs[1], yrs, TREND_YEARS, grey, "Primary series by year")
    annual(axs[1], results["thread_size_R4"]["size_stratified_series"]["rows"], TREND_YEARS, purple,
           "Size-stratified series (R4)")
    for ax in axs:
        ax.set_ylim(0, 1)
        years_axis(ax, TREND_YEARS)
        below(ax, 2)
    axs[0].set_ylabel("Concern share (corrected)")
    save(fig, "fig6_annual")

    r4 = results["thread_size_R4"]
    mo = sens["seasonality"]["month_of_year_decomposition"]
    fig, axs = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
    for ax, (Sx, Ox, name) in zip(axs, ((r4["synthetic_series_S"], r4["observed_series_O"], "thread-size buckets (R4)"),
                                        (mo["synthetic_series_S_m"], mo["observed_series_O"], "month of year"))):
        ax.plot(TREND_YEARS, [np.nan if Ox[k] is None else Ox[k] for k in YLABELS], marker="o", ms=3, color=blue,
                label="Observed")
        ax.plot(TREND_YEARS, [np.nan if Sx[k] is None else Sx[k] for k in YLABELS], marker="s", ms=3, color=red,
                label="Composition alone")
        ax.set_title(f"Decomposition by {name}", fontsize=8)
        years_axis(ax, TREND_YEARS)
        below(ax, 2)
    axs[0].set_ylabel("Share classified CONCERN (weighted)")
    save(fig, "fig7_decompositions")

    st = q["primary_series"]["stl"]
    if st.get("computed"):
        fig, axs = plt.subplots(4, 1, figsize=(6.5, 6), sharex=True)
        for ax, key, name in zip(axs, ("observed", "trend", "seasonal", "residual"),
                                 ("Observed", "Trend", "Seasonal", "Residual")):
            ax.plot(range(TREND_Q), [np.nan if v is None else v for v in st[key]], color=blue, lw=1.0, marker=".", ms=2)
            ax.set_ylabel(name, fontsize=7)
        axs[0].set_title("STL decomposition of the primary series (corrected, before clipping)", fontsize=8)
        axs[-1].set_xticks([4 * k for k in range(9)])
        axs[-1].set_xticklabels([str(2016 + k) for k in range(9)])
        save(fig, "fig8_stl")

    shown = [(s, e) for s, e in results["rq2"]["values"].items() if "series" in e]
    if shown:
        fig, axs = plt.subplots(len(shown), 1, figsize=(6.5, 1.9 * len(shown)), squeeze=False)
        for ax, (s, e) in zip(axs[:, 0], shown):
            if e["series"]["resolution"] == "quarterly":
                draw(ax, e["series"]["pi_s"], blue, None)
                axes_quarters(ax, events=False, ylabel="Share of concern")
            else:
                annual(ax, e["series"]["pi_s"], YEARS, blue, None)
                years_axis(ax, YEARS)
                ax.set_ylabel("Share of concern")
            ax.set_title(f"{s} ({e['series']['resolution']}; corrected, with 95% intervals)", fontsize=8)
            ax.set_ylim(0, 1)
        fig.tight_layout()
        save(fig, "fig9_subsystems")
    return files


# =============================================================================
# the report (rule 16: every figure formatted from its unrounded value)
# =============================================================================
def render_report(r: dict) -> str:
    def pc(x, d=1):
        return "n/a" if x is None else f"{100 * float(x):.{d}f}%"

    def pp(x, d=2):
        return "n/a" if x is None else f"{100 * float(x):+.{d}f}"

    def p4(x):
        return "n/a" if x is None else f"{float(x):.4f}"

    def pv(x):
        """A p-value: four decimals, or eight significant digits when four decimals would show 0.0500."""
        if x is None:
            return "n/a"
        return f"{float(x):.8g}" if f"{float(x):.4f}" == "0.0500" else f"{float(x):.4f}"

    def pa(x, d=2):
        return "n/a" if x is None else f"{100 * float(x):.{d}f}"

    def shown(row):
        """The displayed (clipped) value, with the raw value beside it when it was clipped (R5)."""
        if row.get("value") is None:
            return "n/a"
        return pc(row["value_displayed"]) + (f" (raw {pc(row['value'])})" if row.get("clipped") else "")

    def iv(i, display=True):
        if not i or i.get("low") is None:
            return "n/a"
        lo, hi = (i["low_displayed"], i["high_displayed"]) if display and "low_displayed" in i else (i["low"], i["high"])
        return f"{pc(lo)} to {pc(hi)}"

    def yes(b):
        return "n/a" if b is None else ("yes" if b else "no")

    def trend_cells(t):
        if t.get("sen_slope") is None:
            return ["n/a"] * 4
        return [pp(t["sen_slope_per_year"]), f"{pp(t['gilbert95_low_per_year'])} to {pp(t['gilbert95_high_per_year'])}",
                pv(t["p"]), yes(t["significant"])]

    L = ["# Series analyses of record", "",
         "Deviation 13 of `docs/analysis_preregistration.md`; `analysis_03_series.py`. Shares are corrected by adjusted "
         "classify-and-count with the rates of record and clipped to [0, 1] for display; slopes are in percentage "
         "points per year, on the values before clipping. Exploratory figures are labelled (Family C).", ""]
    cr = r["corpus_runs"]
    L += ["## 1. The corpus runs", "",
          f"- Comments: {cr['comments']:,}; classified relevant at Stage 1: {cr['classified_relevant']:,} "
          f"(Tier 1 {cr['classified_relevant_by_tier']['Tier 1']:,}, Tier 2 {cr['classified_relevant_by_tier']['Tier 2']:,}, "
          f"Tier 3 {cr['classified_relevant_by_tier']['Tier 3']:,}).",
          f"- Population of the series (Tier 1+2 classified relevant): {cr['population_tier_1_and_2_classified_relevant']:,}; "
          f"Stage 2 refusals {cr['stage2_refusals']}; subsystem unclassified {cr['subsystem_unclassified']}; "
          f"validation-only subsystem items {cr['subsystem_validation_only']}.", ""]
    e = r["error_rates"]
    L += ["## 2. Error rates and the temporal calibration check", "",
          f"Rates of record: TPR {p4(e['rates_of_record']['tpr'])}, FPR {p4(e['rates_of_record']['fpr'])} "
          f"(TPR - FPR {p4(e['rates_of_record']['tpr_minus_fpr'])}), reproduced exactly. Item index arrays: "
          f"{'same as the register' if e['item_resamples']['same_as_the_register'] else 'DIFFERENT'}.", "",
          "| Block (both tranches) | TPR | 95% interval | FPR | 95% interval |", "|---|---|---|---|---|"]
    tc = e["block_rates_both_tranches"]
    for b in ("early", "late"):
        x = tc[b]
        L.append(f"| {b} | {p4(x['tpr'])} | {p4(x['tpr_interval95']['low'])} to {p4(x['tpr_interval95']['high'])} | "
                 f"{p4(x['fpr'])} | {p4(x['fpr_interval95']['low'])} to {p4(x['fpr_interval95']['high'])} |")
    for k in ("tpr", "fpr"):
        x = tc[f"{k}_late_minus_early"]
        L.append(f"| late minus early, {k.upper()} | {p4(x['difference'])} | {p4(x['interval95']['low'])} to "
                 f"{p4(x['interval95']['high'])} | | |")
    rule = r["temporal_calibration_check_rule"]
    c = rule["criteria_block_specific_against_primary"] or {}
    L += ["", f"Block-specific against primary: criterion 1 {yes(c.get('criterion1_agreement_of_conclusion'))}, "
              f"criterion 2 {yes(c.get('criterion2_overlap_of_estimate'))}; material: {yes(rule['material'])}. "
              f"Difference in Sen's slope (block-specific minus primary): "
              f"{pp(rule['difference_in_sen_slope_per_year_block_specific_minus_primary'])} points per year, 95% interval "
              f"{pp(rule['difference_interval95_per_year']['low'])} to {pp(rule['difference_interval95_per_year']['high'])} "
              f"({rule['qualification']}).", "", rule["statement"], ""]
    q = r["rq1"]
    ps = q["primary_series"]
    pt = ps["trend"]
    hr = pt.get("hamed_rao", {})
    L += ["## 3. RQ1: the primary series", ""] + [f"- {n}" for n in ps["notes"]] + ["",
          f"Sen's slope {pp(pt.get('sen_slope_per_year'))} points per year (Gilbert 95% interval "
          f"{pp(pt.get('gilbert95_low_per_year'))} to {pp(pt.get('gilbert95_high_per_year'))}); Mann-Kendall "
          f"S = {pt.get('mann_kendall', {}).get('s')}, p = {pv(pt.get('p'))} "
          f"({'significant' if pt.get('significant') else 'not significant'} at 0.05). Hamed-Rao (lag 1): "
          + (f"autocorrelation {p4(hr.get('autocorrelation_lag1'))} (bound {p4(hr.get('bound'))}), p = {pv(hr.get('p'))}"
             if hr.get("computed") and hr.get("computable") else (hr.get("note") or "n/a")) + ".", "",
          "| Quarter | Comments | Retained | ESS | Classified | Corrected | 95% interval |", "|---|---|---|---|---|---|---|"]
    for row in ps["rows"][:TREND_Q]:
        ess = "n/a" if row["effective_sample_size"] is None else f"{row['effective_sample_size']:.1f}"
        L.append(f"| {row['period']} | {row['comments']:,} | {row['retained']:,} | {ess} | "
                 f"{pc(row['classified_share'])} | {shown(row)} | {iv(row['interval95'])} |")
    L += ["", "2025 Q1 and Q2 are shown on the quarterly plot only (R3, Deviation 13).", "",
          "| Year | Corrected | 95% interval |", "|---|---|---|"]
    for row in ps["years"]["rows"]:
        L.append(f"| {row['period']} | {shown(row)} | {iv(row['interval95'])} |")
    L += ["", "### Series beside the primary series", "",
          "| Series | Sen's slope | Gilbert 95% interval | MK p | Significant | Criterion 1 | Criterion 2 |",
          "|---|---|---|---|---|---|---|"]
    for key, name in (("block_specific_series", "Block-specific"), ("companion_series", "Companion"),
                      ("pooled_series", "Pooled (R3)"), ("tier_level_series", "Tier-level"),
                      ("three_class_correction", "Three-class CONCERN (exploratory)")):
        s = q[key]
        crit = (rule["criteria_block_specific_against_primary"] if key == "block_specific_series" else s.get("criteria")) or {}
        L.append(f"| {name} | " + " | ".join(trend_cells(s["trend"])) +
                 f" | {yes(crit.get('criterion1_agreement_of_conclusion'))} | {yes(crit.get('criterion2_overlap_of_estimate'))} |")
    sens = r["sensitivities"]
    for s, name in ((sens["word_floor_25"], "Word floor 25 (exploratory)"),
                    (sens["tier_strata"]["tier1"], "Tier 1 (exploratory)"),
                    (sens["tier_strata"]["tier2"], "Tier 2 (exploratory)")):
        crit = s.get("criteria") or {}
        L.append(f"| {name} | " + " | ".join(trend_cells(s["trend"])) +
                 f" | {yes(crit.get('criterion1_agreement_of_conclusion'))} | {yes(crit.get('criterion2_overlap_of_estimate'))} |")
    L += ["", f"- {q['pooled_series']['statement']}", f"- {q['companion_series']['statement']}",
          f"- {q['three_class_correction']['statement']}", f"- {sens['word_floor_25']['statement']}", ""]
    cp = ps["changepoints"]
    L += ["### Changepoints (Deviation 12)", ""]
    if cp.get("computed"):
        L += ["| Changepoint | Grid values | Every penalty 4-16 | Step better than line (BIC) | Supported | Statement |",
              "|---|---|---|---|---|---|"]
        for x in cp["changepoints"]:
            L.append(f"| {x['quarter']} | {', '.join(str(v) for v in x['grid_values'])} | "
                     f"{yes(x['returned_at_every_penalty_4_to_16'])} | {yes(x['step_better_than_line_by_bic'])} | "
                     f"{yes(x['supported'] and x.get('keeps_the_label', True))} | {x['statement']} |")
        L += [""] + [f"- {x['quarter']}: {x['note']}" for x in cp["changepoints"] if x.get("note")] + ["", cp["statement"], ""]
    else:
        L += [cp.get("note", "not computed"), ""]
    g = ps["glm"]
    L += [f"GLM (exploratory): year odds ratio {g['year_odds_ratio']:.4f} (Wald 95% interval "
          f"{g['year_odds_ratio_wald95_low']:.4f} to {g['year_odds_ratio_wald95_high']:.4f}), {g['comments']:,} comments in "
          f"{g['threads']:,} threads; classified labels, not corrected.", ""]
    t4 = r["thread_size_R4"]
    L += ["## 4. Thread-size composition (R4)", "",
          f"- C = {pp(t4['C'])} points, T = {pp(t4['T'])} points (eight times Sen's slope, 2016-2024, classified shares); "
          f"|C| = {pa(t4['abs_C'])}, 0.20 x |T| = {pa(t4['0.20_x_abs_T'])}, 0.50 x |T| = {pa(t4['0.50_x_abs_T'])}.",
          f"- C / T = {p4(t4['C_over_T'])}; the ratio a common straight-line trend would produce: "
          f"{p4(t4['ratio_a_common_trend_would_produce'])}.",
          f"- Outcome: {t4['outcome']}.",
          (f"- |C| / (TPR - FPR) = {pa(t4['abs_C_corrected_scale'])} points of corrected share." if
           t4["outcome"].startswith("not applied") else
           f"- T - C = {pp(t4['T_minus_C'])} points ({pp(t4['T_minus_C_corrected_scale'])} on the corrected scale)."
           if t4["outcome"].startswith("material") else "- T - C: not needed under this outcome (in the results file)."),
          f"- Comments: {t4['comments']['joined']:,} joined of {t4['comments']['retained_2016_2024']:,} retained in 2016-2024; "
          f"left out: " + ", ".join(f"{k} {v:,}" for k, v in t4["comments"]["left_out_by_status"].items()) + ".",
          f"- Size-stratified series (corrected): trend {pp(t4['size_stratified_series']['trend_8_x_sen_slope'])} points "
          f"over the span, exact p = {pv(t4['size_stratified_series']['trend'].get('p'))}.", ""]
    se = sens["seasonality"]
    mo = se["month_of_year_decomposition"]
    L += ["## 5. Sensitivity analyses (Family C, exploratory)", "",
          f"- Seasonality: mean January-June minus July-December, 2016-2024: "
          f"{pp(se['mean_H1_minus_H2_2016_2024']['value'])} points (95% interval "
          f"{pp(se['mean_H1_minus_H2_2016_2024']['interval95']['low'])} to "
          f"{pp(se['mean_H1_minus_H2_2016_2024']['interval95']['high'])}).",
          f"- Month-of-year decomposition: C_m = {pp(mo['C_m'])} points, T = {pp(mo['T'])} points; 0.20 x |T| = "
          f"{pa(mo['0.20_x_abs_T'])}; C_m / T = {p4(mo['C_m_over_T'])}; ratio of a common trend "
          f"{p4(mo['ratio_a_common_trend_would_produce'])}. Outcome: {mo['outcome']}"
          + (f"; |C_m| / (TPR - FPR) = {pa(mo['abs_C_m_corrected_scale'])} points of corrected share." if
             mo["outcome"].startswith("not applied") else
             f"; T - C_m = {pp(mo['T_minus_C_m'])} points ({pp(mo['T_minus_C_m_corrected_scale'])} corrected)."
             if "material limitation" in mo["outcome"] else "."),
          f"- Word floor 25: {sens['word_floor_25']['statement']}", ""]
    re_ = r["relevance_error_series"]
    L += ["## 6. Relevance error (no interval)", "",
          f"Low series: Sen's slope {pp(re_['low_sen_slope'].get('sen_slope_per_year'))} points per year; high series: "
          f"{pp(re_['high_sen_slope'].get('sen_slope_per_year'))}. Wrongly included items classified CONCERN: "
          f"{re_['wrongly_included_classified_concern_by_stage2']['k']} of "
          f"{re_['wrongly_included_classified_concern_by_stage2']['n']}; wrongly left out items gold CONCERN: "
          f"{re_['wrongly_left_out_gold_concern']['k']} of {re_['wrongly_left_out_gold_concern']['n']}.", ""]
    q2 = r["rq2"]
    L += ["## 7. RQ2 (Deviations 9 and 13)", "",
          f"Concern share C over 2016-2024 (corrected): {shown(q2['concern_share_C_2016_2024'])}. "
          f"{q2['temporal_condition']}", "",
          "| Value | Median quarterly | Median annual | Reported as | pi_s 2016-2024 | C_s | E_s | Family A p (Holm) |",
          "|---|---|---|---|---|---|---|---|"]
    for s, x in q2["values"].items():
        o = x.get("over_2016_2024")
        fa = x.get("family_A_test") or {}
        cells = [shown(o["pi_s"]), shown(o["C_s"]), p4(o["E_s"]["value"])] if o else ["counts", "counts", "counts"]
        test = f"{pv(fa.get('p'))} ({pv(fa.get('holm_adjusted_p'))})" if fa else "n/a"
        L.append(f"| {s} | {x['sparsity']['median_quarterly_count']:g} | {x['sparsity']['median_annual_count']:g} | "
                 f"{x['sparsity']['reported_as']} | {' | '.join(cells)} | {test} |")
    v = r["subsystem_classifier_validation"]
    b = v["both tranches, all items"]
    L += ["", "## 8. Subsystem classifier against the gold subsystems", "",
          f"Items with a gold primary subsystem: {v['items_with_a_gold_subsystem']} (relevant items without one: "
          f"{v['relevant_items_without_a_gold_subsystem']}). Overall agreement, both tranches: "
          f"{b['overall_agreement']['k']} of {b['overall_agreement']['n']} ({pc(b['overall_agreement']['share'])}, Wilson "
          f"{pc(b['overall_agreement']['wilson95_low'])} to {pc(b['overall_agreement']['wilson95_high'])}).", "",
          "| Value | Recall | Precision |", "|---|---|---|"]
    for s, x in b["by_value"].items():
        L.append(f"| {s} | {x['recall']['k']}/{x['recall']['n']} | {x['precision']['k']}/{x['precision']['n']} |")
    s2 = r["stage2_runs_compared_on_the_tranche_items"]
    L += ["", "## 9. The two Stage 2 runs on the tranche items", "",
          f"Items both runs cover: {s2['items_both_runs_cover']}; same label: {s2['same_label']['k']} "
          f"({pc(s2['same_label']['share'])}).", ""]
    t3 = r["tier3"]
    L += ["## 10. Tier 3 (descriptive)", "",
          f"Tier 3 supplies {t3['tier3_classified_relevant']:,} of the comments classified relevant "
          f"({pc(t3['share_of_all_comments_classified_relevant']['share'])}).", ""]
    st = r["stage1_shares"]
    cs = st["corpus_share_classified_relevant"]
    L += ["## 11. Stage 1 shares (added after the counts were seen; description)", "",
          f"Corpus, Tier 1+2: {cs['tier_1_and_2']['k']:,} of {cs['tier_1_and_2']['n']:,} ({pc(cs['tier_1_and_2']['share'])}); "
          f"frame comments: {pc(cs['frame_comments']['overall']['share'])}. Annotated sample (design-weighted): "
          f"cross-validated predictions "
          f"{pc(st['sample_design_weighted']['classified_relevant_by_the_cross_validated_prediction']['overall']['estimate'])}"
          f", gold {pc(st['sample_design_weighted']['gold_relevance_rate']['overall']['estimate'])}.", ""]
    rw = r["reweighting"]
    L += ["## 12. Reweighting", "",
          f"Left out (subreddit-years with fewer than ten comments): {rw['left_out_comments']['2016-2024']} comments in "
          f"2016-2024, {rw['left_out_comments']['2025']} in 2025. Largest weight: "
          + (f"{rw['largest_weight']['weight']:.3f} (r/{rw['largest_weight']['subreddit']}, {rw['largest_weight']['year']})"
             if rw["largest_weight"] else "n/a") + ". Companion subreddits: "
          + ", ".join(rw["companion_subreddits_retained_in_every_year_2016_2024"]) + ".", ""]
    return "\n".join(L) + "\n"


# =============================================================================
# outputs
# =============================================================================
TIER3_COLUMNS = ["id", "subreddit", "created_utc", "year", "thread", "words", "text"]


def library_versions() -> dict:
    v = mc.versions("numpy", "pandas", "scipy", "sklearn", "pyarrow")
    v.update({n: package_version(n) for n in LIBRARIES})
    return v


def write_outputs(results: dict, extra: dict, me: str, out_dir: Path, inputs: dict, scripts: dict) -> None:
    """Written to a fresh work folder, then moved into place with series_results.json last: a run that fails part-way
    leaves no results file, so it can simply be run again (it gives the same bytes)."""
    clean = rounded(results)
    report = render_report(results)
    figures = make_figures(results)
    work = OUT_ROOT / f"in_progress_{os.getpid()}_{time.time_ns()}"
    (work / "figures").mkdir(parents=True)
    try:
        mc.write_json(work / "series_results.json", clean)
        with open(work / "series_report.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
        outputs = {"series_results.json": mc.sha256_file(work / "series_results.json"),
                   "series_report.md": mc.sha256_file(work / "series_report.md"),
                   "series_values.csv": mc.write_rows_csv(work / "series_values.csv", VALUE_COLUMNS, value_rows(results)),
                   "tier3_relevant_comments.csv": mc.write_rows_csv(work / "tier3_relevant_comments.csv", TIER3_COLUMNS,
                                                                    extra["tier3_rows"])}
        for name, blob in sorted(figures.items()):
            with open(work / "figures" / name, "wb") as f:
                f.write(blob)
            outputs[f"figures/{name}"] = hashlib.sha256(blob).hexdigest()
        created = mc.now_iso()
        versions = library_versions()
        mc.write_json(work / "series_manifest.json", {
            "created": created, "script": {"file": SCRIPT, "sha256_lf": me}, "scripts_of_record_sha256_lf": scripts,
            "inputs_sha256": inputs, "outputs_sha256": outputs, "versions": versions})
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "figures").mkdir(exist_ok=True)
        for name in sorted(figures):
            mc.replace_patiently(work / "figures" / name, out_dir / "figures" / name)
        for name in ("tier3_relevant_comments.csv", "series_values.csv", "series_report.md", "series_manifest.json",
                     "series_results.json"):
            mc.replace_patiently(work / name, out_dir / name)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rel = out_dir.relative_to(cfg.REPO).as_posix()
    ci = clean["comment_resamples"]
    v = versions
    man_sha = mc.sha256_file(out_dir / "series_manifest.json")
    mc.show_register_block(out_dir / "PASTE_series_block.txt", [
        f"- `{SCRIPT}` (SHA-256 `{me}`) run {created} with `--confirm-committed`: every input matched its SHA-256 of "
        f"record (the inputs of the sample analyses, checked by `analysis_01_sample.py`; corpus v2.2; "
        f"`stage1_corpus_predictions.csv`, `stage2_predictions.csv` and `subsystem_predictions.csv`; `thread_sizes.csv`); "
        f"the rates of record were reproduced and the item index arrays matched `{ITEM_ARRAYS_SHA256}`.",
        f"- Comment index arrays (`numpy.random.default_rng([24916660, 3, 2])`, {N_RESAMPLES:,} resamples, "
        f"{len(QUARTERS)} quarters, {sum(x['threads'] for x in ci['threads_by_quarter'].values()):,} thread draws per "
        f"resample): SHA-256 `{ci['index_arrays_sha256']}`.",
        f"- Outputs, in `{rel}/` (not committed): `series_results.json` SHA-256 `{outputs['series_results.json']}`; "
        f"`series_report.md` `{outputs['series_report.md']}`; `series_values.csv` `{outputs['series_values.csv']}`; "
        f"{len(figures)} figure files, with their SHA-256 in `series_manifest.json` `{man_sha}`; "
        f"`tier3_relevant_comments.csv` `{outputs['tier3_relevant_comments.csv']}` (comment text for the author's "
        f"reading; not committed). Python {v['python']}, NumPy {v['numpy']}, pandas {v['pandas']}, SciPy {v['scipy']}, "
        f"scikit-learn {v['sklearn']}, pymannkendall {v['pymannkendall']}, ruptures {v['ruptures']}, statsmodels "
        f"{v['statsmodels']}, matplotlib {v['matplotlib']}.",
    ])
    print(f"\nwritten: {out_dir}")


# =============================================================================
# main
# =============================================================================
def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Series analyses of record (Deviation 13).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks and a dry run; writes nothing")
    mode.add_argument("--confirm-committed", action="store_true", help="the run of record (after the commit)")
    args = ap.parse_args()
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit) or --confirm-committed (after the commit: the run of record)")
    started = time.time()
    print("Series analyses (Deviation 13): " + ("preflight, before the commit\n" if args.preflight else "the run of record\n"))
    me = own_sha256()
    out_dir = run_folder(me)
    print(f"this script: {SCRIPT} SHA-256 {me}")
    if (out_dir / "series_results.json").exists():
        stop(f"this script's series analyses have already been run: their results are in {out_dir}. They are run once.")
    scripts = check_modules()
    libs = check_libraries()
    print(f"modules: the five imported modules are the files in the repository at 1397cc9; libraries: "
          f"{', '.join(f'{n} {v}' for n, v in libs.items())}")
    loaded = sample.load_all()
    data = loaded["data"]
    print("inputs of the sample analyses: every input with a recorded SHA-256 matches it (checked by "
          "analysis_01_sample.py)")
    item = item_side(data)
    print(f"error rates: the rates of record are reproduced; the item index arrays match the register "
          f"({ITEM_ARRAYS_SHA256[:16]}...)")
    corpus, cinfo = load_corpus()
    runs = load_runs(corpus, data)
    sizes, sizes_sha = load_thread_sizes(corpus)
    frame = load_frame_ids()
    D = assemble(corpus, runs, sizes, frame, data)
    print(f"corpus runs: corpus v2.2 matches R5 and its file SHA-256 of record; the three prediction files and "
          f"thread_sizes.csv match their SHA-256 of record and cover the comments of their runs "
          f"({int(D['pop'].sum()):,} Tier 1+2 comments classified relevant; {len(runs['validation_only'])} tranche items "
          f"for validation only)")
    inputs = {**{f"{k} (checked by analysis_01_sample.py)": v for k, v in loaded["shas"].items()},
              "corpus.parquet": cinfo["file_sha256"], **runs["shas"], "thread_sizes.csv": sizes_sha}
    if args.preflight:
        dry = dry_run_labels(D, data)
        res, extra = analyse(data, dry, item, DRY_RUN_GENERATORS["comments"], dry=True)
        rounded(res)
        render_report(res)
        make_figures(res)
        value_rows(res)
        print(f"dry run: every analysis ran on the real comments with the labels of the three runs replaced by made-up "
              f"labels drawn at random (rule 17); its report and figures were rendered in memory; the result was "
              f"discarded and nothing was shown ({time.time() - started:.0f} seconds)")
        print("\nPREFLIGHT PASSED: every input matches the record and every analysis can be computed. No label of a "
              "corpus run entered any figure, and no output was written.")
        return
    res, extra = analyse(data, D, item, COMMENT_GENERATOR)
    results = {"specification": "R3, R4, R5 and Deviations 9 to 14 of docs/analysis_preregistration.md; "
                                "analysis_03_series.py", **res,
               "inputs_sha256": inputs, "scripts_of_record_sha256_lf": scripts, "corpus": cinfo}
    write_outputs(results, extra, me, out_dir, inputs, scripts)
    print(f"({time.time() - started:.0f} seconds)")


if __name__ == "__main__":
    main()
