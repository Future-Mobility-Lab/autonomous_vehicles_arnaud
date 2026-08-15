"""
01_scrape.py -- PRODUCTION. Builds the research corpus.

Runs the sampling frame from config.py with comment crawling enabled and writes one
JSON per (subreddit, term, block) into data/raw/, which 02_preprocess.py reads.

Run 00_probe.py FIRST. Besides costing the collection, the probe report is what
tells this script WHICH queries need date-blocking (those that saturated the probe
post cap). Without it every query runs as a single window and high-yield queries
will truncate toward recent years.

Safety properties:
  * RESUMABLE      -- a job whose output file exists is skipped, so a crash or a
                      budget stop never re-pays for completed work.
  * CUMULATIVE CAP -- spend is counted from scrape_log.csv across ALL sessions, not
                      just the current one. (Previously per-session, which meant a
                      resumed run could spend a second full cap.)
  * FAULT TOLERANT -- a failed job is logged and retried on the next run.
  * AUDITED        -- every run appended to data/raw/scrape_log.csv with items and
                      estimated cost: the spend record for the report.

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


def log_run(job: dict, n_items: int, n_comments: int, cost: float) -> None:
    cfg.LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
    row = {"timestamp": datetime.now().isoformat(timespec="seconds"),
           "tier": job["tier"], "subreddit": job["subreddit"], "term": job["term"],
           "start": job["start"], "end": job["end"],
           "blocked": job.get("blocked", False),
           "items": n_items, "comments": n_comments, "est_usd": round(cost, 4)}
    pd.DataFrame([row]).to_csv(cfg.LOG_CSV, mode="a",
                               header=not cfg.LOG_CSV.exists(), index=False)


def main() -> None:
    cfg.load_env()
    jobs = cfg.build_jobs()
    cfg.RAW_DIR.mkdir(parents=True, exist_ok=True)

    todo = [j for j in jobs if not cfg.job_path(j, "collect").exists()]
    done = len(jobs) - len(todo)
    n_blocked_q = len({(j["subreddit"], j["term"]) for j in jobs if j.get("blocked")})
    n_single_q = len({(j["subreddit"], j["term"]) for j in jobs if not j.get("blocked")})

    already = cfg.spent_to_date()
    remaining_budget = cfg.BUDGET_USD_CAP - already

    print("[plan] PRODUCTION collection (posts + comments)")
    print(f"[plan] {n_blocked_q} blocked queries x {len(cfg.build_windows())} "
          f"{cfg.BLOCKING_MODE} blocks + {n_single_q} single-window queries "
          f"= {len(jobs)} jobs")
    print(f"[plan] already done={done}  to run={len(todo)}")
    print(f"[plan] window {cfg.STUDY_START}..{cfg.STUDY_END}")
    print(f"[plan] caps: {cfg.MAX_POSTS_PER_BLOCK} posts/block, "
          f"{cfg.COLLECT_MAX_POSTS} posts/single, "
          f"{cfg.MAX_COMMENTS_PER_POST} comments/post, "
          f"{cfg.MAX_COMMENTS_PER_RUN} comments/run")
    print(f"[plan] budget: cap USD {cfg.BUDGET_USD_CAP:.2f} | already spent "
          f"USD {already:.2f} | remaining USD {remaining_budget:.2f}")

    if not cfg.PROBE_REPORT.exists():
        print("[plan] WARNING: no probe report found. Every query will run as a single "
              "window, so high-yield queries will truncate toward recent years. "
              "Run 00_probe.py first.")
    else:
        est = pd.read_csv(cfg.PROBE_REPORT)
        if "est_collect_usd" in est.columns:
            e = est["est_collect_usd"].sum()
            print(f"[plan] probe-based estimate: USD {e:.2f} "
                  f"(~AUD {e/cfg.AUD_USD:.0f})")
            if e > remaining_budget:
                print(f"[plan] WARNING: estimate EXCEEDS remaining budget by "
                      f"{e/max(remaining_budget,0.01):.1f}x. The run will stop part-way "
                      "through the frame, biasing coverage toward whichever queries run "
                      "first. Tune config.py and re-run 00_probe.py (free) before collecting.")

    if cfg.PILOT_BLOCK_TEST:
        print(f"[plan] PILOT MODE: restricted to {cfg.PILOT_BLOCK_TEST}")

    if DRY_RUN:
        print("\n[dry-run] first 15 jobs:")
        for j in todo[:15]:
            tag = "blocked" if j.get("blocked") else "single "
            print(f"   {tag}  r/{j['subreddit']:<18} {j['term']:<26} "
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

    session_spend, total_items, total_comments = 0.0, 0, 0
    for n, job in enumerate(todo, 1):
        cumulative = already + session_spend
        if cumulative >= cfg.BUDGET_USD_CAP:
            print(f"\n[stop] cumulative budget cap USD {cfg.BUDGET_USD_CAP:.2f} reached "
                  f"(~USD {cumulative:.2f} across all sessions). "
                  f"{len(todo)-n+1} job(s) not run. Raise BUDGET_USD_CAP in config.py "
                  "to continue -- completed jobs are skipped on resume.")
            break

        tag = "blocked" if job.get("blocked") else "single"
        print(f"\n[{n}/{len(todo)}] {tag}  r/{job['subreddit']} | {job['term']}  "
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
        session_spend += cost
        total_items += len(items)
        total_comments += n_comments
        log_run(job, len(items), n_comments, cost)
        print(f"   {len(items)} items ({n_comments} comments)  ~USD {cost:.3f}  "
              f"(cumulative ~USD {already+session_spend:.2f})")
        time.sleep(1)

    remaining = [j for j in jobs if not cfg.job_path(j, "collect").exists()]
    print(f"\n[done] this session: {total_items:,} items, {total_comments:,} comments, "
          f"~USD {session_spend:.2f}")
    print(f"[done] cumulative spend ~USD {already+session_spend:.2f} "
          f"(~AUD {(already+session_spend)/cfg.AUD_USD:.0f})")
    print(f"[done] {len(jobs)-len(remaining)}/{len(jobs)} jobs complete; "
          f"{len(remaining)} remaining")
    if not remaining:
        print("[next] run 02_preprocess.py to build the cleaned corpus")


if __name__ == "__main__":
    main()
