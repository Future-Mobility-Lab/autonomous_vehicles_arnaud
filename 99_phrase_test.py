"""
99_phrase_test.py -- DIAGNOSTIC. Does the actor phrase-match multi-word searchTerms?

Standalone. Does NOT import the job-building machinery and does NOT write into
data/raw/ or data/raw/_probe/, because config.slug() strips quotation marks:

    'autonomous vehicle data'    -> autonomous-vehicle-data
    '"autonomous vehicle data"'  -> autonomous-vehicle-data

so a quoted job would resolve to the SAME filename as the unquoted job already on
disk. Run through 00_probe.py it would be silently skipped as cached; forced, it
would overwrite paid-for data. Hence a separate output directory.

WHY THIS EXISTS
Measured on the collected corpus: search terms of 3+ tokens return posts that
contain the phrase 0% of the time and all tokens ~1% of the time, while 1-2 token
terms match at 92-98%. Four of the five ISSUE_TERMS are 3+ tokens, so Tier 3
(535 of 2,006 corpus comments) may be off-topic. The Apify documentation does not
specify whether searchTerms supports quoted phrases, so this is a controlled test.

DESIGN -- three arms, ~USD 0.21 total:
  A  POSITIVE CONTROL  "autonomous vehicle" quoted, r/technology
     Unquoted baseline: 28 posts, 82% contain the exact phrase. The phrase is
     known-abundant here, so if the quoted arm returns ~nothing, quoting BREAKS
     the query rather than there being nothing to find. Without this arm a null
     result in arm B is uninterpretable.
  B  TEST           "autonomous vehicle data" quoted, r/privacy
     Unquoted baseline: 60 posts, 0% contain the exact phrase. The real question.
  C  MECHANISM      autonomous vehicle data UNQUOTED, r/technology
     Separates "3+ tokens never phrase-match" from "the actor falls back to loose
     matching when strict matching returns few results". Same remediation either
     way, but the report can state the mechanism.

The decisive comparison is free: post IDs returned by the quoted arm versus the
unquoted files already in data/raw/. An identical ID set proves the quotation
marks are stripped before the search is executed.

Run:  (.venv active)  python 99_phrase_test.py
Out:  data/raw/_phrase_test/*.json  (invisible to 02_preprocess.py's non-recursive
      glob over data/raw/*.json)
"""

from __future__ import annotations
import os
import re
import sys
import json
import time
from pathlib import Path

import config as cfg

# ---------------------------------------------------------------------------
DRY_RUN = True     # True = print the plan and cost, call nothing. Run this first.
# ---------------------------------------------------------------------------

TEST_DIR = Path("data/raw/_phrase_test")
MAX_POSTS = 25          # enough to measure a precision rate; keeps the test at ~7c/arm
STUDY_START = cfg.STUDY_START
STUDY_END = cfg.STUDY_END

# arm id, searchTerm sent to the actor, subreddit, phrase to look for in results,
# filename stem, and the glob matching the already-collected unquoted equivalent
ARMS = [
    {
        "id": "A",
        "label": "POSITIVE CONTROL  quoted, phrase known-abundant",
        "term": '"autonomous vehicle"',
        "subreddit": "technology",
        "phrase": "autonomous vehicle",
        "stem": "A_quoted_autonomous-vehicle__technology",
        "baseline_glob": "technology__autonomous-vehicle__*.json",
    },
    {
        "id": "B",
        "label": "TEST              quoted, the actual question",
        "term": '"autonomous vehicle data"',
        "subreddit": "privacy",
        "phrase": "autonomous vehicle data",
        "stem": "B_quoted_autonomous-vehicle-data__privacy",
        "baseline_glob": "privacy__autonomous-vehicle-data__*.json",
    },
    {
        "id": "C",
        "label": "MECHANISM         unquoted 3-token, CAV-dense subreddit",
        "term": "autonomous vehicle data",
        "subreddit": "technology",
        "phrase": "autonomous vehicle data",
        "stem": "C_unquoted_autonomous-vehicle-data__technology",
        "baseline_glob": None,
    },
]


def run_input(arm: dict) -> dict:
    """Identical to config._base_input() plus probe-style caps, except that the
    search term is passed through verbatim so the quotation marks survive."""
    return {
        "searchTerms": [arm["term"]],
        "withinCommunity": f"r/{arm['subreddit']}",
        "searchPosts": True,
        "searchComments": False,
        "searchCommunities": False,
        "searchSort": "new",
        "postedAfter": STUDY_START,
        "postedBefore": STUDY_END,
        "includeNSFW": False,
        "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
        "crawlCommentsPerPost": False,
        "maxPostsCount": MAX_POSTS,
        "maxCommentsPerPost": 0,
        "maxCommentsCount": 0,
    }


def norm(text: str) -> str:
    """Lower-case and collapse punctuation to spaces, so 'self-driving' and
    'self driving' compare equal."""
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def baseline_ids(glob_pat: str | None) -> set[str]:
    """Post ids from the already-collected UNQUOTED files. Free: already paid for."""
    if not glob_pat:
        return set()
    ids: set[str] = set()
    for f in sorted(cfg.RAW_DIR.glob(glob_pat)):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        ids |= {r.get("parsedId") for r in data
                if r.get("dataType") == "post" and r.get("parsedId")}
    return ids


def analyse(arm: dict, items: list[dict]) -> dict:
    posts = [r for r in items if r.get("dataType") == "post"]
    phrase = norm(arm["phrase"])
    tokens = phrase.split()

    n_phrase = n_alltok = 0
    for p in posts:
        hay = norm((p.get("title") or "") + " " + (p.get("body") or ""))
        if phrase in hay:
            n_phrase += 1
        if all(t in hay for t in tokens):
            n_alltok += 1

    got = {p.get("parsedId") for p in posts if p.get("parsedId")}
    base = baseline_ids(arm["baseline_glob"])
    overlap = len(got & base)

    return {
        "id": arm["id"], "posts": len(posts),
        "phrase_pct": round(100 * n_phrase / len(posts), 1) if posts else 0.0,
        "alltok_pct": round(100 * n_alltok / len(posts), 1) if posts else 0.0,
        "baseline_posts": len(base),
        "overlap": overlap,
        "overlap_pct": round(100 * overlap / len(got), 1) if got else 0.0,
        "titles": [p.get("title", "")[:88] for p in posts[:8]],
    }


def report(results: list[dict]) -> None:
    print("\n" + "=" * 78)
    print("RESULTS")
    print("=" * 78)
    print(f"{'arm':<5}{'posts':>7}{'phrase%':>10}{'alltok%':>10}"
          f"{'baseline':>10}{'same ids':>10}{'same%':>8}")
    for r in results:
        print(f"{r['id']:<5}{r['posts']:>7}{r['phrase_pct']:>10.1f}"
              f"{r['alltok_pct']:>10.1f}{r['baseline_posts']:>10}"
              f"{r['overlap']:>10}{r['overlap_pct']:>8.1f}")

    for r in results:
        print(f"\n[arm {r['id']}] first titles returned:")
        if not r["titles"]:
            print("   (no posts returned)")
        for t in r["titles"]:
            print(f"   {t}")

    by_id = {r["id"]: r for r in results}
    a, b = by_id.get("A"), by_id.get("B")
    print("\n" + "=" * 78)
    print("INTERPRETATION")
    print("=" * 78)
    if not (a and b):
        print("Arms A and B are both required to interpret this test.")
        return

    if a["posts"] == 0:
        print("Arm A returned NOTHING for a phrase that is abundant unquoted (28 posts,")
        print("82% containing it). Quotation marks are being passed through literally and")
        print("BREAK the query. Phrase syntax is not supported.")
        print("-> Redesign Tier 3 around single CAV tokens; do not quote.")
    elif a["overlap_pct"] >= 90 and b["phrase_pct"] < 20:
        print("Arm A returned essentially the SAME posts as the unquoted baseline, and arm B")
        print("still returns off-topic results. The quotation marks are stripped before the")
        print("search runs, so quoting changes nothing.")
        print("-> Redesign Tier 3 around single CAV tokens.")
    elif b["phrase_pct"] >= 80:
        print("Arm B returns posts that genuinely contain the phrase. Quoting WORKS.")
        print("-> Keep the ISSUE_TERMS list, quote every multi-word term in config.py,")
        print("   re-run 00_probe.py (saturation status will change), then re-collect Tier 3.")
    else:
        print("Mixed result -- read the titles above before deciding. Arm A tells you whether")
        print("quoting is honoured at all; arm B whether it helps the terms you actually need.")

    c = by_id.get("C")
    if c:
        print()
        if c["phrase_pct"] >= 60:
            print("Arm C: the same 3-token query phrase-matches well in a CAV-dense subreddit.")
            print("Mechanism is a LOOSE FALLBACK when strict matching returns few results,")
            print("not a hard limit on multi-word terms. Worth stating in the methodology.")
        else:
            print("Arm C: the 3-token query fails even where CAV content is dense, so the")
            print("limitation is in multi-word matching itself, not a sparse-result fallback.")


def main() -> None:
    cfg.load_env()
    TEST_DIR.mkdir(parents=True, exist_ok=True)

    todo = [a for a in ARMS if not (TEST_DIR / f"{a['stem']}.json").exists()]
    cost = cfg.estimate_cost(MAX_POSTS * len(todo), len(todo))

    print("[plan] PHRASE-MATCHING TEST (posts only, no comments)")
    print(f"[plan] arms to run: {len(todo)} of {len(ARMS)}   cap {MAX_POSTS} posts/arm")
    print(f"[plan] worst-case cost: USD {cost:.2f}  (most arms return fewer)")
    print(f"[plan] output -> {TEST_DIR}/  (separate from data/raw/, nothing overwritten)")
    for a in ARMS:
        mark = "run " if a in todo else "done"
        print(f"   [{mark}] arm {a['id']}  {a['label']}")
        print(f"          searchTerms=[{a['term']!r}]  r/{a['subreddit']}")

    if DRY_RUN:
        print("\n[dry-run] nothing was called. Set DRY_RUN = False to run the test.")
        return

    if todo:
        token = os.environ.get("APIFY_API_TOKEN", "").strip()
        if not token:
            sys.exit("[stop] No APIFY_API_TOKEN found. Put it in .env at the repo root.")
        from apify_client import ApifyClient
        client = ApifyClient(token)

        spent = 0.0
        for arm in todo:
            print(f"\n[arm {arm['id']}] r/{arm['subreddit']} | {arm['term']}")
            try:
                run = client.actor(cfg.ACTOR_ID).call(run_input=run_input(arm))
                if run is None:
                    print("   ! run returned None -- skipping")
                    continue
                ds = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
                items = list(client.dataset(ds).iterate_items())
            except Exception as e:
                print(f"   ! failed: {type(e).__name__}: {e}")
                continue

            (TEST_DIR / f"{arm['stem']}.json").write_text(
                json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
            spent += cfg.estimate_cost(len(items))
            print(f"   {len(items)} posts  (running ~USD {spent:.3f})")
            time.sleep(1)
        print(f"\n[done] test spend ~USD {spent:.3f} "
              "(NOT written to scrape_log.csv -- add it to your budget register by hand)")

    results = []
    for arm in ARMS:
        p = TEST_DIR / f"{arm['stem']}.json"
        if p.exists():
            results.append(analyse(arm, json.loads(p.read_text(encoding="utf-8"))))
    if results:
        report(results)


if __name__ == "__main__":
    main()
