"""
config.py -- shared settings for the CAV-concern collection stage.

Both 00_probe.py (diagnostic) and 01_scrape.py (production) import from here, so
the queries the probe MEASURES are by construction the same queries the scrape
FETCHES. If these lived in two files they could drift, and the probe's cost
estimate would describe a run you never make.

Nothing in this file calls the network. Edit settings here, not in the scripts.
"""

from __future__ import annotations
import os
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# APIFY
# ---------------------------------------------------------------------------
ACTOR_ID = "harshmaur/reddit-scraper"

# Pay-per-result pricing, USD (from the actor's pricing page -- re-check if it changes)
COST_PER_RUN_USD = 0.02       # actor start
COST_PER_ITEM_USD = 0.002     # each stored result (post OR comment)

# Hard budget stop. Keep BELOW your AUD budget converted to USD, with headroom.
# AUD 60 is roughly USD 39 at the time of writing -- CHECK THE LIVE RATE.
BUDGET_USD_CAP = 30.00

# ---------------------------------------------------------------------------
# STUDY WINDOW  (must match 02_preprocess.py)
# ---------------------------------------------------------------------------
STUDY_START = "2016-01-01"
STUDY_END = "2025-04-30"
SPLIT_BY_YEAR = False
# Leave False unless the probe shows queries saturating. Splitting by year turns
# ~74 runs into ~740, costing ~USD 14.80 in actor-start fees alone -- over a
# third of the budget spent on overhead rather than data.

# ---------------------------------------------------------------------------
# CAPS
# ---------------------------------------------------------------------------
PROBE_MAX_POSTS = 100         # diagnostic: posts only, no comments fetched
COLLECT_MAX_POSTS = 60        # production: posts discovered per (subreddit, term)
MAX_COMMENTS_PER_POST = 25    # <-- MAIN BUDGET LEVER. Breadth beats depth for
#                                  time-series: many posts x few comments spreads
#                                  coverage across months instead of over-sampling
#                                  a handful of viral threads.
MAX_COMMENTS_PER_RUN = 1500   # kill-switch per single run

# ---------------------------------------------------------------------------
# SAMPLING FRAME  (three tiers, per the proposal)
# ---------------------------------------------------------------------------
CORE_TERMS = [
    "self-driving", "autonomous vehicle", "robotaxi",
    "Autopilot", "FSD", "Waymo", "V2X", "LiDAR",
]

# Tier 3 communities are large and mostly off-topic, so the CAV context must be
# carried by the term itself -- searching "privacy" inside r/privacy returns
# everything and nothing useful.
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
RAW_DIR = Path("data/raw")                      # production corpus -> 02_preprocess reads this
PROBE_DIR = Path("data/raw/_probe")             # diagnostic; ignored by 02_preprocess's
#                                                 non-recursive glob("*.json")
PROBE_REPORT = PROBE_DIR / "probe_report.csv"
LOG_CSV = RAW_DIR / "scrape_log.csv"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def load_env(path: str = ".env") -> None:
    """Read APIFY_API_TOKEN from a git-ignored .env at the repo root."""
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


def build_jobs() -> list[dict]:
    """One job per (subreddit, term[, year]). Shared by probe and scrape."""
    if SPLIT_BY_YEAR:
        y0, y1 = int(STUDY_START[:4]), int(STUDY_END[:4])
        windows = []
        for y in range(y0, y1 + 1):
            start = f"{y}-01-01"
            end = min(f"{y}-12-31", STUDY_END)
            if start <= STUDY_END:
                windows.append((start, end))
    else:
        windows = [(STUDY_START, STUDY_END)]

    jobs: list[dict] = []
    for tier, cfg in TIERS.items():
        for sub in cfg["subreddits"]:
            for term in cfg["terms"]:
                for start, end in windows:
                    jobs.append({"tier": tier, "subreddit": sub, "term": term,
                                 "start": start, "end": end})
    return jobs


def job_path(job: dict, kind: str) -> Path:
    """kind: 'probe' or 'collect'. Separate dirs so a probe never marks a
    collect job as already done."""
    base = PROBE_DIR if kind == "probe" else RAW_DIR
    name = (f"{slug(job['subreddit'])}__{slug(job['term'])}"
            f"__{job['start']}_{job['end']}.json")
    return base / name


def _base_input(job: dict) -> dict:
    """Shared query shape. Dates are EXPLICIT: never use the relative
    'searchTime' dropdown, which is anchored to today rather than a calendar
    range, and would silently collect the wrong period."""
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
    """Production: posts plus their comment threads."""
    run_input = _base_input(job)
    run_input.update({"crawlCommentsPerPost": True,
                      "maxPostsCount": COLLECT_MAX_POSTS,
                      "maxCommentsPerPost": MAX_COMMENTS_PER_POST,
                      "maxCommentsCount": MAX_COMMENTS_PER_RUN})
    return run_input


def estimate_cost(n_items: int, n_runs: int = 1) -> float:
    return n_runs * COST_PER_RUN_USD + n_items * COST_PER_ITEM_USD
