"""
config.py -- shared settings for the CAV-concern collection stage.

Imported by 00_probe.py (diagnostic) and 01_scrape.py (production) so the queries
the probe MEASURES are by construction the queries the scrape FETCHES.

REVISION 3 August 2026, after the 74-query diagnostic probe. Changes and evidence:

  * FULL FRAME RETAINED. Trimming was considered and rejected on measured grounds:
    dropping the 14 lowest-yield queries saves USD 2.94 (1.3% of yield), and term
    overlap measured on three complete subreddits is only 8-10%. Terms return
    substantially distinct post sets, so trimming costs unique data without
    materially cutting cost. All 74 queries stay.
  * MAX_COMMENTS_PER_POST 25 -> 15. Posts are pure overhead (same $0.002, not
    analysed), so a higher cap is marginally cheaper per comment -- but threads are
    comment-rich (median 52 comments/post) and 25 comments from one thread are not
    25 independent observations. Cap 15 costs ~USD 2 more than cap 25 and samples
    67% more threads. Thread effects are a documented Reddit-research limitation;
    this is a deliberate trade.
  * SELECTIVE BLOCKING. The scraper walks newest-first and stops at the post cap,
    so high-yield queries truncate toward recent years. Measured: 38 of 74 queries
    saturated the probe cap and 11 of those covered under 3 years. Queries flagged
    `saturated` in the probe report are split into blocks; the other 36 run as
    single-window jobs, since blocking a query that already returns everything only
    adds actor-start fees.
  * BUDGET_USD_CAP 30 -> 85, now counted cumulatively.

Nothing here calls the network. Edit settings here, not in the scripts.
"""

from __future__ import annotations
import os
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# APIFY
# ---------------------------------------------------------------------------
ACTOR_ID = "harshmaur/reddit-scraper"

COST_PER_RUN_USD = 0.02       # actor start
COST_PER_ITEM_USD = 0.002     # each stored result (post OR comment)

# Hard stop. Raised USD 85 -> 110 on 16 Aug 2026 to provide headroom for the
# Tier 3 re-probe and re-collection after the multi-word phrase-matching issue.
# This is a safety ceiling, not a spending target.
# 01_scrape.py counts spend CUMULATIVELY from scrape_log.csv, so this cap survives
# resumed sessions instead of resetting each run. Probe/test spend not written to
# scrape_log.csv must still be tracked separately.
BUDGET_USD_CAP = 110.00

AUD_USD = 0.70                # Updated early August -- verify against the live rate

# ---------------------------------------------------------------------------
# STUDY WINDOW  (must match 02_preprocess.py)
# ---------------------------------------------------------------------------
STUDY_START = "2016-01-01"
STUDY_END = "2025-04-30"

# ---------------------------------------------------------------------------
# BLOCKING
# ---------------------------------------------------------------------------
# "annual"    -> saturated queries split into 10 year-blocks  (~414 runs, USD  8.28)
# "quarterly" -> split into 37 quarter-blocks                 (~1,440 runs, USD 28.80)
# "none"      -> single window per query                      (74 runs,    USD  1.48)
#
# Annual is the default: it fixes the multi-year recency bias affordably. The
# residual risk was that it enforces balance BETWEEN years without enforcing it
# WITHIN a year -- if a query has 30 posts in 2020 and the block cap takes the 3
# newest, they could cluster in Q4 and distort a QUARTERLY series.
#
# SUPERSEDED. The 3 Aug 2026 pilot (n=30, r/SelfDrivingCars | self-driving)
# concluded annual blocking was sufficient: pooled quarterly shares 37/20/10/33%,
# chi-square 5.5 against a critical 7.81. Its own caveat was that n=30 excludes
# gross clustering but does not establish uniformity. That caveat was correct and
# the conclusion was wrong.
#
# FALSIFIED 16 Aug 2026 against 181 collected year-blocked posts across four
# subreddits: quarterly shares 10/7/15/67, chi-square 176.1. Mean sampling
# position within the block is 0.77 where uniform would be 0.50 (t = 11.97,
# p < 0.00001; KS D = 0.430, p < 0.00001). Cause: searchSort = "new" with
# MAX_POSTS_PER_BLOCK = 3 returns the three NEWEST posts in each block, so the
# sample lands at the block's end.
#
# WORSE, THE SKEW DRIFTS. Mean within-year position rises from ~0.5-0.8 in
# 2016-2019 to ~0.88-0.92 in 2022-2025 (slope +0.044/yr, p = 0.0055), because
# sampling position depends on post density and density trends upward across the
# study window. The seasonal confound therefore moves in the same direction as the
# outcome variable and is NOT a constant offset that cancels in a trend test.
#
# The earlier note that 10 saturated queries spanned 6+ years is not evidence
# against newest-first ordering: those ran UNBLOCKED at the single-window cap,
# where the cap is not binding relative to available volume, so newest-first still
# reaches back years. Ordering is newest-first in both regimes; only the 3-post cap
# makes it bite.
#
# REMEDIATION: supplementary Jan-Jun blocks, see build_supp_windows(). Annual
# blocking is retained; quarterly would require re-collecting everything.
BLOCKING_MODE = "annual"

# ---------------------------------------------------------------------------
# CAPS
# ---------------------------------------------------------------------------
PROBE_MAX_POSTS = 100

# Raised 60 -> 100 on 16 Aug 2026 after the truncation-band diagnostic found
# queries with 60-99 probe posts could remain unblocked but be capped at 60
# during single-window collection. Maintain COLLECT_MAX_POSTS >= PROBE_MAX_POSTS
# so an unsaturated probe result is not truncated by a lower production cap.
COLLECT_MAX_POSTS = 100
MAX_POSTS_PER_BLOCK = 3       # production, BLOCKED queries (per block). Tuned against the
#                               probe: 3 x 10 blocks = 30 posts per blocked query,
#                               giving ~29,400 comments for ~USD 71.75 -- on target and
#                               within cap. At 8 it was 80 posts, MORE than an
#                               unblocked query would take, projecting USD 109.
SUPP_BLOCKS_ENABLED = True    # C2: Jan-Jun supplementary blocks, see build_supp_windows
MAX_POSTS_PER_SUPP_BLOCK = 2  # 2 not 3: the measured defect was DRIFT, not level. A
#                               June anchor is density-independent so it breaks the
#                               drift; the residual constant H2/H1 offset cancels in a
#                               trend test. 3 posts would cost USD 6.17 more for no
#                               gain in trend validity.
MAX_COMMENTS_PER_POST = 15    # see header note on thread effects
MAX_COMMENTS_PER_RUN = 1500   # kill-switch per single run

# Pilot: restrict a run to these (subreddit, term) pairs so blocking behaviour can
# be tested cheaply. Empty list = no restriction (normal operation).
PILOT_BLOCK_TEST: list[tuple[str, str]] = []
# e.g. [("SelfDrivingCars", "self-driving")]  -> ~10 runs, roughly USD 2

# ---------------------------------------------------------------------------
# SAMPLING FRAME  (three tiers, per the proposal -- FULL frame, nothing trimmed)
# ---------------------------------------------------------------------------
CORE_TERMS = [
    "self-driving", "autonomous vehicle", "robotaxi",
    "Autopilot", "FSD", "Waymo", "V2X", "LiDAR",
]
# V2X is retained deliberately despite near-zero yield (40 posts / 939 comments
# across 8 subreddits, 2 returning nothing). Its absence is a RESULT for RQ2 --
# evidence the public does not discuss V2X by name -- and costs USD 0.02 per empty
# run to demonstrate. Do not silently drop it.

# Retained from the v1 Tier 3 design, now QUOTED. The actor does not phrase-match
# unquoted 3+ token terms: measured across 78 collected files, 0% of posts returned
# by 3-token terms contained the search phrase, against 87-98% for 1-2 token terms.
# Quoting IS honoured -- confirmed by controlled test 16 Aug 2026; the quoted string
# reaches Reddit's search endpoint verbatim (observed in the request URL).
# Expected yield is LOW BUT UNKNOWN. A single quoted run for "autonomous vehicle
# data" in r/privacy returned no posts, but that run's coverage ladder terminated
# with a date_window_unreached skip on its final seed, so it does NOT establish
# that the phrase is absent from the subreddit. Whether these terms have genuine
# zero yield is an OPEN QUESTION for the re-probe, not an assumption. Retained
# because an empty run costs ~USD 0.02 and a measured yield is worth more than a
# dropped query.
LEGACY_ISSUE_TERMS = [
    '"self-driving car privacy"', '"autonomous vehicle data"',
    '"car data collection"', '"connected car security"', '"vehicle tracking"',
]

# Tier 3 primary terms: the SAME CORE_TERMS used by Tiers 1 and 2, unquoted.
# Identical queries across all tiers means any difference in measured concern is
# attributable to the COMMUNITY rather than to the query wording.
ISSUE_TERMS = CORE_TERMS + LEGACY_ISSUE_TERMS

TIERS = {
    "Tier 1": {"subreddits": ["SelfDrivingCars", "teslamotors", "RealTesla", "Waymo"],
               "terms": CORE_TERMS},
    "Tier 2": {"subreddits": ["electricvehicles", "cars", "technology", "Futurology"],
               "terms": CORE_TERMS},
    "Tier 3": {"subreddits": ["privacy", "cybersecurity"],
               "terms": ISSUE_TERMS},
}

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
RAW_DIR = Path("data/raw")                  # corpus -> 02_preprocess reads this
PROBE_DIR = Path("data/raw/_probe")         # diagnostic; invisible to 02_preprocess's
#                                             non-recursive glob("*.json")
PROBE_REPORT = PROBE_DIR / "probe_report.csv"
LOG_CSV = RAW_DIR / "scrape_log.csv"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()


def build_windows(mode: str | None = None) -> list[tuple[str, str]]:
    """Date blocks for a BLOCKED query."""
    mode = mode or BLOCKING_MODE
    if mode == "none":
        return [(STUDY_START, STUDY_END)]

    y0, y1 = int(STUDY_START[:4]), int(STUDY_END[:4])
    out: list[tuple[str, str]] = []
    if mode == "annual":
        for y in range(y0, y1 + 1):
            start = max(f"{y}-01-01", STUDY_START)
            end = min(f"{y}-12-31", STUDY_END)
            if start <= end:
                out.append((start, end))
    elif mode == "quarterly":
        starts = {1: "01-01", 2: "04-01", 3: "07-01", 4: "10-01"}
        ends = {1: "03-31", 2: "06-30", 3: "09-30", 4: "12-31"}
        for y in range(y0, y1 + 1):
            for q in (1, 2, 3, 4):
                start = max(f"{y}-{starts[q]}", STUDY_START)
                end = min(f"{y}-{ends[q]}", STUDY_END)
                if start <= end:
                    out.append((start, end))
    else:
        raise ValueError(f"BLOCKING_MODE must be annual/quarterly/none, got {mode!r}")
    return out

def build_supp_windows() -> list[tuple[str, str]]:
    """C2: Jan-Jun supplementary blocks for saturated queries.

    Corrects the measured block-end clustering. With searchSort="new" and a small
    post cap, each block's sample lands near that block's END, so annual blocks
    produce a December-heavy sample whose position drifts with post density. A
    Jan-Jun block anchors a second, density-independent sample point near 30 June.

    Skips any year whose annual block already ends on or before 30 June (2025,
    since STUDY_END is 2025-04-30) -- that block IS an H1 block.
    """
    if not SUPP_BLOCKS_ENABLED:
        return []

    y0, y1 = int(STUDY_START[:4]), int(STUDY_END[:4])
    out: list[tuple[str, str]] = []

    for y in range(y0, y1 + 1):
        start = max(f"{y}-01-01", STUDY_START)
        end = min(f"{y}-06-30", STUDY_END)

        if start > end:
            continue

        annual_end = min(f"{y}-12-31", STUDY_END)

        if annual_end <= end:
            continue

        out.append((start, end))

    return out

def load_saturated() -> set[tuple[str, str]]:
    """(subreddit, term) pairs that hit the probe post cap and therefore need
    blocking. Empty set if the probe has not been run."""
    if not PROBE_REPORT.exists():
        return set()
    try:
        import pandas as pd
        df = pd.read_csv(PROBE_REPORT)
    except Exception:
        return set()
    if "saturated" not in df.columns:
        return set()
    sat = df[df["saturated"].astype(str).str.lower().isin(["true", "1"])]
    return {(str(r.subreddit), str(r.term)) for r in sat.itertuples()}


def build_jobs(force_single_window: bool = False) -> list[dict]:
    """One job per (subreddit, term) for unsaturated queries; one per
    (subreddit, term, block) for saturated ones, plus C2 Jan-Jun supplementary
    blocks for saturated queries.

    force_single_window=True is used by the probe, which always measures the whole
    window in one run and never gets supplementary blocks.
    """
    saturated = set() if force_single_window else load_saturated()
    blocks = build_windows()
    supp = [] if force_single_window else build_supp_windows()
    whole = [(STUDY_START, STUDY_END)]

    jobs: list[dict] = []
    for tier, cfg in TIERS.items():
        for sub in cfg["subreddits"]:
            for term in cfg["terms"]:
                if PILOT_BLOCK_TEST and (sub, term) not in PILOT_BLOCK_TEST:
                    continue

                is_blocked = (sub, term) in saturated

                for start, end in (blocks if is_blocked else whole):
                    jobs.append({
                        "tier": tier,
                        "subreddit": sub,
                        "term": term,
                        "start": start,
                        "end": end,
                        "blocked": is_blocked,
                        "supp": False,
                    })

                if is_blocked:
                    for start, end in supp:
                        jobs.append({
                            "tier": tier,
                            "subreddit": sub,
                            "term": term,
                            "start": start,
                            "end": end,
                            "blocked": True,
                            "supp": True,
                        })

    return jobs


def job_path(job: dict, kind: str) -> Path:
    """kind: 'probe' or 'collect'. Separate directories so a probe never marks a
    collect job as done. The date range is in the filename, so blocked jobs never
    collide with each other."""
    base = PROBE_DIR if kind == "probe" else RAW_DIR
    name = (f"{slug(job['subreddit'])}__{slug(job['term'])}"
            f"__{job['start']}_{job['end']}.json")
    return base / name


def _base_input(job: dict) -> dict:
    """Shared query shape. Dates are EXPLICIT: the relative 'searchTime' dropdown is
    anchored to today, not a calendar range, and would silently collect the wrong
    period."""
    return {
        "searchTerms": [job["term"]],
        "withinCommunity": f"r/{job['subreddit']}",
        "searchPosts": True,
        "searchComments": False,
        "searchCommunities": False,
        "searchSort": "new",
        "postedAfter": job["start"],
        "postedBefore": job["end"],
        "includeNSFW": False,
        "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
    }


def probe_input(job: dict) -> dict:
    """Diagnostic: discover posts, fetch NO comments. Post records still carry
    commentsCount, which is what lets us estimate comment yield for free."""
    run_input = _base_input(job)
    run_input.update({"crawlCommentsPerPost": False,
                      "maxPostsCount": PROBE_MAX_POSTS,
                      "maxCommentsPerPost": 0,
                      "maxCommentsCount": 0})
    return run_input


def collect_input(job: dict) -> dict:
    """Production: posts plus comment threads. C2 supplementary Jan-Jun blocks get
    a smaller post budget than the main annual blocks."""
    if job.get("supp"):
        max_posts = MAX_POSTS_PER_SUPP_BLOCK
    elif job.get("blocked"):
        max_posts = MAX_POSTS_PER_BLOCK
    else:
        max_posts = COLLECT_MAX_POSTS

    run_input = _base_input(job)
    run_input.update({
        "crawlCommentsPerPost": True,
        "maxPostsCount": max_posts,
        "maxCommentsPerPost": MAX_COMMENTS_PER_POST,
        "maxCommentsCount": MAX_COMMENTS_PER_RUN,
    })
    return run_input


def estimate_cost(n_items: int, n_runs: int = 1) -> float:
    return n_runs * COST_PER_RUN_USD + n_items * COST_PER_ITEM_USD


def spent_to_date() -> float:
    """Cumulative estimated spend from the audit log, so BUDGET_USD_CAP survives
    resumed sessions instead of resetting to zero each run."""
    if not LOG_CSV.exists():
        return 0.0
    try:
        import pandas as pd
        return float(pd.read_csv(LOG_CSV)["est_usd"].sum())
    except Exception:
        return 0.0
