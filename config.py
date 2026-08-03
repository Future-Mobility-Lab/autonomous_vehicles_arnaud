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
    `saturated` in the probe report are split into blocks; the other 34 run as
    single-window jobs, since blocking a query that already returns everything only
    adds actor-start fees.
  * BUDGET_USD_CAP 30 -> 75, now counted cumulatively. See DECISIONS.md A3.

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

# Hard stop. USD 11.64 already spent (probe + tests); collection estimated at
# USD 55-65, so 75 is headroom, not a spending target.
# 01_scrape.py counts spend CUMULATIVELY from scrape_log.csv, so this cap survives
# resumed sessions instead of resetting each run.
BUDGET_USD_CAP = 75.00

AUD_USD = 0.65                # reporting only -- verify against the live rate

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
# Annual is the default: it fixes the multi-year recency bias affordably. It does
# NOT guarantee balance WITHIN a year -- if a query has 30 posts in 2020 and the
# block cap takes the 8 newest, they may cluster in Q4, which would distort a
# QUARTERLY series. Whether this happens is UNVERIFIED: probe evidence was mixed,
# since 10 saturated queries still spanned 6+ years, inconsistent with pure
# newest-first ordering. Use PILOT_BLOCK_TEST below to check for ~USD 2 before
# committing the full budget.
BLOCKING_MODE = "annual"

# ---------------------------------------------------------------------------
# CAPS
# ---------------------------------------------------------------------------
PROBE_MAX_POSTS = 100         # diagnostic: posts only
COLLECT_MAX_POSTS = 60        # production, UNBLOCKED queries (whole window)
MAX_POSTS_PER_BLOCK = 3       # production, BLOCKED queries (per block). Tuned against the
#                               probe: 3 x 10 blocks = 30 posts per blocked query,
#                               giving ~21,700 comments for ~USD 67 -- on target and
#                               within cap. At 8 it was 80 posts, MORE than an
#                               unblocked query would take, projecting USD 109.
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

ISSUE_TERMS = [
    "self-driving car privacy", "autonomous vehicle data",
    "car data collection", "connected car security", "vehicle tracking",
]

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
    (subreddit, term, block) for saturated ones.

    force_single_window=True is used by the probe, which always measures the whole
    window in one run regardless of the production blocking scheme.
    """
    saturated = set() if force_single_window else load_saturated()
    blocks = build_windows()
    whole = [(STUDY_START, STUDY_END)]

    jobs: list[dict] = []
    for tier, cfg in TIERS.items():
        for sub in cfg["subreddits"]:
            for term in cfg["terms"]:
                if PILOT_BLOCK_TEST and (sub, term) not in PILOT_BLOCK_TEST:
                    continue
                is_blocked = (sub, term) in saturated
                for start, end in (blocks if is_blocked else whole):
                    jobs.append({"tier": tier, "subreddit": sub, "term": term,
                                 "start": start, "end": end, "blocked": is_blocked})
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
    """Production: posts plus comment threads. Blocked jobs get a smaller per-run
    post budget, because each such query gets one run per block."""
    max_posts = MAX_POSTS_PER_BLOCK if job.get("blocked") else COLLECT_MAX_POSTS
    run_input = _base_input(job)
    run_input.update({"crawlCommentsPerPost": True,
                      "maxPostsCount": max_posts,
                      "maxCommentsPerPost": MAX_COMMENTS_PER_POST,
                      "maxCommentsCount": MAX_COMMENTS_PER_RUN})
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
