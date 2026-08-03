"""
00_probe.py -- DIAGNOSTIC. The volume gate. Run this before 01_scrape.py.

Runs post discovery ONLY (no comment crawling) across the full sampling frame.
Every post record carries a `commentsCount` field, so this measures how many
comments the real collection would yield -- and what it would cost -- WITHOUT
paying for a single comment.

Answers the questions that decide the research design:
  * How much CAV discussion actually exists in each subreddit, for each term?
  * How far back does each query reach? (Reddit serves ~1,000 posts per listing,
    so a query can be truncated before reaching 2016.)
  * Which (subreddit, term) pairs return nothing and should be dropped?
  * Which saturate the cap, meaning more data exists than measured?
  * What would full collection cost, versus the budget?

Output: data/raw/_probe/*.json  and  data/raw/_probe/probe_report.csv
        (the _probe subdirectory is NOT read by 02_preprocess.py, whose glob is
        non-recursive -- diagnostic data never contaminates the corpus)

Run:  (.venv active)  python 00_probe.py
"""

from __future__ import annotations
import os
import sys
import json
import time
from datetime import datetime

import pandas as pd

import config as cfg

# ---------------------------------------------------------------------------
DRY_RUN = True    # True = print the plan and worst-case cost, call nothing.
#                   ALWAYS dry-run first. Set False to actually run the probe.
# ---------------------------------------------------------------------------


def summarise(job: dict, items: list[dict]) -> dict:
    """Turn one probe result into a row of the volume-gate report."""
    posts = [i for i in items if i.get("dataType") == "post"]
    dates = sorted(p.get("createdAt", "") for p in posts if p.get("createdAt"))
    available = sum(int(p.get("commentsCount") or 0) for p in posts)
    # what collection would actually STORE, given the per-post cap
    capped = sum(min(int(p.get("commentsCount") or 0), cfg.MAX_COMMENTS_PER_POST)
                 for p in posts)
    return {
        "tier": job["tier"], "subreddit": job["subreddit"], "term": job["term"],
        "posts_found": len(posts),
        "saturated": len(posts) >= cfg.PROBE_MAX_POSTS,
        "earliest_post": dates[0][:10] if dates else "",
        "latest_post": dates[-1][:10] if dates else "",
        "comments_available": available,
        "comments_if_capped": capped,
        "est_collect_items": len(posts) + capped,
        "est_collect_usd": round(cfg.estimate_cost(len(posts) + capped), 3),
    }


def write_report(rows: list[dict]) -> None:
    cfg.PROBE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if df.empty:
        print("[probe] no results to report.")
        return
    df = df.sort_values(["tier", "subreddit", "term"])
    df.to_csv(cfg.PROBE_REPORT, index=False, encoding="utf-8-sig")
    print(f"\n[probe] report -> {cfg.PROBE_REPORT}  ({len(df)} queries)")

    print("\n[probe] posts found per tier:")
    print(df.groupby("tier")["posts_found"].sum().to_string())

    print("\n[probe] estimated FULL COLLECTION cost per tier (USD):")
    print(df.groupby("tier")["est_collect_usd"].sum().round(2).to_string())

    total = df["est_collect_usd"].sum()
    print(f"\n[probe] TOTAL estimated collection cost: USD {total:.2f}"
          f"   (budget cap USD {cfg.BUDGET_USD_CAP:.2f})")
    if total > cfg.BUDGET_USD_CAP:
        print(f"[probe] OVER BUDGET by {total/cfg.BUDGET_USD_CAP:.1f}x. Options, in order "
              "of least damage to the study:\n"
              f"        1. lower MAX_COMMENTS_PER_POST (now {cfg.MAX_COMMENTS_PER_POST}) "
              "-- costs depth, keeps temporal coverage\n"
              "        2. drop zero/low-yield (subreddit, term) pairs listed below\n"
              f"        3. lower COLLECT_MAX_POSTS (now {cfg.COLLECT_MAX_POSTS}) "
              "-- costs coverage, use last")
    else:
        print("[probe] within budget.")

    # temporal reach -- this decides monthly vs quarterly resolution
    reach = df[df["earliest_post"] != ""]
    if len(reach):
        print("\n[probe] earliest post reached, per subreddit (temporal coverage):")
        print(reach.groupby("subreddit")["earliest_post"].min().to_string())

    sat = df[df["saturated"]]
    if len(sat):
        print(f"\n[probe] {len(sat)} query/queries hit the {cfg.PROBE_MAX_POSTS}-post cap "
              "-- MORE data exists than measured here, so their estimates are FLOORS:")
        print(sat[["subreddit", "term", "earliest_post"]].to_string(index=False))

    empty = df[df["posts_found"] == 0]
    if len(empty):
        print(f"\n[probe] {len(empty)} query/queries returned NOTHING -- drop candidates:")
        print(empty[["subreddit", "term"]].to_string(index=False))


def main() -> None:
    cfg.load_env()
    jobs = cfg.build_jobs()
    cfg.PROBE_DIR.mkdir(parents=True, exist_ok=True)

    todo = [j for j in jobs if not cfg.job_path(j, "probe").exists()]
    done = len(jobs) - len(todo)
    worst = cfg.estimate_cost(cfg.PROBE_MAX_POSTS * len(todo), len(todo))

    print(f"[plan] DIAGNOSTIC probe (posts only, no comments)")
    print(f"[plan] jobs={len(jobs)}  already done={done}  to run={len(todo)}")
    print(f"[plan] window {cfg.STUDY_START}..{cfg.STUDY_END}  "
          f"split_by_year={cfg.SPLIT_BY_YEAR}")
    print(f"[plan] worst-case cost: USD {worst:.2f} "
          f"(<= {cfg.PROBE_MAX_POSTS} posts per query; most queries return fewer)")

    if DRY_RUN:
        print("\n[dry-run] first 15 queries:")
        for j in todo[:15]:
            print(f"   {j['tier']}  r/{j['subreddit']:<18} {j['term']:<28} "
                  f"{j['start']}..{j['end']}")
        if len(todo) > 15:
            print(f"   ... and {len(todo)-15} more")
        print("\n[dry-run] nothing was called. Set DRY_RUN = False to run the probe.")
        return

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not token:
        sys.exit("[stop] No APIFY_API_TOKEN found. Put it in .env at the repo root.")

    from apify_client import ApifyClient
    client = ApifyClient(token)

    spent = 0.0
    for n, job in enumerate(todo, 1):
        if spent >= cfg.BUDGET_USD_CAP:
            print(f"\n[stop] budget cap reached (~USD {spent:.2f}). "
                  f"{len(todo)-n+1} job(s) not run; re-run to resume.")
            break

        print(f"\n[{n}/{len(todo)}] r/{job['subreddit']} | {job['term']}")
        try:
            run = client.actor(cfg.ACTOR_ID).call(run_input=cfg.probe_input(job))
            if run is None:
                print("   ! run returned None -- skipping (retries next time)")
                continue
            ds = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
            items = list(client.dataset(ds).iterate_items())
        except Exception as e:
            print(f"   ! failed: {type(e).__name__}: {e}")
            continue

        path = cfg.job_path(job, "probe")
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        cost = cfg.estimate_cost(len(items))
        spent += cost
        print(f"   {len(items)} posts  ~USD {cost:.3f}  (running ~USD {spent:.2f})")
        time.sleep(1)

    # build the report from EVERY probe file on disk, including earlier sessions
    rows = []
    for j in jobs:
        p = cfg.job_path(j, "probe")
        if not p.exists():
            continue
        try:
            rows.append(summarise(j, json.loads(p.read_text(encoding="utf-8"))))
        except json.JSONDecodeError:
            print(f"   ! unreadable probe file skipped: {p.name}")
    write_report(rows)

    print(f"\n[done] probe spend this session ~USD {spent:.2f}")
    print("[next] read the report, tune MAX_COMMENTS_PER_POST / drop dead queries "
          "in config.py, then run 01_scrape.py")


if __name__ == "__main__":
    main()
