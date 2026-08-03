"""
01_scrape.py -- PRODUCTION. Builds the research corpus.

Runs the sampling frame defined in config.py with comment crawling enabled and
writes one JSON file per (subreddit, term) into data/raw/, which 02_preprocess.py
reads directly.

Run 00_probe.py FIRST. The probe tells you what this will cost before you spend
it; without that, you are collecting blind against a fixed budget.

Safety properties:
  * RESUMABLE   -- a job whose output file exists is skipped, so a crash or a
                   budget stop at job 40 of 74 never re-pays for the first 39.
  * BUDGET STOP -- estimated spend is tracked and the run halts before exceeding
                   config.BUDGET_USD_CAP.
  * FAULT TOLERANT -- a failed job is logged and simply retried on the next run.
  * AUDITED     -- every run is appended to data/raw/scrape_log.csv with item
                   counts and estimated cost (your spend record for the report).

Output: data/raw/*.json, data/raw/scrape_log.csv
Run:    (.venv active)  python 01_scrape.py
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
DRY_RUN = True    # True = print the plan and cost estimate, call nothing.
#                   ALWAYS dry-run first. Set False to collect for real.
# ---------------------------------------------------------------------------


def log_run(job: dict, n_items: int, cost: float) -> None:
    cfg.LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now().isoformat(timespec="seconds"),
           "tier": job["tier"], "subreddit": job["subreddit"], "term": job["term"],
           "start": job["start"], "end": job["end"],
           "items": n_items, "est_usd": round(cost, 4)}
    pd.DataFrame([row]).to_csv(cfg.LOG_CSV, mode="a",
                               header=not cfg.LOG_CSV.exists(), index=False)


def main() -> None:
    cfg.load_env()
    jobs = cfg.build_jobs()
    cfg.RAW_DIR.mkdir(parents=True, exist_ok=True)

    todo = [j for j in jobs if not cfg.job_path(j, "collect").exists()]
    done = len(jobs) - len(todo)
    worst = cfg.estimate_cost(
        (cfg.COLLECT_MAX_POSTS + cfg.MAX_COMMENTS_PER_RUN) * len(todo), len(todo))

    print("[plan] PRODUCTION collection (posts + comments)")
    print(f"[plan] jobs={len(jobs)}  already done={done}  to run={len(todo)}")
    print(f"[plan] window {cfg.STUDY_START}..{cfg.STUDY_END}  "
          f"split_by_year={cfg.SPLIT_BY_YEAR}")
    print(f"[plan] caps: {cfg.COLLECT_MAX_POSTS} posts/query, "
          f"{cfg.MAX_COMMENTS_PER_POST} comments/post, "
          f"{cfg.MAX_COMMENTS_PER_RUN} comments/run")
    print(f"[plan] budget cap USD {cfg.BUDGET_USD_CAP:.2f}   "
          f"absolute worst case if every cap is hit: USD {worst:.2f}")

    if cfg.PROBE_REPORT.exists():
        est = pd.read_csv(cfg.PROBE_REPORT)["est_collect_usd"].sum()
        print(f"[plan] probe-based estimate: USD {est:.2f}")
        if est > cfg.BUDGET_USD_CAP:
            print(f"[plan] WARNING: probe estimate EXCEEDS the budget cap by "
                  f"{est/cfg.BUDGET_USD_CAP:.1f}x. The run will stop part-way through "
                  "the frame, biasing coverage toward whichever queries run first. "
                  "Tune config.py before collecting.")
    else:
        print("[plan] WARNING: no probe report found. Run 00_probe.py first so you "
              "know what this costs before spending it.")

    if DRY_RUN:
        print("\n[dry-run] first 15 queries:")
        for j in todo[:15]:
            print(f"   {j['tier']}  r/{j['subreddit']:<18} {j['term']:<28} "
                  f"{j['start']}..{j['end']}")
        if len(todo) > 15:
            print(f"   ... and {len(todo)-15} more")
        print("\n[dry-run] nothing was called. Set DRY_RUN = False to collect.")
        return

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not token:
        sys.exit("[stop] No APIFY_API_TOKEN found. Put it in .env at the repo root.")

    from apify_client import ApifyClient
    client = ApifyClient(token)

    spent, total_items = 0.0, 0
    for n, job in enumerate(todo, 1):
        if spent >= cfg.BUDGET_USD_CAP:
            print(f"\n[stop] budget cap USD {cfg.BUDGET_USD_CAP:.2f} reached "
                  f"(~USD {spent:.2f}). {len(todo)-n+1} job(s) not run. "
                  "Re-run to resume -- completed jobs are skipped.")
            break

        print(f"\n[{n}/{len(todo)}] r/{job['subreddit']} | {job['term']}  "
              f"{job['start']}..{job['end']}")
        try:
            run = client.actor(cfg.ACTOR_ID).call(run_input=cfg.collect_input(job))
            if run is None:
                print("   ! run returned None -- skipping (retries next time)")
                continue
            ds = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
            items = list(client.dataset(ds).iterate_items())
        except Exception as e:
            print(f"   ! failed: {type(e).__name__}: {e}")
            continue

        path = cfg.job_path(job, "collect")
        path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        n_comments = sum(1 for i in items if i.get("dataType") == "comment")
        cost = cfg.estimate_cost(len(items))
        spent += cost
        total_items += len(items)
        log_run(job, len(items), cost)
        print(f"   {len(items)} items ({n_comments} comments)  ~USD {cost:.3f}  "
              f"(running ~USD {spent:.2f})  -> {path.name}")
        time.sleep(1)

    remaining = [j for j in jobs if not cfg.job_path(j, "collect").exists()]
    print(f"\n[done] collected {total_items} items this session (~USD {spent:.2f})")
    print(f"[done] {len(jobs)-len(remaining)}/{len(jobs)} queries complete; "
          f"{len(remaining)} remaining")
    if not remaining:
        print("[next] run 02_preprocess.py to build the cleaned corpus")


if __name__ == "__main__":
    main()
