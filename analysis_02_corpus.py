"""Corpus description of record (on the PC): the figures that Deviation 13 of docs/analysis_preregistration.md
regenerates from corpus v2.2 "by a committed script" (year totals, composition by year, thread counts, the
preprocessing funnel, the lexical proxy, the reweighting cell sizes and the within-year sampling position), with
`commentsCount` "joined from the raw post records by the same script" for the thread-size composition of R4.

From the repository folder, with the virtual environment active (no GPU, no internet):
    python analysis_02_corpus.py --preflight
        Before the commit. Checks every input against the record, computes every figure once and discards it
        unseen (so that the code is exercised on the real inputs), and compares the previews named below with what
        it computes, printing "same" or the computed values. It writes nothing.
    python analysis_02_corpus.py --confirm-committed
        After this file is committed and its SHA-256 recorded. The run of record. It runs once: it refuses to start
        if this file's results already exist (the SHA-256 is that of the file with LF line endings, as the register
        records script hashes).

It reads no output of a corpus run: nothing in data/models/ is opened. Its inputs are corpus v2.2
(data/clean_v2_2/corpus.parquet), the preprocessing funnel written with it (data/clean_v2_2/preprocess_funnel.csv),
the top-level raw files that 02_preprocess.py reads (data/raw/*.json, the same non-recursive glob), the collection
log (data/raw/scrape_log.csv), and config.py as committed at be001c7 (the study window and post caps, and the term
list of the lexical proxy). Every figure is computed from the corpus or the raw files alone, so none is formed from a
classifier output.

What it computes
  1. Corpus: rows, membership and counts checked against R5; the file's SHA-256 against the record; the date range.
  2. Year totals, all tiers and each tier, and the ratio of the 2025 monthly rate to the 2024 monthly rate.
  3. Composition by year: comments by subreddit and year; each subreddit's share of the Tier 1+2 comments of each
     year; Tier 1's share of all comments by year; each subreddit's first and last comment and missing study years.
  4. Thread structure of corpus v2.2: threads (parsedPostId), by tier; threads spanning two tiers or two
     subreddits; comments per thread; and the raw union of check_final_corpus.py (each raw comment id once, in the
     thread of its first retrieval): the most unique comments in one thread and the threads with more than 15.
  5. Thread size (R4): commentsCount joined from the raw post records to each comment's thread, the largest reported
     count where a thread has more than one post record; the comments left out because their thread has no post
     record, no reported count or a reported count of zero, counted; comments and threads by bucket, and comments by
     bucket and year (Tier 1+2). The joined value of every comment is written to thread_sizes.csv for the
     series-analysis script.
  6. Capture against Reddit-reported thread size, by the method of check_capture_rate.py (which produced the figures
     of docs/corpus_manifest.md): per sampled thread with a post record, captured = unique raw comment ids, effective
     denominator = max(commentsCount, captured); overall and by bucket; the threads where captured exceeds
     commentsCount and the [deleted] and [removed] comments on them; the reconciliation with the corpus threads.
  7. The preprocessing funnel of corpus v2.2, as written by 02_preprocess.py, its first three stages recomputed from
     the raw files and its last stage checked against the corpus.
  8. The lexical proxy (Deviations 13 and 14) over corpus v2.2: by tier, by subreddit, by subreddit and era, by era
     and by year; the composition check of Deviation 8 applied to the Tier 1+2 era rates (seven groups and two
     groups, exploratory); threads with at least one matching comment, by tier; and the rate by reply depth (Tier 1+2).
  9. The reweighting cell sizes of R3 on the Tier 1+2 comments: subreddit-quarter and subreddit-year cells over the
     full span (2016 Q1 to 2025 Q2) and the trend span (2016 Q1 to 2024 Q4).
 10. The within-year sampling position, by the method of check_c2_audit.py (which produced the figures of the
     corpus manifest): positions of the year-blocked posts in their year, before C2 (annual blocks), after C2
     (deduplicated, primary) and after C2 with overlaps kept (sensitivity), with the slope over 2016-2024, its shift
     across the span, and the yield by year; the checks of that script that need no job list (the number of
     supplementary blocks, one block for each year 2016-2024 in every supplementary group, the supplementary post
     cap, every post inside its window, and the supplementary items against the collection log); and the log's totals.
 11. The previews named in PREVIEWS, compared with what this script computes ("same", or the computed values).

Rules fixed with this file (where the committed text is silent, or to say how a committed rule is applied)
  1. Inputs. Corpus v2.2 must match R5 (membership SHA-256, rows, counts by subreddit and by tier) and the file SHA-256
     recorded on 14 October 2026; every comment must have a creation time in the study window, a year equal to its
     UTC calendar year, a thread id and at least 20 words; a reply depth, where a comment has one, must be a whole
     number of at least zero (a comment without one is left out of the rate by depth and counted). The raw files must
     number 694 and reproduce the first three stages of the funnel (items, comments, unique comment ids); every corpus
     comment must be a raw comment whose first retrieval names the same thread. Any departure stops the script.
  2. Thread size (R4) as Deviation 13 states it. A post record's commentsCount is a reported count when it is a whole
     number of at least zero; a missing or empty value is no reported count; any other value stops the script. A
     thread's count is the largest reported count among its post records. Buckets: 1-5, 6-15, 16-50, 51-200,
     201-1000 and more than 1,000. Comments are matched to post records by thread id (comment parsedPostId, post
     parsedId).
  3. Capture (figure 6) follows check_capture_rate.py exactly, including its treatment of a missing commentsCount as
     zero and its bucket for zero; it is description and enters no analysis.
  4. The lexical proxy is analysis_01_sample.py's (Deviation 14's patterns, config.py at be001c7), on clean_body.
     Shares carry Wilson 95% intervals on the unweighted counts, as description of the corpus. The composition check
     is analysis_01_sample.decomposition on the Tier 1+2 comments, with each era's number of Tier 1+2 comments as
     S_e, so that the standardised era rates use the pooled mix of the three eras.
  5. Cells (R3): quarters and years in UTC; the eight Tier 1+2 subreddits; a cell is empty when it holds no comment;
     the median and the share below ten are over the non-empty cells.
  6. Within-year position follows check_c2_audit.py exactly (its file classification, its positions, its
     deduplication, its regression over the year means of 2016-2024, its quarterly shares and its yield table). The
     shift across the span is eight times the slope (the eight intervals between the nine year-points), in years and
     in days of 365.25.
  7. A preview is "same" when the computed value, formatted at the precision the preview was recorded with, equals
     it. A preview that differs is reported with its computed value and recorded in the register; the computed
     value stands (Deviation 13). The results file gives values rounded to six decimals beside their counts; the
     report formats every share from its exact counts and every other figure from its unrounded value, so that no
     figure is rounded twice.

Writes, in data/analysis/corpus/run_<first 12 hex digits of this file's SHA-256>/ (data/ is not committed):
  corpus_results.json       every figure (no timestamp: a rerun on the same inputs gives the same bytes)
  corpus_report.md          the main figures, as tables
  thread_sizes.csv          each comment's thread, joined commentsCount, bucket and status (for the series analysis)
  corpus_manifest.json      time, versions, and the SHA-256 of every input file and of the files above
  PASTE_corpus_block.txt    the register lines (hashes only)
After the run, corpus_results.json and corpus_report.md are copied to results/ and committed with the register
lines, so that every figure is in a results file committed to the repository (Deviation 13).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import shutil
import time
from collections import Counter, defaultdict
from fractions import Fraction
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
REPORT = "Report this message before going further."
MODULES_OF_RECORD = {                             # SHA-256 with LF line endings: the files at 6d5e400 (= 8d9c0d1)
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
    "models_05_evaluate.py": "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734",
    "analysis_01_sample.py": "95f7a48c7509c58eca11330814be32fef0a8c1e430447790fdccfa5da6fdd952",
}
OUT_ROOT = cfg.REPO / "data" / "analysis" / "corpus"
CORPUS = sample.CORPUS                            # data/clean_v2_2/corpus.parquet
CORPUS_FILE_SHA256 = "958f480ec13d469dbf285714e2601e5035cf05e10126a7f9b598e32e4b33b39d"   # register, 14 October 2026
FUNNEL = cfg.REPO / "data" / "clean_v2_2" / "preprocess_funnel.csv"
FUNNEL_FIRST = ["raw items", "comments", "after dedup"]          # recomputed from the raw files
FUNNEL_LAST = "after English filter"                             # must equal the corpus rows
RAW_DIR = cfg.REPO / "data" / "raw"               # config.py RAW_DIR; 02_preprocess.py reads data/raw/*.json
RAW_FILES = 694                                   # R5 (reproducibility); docs/corpus_manifest.md
SCRAPE_LOG = RAW_DIR / "scrape_log.csv"           # config.py LOG_CSV
LOG_COLUMNS = ["timestamp", "tier", "subreddit", "term", "start", "end", "blocked", "items", "comments", "est_usd"]
CONFIG_CONSTANTS = {"STUDY_START": "2016-01-01", "STUDY_END": "2025-04-30",    # config.py at be001c7
                    "MAX_POSTS_PER_BLOCK": 3, "MAX_POSTS_PER_SUPP_BLOCK": 2}
STUDY_START = CONFIG_CONSTANTS["STUDY_START"]
STUDY_END = CONFIG_CONSTANTS["STUDY_END"]
WINDOW = (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2025-05-01", tz="UTC"))  # 02_preprocess.py, end exclusive
WORD_FLOOR = 20                                   # 02_preprocess.py

TIER12 = ("Tier 1", "Tier 2")
TIERS = ("Tier 1", "Tier 2", "Tier 3")
YEARS = list(range(2016, 2026))
SUBREDDITS10 = list(sample.R5_SUBREDDIT_COUNTS)   # the eight Tier 1+2 subreddits, then privacy and cybersecurity
SUBREDDITS8 = list(sample.SUBREDDITS)
ERA_ORDER = list(sample.ERA_ORDER)
SIZE_BUCKETS = [("1-5", 1, 5), ("6-15", 6, 15), ("16-50", 16, 50), ("51-200", 51, 200), ("201-1000", 201, 1000),
                ("1000+", 1001, None)]           # R4 (docs/corpus_manifest.md); "1000+" is more than 1,000
SIZE_NAMES = [b[0] for b in SIZE_BUCKETS]
CAPTURE_EDGES = [-1, 0, 5, 15, 50, 200, 1000, 10 ** 9]          # check_capture_rate.py
CAPTURE_NAMES = ["0", "1-5", "6-15", "16-50", "51-200", "201-1000", "1000+"]
DEPTH_NAMES = ["0", "1", "2", "3", "4", "5", "6", "7 or more"]
SPANS = {"full span, 2016 Q1 to 2025 Q2": ((2016, 1), (2025, 2)),
         "trend span, 2016 Q1 to 2024 Q4": ((2016, 1), (2024, 4))}   # R3
TREND_SPAN = "trend span, 2016 Q1 to 2024 Q4"
YEAR_START_RE = re.compile(r"^(\d{4})-01-01$")   # check_c2_audit.py
SPAN_INTERVALS = 8                                # 2016-2024: nine year-points, eight intervals
C2_SUPP_FILES, C2_GROUPS, C2_BLOCKS = 297, 33, 9  # docs/corpus_manifest.md
EXPLORATORY = sample.EXPLORATORY

# Previews: figures recorded before this script on the same corpus or the same raw files, compared with what it
# computes (rule 7). Figures recorded on corpus v1 or v2, or with another term list, are not previews of these.
PREVIEWS = {
    "corpus v2.2 (R5)": {
        "date range": "2016-01-04 to 2025-04-30", "after the author-based bot filter": "22165",
        "removed by the content-based filter": "7", "wrapper stripping: rows modified / below the word floor": "79/7",
        "removed as relay duplicates": "22", "rows masked": "61"},
    "thread caps (docs/corpus_manifest.md; design document 7.10e)": {
        "raw union: most unique comments in one thread": "16", "raw union: threads with more than 15": "1",
        "corpus v2.2: threads with more than 15": "0"},
    "reweighting cells, trend span (R3)": {
        "subreddit-quarter cells, non-empty": "258", "subreddit-quarter cells, median": "34",
        "subreddit-quarter cells, below ten (%)": "10.9", "subreddit-quarter cells, empty": "30",
        "subreddit-year cells, non-empty": "69", "subreddit-year cells, median": "143",
        "subreddit-year cells, below ten (%)": "7"},
    "reweighting cells, full span (design document 7.10d)": {
        "comments": "12212", "subreddit-quarter cells, non-empty": "274", "subreddit-quarter cells, median": "35",
        "subreddit-quarter cells, below ten (%)": "10.9", "subreddit-quarter cells, empty": "30",
        "subreddit-year cells, non-empty": "77", "subreddit-year cells, median": "139",
        "subreddit-year cells, below ten (%)": "6"},
    "coverage (design document 7.1 and 7.10c)": {
        "realtesla missing study years": "2016", "cybersecurity missing study years": "2016,2017",
        "waymo missing study years": "2016,2017", "waymo comments 2021/2022/2023": "6/2/5",
        "waymo share of its comments in 2024-2025 (%)": "89.6",
        "Tier 1 share of all comments by year (%)": "44.1/44.6/55.4/65.2/50.0/48.4/41.7/39.8/53.2/72.3"},
    "capture (docs/corpus_manifest.md)": {
        "threads": "2237", "reported total": "250781", "effective denominator": "250909",
        "captured": "23534", "original rate (%)": "9.384", "corrected rate (%)": "9.379",
        "threads where captured exceeds commentsCount": "95", "of all threads (%)": "4.2", "total excess": "128",
        "largest excess": "4", "[deleted] on those threads": "133", "[removed] on those threads": "13",
        "threads whose excess deleted and removed cover": "95", "excess not covered": "0",
        "by bucket: threads": "191/414/360/474/525/234/39",
        "by bucket: reported": "0/1066/3496/14548/54519/91707/85445",
        "by bucket: effective": "0/1096/3594/14548/54519/91707/85445",
        "by bucket: captured": "0/1006/3469/7089/7875/3510/585",
        "by bucket: rate (%)": "n/a/91.8/96.5/48.7/14.4/3.8/0.7"},
    "within-year sampling position (docs/corpus_manifest.md, design document 7.4)": {
        "before C2: posts": "738", "before C2: mean position": "0.73", "before C2: quarterly shares (%)": "10/11/16/63",
        "before C2: slope per year": "+0.0256", "before C2: p": "0.0075",
        "after C2: mean position": "0.62", "after C2: quarterly shares (%)": "13/32/11/44",
        "after C2: slope per year": "+0.0133", "after C2: p": "0.0209",
        "overlaps kept: slope per year": "+0.0190", "overlaps kept: p": "0.0098",
        "duplicate retrievals removed / retrievals": "143/1205",
        "H1 share across years, lowest/highest (%)": "37/40",
        "shift across the span (years)": "0.10", "shift across the span (days)": "37"},
    "collection log (docs/corpus_manifest.md)": {
        "log rows": "750", "logged spend (USD)": "80.25", "supplementary files": "297",
        "supplementary posts / comments / items": "467/5600/6067", "supplementary spend (USD)": "18.07"},
}


# =============================================================================
# helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


fl = sample.fl
strip = sample.strip


def wilson(k: int, n: int) -> dict:
    """analysis_01_sample.wilson (rounded to six decimals for the results file), with the share as a fraction and the
    unrounded limits kept for the report (keys beginning with _ are not written to the results file)."""
    out = sample.wilson(int(k), int(n))
    if n:
        phat = k / n
        den = 1 + ev.Z95 ** 2 / n
        centre = (phat + ev.Z95 ** 2 / (2 * n)) / den
        half = ev.Z95 * math.sqrt(phat * (1 - phat) / n + ev.Z95 ** 2 / (4 * n * n)) / den
        out.update({"_share": Fraction(int(k), int(n)), "_low": centre - half, "_high": centre + half})
    else:
        out.update({"_share": None, "_low": None, "_high": None})
    return out


def text_file_sha256(path: Path) -> str:
    return ev.text_sha256(Path(path))


def own_sha256() -> str:
    return text_file_sha256(Path(__file__).resolve())


def share(k: int, n: int) -> float | None:
    return fl(Fraction(int(k), int(n))) if n else None


def pct_text(k: int, n: int, digits: int) -> str:
    if not n:
        return "n/a"
    return f"{float(Fraction(int(k), int(n)) * 100):.{digits}f}"


def run_folder(me: str) -> Path:
    return OUT_ROOT / f"run_{me[:12]}"


def subreddit_key(s) -> str:
    return re.sub(r"^/?r/", "", str(s).strip()).lower()


def size_bucket(n: int) -> str:
    for name, low, high in SIZE_BUCKETS:
        if n >= low and (high is None or n <= high):
            return name
    stop(f"no thread-size bucket for {n}")


def reported_count(value, where: str):
    """Rule 2: a whole number of at least zero is a reported count; a missing or empty value is none."""
    if value is None or (isinstance(value, str) and value.strip() == ""):
        return None
    if isinstance(value, bool):
        stop(f"a post record in {where} has commentsCount {value!r}, which is not a count. {REPORT}")
    if isinstance(value, int) and value >= 0:
        return value
    if isinstance(value, float) and value.is_integer() and value >= 0:
        return int(value)
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    stop(f"a post record in {where} has commentsCount {value!r}, which is not a whole number of at least zero. "
         f"{REPORT}")


# =============================================================================
# inputs (rule 1)
# =============================================================================
def check_modules() -> dict:
    out = {}
    for module in (cfg, mc, prep, ev, sample):
        path = Path(module.__file__).resolve()
        want = MODULES_OF_RECORD.get(path.name)
        got = text_file_sha256(path)
        if got != want:
            stop(f"{path.name} is not the file in the repository at 6d5e400 (SHA-256 {got[:16]}..., recorded "
                 f"{(want or 'none')[:16]}...). {REPORT}")
        out[path.name] = got
    return out


def check_config() -> dict:
    """config.py is the file committed at be001c7 (analysis_01_sample checks its SHA-256, its term list and the
    patterns); the constants this script uses are read from it without running it."""
    sample.check_proxy_source()
    path = cfg.REPO / sample.PROXY_SOURCE["file"]
    found = {}
    for node in ast.parse(path.read_text(encoding="utf-8-sig")).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in CONFIG_CONSTANTS:
                    found[target.id] = ast.literal_eval(node.value)
    if found != CONFIG_CONSTANTS:
        stop(f"config.py does not hold the study window and post caps this script uses ({found}). {REPORT}")
    return {"file": "config.py", "commit": sample.PROXY_SOURCE["commit"], "sha256_lf": sample.PROXY_SOURCE["sha256_lf"],
            "constants": CONFIG_CONSTANTS}


def load_corpus() -> tuple[pd.DataFrame, dict]:
    if not CORPUS.exists():
        stop(f"corpus v2.2 not found at {CORPUS}")
    got = mc.sha256_file(CORPUS)
    if got != CORPUS_FILE_SHA256:
        stop(f"corpus.parquet is not the file of record (SHA-256 {got[:16]}..., recorded {CORPUS_FILE_SHA256[:16]}...). "
             f"{REPORT}")
    cols = ["id", "created", "year", "subreddit", "tier", "depth", "parsedPostId", "clean_body"]
    try:
        corpus = pd.read_parquet(CORPUS, columns=cols)
    except Exception as e:                                  # noqa: BLE001 - reported, not handled
        stop(f"corpus v2.2 could not be read with the columns {', '.join(cols)} ({e})")
    corpus["id"] = corpus["id"].astype(str)
    if len(corpus) != sample.CORPUS_ROWS or corpus["id"].duplicated().any() \
            or mc.ids_sha256(corpus["id"]) != sample.CORPUS_MEMBERSHIP_SHA256:
        stop(f"corpus v2.2: the membership does not match R5 (SHA-256 of the sorted ids). {REPORT}")
    corpus["sub"] = corpus["subreddit"].map(subreddit_key)
    corpus["tier"] = corpus["tier"].astype(str)
    if dict(Counter(corpus["sub"])) != sample.R5_SUBREDDIT_COUNTS or \
            dict(Counter(corpus["tier"])) != sample.R5_TIER_COUNTS:
        stop(f"corpus v2.2: the counts by subreddit or by tier differ from R5. {REPORT}")
    created = pd.to_datetime(corpus["created"], utc=True, errors="coerce")
    if created.isna().any() or (created < WINDOW[0]).any() or (created >= WINDOW[1]).any():
        stop(f"corpus v2.2: a comment has no creation time in the study window. {REPORT}")
    year = pd.to_numeric(corpus["year"], errors="coerce")
    if year.isna().any() or (year.astype(int) != created.dt.year).any():
        stop(f"corpus v2.2: a comment's year is not the UTC calendar year of its creation time. {REPORT}")
    thread = corpus["parsedPostId"].astype(object).map(lambda x: "" if pd.isna(x) else str(x).strip())
    if (thread == "").any():
        stop(f"corpus v2.2: {int((thread == '').sum())} comments have no thread id (parsedPostId). {REPORT}")
    depth = pd.to_numeric(corpus["depth"], errors="coerce")
    given = corpus["depth"].notna() & (corpus["depth"].astype(str).str.strip() != "")
    if (given & depth.isna()).any() or (depth < 0).any() or (depth.notna() & (depth != depth.round())).any():
        stop(f"corpus v2.2: a comment's reply depth is not a whole number of at least zero. {REPORT}")
    words = corpus["clean_body"].astype(str).str.split().map(len)
    if (words < WORD_FLOOR).any():
        stop(f"corpus v2.2: a comment has fewer than {WORD_FLOOR} words. {REPORT}")
    tiers = corpus.groupby("sub")["tier"].nunique()
    if (tiers > 1).any():
        stop(f"corpus v2.2: a subreddit is in more than one tier. {REPORT}")
    display = (corpus.groupby("sub")["subreddit"].agg(lambda s: Counter(s.astype(str)).most_common(1)[0][0]))
    df = pd.DataFrame({"id": corpus["id"].values, "created": created.values, "year": year.astype(int).values,
                       "quarter": created.dt.quarter.astype(int).values, "sub": corpus["sub"].values,
                       "tier": corpus["tier"].values, "thread": thread.values, "depth": depth.values,
                       "text": corpus["clean_body"].astype(str).values})
    df["era"] = [sample.era_of_year(int(y)) for y in df["year"]]
    df = df.sort_values("id").reset_index(drop=True)
    info = {"rows": sample.CORPUS_ROWS, "membership_sha256": sample.CORPUS_MEMBERSHIP_SHA256,
            "file_sha256": got, "counts_by_subreddit_and_tier": "as in R5",
            "subreddit_display_names": {k: display[k] for k in SUBREDDITS10},
            "tier_of_subreddit": {k: str(corpus.loc[corpus["sub"] == k, "tier"].iloc[0]) for k in SUBREDDITS10}}
    return df, info


def load_funnel() -> tuple[list[tuple[str, int]], str]:
    if not FUNNEL.exists():
        stop(f"the preprocessing funnel was not found at {FUNNEL} (02_preprocess.py writes it)")
    try:
        f = pd.read_csv(FUNNEL, dtype=str, keep_default_na=False, encoding="utf-8")
    except Exception as e:                                  # noqa: BLE001 - reported, not handled
        stop(f"preprocess_funnel.csv could not be read ({e})")
    if list(f.columns) != ["stage", "items"] or not f["items"].str.fullmatch(r"\d+").all():
        stop(f"preprocess_funnel.csv must have the columns stage,items with whole numbers. {REPORT}")
    rows = [(str(s), int(n)) for s, n in zip(f["stage"], f["items"])]
    if [s for s, _ in rows[:3]] != FUNNEL_FIRST or rows[-1][0] != FUNNEL_LAST:
        stop(f"preprocess_funnel.csv does not begin with {FUNNEL_FIRST} and end with '{FUNNEL_LAST}'. {REPORT}")
    if rows[-1][1] != sample.CORPUS_ROWS:
        stop(f"preprocess_funnel.csv ends at {rows[-1][1]:,} comments; corpus v2.2 holds {sample.CORPUS_ROWS:,}. {REPORT}")
    if any(b[1] > a[1] for a, b in zip(rows, rows[1:])):
        stop(f"preprocess_funnel.csv: a stage holds more items than the one before it. {REPORT}")
    return rows, mc.sha256_file(FUNNEL)


def load_raw() -> dict:
    """Every top-level raw file, read as 02_preprocess.py reads it. Keeps, for each comment retrieval, its id,
    thread and whether its body is [deleted] or [removed]; for each post record, its file, ids, commentsCount and
    creation time. No author field and no text is kept."""
    files = sorted(RAW_DIR.glob("*.json"))
    if len(files) != RAW_FILES:
        stop(f"data/raw/ holds {len(files)} top-level .json files; the record is {RAW_FILES}. {REPORT}")
    shas, per_file, comments, posts = {}, [], [], []
    items = other_case = 0
    for path in files:
        raw = path.read_bytes()
        shas[path.name] = hashlib.sha256(raw).hexdigest()
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            stop(f"{path.name} cannot be read as UTF-8 JSON ({e}). {REPORT}")
        if not isinstance(data, list):
            stop(f"{path.name} is not a JSON list. {REPORT}")
        items += len(data)
        n_posts = n_comments = 0
        for rec in data:
            if not isinstance(rec, dict):
                continue
            kind = rec.get("dataType")
            if kind == "comment":
                n_comments += 1
                body = str(rec.get("body") or "").strip().lower()
                comments.append((rec.get("id"), str(rec.get("parsedPostId") or "").strip(),
                                 "deleted" if body == "[deleted]" else "removed" if body == "[removed]" else ""))
            elif kind == "post":
                n_posts += 1
                posts.append({"file": path.name, "id": rec.get("id"), "parsedId": rec.get("parsedId"),
                              "commentsCount": rec.get("commentsCount"), "createdAt": rec.get("createdAt")})
            elif isinstance(kind, str) and kind.lower() in ("comment", "post"):
                other_case += 1
        per_file.append({"file": path.name, "items": len(data), "posts": n_posts, "comments": n_comments})
    if other_case:
        stop(f"{other_case} raw records name their type in another letter case; 02_preprocess.py and "
             f"check_capture_rate.py would then count them differently. {REPORT}")
    return {"files": per_file, "shas": shas, "manifest_sha256": mc.pairs_sha256(shas), "items": items,
            "comments": comments, "posts": posts}


def reconcile(raw: dict, funnel: list, corpus: pd.DataFrame) -> dict:
    """Rule 1: the raw files reproduce the funnel's first three stages, and every corpus comment is a raw comment
    whose first retrieval names the same thread (02_preprocess.py keeps the first retrieval of each id)."""
    ids = pd.Series([c[0] for c in raw["comments"]], dtype=object)
    unique = int(ids.drop_duplicates(keep="first").shape[0])
    got = {"raw items": raw["items"], "comments": len(raw["comments"]), "after dedup": unique}
    want = dict(funnel[:3])
    if got != want:
        stop(f"the raw files give {got}; preprocess_funnel.csv records {want}. {REPORT}")
    first = {}
    for cid, thread, _ in raw["comments"]:
        if cid is not None and str(cid) not in first:
            first[str(cid)] = thread
    missing = [i for i in corpus["id"] if i not in first]
    if missing:
        stop(f"{len(missing)} corpus comments are not in the raw files. {REPORT}")
    other = int((corpus["thread"].values != np.array([first[i] for i in corpus["id"]], dtype=object)).sum())
    if other:
        stop(f"{other} corpus comments name another thread than their first raw retrieval. {REPORT}")
    return {"raw_items": raw["items"], "raw_comments": len(raw["comments"]), "unique_raw_comment_ids": unique}


def load_log() -> tuple[pd.DataFrame, str]:
    if not SCRAPE_LOG.exists():
        stop(f"scrape_log.csv not found at {SCRAPE_LOG}")
    try:
        log = pd.read_csv(SCRAPE_LOG, dtype=str, keep_default_na=False, encoding="utf-8")
    except Exception as e:                                  # noqa: BLE001 - reported, not handled
        stop(f"scrape_log.csv could not be read ({e})")
    if list(log.columns) != LOG_COLUMNS:
        stop(f"scrape_log.csv must have the ten columns {LOG_COLUMNS}. {REPORT}")
    for c in ("items", "comments"):
        if not log[c].str.fullmatch(r"\d+").all():
            stop(f"scrape_log.csv: the column {c} must hold whole numbers. {REPORT}")
    try:
        usd = log["est_usd"].map(Fraction)
    except (ValueError, ZeroDivisionError):
        stop(f"scrape_log.csv: the column est_usd must hold numbers. {REPORT}")
    out = pd.DataFrame({"start": log["start"].str.strip(), "end": log["end"].str.strip(),
                        "items": log["items"].astype(int), "comments": log["comments"].astype(int), "usd": usd})
    return out, mc.sha256_file(SCRAPE_LOG)


# =============================================================================
# 1-3: corpus, year totals, composition by year
# =============================================================================
def corpus_figures(c: pd.DataFrame, info: dict) -> dict:
    return {**info, "first_comment_date": str(c["created"].min().date()), "last_comment_date": str(c["created"].max().date()),
            "by_tier": {t: int((c["tier"] == t).sum()) for t in TIERS},
            "by_subreddit": {s: int((c["sub"] == s).sum()) for s in SUBREDDITS10},
            "tier_1_and_2": int(c["tier"].isin(TIER12).sum())}


def year_totals(c: pd.DataFrame) -> dict:
    out = {}
    for y in YEARS:
        m = c["year"] == y
        out[str(y)] = {"all": int(m.sum()), "tier_1_and_2": int((m & c["tier"].isin(TIER12)).sum()),
                       **{t: int((m & (c["tier"] == t)).sum()) for t in TIERS}}
    ratio = {}
    for scope, mask in (("all", np.ones(len(c), bool)), ("tier_1_and_2", c["tier"].isin(TIER12).values)):
        n24, n25 = int((mask & (c["year"] == 2024).values).sum()), int((mask & (c["year"] == 2025).values).sum())
        ratio[scope] = {"2024_comments": n24, "2025_comments": n25,
                        "2025_monthly_rate_over_2024_monthly_rate": fl(Fraction(n25, 4) / Fraction(n24, 12)) if n24 else None}
    return {"by_year": out, "monthly_rate_2025_against_2024": ratio,
            "note": "2025 covers January to April (the study window ends on 30 April 2025): four months against twelve"}


def composition_by_year(c: pd.DataFrame) -> dict:
    counts = {s: {str(y): int(((c["sub"] == s) & (c["year"] == y)).sum()) for y in YEARS} for s in SUBREDDITS10}
    t12 = c[c["tier"].isin(TIER12)]
    shares = {}
    for y in YEARS:
        n = int((t12["year"] == y).sum())
        shares[str(y)] = {s: share(((t12["sub"] == s) & (t12["year"] == y)).sum(), n) for s in SUBREDDITS8}
    tier1 = {str(y): {"tier_1": int(((c["tier"] == "Tier 1") & (c["year"] == y)).sum()), "all": int((c["year"] == y).sum()),
                      "share": share(((c["tier"] == "Tier 1") & (c["year"] == y)).sum(), (c["year"] == y).sum())}
             for y in YEARS}
    coverage = {}
    for s in SUBREDDITS10:
        g = c[c["sub"] == s]
        present = sorted(int(y) for y in g["year"].unique())
        coverage[s] = {"comments": int(len(g)), "first": str(g["created"].min().date()), "last": str(g["created"].max().date()),
                       "missing_study_years": [y for y in YEARS if y not in present]}
    w = c[c["sub"] == "waymo"]
    return {"comments_by_subreddit_and_year": counts, "share_of_tier_1_and_2_comments_by_year": shares,
            "tier_1_share_of_all_comments_by_year": tier1, "subreddit_coverage": coverage,
            "waymo_comments_in_2024_2025": {"k": int(w["year"].isin([2024, 2025]).sum()), "n": int(len(w)),
                                            "share": share(w["year"].isin([2024, 2025]).sum(), len(w))}}


# =============================================================================
# 4-6: threads, thread size (R4), capture
# =============================================================================
def thread_structure(c: pd.DataFrame) -> dict:
    per = c.groupby("thread").size()
    dist = Counter(int(v) for v in per.values)
    by_tier = {t: int(c.loc[c["tier"] == t, "thread"].nunique()) for t in TIERS}
    return {"threads": int(per.shape[0]), "threads_by_tier": by_tier,
            "threads_tier_1_and_2": int(c.loc[c["tier"].isin(TIER12), "thread"].nunique()),
            "threads_in_more_than_one_tier": int((c.groupby("thread")["tier"].nunique() > 1).sum()),
            "threads_in_more_than_one_subreddit": int((c.groupby("thread")["sub"].nunique() > 1).sum()),
            "comments_per_thread": {"mean": fl(Fraction(int(per.sum()), int(per.shape[0]))), "median": fl(float(np.median(per.values))),
                                    "largest": int(per.max()),
                                    "threads_by_number_of_comments": {str(k): dist.get(k, 0) for k in range(1, max(16, int(per.max()) + 1))},
                                    "threads_with_more_than_15": int((per > 15).sum())}}


def raw_union(raw: dict) -> dict:
    """Unique raw comment ids per thread, as check_final_corpus.py counted them for the corpus manifest: each non-empty
    id kept at its first retrieval, grouped by its non-empty thread id."""
    seen, per = set(), Counter()
    for cid, thread, _ in raw["comments"]:
        cid = str(cid or "").strip()
        if not cid or cid in seen:
            continue
        seen.add(cid)
        if thread:
            per[thread] += 1
    return {"threads": len(per), "most_unique_comments_in_one_thread": max(per.values()) if per else 0,
            "threads_with_more_than_15": sum(1 for v in per.values() if v > 15)}


def thread_counts(raw: dict) -> tuple[dict, dict]:
    """Rule 2: each thread's largest reported commentsCount over its post records (None when none reports one)."""
    values = defaultdict(list)
    for p in raw["posts"]:
        pid = str(p["parsedId"] or "").strip()
        if pid:
            values[pid].append(reported_count(p["commentsCount"], p["file"]))
    counts = {}
    for pid, vals in values.items():
        rep = [v for v in vals if v is not None]
        counts[pid] = max(rep) if rep else None
    info = {"post_records": len(raw["posts"]),
            "post_records_without_thread_id": sum(1 for p in raw["posts"] if not str(p["parsedId"] or "").strip()),
            "threads_with_a_post_record": len(values),
            "threads_with_more_than_one_post_record": sum(1 for v in values.values() if len(v) > 1),
            "threads_whose_post_records_report_different_counts":
                sum(1 for v in values.values() if len({x for x in v if x is not None}) > 1),
            "threads_with_no_reported_count": sum(1 for v in counts.values() if v is None)}
    return counts, info


def thread_size(c: pd.DataFrame, counts: dict, info: dict) -> tuple[dict, list]:
    status, value, bucket = [], [], []
    for t in c["thread"]:
        if t not in counts:
            status.append("no post record"); value.append(None); bucket.append("")
        elif counts[t] is None:
            status.append("no reported count"); value.append(None); bucket.append("")
        elif counts[t] == 0:
            status.append("reported count of zero"); value.append(0); bucket.append("")
        else:
            status.append("joined"); value.append(counts[t]); bucket.append(size_bucket(counts[t]))
    c = c.assign(size_status=status, size_value=value, size_bucket=bucket)
    out = {"join": {**info, "rule": "comment parsedPostId = post parsedId; the largest reported count where a thread "
                                    "has more than one post record (Deviation 13)"}}
    for scope, sub in (("all tiers", c), ("tier_1_and_2", c[c["tier"].isin(TIER12)])):
        threads = sub.drop_duplicates("thread")
        out[scope] = {"comments": int(len(sub)),
                      "comments_by_status": {s: int((sub["size_status"] == s).sum()) for s in
                                             ("joined", "no post record", "no reported count", "reported count of zero")},
                      "threads_by_status": {s: int((threads["size_status"] == s).sum()) for s in
                                            ("joined", "no post record", "no reported count", "reported count of zero")},
                      "comments_by_bucket": {b: int((sub["size_bucket"] == b).sum()) for b in SIZE_NAMES},
                      "threads_by_bucket": {b: int((threads["size_bucket"] == b).sum()) for b in SIZE_NAMES}}
    t12 = c[c["tier"].isin(TIER12) & (c["size_status"] == "joined")]
    out["tier_1_and_2"]["comments_by_bucket_and_year"] = {
        str(y): {b: int(((t12["year"] == y) & (t12["size_bucket"] == b)).sum()) for b in SIZE_NAMES} for y in YEARS}
    rows = [[i, t, "" if v is None else str(int(v)), b, s]
            for i, t, v, b, s in zip(c["id"], c["thread"], value, bucket, status)]
    return out, rows


def capture(raw: dict, corpus_threads: set) -> dict:
    """check_capture_rate.py, step by step (rule 3)."""
    posts = {}
    for p in raw["posts"]:
        pid = str(p["parsedId"] or "").strip()
        if not pid:
            continue
        try:
            n = int(p["commentsCount"] or 0)
        except (TypeError, ValueError):
            stop(f"non-numeric commentsCount in {p['file']}. {REPORT}")
        posts[pid] = max(posts.get(pid, 0), n)
    captured, status = defaultdict(set), defaultdict(dict)
    for cid, pid, st in raw["comments"]:
        cid = str(cid or "").strip()
        if not (pid and cid):
            continue
        captured[pid].add(cid)
        if cid not in status[pid]:
            status[pid][cid] = st
    rows = []
    for pid, rep in posts.items():
        cap = len(captured.get(pid, ()))
        sts = list(status.get(pid, {}).values())
        rows.append({"pid": pid, "reported": rep, "captured": cap, "effective": max(rep, cap), "excess": max(0, cap - rep),
                     "deleted": sts.count("deleted"), "removed": sts.count("removed")})
    df = pd.DataFrame(rows)
    df["bucket"] = pd.cut(df["reported"], CAPTURE_EDGES, labels=CAPTURE_NAMES)
    tot = {k: int(df[k].sum()) for k in ("reported", "effective", "captured")}
    inc = df[df["excess"] > 0]
    by_bucket = {}
    for b in CAPTURE_NAMES:
        g = df[df["bucket"] == b]
        eff, cap = int(g["effective"].sum()), int(g["captured"].sum())
        by_bucket[b] = {"threads": int(len(g)), "reported": int(g["reported"].sum()), "effective": eff, "captured": cap,
                        "rate": share(cap, eff) if eff else None}
    in_posts = sum(len(v) for k, v in captured.items() if k in posts)
    all_ids = len({cid for v in captured.values() for cid in v})
    return {"method": "check_capture_rate.py: captured = unique raw comment ids of a thread; effective denominator = "
                      "max(commentsCount, captured); a missing commentsCount counts as 0",
            "threads": int(len(df)), "reported_total": tot["reported"], "effective_total": tot["effective"],
            "denominator_adjustment": tot["effective"] - tot["reported"], "captured_total": tot["captured"],
            "original_rate": share(tot["captured"], tot["reported"]), "corrected_rate": share(tot["captured"], tot["effective"]),
            "threads_where_captured_exceeds_commentsCount": int(len(inc)),
            "share_of_threads": share(len(inc), len(df)), "total_excess": int(inc["excess"].sum()),
            "largest_excess": int(inc["excess"].max()) if len(inc) else 0,
            "deleted_on_those_threads": int(inc["deleted"].sum()), "removed_on_those_threads": int(inc["removed"].sum()),
            "threads_whose_excess_deleted_and_removed_cover": int(((inc["deleted"] + inc["removed"]) >= inc["excess"]).sum()),
            "excess_not_covered": int((inc["excess"] - inc["deleted"] - inc["removed"]).clip(lower=0).sum()),
            "threads_with_no_comment_captured": int((df["effective"] == 0).sum()),
            "by_bucket": by_bucket,
            "reconciliation": {"unique_raw_comment_ids_with_a_thread_id": all_ids,
                               "of_which_in_threads_with_a_post_record": in_posts,
                               "corpus_threads": len(corpus_threads),
                               "corpus_threads_with_a_post_record": len(corpus_threads & set(posts)),
                               "sampled_threads_with_no_corpus_comment": len(set(posts) - corpus_threads)}}


# =============================================================================
# 7: funnel
# =============================================================================
def funnel_figures(rows: list, sha: str) -> dict:
    stages = []
    for k, (s, n) in enumerate(rows):
        stages.append({"stage": s, "items": n, "removed": (rows[k - 1][1] - n) if k else None})
    floor = next((k for k, (s, _) in enumerate(rows) if s.startswith("after >= 20-word floor")), None)
    word_floor = None
    if floor:
        before, after = rows[floor - 1][1], rows[floor][1]
        word_floor = {"before": before, "after": after, "removed": before - after, "share_removed": share(before - after, before)}
    return {"file_sha256": sha, "stages": stages, "word_floor": word_floor,
            "checks": "the first three stages equal the raw files; the last equals the corpus rows"}


# =============================================================================
# 8: the lexical proxy
# =============================================================================
def standardised_exact(y, era, groups, names) -> dict:
    """analysis_01_sample.decomposition's standardised era rates as fractions, with S_e each era's number of items:
    the pooled mix of group g is then its share of the three eras' items, n_g / N."""
    y, era, groups = np.asarray(y, dtype=np.int64), np.asarray(era, dtype=object), np.asarray(groups, dtype=object)
    n_g = {g: int((groups == g).sum()) for g in names}
    rate = {}
    for e in ERA_ORDER:
        for g in names:
            m = (era == e) & (groups == g)
            if m.sum():
                rate[(e, g)] = Fraction(int(y[m].sum()), int(m.sum()))
    common = [g for g in names if all((e, g) in rate for e in ERA_ORDER)]
    tot = sum(n_g[g] for g in common)
    return {e: (sum((n_g[g] * rate[(e, g)] for g in common), Fraction(0)) / tot if tot else None) for e in ERA_ORDER}


def lexical_proxy(c: pd.DataFrame) -> dict:
    hit = sample.proxy_hits(c["text"].tolist())
    c = c.assign(hit=hit)

    def rate(m) -> dict:
        m = np.asarray(m, dtype=bool)
        return wilson(int((hit & m).sum()), int(m.sum()))

    t12 = c["tier"].isin(TIER12).values
    out = {"source": sample.PROXY_SOURCE, "patterns_ignoring_case": sample.PROXY_PATTERNS, "text": "clean_body of corpus v2.2",
           "overall": {"all tiers": rate(np.ones(len(c), bool)), "tier_1_and_2": rate(t12),
                       **{t: rate(c["tier"] == t) for t in TIERS}},
           "by_subreddit": {s: rate(c["sub"] == s) for s in SUBREDDITS10},
           "by_subreddit_and_era": {s: {e: rate((c["sub"] == s) & (c["era"] == e)) for e in ERA_ORDER} for s in SUBREDDITS10},
           "by_tier_and_era": {t: {e: rate((c["tier"] == t) & (c["era"] == e)) for e in ERA_ORDER} for t in TIERS},
           "by_era": {"tier_1_and_2": {e: rate(t12 & (c["era"] == e).values) for e in ERA_ORDER},
                      "all tiers": {e: rate(c["era"] == e) for e in ERA_ORDER}},
           "by_year": {"tier_1_and_2": {str(y): rate(t12 & (c["year"] == y).values) for y in YEARS},
                       "all tiers": {str(y): rate(c["year"] == y) for y in YEARS}}}
    d = c[t12]
    sizes = {e: Fraction(int((d["era"] == e).sum())) for e in ERA_ORDER}
    g7 = np.array([sample.SEVEN_GROUPS[s] for s in d["sub"]], dtype=object)
    g2 = np.array([sample.TWO_GROUPS[s] for s in d["sub"]], dtype=object)
    check = {"status": EXPLORATORY, "method": "Deviation 8 (analysis_01_sample.decomposition), S_e = each era's Tier 1+2 comments",
             "note": "standardised_era_rates_pooled_frame_mix (the helper's name) holds the era rates standardised to the "
                     "pooled mix of the three eras' Tier 1+2 comments, not to the draw frame"}
    for name, groups, names in (("seven_groups", g7, sample.SEVEN_NAMES), ("two_groups", g2, ["narrow", "broad"])):
        dec = sample.decomposition(d["hit"].values, d["era"].values, groups, names, sizes)
        exact = standardised_exact(d["hit"].values, d["era"].values, groups, names)
        if any(fl(exact[e]) != dec["standardised_era_rates_pooled_frame_mix"][e] for e in ERA_ORDER):
            stop(f"the standardised era rates do not agree with analysis_01_sample.decomposition. {REPORT}")
        check[name] = {**dec, "_standardised": exact}
    out["composition_check_tier_1_and_2"] = check
    th = c.groupby("thread").agg(tier=("tier", "first"), hits=("hit", "sum"), n=("hit", "size"))
    out["threads_with_a_matching_comment"] = {t: wilson(int(((th["tier"] == t) & (th["hits"] > 0)).sum()), int((th["tier"] == t).sum()))
                                              for t in TIERS}
    t3 = th[th["tier"] == "Tier 3"]
    out["tier_3"] = {"threads_with_a_matching_comment": int((t3["hits"] > 0).sum()),
                     "comments_in_those_threads": int(t3.loc[t3["hits"] > 0, "n"].sum()),
                     "matching_comments": int(t3["hits"].sum()), "comments": int(t3["n"].sum())}
    dv = d["depth"].values.astype(float)
    known = ~np.isnan(dv)
    depth = np.array(["" if not ok else ("7 or more" if v >= 7 else str(int(v))) for v, ok in zip(dv, known)], dtype=object)
    out["by_reply_depth_tier_1_and_2"] = {k: wilson(int((d["hit"].values & (depth == k)).sum()), int((depth == k).sum()))
                                          for k in DEPTH_NAMES}
    out["tier_1_and_2_comments_without_a_reply_depth"] = int((~known).sum())
    top = known & (np.nan_to_num(dv, nan=-1) == 0)
    deep = known & (np.nan_to_num(dv, nan=-1) >= 3)
    out["depth_0_against_depth_3_or_more"] = {"depth_0": wilson(int(d["hit"].values[top].sum()), int(top.sum())),
                                              "depth_3_or_more": wilson(int(d["hit"].values[deep].sum()), int(deep.sum())),
                                              "difference": fl(Fraction(int(d["hit"].values[top].sum()), int(top.sum())) -
                                                               Fraction(int(d["hit"].values[deep].sum()), int(deep.sum())))
                                              if top.sum() and deep.sum() else None,
                                              "_difference": (Fraction(int(d["hit"].values[top].sum()), int(top.sum())) -
                                                              Fraction(int(d["hit"].values[deep].sum()), int(deep.sum())))
                                              if top.sum() and deep.sum() else None}
    return out


# =============================================================================
# 9: reweighting cells (R3)
# =============================================================================
def cell_stats(counts: list[int]) -> dict:
    nonempty = [n for n in counts if n > 0]
    below = sum(1 for n in nonempty if n < 10)
    return {"cells": len(counts), "non_empty": len(nonempty), "empty": len(counts) - len(nonempty),
            "median_non_empty": fl(float(np.median(nonempty))) if nonempty else None,
            "below_ten": below, "below_ten_share": share(below, len(nonempty)),
            "_below_ten": Fraction(below, len(nonempty)) if nonempty else None}


def reweighting_cells(c: pd.DataFrame) -> dict:
    t12 = c[c["tier"].isin(TIER12)]
    sq = Counter(zip(t12["sub"], t12["year"], t12["quarter"]))
    sy = Counter(zip(t12["sub"], t12["year"]))
    out = {}
    for name, (a, b) in SPANS.items():
        quarters = [(y, q) for y in range(a[0], b[0] + 1) for q in range(1, 5) if a <= (y, q) <= b]
        years = sorted({y for y, _ in quarters})
        qset = set(quarters)
        inside = [(y, q) in qset for y, q in zip(t12["year"], t12["quarter"])]
        out[name] = {"quarters": len(quarters), "years": len(years), "comments": int(sum(inside)),
                     "subreddit_quarter_cells": cell_stats([sq.get((s, y, q), 0) for s in SUBREDDITS8 for y, q in quarters]),
                     "subreddit_year_cells": cell_stats([sy.get((s, y), 0) for s in SUBREDDITS8 for y in years])}
    return out


# =============================================================================
# 10: within-year sampling position (check_c2_audit.py, rule 6)
# =============================================================================
def classify(name: str) -> dict | None:
    try:
        sub, term, rng = Path(name).stem.split("__")
        start, end = rng.split("_")
    except ValueError:
        return None
    m = YEAR_START_RE.match(start)
    if not m:
        return None
    if start == STUDY_START and end == STUDY_END:
        return None
    return {"sub": sub, "term": term, "year": int(m.group(1)), "start": start, "end": end,
            "kind": "supp" if end.endswith("-06-30") else "annual"}


def c2_posts(raw: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    jobs = {f["file"]: classify(f["file"]) for f in raw["files"]}
    files = [{**jobs[f["file"]], "file": f["file"], "posts": f["posts"], "comments": f["comments"]}
             for f in raw["files"] if jobs[f["file"]] is not None]
    posts = []
    for p in raw["posts"]:
        job = jobs.get(p["file"])
        if job is None:
            continue
        ws, we = pd.Timestamp(job["start"], tz="UTC"), pd.Timestamp(job["end"], tz="UTC")
        y0, y1 = pd.Timestamp(f"{job['year']}-01-01", tz="UTC"), pd.Timestamp(f"{job['year']}-12-31", tz="UTC")
        try:
            created = pd.Timestamp(p["createdAt"])
            if created.tzinfo is None:
                raise ValueError("no time zone")
        except (TypeError, ValueError) as e:
            stop(f"a post record in {p['file']} has no creation time that can be read ({e}). {REPORT}")
        posts.append({**job, "post_id": str(p["id"] or p["parsedId"] or ""), "created": created,
                      "pos_in_year": float((created - y0) / (y1 - y0)),
                      "in_window": bool(ws <= created < we + pd.Timedelta(days=1))})
    cols = ["sub", "term", "year", "start", "end", "kind", "post_id", "created", "pos_in_year", "in_window"]
    return pd.DataFrame(files), pd.DataFrame(posts, columns=cols)


def quarter_shares(series: pd.Series) -> tuple[list[int], float]:
    from scipy import stats
    q = pd.cut(series, [0, .25, .5, .75, 1.01], labels=["Q1", "Q2", "Q3", "Q4"]).value_counts().sort_index()
    return [round(100 * v / q.sum()) for v in q], float(stats.chisquare(q.values).statistic)


def drift_summary(subset: pd.DataFrame) -> dict:
    from scipy import stats
    by_year = subset.groupby("year")["pos_in_year"].agg(["size", "mean"])
    reg = stats.linregress(by_year.index, by_year["mean"])
    pct, chi = quarter_shares(subset["pos_in_year"])
    return {"posts": int(len(subset)),
            "by_year": {str(int(y)): {"posts": int(r["size"]), "mean_position": fl(r["mean"])} for y, r in by_year.iterrows()},
            "mean_position": fl(subset["pos_in_year"].mean()), "quarterly_shares_percent": pct,
            "chi_square": fl(chi), "slope_per_year": fl(reg.slope), "p_value": fl(reg.pvalue),
            "shift_across_the_span_years": fl(reg.slope * SPAN_INTERVALS),
            "shift_across_the_span_days": fl(reg.slope * SPAN_INTERVALS * 365.25),
            "_slope": float(reg.slope), "_p": float(reg.pvalue), "_mean": float(subset["pos_in_year"].mean())}


def sampling_position(raw: dict, log: pd.DataFrame) -> dict:
    files, posts = c2_posts(raw)
    if files.empty or posts.empty:
        stop(f"no year-blocked raw file or post was found. {REPORT}")
    supp_f, ann_f = files[files["kind"] == "supp"], files[files["kind"] == "annual"]
    groups = supp_f.groupby(["sub", "term"]).size()
    years_ok = supp_f.groupby(["sub", "term"])["year"].agg(lambda y: sorted(y) == list(range(2016, 2025)))
    caps = {"annual": CONFIG_CONSTANTS["MAX_POSTS_PER_BLOCK"], "supp": CONFIG_CONSTANTS["MAX_POSTS_PER_SUPP_BLOCK"]}
    integrity = {"year_blocked_files": int(len(files)), "annual_files": int(len(ann_f)), "supplementary_files": int(len(supp_f)),
                 "supplementary_groups": int(len(groups)), "complete_supplementary_groups": int((groups == C2_BLOCKS).sum()),
                 "groups_with_one_block_for_each_year_2016_to_2024": int(years_ok.sum()),
                 "files_over_their_post_cap": {k: int((files.loc[files["kind"] == k, "posts"] > v).sum()) for k, v in caps.items()},
                 "posts_outside_their_window": int((~posts["in_window"]).sum()),
                 "empty_supplementary_files": int((supp_f["posts"] == 0).sum())}
    if integrity["supplementary_files"] != C2_SUPP_FILES or integrity["complete_supplementary_groups"] != C2_GROUPS \
            or integrity["groups_with_one_block_for_each_year_2016_to_2024"] != C2_GROUPS \
            or integrity["files_over_their_post_cap"]["supp"] or integrity["posts_outside_their_window"]:
        stop(f"the year-blocked raw files do not pass check_c2_audit.py's checks: {integrity}. {REPORT}")
    full = posts[posts["year"] < 2025]
    annual = full[full["kind"] == "annual"].copy()
    after_unique = (full.sort_values(["sub", "term", "year", "kind"])
                        .drop_duplicates(subset=["sub", "term", "year", "post_id"], keep="first").copy())
    out = {"method": "check_c2_audit.py: year-blocked files, positions within the year, 2016-2024",
           "integrity": integrity,
           "before_C2_annual_blocks": drift_summary(annual),
           "after_C2_deduplicated_primary": drift_summary(after_unique),
           "after_C2_overlaps_kept_sensitivity": drift_summary(full.copy()),
           "duplicate_retrievals_removed": int(len(full) - len(after_unique)), "retrievals": int(len(full))}
    g = files[files["year"] < 2025]
    yield_rows = {}
    for y in sorted(g["year"].unique()):
        row = {}
        for k in ("annual", "supp"):
            gk = g[(g["year"] == y) & (g["kind"] == k)]
            row[f"{k}_files"] = int(len(gk))
            row[f"{k}_posts"] = int(gk["posts"].sum())
            row[f"{k}_per_block"] = round(gk["posts"].sum() / len(gk), 2) if len(gk) else None
        row["H1_share_percent"] = (round(100 * row["supp_per_block"] / (row["annual_per_block"] + row["supp_per_block"]), 0)
                                   if row["annual_per_block"] is not None and row["supp_per_block"] is not None
                                   and (row["annual_per_block"] + row["supp_per_block"]) else None)
        yield_rows[str(int(y))] = row
    out["yield_by_year"] = yield_rows
    slog = log[log["end"].str.endswith("-06-30")]
    file_items = int(supp_f["posts"].sum() + supp_f["comments"].sum())
    out["collection_log"] = {"rows": int(len(log)), "logged_spend_usd": fl(sum(log["usd"], Fraction(0))),
                             "_logged_spend": sum(log["usd"], Fraction(0)), "_supplementary_spend": sum(slog["usd"], Fraction(0)),
                             "supplementary_rows": int(len(slog)), "supplementary_items_logged": int(slog["items"].sum()),
                             "supplementary_items_in_files": file_items,
                             "supplementary_posts_in_files": int(supp_f["posts"].sum()),
                             "supplementary_comments_in_files": int(supp_f["comments"].sum()),
                             "supplementary_spend_usd": fl(sum(slog["usd"], Fraction(0)))}
    if out["collection_log"]["supplementary_items_logged"] != file_items:
        stop(f"scrape_log.csv records {out['collection_log']['supplementary_items_logged']:,} supplementary items; the "
             f"files hold {file_items:,} (check_c2_audit.py's reconciliation). {REPORT}")
    return out


# =============================================================================
# 11: previews (rule 7)
# =============================================================================
def compare_previews(r: dict) -> dict:
    def f4(x):
        return f"{x:+.4f}"

    def p4(x):
        return f"{x:.4f}"

    cells = r["reweighting_cells"]
    computed = {}
    for name, span in (("reweighting cells, trend span (R3)", TREND_SPAN),
                       ("reweighting cells, full span (design document 7.10d)", "full span, 2016 Q1 to 2025 Q2")):
        q, y = cells[span]["subreddit_quarter_cells"], cells[span]["subreddit_year_cells"]
        med = lambda v: "n/a" if v is None else f"{v:.0f}"
        computed[name] = {"comments": str(cells[span]["comments"]),
                          "subreddit-quarter cells, non-empty": str(q["non_empty"]),
                          "subreddit-quarter cells, median": med(q["median_non_empty"]),
                          "subreddit-quarter cells, below ten (%)": pct_text(q["below_ten"], q["non_empty"], 1),
                          "subreddit-quarter cells, empty": str(q["empty"]),
                          "subreddit-year cells, non-empty": str(y["non_empty"]),
                          "subreddit-year cells, median": med(y["median_non_empty"]),
                          "subreddit-year cells, below ten (%)": pct_text(y["below_ten"], y["non_empty"], 0)}
    comp = r["composition_by_year"]
    cov = comp["subreddit_coverage"]
    wy = comp["comments_by_subreddit_and_year"]["waymo"]
    w = comp["waymo_comments_in_2024_2025"]
    t1 = comp["tier_1_share_of_all_comments_by_year"]
    computed["coverage (design document 7.1 and 7.10c)"] = {
        f"{s} missing study years": ",".join(str(x) for x in cov[s]["missing_study_years"]) or "none"
        for s in ("realtesla", "cybersecurity", "waymo")}
    computed["coverage (design document 7.1 and 7.10c)"].update({
        "waymo comments 2021/2022/2023": "/".join(str(wy[str(y)]) for y in (2021, 2022, 2023)),
        "waymo share of its comments in 2024-2025 (%)": pct_text(w["k"], w["n"], 1),
        "Tier 1 share of all comments by year (%)": "/".join(pct_text(t1[str(y)]["tier_1"], t1[str(y)]["all"], 1) for y in YEARS)})
    cp = r["capture"]
    bb = cp["by_bucket"]
    computed["capture (docs/corpus_manifest.md)"] = {
        "threads": str(cp["threads"]), "reported total": str(cp["reported_total"]),
        "effective denominator": str(cp["effective_total"]), "captured": str(cp["captured_total"]),
        "original rate (%)": pct_text(cp["captured_total"], cp["reported_total"], 3),
        "corrected rate (%)": pct_text(cp["captured_total"], cp["effective_total"], 3),
        "threads where captured exceeds commentsCount": str(cp["threads_where_captured_exceeds_commentsCount"]),
        "of all threads (%)": pct_text(cp["threads_where_captured_exceeds_commentsCount"], cp["threads"], 1),
        "total excess": str(cp["total_excess"]), "largest excess": str(cp["largest_excess"]),
        "[deleted] on those threads": str(cp["deleted_on_those_threads"]),
        "[removed] on those threads": str(cp["removed_on_those_threads"]),
        "threads whose excess deleted and removed cover": str(cp["threads_whose_excess_deleted_and_removed_cover"]),
        "excess not covered": str(cp["excess_not_covered"]),
        "by bucket: threads": "/".join(str(bb[b]["threads"]) for b in CAPTURE_NAMES),
        "by bucket: reported": "/".join(str(bb[b]["reported"]) for b in CAPTURE_NAMES),
        "by bucket: effective": "/".join(str(bb[b]["effective"]) for b in CAPTURE_NAMES),
        "by bucket: captured": "/".join(str(bb[b]["captured"]) for b in CAPTURE_NAMES),
        "by bucket: rate (%)": "/".join(pct_text(bb[b]["captured"], bb[b]["effective"], 1) for b in CAPTURE_NAMES)}
    sp = r["within_year_sampling_position"]
    b, a, k = sp["before_C2_annual_blocks"], sp["after_C2_deduplicated_primary"], sp["after_C2_overlaps_kept_sensitivity"]
    h1 = [v["H1_share_percent"] for v in sp["yield_by_year"].values() if v["H1_share_percent"] is not None]
    computed["within-year sampling position (docs/corpus_manifest.md, design document 7.4)"] = {
        "before C2: posts": str(b["posts"]), "before C2: mean position": f"{b['_mean']:.2f}",
        "before C2: quarterly shares (%)": "/".join(str(x) for x in b["quarterly_shares_percent"]),
        "before C2: slope per year": f4(b["_slope"]), "before C2: p": p4(b["_p"]),
        "after C2: mean position": f"{a['_mean']:.2f}",
        "after C2: quarterly shares (%)": "/".join(str(x) for x in a["quarterly_shares_percent"]),
        "after C2: slope per year": f4(a["_slope"]), "after C2: p": p4(a["_p"]),
        "overlaps kept: slope per year": f4(k["_slope"]), "overlaps kept: p": p4(k["_p"]),
        "duplicate retrievals removed / retrievals": f"{sp['duplicate_retrievals_removed']}/{sp['retrievals']}",
        "H1 share across years, lowest/highest (%)": (f"{min(h1):.0f}/{max(h1):.0f}" if h1 else "n/a"),
        "shift across the span (years)": f"{a['_slope'] * SPAN_INTERVALS:.2f}",
        "shift across the span (days)": f"{a['_slope'] * SPAN_INTERVALS * 365.25:.0f}"}
    lg = sp["collection_log"]
    computed["collection log (docs/corpus_manifest.md)"] = {
        "log rows": str(lg["rows"]), "logged spend (USD)": f"{float(lg['_logged_spend']):.2f}",
        "supplementary files": str(sp["integrity"]["supplementary_files"]),
        "supplementary posts / comments / items": f"{lg['supplementary_posts_in_files']}/{lg['supplementary_comments_in_files']}/"
                                                  f"{lg['supplementary_items_in_files']}",
        "supplementary spend (USD)": f"{float(lg['_supplementary_spend']):.2f}"}
    st = {x["stage"]: x for x in r["funnel"]["stages"]}
    after = lambda prefix: next((x for k_, x in st.items() if k_.startswith(prefix)), None)
    bot, content, wrap, relay, mask = (after("after bot filter"), after("after content bot filter"),
                                       after("after submission wrapper strip"), after("after relay duplicate resolution"),
                                       after("after username masking"))
    wm = re.search(r"\((\d+) stripped; (\d+) fall below word floor\)", wrap["stage"]) if wrap else None
    mm = re.search(r"\((\d+) rows masked\)", mask["stage"]) if mask else None
    computed["corpus v2.2 (R5)"] = {
        "date range": f"{r['corpus']['first_comment_date']} to {r['corpus']['last_comment_date']}",
        "after the author-based bot filter": str(bot["items"]) if bot else "n/a",
        "removed by the content-based filter": str(content["removed"]) if content else "n/a",
        "wrapper stripping: rows modified / below the word floor": f"{wm.group(1)}/{wm.group(2)}" if wm else "n/a",
        "removed as relay duplicates": str(relay["removed"]) if relay else "n/a",
        "rows masked": mm.group(1) if mm else "n/a"}
    ru = r["threads"]["raw_union"]
    computed["thread caps (docs/corpus_manifest.md; design document 7.10e)"] = {
        "raw union: most unique comments in one thread": str(ru["most_unique_comments_in_one_thread"]),
        "raw union: threads with more than 15": str(ru["threads_with_more_than_15"]),
        "corpus v2.2: threads with more than 15": str(r["threads"]["comments_per_thread"]["threads_with_more_than_15"])}
    out = {}
    for name, recorded in PREVIEWS.items():
        items = {}
        for key, want in recorded.items():
            got = computed[name][key]
            items[key] = {"recorded": want, "computed": got, "same": got == want}
        out[name] = {"same": all(v["same"] for v in items.values()), "items": items}
    return out


# =============================================================================
# analysis, outputs, main
# =============================================================================
def load_all() -> dict:
    scripts = check_modules()
    config = check_config()
    corpus, info = load_corpus()
    funnel, funnel_sha = load_funnel()
    raw = load_raw()
    rec = reconcile(raw, funnel, corpus)
    log, log_sha = load_log()
    return {"scripts": scripts, "config": config, "corpus": corpus, "corpus_info": info, "funnel": funnel,
            "funnel_sha": funnel_sha, "raw": raw, "reconciliation": rec, "log": log, "log_sha": log_sha}


def analyse(L: dict) -> tuple[dict, list]:
    c = L["corpus"]
    counts, join_info = thread_counts(L["raw"])
    size, rows = thread_size(c, counts, join_info)
    results = {
        "specification": "Deviation 13 of docs/analysis_preregistration.md (the corpus description and the commentsCount "
                         "join); R3, R4 and Deviations 8, 13 and 14; analysis_02_corpus.py",
        "corpus": corpus_figures(c, L["corpus_info"]),
        "year_totals": year_totals(c),
        "composition_by_year": composition_by_year(c),
        "threads": {**thread_structure(c), "raw_union": raw_union(L["raw"])},
        "thread_size_R4": size,
        "capture": capture(L["raw"], set(c["thread"])),
        "funnel": funnel_figures(L["funnel"], L["funnel_sha"]),
        "lexical_proxy": lexical_proxy(c),
        "reweighting_cells": reweighting_cells(c),
        "within_year_sampling_position": sampling_position(L["raw"], L["log"]),
        "raw_files": {"files": RAW_FILES, "manifest_sha256": L["raw"]["manifest_sha256"],
                      "manifest_rule": "SHA-256 of the lines 'file name:SHA-256 of the file', sorted by name, joined by a "
                                       "newline, no trailing newline (models_common.pairs_sha256)",
                      **L["reconciliation"]},
        "inputs_sha256": {"corpus.parquet": L["corpus_info"]["file_sha256"], "preprocess_funnel.csv": L["funnel_sha"],
                          "scrape_log.csv": L["log_sha"], "raw files (manifest)": L["raw"]["manifest_sha256"],
                          "config.py (LF)": L["config"]["sha256_lf"]},
        "config": L["config"],
    }
    results["comparison_with_previews"] = compare_previews(results)
    return results, rows


def json_default(x):
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return fl(x)
    raise TypeError(f"a result of type {type(x).__name__} cannot be written: {REPORT}")


def render_report(r: dict) -> str:
    """The report, from the results before rounding: every share is formatted from its exact counts and every other
    figure from its unrounded value, so that no figure is rounded twice."""
    def pk(k, n, d=1):
        return "n/a" if not n else f"{float(Fraction(int(k), int(n)) * 100):.{d}f}%"

    def pc(x, d=1):
        return "n/a" if x is None else f"{float(x) * 100:.{d}f}%"

    def pts(x):
        if x is None:
            return "n/a"
        v = f"{float(x) * 100:+.1f}"
        return "0.0" if v in ("+0.0", "-0.0") else v

    def wil(v):
        if not v["n"]:
            return "n/a"
        return f"{pk(v['k'], v['n'])} ({v['k']:,}/{v['n']:,}; {pc(v['_low'])} to {pc(v['_high'])})"

    disp = r["corpus"]["subreddit_display_names"]
    tier_of = r["corpus"]["tier_of_subreddit"]
    L = ["# Corpus description of record (Deviation 13)", "",
         "The main figures, from corpus v2.2 and the raw files only. Every figure, with its counts, is in "
         "`corpus_results.json`. Counts measure the sampling configuration, not discourse volume.", ""]
    co = r["corpus"]
    L += ["## Corpus", "", f"Comments: {co['rows']:,} (Tier 1+2: {co['tier_1_and_2']:,}). First comment {co['first_comment_date']}, "
          f"last {co['last_comment_date']}. Membership SHA-256 `{co['membership_sha256']}`.", "",
          "| Tier | Subreddit | Comments |", "|---|---|---:|"]
    for s in SUBREDDITS10:
        L.append(f"| {tier_of[s]} | r/{disp[s]} | {co['by_subreddit'][s]:,} |")
    L += [f"| | **Total** | **{co['rows']:,}** |", ""]
    yt = r["year_totals"]
    L += ["## Year totals", "", "| Year | All | Tier 1 | Tier 2 | Tier 3 | Tier 1+2 |", "|---|---:|---:|---:|---:|---:|"]
    for y in YEARS:
        v = yt["by_year"][str(y)]
        L.append(f"| {y} | {v['all']:,} | {v['Tier 1']:,} | {v['Tier 2']:,} | {v['Tier 3']:,} | {v['tier_1_and_2']:,} |")

    def ratio(m):
        return "n/a" if not m["2024_comments"] else f"{float(Fraction(m['2025_comments'], 4) / Fraction(m['2024_comments'], 12)):.2f}"

    m = yt["monthly_rate_2025_against_2024"]
    L += ["", f"2025 monthly rate against 2024 (2025 has four months): all comments {ratio(m['all'])}; Tier 1+2 "
          f"{ratio(m['tier_1_and_2'])}.", ""]
    cp = r["composition_by_year"]
    counts = cp["comments_by_subreddit_and_year"]
    L += ["## Composition by year: share of the year's Tier 1+2 comments", "",
          "| Year | " + " | ".join(f"r/{disp[s]}" for s in SUBREDDITS8) + " |", "|---|" + "---:|" * len(SUBREDDITS8)]
    for y in YEARS:
        n = yt["by_year"][str(y)]["tier_1_and_2"]
        L.append(f"| {y} | " + " | ".join(pk(counts[s][str(y)], n) for s in SUBREDDITS8) + " |")
    t1 = cp["tier_1_share_of_all_comments_by_year"]
    w = cp["waymo_comments_in_2024_2025"]
    L += ["", "Tier 1 share of all comments by year: " + " / ".join(pk(t1[str(y)]["tier_1"], t1[str(y)]["all"]) for y in YEARS) + ".",
          f"r/waymo comments in 2024-2025: {pk(w['k'], w['n'])} of its {w['n']:,}.", "",
          "| Subreddit | Comments | First | Last | Missing study years |", "|---|---:|---|---|---|"]
    for s in SUBREDDITS10:
        v = cp["subreddit_coverage"][s]
        L.append(f"| r/{disp[s]} | {v['comments']:,} | {v['first']} | {v['last']} | "
                 f"{', '.join(str(x) for x in v['missing_study_years']) or 'none'} |")
    th = r["threads"]
    cpt = th["comments_per_thread"]
    ru = th["raw_union"]
    total_comments = sum(int(k) * n for k, n in cpt["threads_by_number_of_comments"].items())
    L += ["", "## Thread structure", "",
          f"Threads: {th['threads']:,} (Tier 1 {th['threads_by_tier']['Tier 1']:,}, Tier 2 {th['threads_by_tier']['Tier 2']:,}, "
          f"Tier 3 {th['threads_by_tier']['Tier 3']:,}); threads in more than one tier: {th['threads_in_more_than_one_tier']}; "
          f"in more than one subreddit: {th['threads_in_more_than_one_subreddit']}. Comments per thread: mean "
          f"{float(Fraction(total_comments, th['threads'])):.2f}, median {cpt['median']:g}, largest {cpt['largest']}; threads with "
          f"more than 15: {cpt['threads_with_more_than_15']}. Raw union (each comment id once, in its first thread): "
          f"{ru['threads']:,} threads, at most {ru['most_unique_comments_in_one_thread']} unique comments in one, "
          f"{ru['threads_with_more_than_15']} with more than 15.", ""]
    ts = r["thread_size_R4"]
    L += ["## Thread size (commentsCount joined for R4)", "",
          f"Post records {ts['join']['post_records']:,}; threads with a post record {ts['join']['threads_with_a_post_record']:,}; "
          f"with more than one post record {ts['join']['threads_with_more_than_one_post_record']:,} (different counts: "
          f"{ts['join']['threads_whose_post_records_report_different_counts']:,}).", "",
          "| Scope | Comments | Joined | No post record | No reported count | Reported count of zero |", "|---|---:|---:|---:|---:|---:|"]
    for scope, label in (("all tiers", "All tiers"), ("tier_1_and_2", "Tier 1+2")):
        v = ts[scope]["comments_by_status"]
        L.append(f"| {label} | {ts[scope]['comments']:,} | {v['joined']:,} | {v['no post record']:,} | "
                 f"{v['no reported count']:,} | {v['reported count of zero']:,} |")
    L += ["", "| Bucket (reported comments) | Tier 1+2 comments | Tier 1+2 threads |", "|---|---:|---:|"]
    for b in SIZE_NAMES:
        L.append(f"| {b} | {ts['tier_1_and_2']['comments_by_bucket'][b]:,} | {ts['tier_1_and_2']['threads_by_bucket'][b]:,} |")
    ca = r["capture"]
    L += ["", "## Capture against Reddit-reported thread size (method of check_capture_rate.py)", "",
          f"Threads with a post record {ca['threads']:,}; reported {ca['reported_total']:,}; effective denominator "
          f"{ca['effective_total']:,}; captured {ca['captured_total']:,}; capture {pk(ca['captured_total'], ca['reported_total'], 3)} "
          f"uncorrected, {pk(ca['captured_total'], ca['effective_total'], 3)} corrected. Threads where captured exceeds "
          f"commentsCount: {ca['threads_where_captured_exceeds_commentsCount']:,} "
          f"({pk(ca['threads_where_captured_exceeds_commentsCount'], ca['threads'])}), total excess {ca['total_excess']:,}, largest "
          f"{ca['largest_excess']}; [deleted] {ca['deleted_on_those_threads']:,} and [removed] {ca['removed_on_those_threads']:,} on "
          f"them; covered {ca['threads_whose_excess_deleted_and_removed_cover']:,}; excess not covered {ca['excess_not_covered']:,}.", "",
          "| commentsCount | Threads | Reported | Effective | Captured | Capture |", "|---|---:|---:|---:|---:|---:|"]
    for b in CAPTURE_NAMES:
        v = ca["by_bucket"][b]
        L.append(f"| {b} | {v['threads']:,} | {v['reported']:,} | {v['effective']:,} | {v['captured']:,} | "
                 f"{pk(v['captured'], v['effective'])} |")
    rc = ca["reconciliation"]
    L += ["", f"Reconciliation: corpus threads {rc['corpus_threads']:,}, of which with a post record "
          f"{rc['corpus_threads_with_a_post_record']:,}; sampled threads with no corpus comment "
          f"{rc['sampled_threads_with_no_corpus_comment']:,}; unique raw comment ids in threads with a post record "
          f"{rc['of_which_in_threads_with_a_post_record']:,} of {rc['unique_raw_comment_ids_with_a_thread_id']:,}.", ""]
    fu = r["funnel"]
    L += ["## Preprocessing funnel (data/clean_v2_2/preprocess_funnel.csv)", "",
          "The first row counts every raw item (posts included); the rows after it count comments.", "",
          "| Stage | Retained | Removed |", "|---|---:|---:|"]
    for k, st in enumerate(fu["stages"]):
        removed = "" if k < 2 else format(st["removed"], ",")
        L.append(f"| {st['stage']} | {st['items']:,} | {removed} |")
    if fu["word_floor"]:
        wf = fu["word_floor"]
        L += ["", f"The 20-word floor removes {wf['removed']:,} of {wf['before']:,} ({pk(wf['removed'], wf['before'])})."]
    lp = r["lexical_proxy"]
    L += ["", "## Lexical proxy (Deviation 14), comments with a CAV term", "",
          f"All tiers {wil(lp['overall']['all tiers'])}; Tier 1+2 {wil(lp['overall']['tier_1_and_2'])}; "
          + "; ".join(f"{t} {wil(lp['overall'][t])}" for t in TIERS) + ".", "",
          "| Subreddit | All years | " + " | ".join(ERA_ORDER) + " |", "|---|---|" + "---|" * len(ERA_ORDER)]
    for s in SUBREDDITS10:
        L.append(f"| r/{disp[s]} | {wil(lp['by_subreddit'][s])} | " +
                 " | ".join(pk(lp["by_subreddit_and_era"][s][e]["k"], lp["by_subreddit_and_era"][s][e]["n"]) for e in ERA_ORDER) + " |")
    L += ["", "Tier 1+2 by era: " + "; ".join(f"{e} {wil(lp['by_era']['tier_1_and_2'][e])}" for e in ERA_ORDER) + ".",
          "Tier 1+2 by year: " + " / ".join(f"{y} {pk(lp['by_year']['tier_1_and_2'][str(y)]['k'], lp['by_year']['tier_1_and_2'][str(y)]['n'])}"
                                            for y in YEARS) + "."]
    cc = lp["composition_check_tier_1_and_2"]
    L += ["", f"Composition check of Deviation 8 on the Tier 1+2 era rates ({cc['status']}; standardised to the pooled mix of the "
          f"three eras' Tier 1+2 comments):", "",
          "| Groups | 2022-2025 minus 2016-2018 | Mix part | Within-group part | Standardised era rates |", "|---|---:|---:|---:|---|"]
    for g, label in (("seven_groups", "Seven groups"), ("two_groups", "Two groups")):
        v = cc[g]
        L.append(f"| {label} | {pts(v['_difference'])} points | {pts(v['_mix'])} | {pts(v['_within'])} | " +
                 " / ".join(pc(v["_standardised"][e]) for e in ERA_ORDER) + " |")
    L += ["", "Threads with at least one matching comment: " +
          "; ".join(f"{t} {wil(lp['threads_with_a_matching_comment'][t])}" for t in TIERS) + ".",
          f"Tier 3: {lp['tier_3']['threads_with_a_matching_comment']} threads with a matching comment, holding "
          f"{lp['tier_3']['comments_in_those_threads']} of {lp['tier_3']['comments']} comments; "
          f"{lp['tier_3']['matching_comments']} matching comments.", "",
          "| Reply depth (Tier 1+2) | " + " | ".join(DEPTH_NAMES) + " |", "|---|" + "---:|" * len(DEPTH_NAMES),
          "| Comments | " + " | ".join(f"{lp['by_reply_depth_tier_1_and_2'][k]['n']:,}" for k in DEPTH_NAMES) + " |",
          "| CAV term | " + " | ".join(pk(lp["by_reply_depth_tier_1_and_2"][k]["k"], lp["by_reply_depth_tier_1_and_2"][k]["n"])
                                      for k in DEPTH_NAMES) + " |"]
    if lp["tier_1_and_2_comments_without_a_reply_depth"]:
        L.append(f"\nTier 1+2 comments without a reply depth, left out of this table: {lp['tier_1_and_2_comments_without_a_reply_depth']}.")
    dg = lp["depth_0_against_depth_3_or_more"]
    if dg["_difference"] is not None:
        L += ["", f"Depth 0 against depth 3 or more: {pk(dg['depth_0']['k'], dg['depth_0']['n'])} against "
              f"{pk(dg['depth_3_or_more']['k'], dg['depth_3_or_more']['n'])} ({pts(dg['_difference'])} points)."]
    L += ["", "## Reweighting cell sizes (R3; Tier 1+2)", "",
          "| Span | Comments | Sub-quarter cells | Median | Below ten | Empty | Sub-year cells | Median | Below ten |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, v in r["reweighting_cells"].items():
        q, y = v["subreddit_quarter_cells"], v["subreddit_year_cells"]
        L.append(f"| {name} | {v['comments']:,} | {q['non_empty']} | {q['median_non_empty']:g} | {pk(q['below_ten'], q['non_empty'])} | "
                 f"{q['empty']} | {y['non_empty']} | {y['median_non_empty']:g} | {pk(y['below_ten'], y['non_empty'], 0)} |")
    sp = r["within_year_sampling_position"]
    L += ["", "## Within-year sampling position (method of check_c2_audit.py)", "",
          "| Set | Posts | Mean position | Quarterly shares | Slope per year | p | Shift across the span |",
          "|---|---:|---:|---|---:|---:|---|"]
    for name, key in (("Before C2 (annual blocks)", "before_C2_annual_blocks"),
                      ("After C2, deduplicated (primary)", "after_C2_deduplicated_primary"),
                      ("After C2, overlaps kept (sensitivity)", "after_C2_overlaps_kept_sensitivity")):
        v = sp[key]
        L.append(f"| {name} | {v['posts']:,} | {v['_mean']:.2f} | {'/'.join(str(x) for x in v['quarterly_shares_percent'])} | "
                 f"{v['_slope']:+.4f} | {v['_p']:.4f} | {v['_slope'] * SPAN_INTERVALS:.3f} years "
                 f"({v['_slope'] * SPAN_INTERVALS * 365.25:.0f} days) |")
    L += ["", f"Duplicate retrievals removed: {sp['duplicate_retrievals_removed']} of {sp['retrievals']}. The shift is eight times "
          "the slope (2016-2024: nine year-points).", "",
          "| Year | Annual posts per block | Supplementary posts per block | H1 share |", "|---|---:|---:|---:|"]
    two = lambda x: "n/a" if x is None else f"{x:.2f}"
    for y, v in sp["yield_by_year"].items():
        L.append(f"| {y} | {two(v['annual_per_block'])} | {two(v['supp_per_block'])} | "
                 f"{'n/a' if v['H1_share_percent'] is None else format(v['H1_share_percent'], '.0f') + '%'} |")
    lg = sp["collection_log"]
    L += ["", "The per-block figures and H1 shares are rounded as check_c2_audit.py rounds them.", "",
          f"Collection log: {lg['rows']} rows, logged spend USD {float(lg['_logged_spend']):.2f}; supplementary (C2): "
          f"{lg['supplementary_rows']} rows, {lg['supplementary_items_logged']:,} items (files: {lg['supplementary_posts_in_files']} "
          f"posts, {lg['supplementary_comments_in_files']:,} comments), USD {float(lg['_supplementary_spend']):.2f}.", ""]
    L += ["## Previews compared with this script (rule 7)", ""]
    for name, v in r["comparison_with_previews"].items():
        if v["same"]:
            L.append(f"- {name}: same")
        else:
            diff = [f"{k}: recorded {x['recorded']}, computed {x['computed']}" for k, x in v["items"].items() if not x["same"]]
            L.append(f"- {name}: DIFFERENT ({'; '.join(diff)})")
    return "\n".join(L) + "\n"


def write_outputs(results: dict, rows: list, me: str, out_dir: Path, L: dict) -> None:
    """Written to a fresh work folder, then moved into place with corpus_results.json last: a run that fails part-way
    leaves no results file, so it can simply be run again (it gives the same bytes)."""
    clean = json.loads(json.dumps(strip(results), default=json_default))
    report = render_report(results)
    work = OUT_ROOT / f"in_progress_{os.getpid()}_{time.time_ns()}"
    work.mkdir(parents=True)
    try:
        mc.write_json(work / "corpus_results.json", clean)
        with open(work / "corpus_report.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
        sizes_sha = mc.write_rows_csv(work / "thread_sizes.csv", ["id", "thread", "comments_count", "bucket", "status"], rows)
        outputs = {name: mc.sha256_file(work / name) for name in ("corpus_results.json", "corpus_report.md")}
        outputs["thread_sizes.csv"] = sizes_sha
        created = mc.now_iso()
        mc.write_json(work / "corpus_manifest.json", {
            "created": created, "script": {"file": "analysis_02_corpus.py", "sha256_lf": me},
            "scripts_of_record_sha256_lf": L["scripts"], "config": L["config"], "inputs_sha256": clean["inputs_sha256"],
            "raw_files_sha256": L["raw"]["shas"], "outputs_sha256": outputs,
            "versions": mc.versions("numpy", "pandas", "scipy", "pyarrow")})
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in ("thread_sizes.csv", "corpus_report.md", "corpus_manifest.json", "corpus_results.json"):
            mc.replace_patiently(work / name, out_dir / name)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rel = out_dir.relative_to(cfg.REPO).as_posix()
    prev = clean["comparison_with_previews"]
    differ = [n for n, v in prev.items() if not v["same"]]
    v = mc.versions("numpy", "pandas", "scipy", "pyarrow")
    mc.show_register_block(out_dir / "PASTE_corpus_block.txt", [
        f"- `analysis_02_corpus.py` (SHA-256 `{me}`) run {created} with `--confirm-committed`: corpus v2.2 matched R5 and "
        f"its file SHA-256 of record; the {RAW_FILES} top-level raw files (manifest SHA-256 "
        f"`{clean['raw_files']['manifest_sha256']}`) reproduce the first three stages of the preprocessing funnel "
        f"({clean['raw_files']['raw_items']:,} items, {clean['raw_files']['raw_comments']:,} comments, "
        f"{clean['raw_files']['unique_raw_comment_ids']:,} unique ids); config.py as committed at be001c7. No output of a "
        f"corpus run was read.",
        f"- Inputs: `preprocess_funnel.csv` SHA-256 `{clean['inputs_sha256']['preprocess_funnel.csv']}`; `scrape_log.csv` "
        f"`{clean['inputs_sha256']['scrape_log.csv']}`.",
        f"- Outputs, in `{rel}/` (not committed): `corpus_results.json` SHA-256 `{outputs['corpus_results.json']}`; "
        f"`corpus_report.md` `{outputs['corpus_report.md']}`; `thread_sizes.csv` `{outputs['thread_sizes.csv']}` (the "
        f"commentsCount join of R4, read by the series-analysis script). Python {v['python']}, NumPy {v['numpy']}, pandas "
        f"{v['pandas']}, SciPy {v['scipy']}, PyArrow {v['pyarrow']}.",
        f"- Previews compared (rule 7 of the script): {len(prev) - len(differ)} of {len(prev)} groups the same"
        + (f"; different: {'; '.join(differ)} (computed values in corpus_results.json, comparison_with_previews; the "
           f"computed values stand)." if differ else "."),
    ])
    print(f"\nwritten: {out_dir}")


def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Corpus description of record (Deviation 13).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks; writes nothing")
    mode.add_argument("--confirm-committed", action="store_true", help="the run of record (after the commit)")
    args = ap.parse_args()
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit) or --confirm-committed (after the commit: the run of record)")
    print("Corpus description (Deviation 13): " + ("preflight, before the commit\n" if args.preflight else "the run of record\n"))
    me = own_sha256()
    out_dir = run_folder(me)
    print(f"this script: analysis_02_corpus.py SHA-256 {me}")
    if (out_dir / "corpus_results.json").exists():
        stop(f"this script's corpus description has already been run: its results are in {out_dir}. It is run once.")
    L = load_all()
    print(f"inputs: the scripts of record match; config.py is the file committed at be001c7 (term list, study window and "
          f"post caps); corpus v2.2 matches R5 and its file SHA-256 of record; the {RAW_FILES} raw files reproduce the first "
          f"three stages of the funnel and hold every corpus comment with its thread; scrape_log.csv has its ten columns")
    results, rows = analyse(L)
    clean = json.loads(json.dumps(strip(results), default=json_default))
    render_report(results)
    for name, v in clean["comparison_with_previews"].items():
        if v["same"]:
            print(f"preview {name}: same")
        else:
            diff = {k: x["computed"] for k, x in v["items"].items() if not x["same"]}
            print(f"preview {name}: DIFFERENT: computed {json.dumps(diff, ensure_ascii=False)}")
    if args.preflight:
        n_diff = sum(not v["same"] for v in clean["comparison_with_previews"].values())
        print("dry run: every figure was computed on the real inputs and the report rendered; the result was discarded")
        print("\nPREFLIGHT PASSED: every input matches the record and every figure can be computed. Nothing was written.")
        if n_diff:
            print(f"{n_diff} of {len(clean['comparison_with_previews'])} preview groups differ from what this script computes. "
                  f"The run of record lists them in its register lines; the computed values stand (rule 7).")
        return
    write_outputs(results, rows, me, out_dir, L)


if __name__ == "__main__":
    main()
