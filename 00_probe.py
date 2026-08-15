"""
00_probe.py -- DIAGNOSTIC. The volume gate. Run before 01_scrape.py.

Post discovery ONLY (no comment crawling) across the full sampling frame. Every
post record carries `commentsCount`, so this measures how many comments the real
collection would yield -- and what it would cost -- WITHOUT paying for a comment.

Answers the questions that decide the research design:
  * How much CAV discussion exists per subreddit, per term?
  * How far back does each query reach? (Reddit serves ~1,000 posts per listing,
    and the scraper walks newest-first, so a query can truncate before 2016.)
  * Which queries saturate the cap and therefore need date-blocking?
  * Which return nothing?
  * What would full collection cost against the budget?

ESTIMATOR FIX (3 August 2026): the previous version summed comments over every
probe post (up to PROBE_MAX_POSTS = 100) while collection takes far fewer, and it
capped at the old MAX_COMMENTS_PER_POST. It therefore overstated cost by ~30%.
Estimates now use the ACTUAL collection caps and blocking scheme from config.py,
so re-running this report after changing config gives a valid new estimate --
free, since it re-reads cached probe files rather than re-scraping.

Output: data/raw/_probe/*.json  and  data/raw/_probe/probe_report.csv
        (_probe is NOT read by 02_preprocess.py -- its glob is non-recursive)

Run:  (.venv active)  python 00_probe.py
"""

from __future__ import annotations
import os
import sys
import json
import time

import pandas as pd

import config as cfg

# ---------------------------------------------------------------------------
DRY_RUN = True    # True = print the plan and worst-case cost, call nothing.
#                   ALWAYS dry-run first. Set False to run the probe.
# ---------------------------------------------------------------------------


def summarise(job: dict, items: list[dict]) -> dict:
    """One probe result -> one row of the volume-gate report.

    Estimates model what COLLECTION would do, not what the probe did:
      * saturated queries are blocked, so they get MAX_POSTS_PER_BLOCK per block
      * unsaturated queries run once, taking min(available, COLLECT_MAX_POSTS)
      * comments are capped at MAX_COMMENTS_PER_POST, not the probe's cap
    """
    posts = [i for i in items if i.get("dataType") == "post"]
    counts = [int(p.get("commentsCount") or 0) for p in posts]
    dates = sorted(p.get("createdAt", "") for p in posts if p.get("createdAt"))

    n_found = len(posts)
    saturated = n_found >= cfg.PROBE_MAX_POSTS

    # posts the real collection would fetch
    if saturated and cfg.BLOCKING_MODE != "none":
        n_blocks = len(cfg.build_windows())
        n_collect = cfg.MAX_POSTS_PER_BLOCK * n_blocks
        n_runs = n_blocks
    else:
        n_collect = min(n_found, cfg.COLLECT_MAX_POSTS)
        n_runs = 1

    # average stored comments per post at the COLLECTION cap
    if counts:
        stored_per_post = sum(min(c, cfg.MAX_COMMENTS_PER_POST) for c in counts) / len(counts)
    else:
        stored_per_post = 0.0

    est_comments = round(n_collect * stored_per_post)
    est_items = n_collect + est_comments

    return {
        "tier": job["tier"], "subreddit": job["subreddit"], "term": job["term"],
        "posts_found": n_found,
        "saturated": saturated,
        "will_block": bool(saturated and cfg.BLOCKING_MODE != "none"),
        "earliest_post": dates[0][:10] if dates else "",
        "latest_post": dates[-1][:10] if dates else "",
        "comments_available": sum(counts),
        "stored_per_post": round(stored_per_post, 1),
        "est_runs": n_runs,
        "est_collect_posts": n_collect,
        "est_collect_comments": est_comments,
        "est_collect_items": est_items,
        "est_collect_usd": round(cfg.estimate_cost(est_items, n_runs), 3),
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

    print(f"\n[probe] settings modelled: blocking={cfg.BLOCKING_MODE}, "
          f"{cfg.MAX_POSTS_PER_BLOCK} posts/block, {cfg.COLLECT_MAX_POSTS} posts/single, "
          f"{cfg.MAX_COMMENTS_PER_POST} comments/post")

    print("\n[probe] posts found per tier:")
    print(df.groupby("tier")["posts_found"].sum().to_string())

    print("\n[probe] estimated collection cost per tier (USD):")
    print(df.groupby("tier")["est_collect_usd"].sum().round(2).to_string())

    runs = int(df["est_runs"].sum())
    comments = int(df["est_collect_comments"].sum())
    total = df["est_collect_usd"].sum()
    print(f"\n[probe] projected: {runs:,} runs, {int(df.est_collect_posts.sum()):,} posts, "
          f"{comments:,} comments")
    print(f"[probe] TOTAL estimated collection cost: USD {total:.2f}"
          f"   (cap USD {cfg.BUDGET_USD_CAP:.2f}, ~AUD {total/cfg.AUD_USD:.0f})")

    already = cfg.spent_to_date()
    if already:
        print(f"[probe] already logged as spent: USD {already:.2f} "
              f"-> projected total USD {total+already:.2f}")

    if total > cfg.BUDGET_USD_CAP:
        print(f"[probe] OVER CAP by {total/cfg.BUDGET_USD_CAP:.1f}x. Levers, least damaging first:\n"
              f"        1. lower MAX_POSTS_PER_BLOCK (now {cfg.MAX_POSTS_PER_BLOCK})\n"
              f"        2. lower MAX_COMMENTS_PER_POST (now {cfg.MAX_COMMENTS_PER_POST}) "
              "-- costs thread depth\n"
              "        3. raise BUDGET_USD_CAP if the spend is justified\n"
              "        Re-run this script afterwards: it re-reads cached probe files, so "
              "re-estimating is FREE.")
    else:
        print("[probe] within cap.")

    print("\n[probe] earliest post reached, per subreddit (temporal coverage):")
    reach = df[df["earliest_post"] != ""]
    if len(reach):
        print(reach.groupby("subreddit")["earliest_post"].min().to_string())

    blocked = df[df["will_block"]]
    print(f"\n[probe] {len(blocked)} query/queries will be DATE-BLOCKED "
          f"({cfg.BLOCKING_MODE}); {len(df)-len(blocked)} run as single-window jobs.")

    empty = df[df["posts_found"] == 0]
    if len(empty):
        print(f"\n[probe] {len(empty)} query/queries returned NOTHING "
              "(retained deliberately -- absence is a result):")
        print(empty[["subreddit", "term"]].to_string(index=False))


def main() -> None:
    cfg.load_env()
    # the probe always measures the whole window in one run per query
    jobs = cfg.build_jobs(force_single_window=True)
    cfg.PROBE_DIR.mkdir(parents=True, exist_ok=True)

    todo = [j for j in jobs if not cfg.job_path(j, "probe").exists()]
    done = len(jobs) - len(todo)
    worst = cfg.estimate_cost(cfg.PROBE_MAX_POSTS * len(todo), len(todo))

    print("[plan] DIAGNOSTIC probe (posts only, no comments)")
    print(f"[plan] queries={len(jobs)}  already done={done}  to run={len(todo)}")
    print(f"[plan] window {cfg.STUDY_START}..{cfg.STUDY_END}")
    print(f"[plan] worst-case cost: USD {worst:.2f} "
          f"(<= {cfg.PROBE_MAX_POSTS} posts per query; most return fewer)")
    if done and not todo:
        print("[plan] all probe files cached -- this run only RE-ESTIMATES from them, "
              "at no cost.")

    if DRY_RUN and todo:
        print("\n[dry-run] first 15 queries:")
        for j in todo[:15]:
            print(f"   {j['tier']}  r/{j['subreddit']:<18} {j['term']:<28} "
                  f"{j['start']}..{j['end']}")
        if len(todo) > 15:
            print(f"   ... and {len(todo)-15} more")
        print("\n[dry-run] nothing was called. Set DRY_RUN = False to run the probe.")
        return

    spent = 0.0
    if todo:
        token = os.environ.get("APIFY_API_TOKEN", "").strip()
        if not token:
            sys.exit("[stop] No APIFY_API_TOKEN found. Put it in .env at the repo root.")
        from apify_client import ApifyClient
        client = ApifyClient(token)

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

            cfg.job_path(job, "probe").write_text(
                json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
            cost = cfg.estimate_cost(len(items))
            spent += cost
            print(f"   {len(items)} posts  ~USD {cost:.3f}  (running ~USD {spent:.2f})")
            time.sleep(1)

    # build the report from EVERY cached probe file, including earlier sessions
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
    print("[next] check the estimate against the cap, adjust config.py if needed "
          "(re-running this is free), then run 01_scrape.py")


if __name__ == "__main__":
    main()
