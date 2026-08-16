"""
01b_backfill_truncation.py -- targeted Scope C recovery of the old 60-post cap.

BACKGROUND
----------
Ten Tier 1 / Tier 2 queries were collected when COLLECT_MAX_POSTS was 60 even
though their probes observed between 60 and 99 posts.

The original production files are NOT deleted or overwritten.

For each agreed query this script:
  1. reads the existing full-study production JSON;
  2. verifies that it contains exactly 60 POST records;
  3. derives the backfill boundary from the earliest POST actually held;
  4. creates a custom backfill window from STUDY_START to that boundary;
  5. collects that window as an unblocked job, so COLLECT_MAX_POSTS applies;
  6. writes to a different filename because the end date differs;
  7. appends the run to the existing ten-column scrape_log.csv;
  8. compares probe post IDs with:
         original production post IDs UNION backfill post IDs
     and reports ID-level coverage.

The ID comparison reports what was actually recovered. It does NOT assume that
posts_found - 60 represents a guaranteed set of missing Reddit posts.

LOGGING CONVENTION
------------------
No new "backfill" column is added to scrape_log.csv. The existing production
log schema remains unchanged at ten columns.

Backfill runs can be identified from their custom end dates, which differ from
the normal full-study end date and normal annual-block end dates.

BOUNDARY OVERLAP
----------------
The boundary date is deliberately reused as postedBefore. If the actor returns
records that overlap with the existing file, 02_preprocess.py performs
cross-file deduplication by Reddit id.

CRAWL-DATE / SCORE NOTE
-----------------------
02_preprocess.py reads sorted data/raw/*.json files and deduplicates by id with
keep="first". A backfill filename can sort before the original full-window file.
If an overlapping comment appears in both files, the retained copy may therefore
be the backfill-crawl version.

Reddit score is captured at crawl time and may differ between crawls. This is
harmless if score is not used analytically, but must be documented if score is
later analysed.

CAP INTERACTION
---------------
COLLECT_MAX_POSTS is now 100, equal to PROBE_MAX_POSTS. Therefore these
backfills are no longer restricted by the old 60-post single-window cap. This
does not prove exhaustive Reddit coverage, but it removes the known lower-cap
truncation mechanism.

SEQUENCING
----------
This script handles only the ten Scope C Tier 1 / Tier 2 backfills.

It does NOT call cfg.build_jobs().
It does NOT run the 26 prospective Tier 3 jobs.
It does NOT implement or run C2 supplementary sampling.

Tier 3 and Scope C must be completed and verified before C2 is enabled.

Run:
    (.venv active) python 01b_backfill_truncation.py

ALWAYS run first with DRY_RUN = True.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

import config as cfg


# ---------------------------------------------------------------------------
DRY_RUN = True
MAX_LIVE_JOBS = 1
# True = inspect files, derive windows and print the plan. No Apify calls.
# Set False only after the complete dry-run output has been checked.
# ---------------------------------------------------------------------------


OLD_COLLECT_MAX_POSTS = 60

# Used only for the forward cost estimate.
# This is an empirical modelling assumption, not a measured backfill yield.
CPP = 9.4


# Exact ten Tier 1 / Tier 2 queries approved for Scope C.
AFFECTED = [
    ("Tier 1", "SelfDrivingCars", "robotaxi"),
    ("Tier 1", "Waymo", "Waymo"),
    ("Tier 1", "Waymo", "autonomous vehicle"),
    ("Tier 1", "teslamotors", "LiDAR"),
    ("Tier 1", "teslamotors", "robotaxi"),
    ("Tier 2", "Futurology", "LiDAR"),
    ("Tier 2", "Futurology", "robotaxi"),
    ("Tier 2", "cars", "autonomous vehicle"),
    ("Tier 2", "electricvehicles", "autonomous vehicle"),
    ("Tier 2", "electricvehicles", "robotaxi"),
]


# Must remain identical to the existing 01_scrape.py audit-log schema.
LOG_COLUMNS = [
    "timestamp",
    "tier",
    "subreddit",
    "term",
    "start",
    "end",
    "blocked",
    "items",
    "comments",
    "est_usd",
]


def source_job(tier: str, subreddit: str, term: str) -> dict:
    """Return the original full-study production job."""
    return {
        "tier": tier,
        "subreddit": subreddit,
        "term": term,
        "start": cfg.STUDY_START,
        "end": cfg.STUDY_END,
        "blocked": False,
    }


def load_json_list(path: Path, label: str) -> list[dict]:
    """Read a raw/probe JSON file and require the normal list structure."""
    if not path.exists():
        raise SystemExit(f"[stop] {label} file does not exist: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(
            f"[stop] could not read {label} file {path}: "
            f"{type(exc).__name__}: {exc}"
        )

    if not isinstance(data, list):
        raise SystemExit(
            f"[stop] expected a JSON list in {label} file: {path}"
        )

    return data


def post_records(items: list[dict]) -> list[dict]:
    """Keep only Reddit POST records."""
    return [
        item
        for item in items
        if isinstance(item, dict)
        and str(item.get("dataType", "")).lower() == "post"
    ]


def post_ids(items: list[dict], label: str) -> set[str]:
    """
    Return unique non-empty post IDs.

    Coverage is assessed by Reddit post ID rather than by row position or date.
    """
    posts = post_records(items)

    ids = {
        str(item.get("id")).strip()
        for item in posts
        if item.get("id") is not None
        and str(item.get("id")).strip()
    }

    if len(ids) != len(posts):
        print(
            f"[check] WARNING: {label} contains {len(posts)} post records "
            f"but {len(ids)} unique non-empty post IDs"
        )

    return ids


def validate_log_schema() -> None:
    """Refuse to append if the existing audit-log header is not the expected one."""
    if not cfg.LOG_CSV.exists():
        return

    try:
        columns = pd.read_csv(cfg.LOG_CSV, nrows=0).columns.tolist()
    except Exception as exc:
        raise SystemExit(
            f"[stop] could not inspect audit-log header {cfg.LOG_CSV}: "
            f"{type(exc).__name__}: {exc}"
        )

    if columns != LOG_COLUMNS:
        raise SystemExit(
            "[stop] scrape_log.csv schema differs from the expected ten-column "
            "01_scrape.py schema.\n"
            f"expected={LOG_COLUMNS}\n"
            f"found={columns}"
        )


def log_run(job: dict, n_items: int, n_comments: int, cost: float) -> None:
    """Append using exactly the same ten fields as 01_scrape.py."""
    validate_log_schema()

    cfg.LOG_CSV.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "tier": job["tier"],
        "subreddit": job["subreddit"],
        "term": job["term"],
        "start": job["start"],
        "end": job["end"],
        "blocked": job.get("blocked", False),
        "items": n_items,
        "comments": n_comments,
        "est_usd": round(cost, 4),
    }

    pd.DataFrame(
        [row],
        columns=LOG_COLUMNS,
    ).to_csv(
        cfg.LOG_CSV,
        mode="a",
        header=not cfg.LOG_CSV.exists(),
        index=False,
    )


def earliest_held_post_date(job: dict) -> tuple[str, int]:
    """
    Derive the Scope C boundary from the actual existing production JSON.

    The probe's earliest date is deliberately NOT used.
    """
    path = cfg.job_path(job, "collect")
    items = load_json_list(path, "source production")

    posts = post_records(items)

    if len(posts) != OLD_COLLECT_MAX_POSTS:
        raise SystemExit(
            f"[stop] expected exactly {OLD_COLLECT_MAX_POSTS} held posts in "
            f"{path}, found {len(posts)}. Re-check this query before backfilling."
        )

    dates = pd.to_datetime(
        [item.get("createdAt") for item in posts],
        utc=True,
        errors="coerce",
    )

    if dates.isna().any():
        raise SystemExit(
            f"[stop] one or more held posts have an invalid createdAt in {path}"
        )

    earliest = dates.min().date().isoformat()

    return earliest, len(posts)


def read_probe_expectations() -> dict[tuple[str, str, str], dict]:
    """
    Read the original probe observations for the exact ten Scope C queries.

    Also verify that each probe JSON's number of POST records agrees with the
    posts_found value recorded in probe_report.csv.
    """
    if not cfg.PROBE_REPORT.exists():
        raise SystemExit(
            f"[stop] probe report does not exist: {cfg.PROBE_REPORT}"
        )

    df = pd.read_csv(cfg.PROBE_REPORT)

    required = {"tier", "subreddit", "term", "posts_found"}
    missing = required - set(df.columns)

    if missing:
        raise SystemExit(
            f"[stop] probe report missing required column(s): {sorted(missing)}"
        )

    expectations: dict[tuple[str, str, str], dict] = {}

    for tier, subreddit, term in AFFECTED:
        key = (tier, subreddit, term)

        row = df[
            (df["tier"] == tier)
            & (df["subreddit"] == subreddit)
            & (df["term"] == term)
        ]

        if len(row) != 1:
            raise SystemExit(
                f"[stop] expected exactly one probe-report row for "
                f"{tier} | r/{subreddit} | {term}; found {len(row)}"
            )

        posts_found = int(row.iloc[0]["posts_found"])

        if not (
            OLD_COLLECT_MAX_POSTS
            <= posts_found
            < cfg.PROBE_MAX_POSTS
        ):
            raise SystemExit(
                f"[stop] query no longer matches the original 60-99 "
                f"truncation band: {tier} | r/{subreddit} | {term} | "
                f"posts_found={posts_found}"
            )

        probe_job = source_job(tier, subreddit, term)
        probe_path = cfg.job_path(probe_job, "probe")
        probe_items = load_json_list(probe_path, "probe")
        probe_posts = post_records(probe_items)

        if len(probe_posts) != posts_found:
            raise SystemExit(
                f"[stop] probe-report/file mismatch for "
                f"{tier} | r/{subreddit} | {term}: "
                f"probe_report posts_found={posts_found}, "
                f"probe JSON POST records={len(probe_posts)}"
            )

        expectations[key] = {
            "posts_found": posts_found,
            "above_old_cap": posts_found - OLD_COLLECT_MAX_POSTS,
            "probe_path": probe_path,
        }

    return expectations


def build_backfill_jobs() -> list[dict]:
    """Build exactly ten jobs using measured earliest-held production dates."""
    jobs: list[dict] = []

    for tier, subreddit, term in AFFECTED:
        original = source_job(tier, subreddit, term)
        earliest, held_posts = earliest_held_post_date(original)

        if held_posts != OLD_COLLECT_MAX_POSTS:
            raise SystemExit(
                f"[stop] unexpected held-post count for "
                f"{tier} | r/{subreddit} | {term}"
            )

        if earliest <= cfg.STUDY_START:
            raise SystemExit(
                f"[stop] earliest held post {earliest} is not after "
                f"STUDY_START={cfg.STUDY_START} for "
                f"{tier} | r/{subreddit} | {term}"
            )

        jobs.append(
            {
                "tier": tier,
                "subreddit": subreddit,
                "term": term,
                "start": cfg.STUDY_START,
                "end": earliest,
                "blocked": False,
            }
        )

    return jobs


def coverage_stats(
    job: dict,
    expectations: dict[tuple[str, str, str], dict],
) -> dict:
    """
    Compare probe post IDs against original production UNION backfill.

    "Recovered" means a probe ID absent from the original production file but
    present in the backfill file.
    """
    key = (job["tier"], job["subreddit"], job["term"])
    expected = expectations[key]

    original = source_job(
        job["tier"],
        job["subreddit"],
        job["term"],
    )

    original_path = cfg.job_path(original, "collect")
    backfill_path = cfg.job_path(job, "collect")
    probe_path = expected["probe_path"]

    original_items = load_json_list(original_path, "source production")
    backfill_items = load_json_list(backfill_path, "backfill")
    probe_items = load_json_list(probe_path, "probe")

    original_ids = post_ids(
        original_items,
        f"original {job['subreddit']} | {job['term']}",
    )

    backfill_ids = post_ids(
        backfill_items,
        f"backfill {job['subreddit']} | {job['term']}",
    )

    probe_ids = post_ids(
        probe_items,
        f"probe {job['subreddit']} | {job['term']}",
    )

    matched_original = probe_ids & original_ids

    recovered = (
        probe_ids
        - original_ids
    ) & backfill_ids

    represented = probe_ids & (
        original_ids | backfill_ids
    )

    unaccounted = probe_ids - (
        original_ids | backfill_ids
    )

    new_backfill_vs_original = backfill_ids - original_ids

    return {
        "probe_ids": len(probe_ids),
        "original_ids": len(original_ids),
        "backfill_ids": len(backfill_ids),
        "matched_original": len(matched_original),
        "recovered": len(recovered),
        "represented": len(represented),
        "unaccounted": len(unaccounted),
        "new_backfill_vs_original": len(new_backfill_vs_original),
    }


def print_coverage(
    job: dict,
    expectations: dict[tuple[str, str, str], dict],
) -> dict:
    """Print the ID-level recovery result for one completed backfill."""
    stats = coverage_stats(job, expectations)

    print("   [coverage]")
    print(
        f"      probe unique post IDs:                    "
        f"{stats['probe_ids']}"
    )
    print(
        f"      original production unique post IDs:      "
        f"{stats['original_ids']}"
    )
    print(
        f"      backfill unique post IDs:                 "
        f"{stats['backfill_ids']}"
    )
    print(
        f"      probe IDs already in original:            "
        f"{stats['matched_original']}"
    )
    print(
        f"      probe IDs newly recovered by backfill:    "
        f"{stats['recovered']}"
    )
    print(
        f"      probe IDs represented after union:        "
        f"{stats['represented']}"
    )
    print(
        f"      probe IDs still unaccounted for:          "
        f"{stats['unaccounted']}"
    )
    print(
        f"      all new backfill post IDs vs original:    "
        f"{stats['new_backfill_vs_original']}"
    )

    return stats


def main() -> None:
    cfg.load_env()
    cfg.RAW_DIR.mkdir(parents=True, exist_ok=True)

    validate_log_schema()

    if cfg.COLLECT_MAX_POSTS < cfg.PROBE_MAX_POSTS:
        raise SystemExit(
            "[stop] COLLECT_MAX_POSTS has fallen below PROBE_MAX_POSTS. "
            "The sampling-cap invariant is no longer satisfied."
        )

    expectations = read_probe_expectations()
    jobs = build_backfill_jobs()

    if len(jobs) != 10:
        raise SystemExit(
            f"[stop] expected exactly 10 Scope C jobs; built {len(jobs)}"
        )

    todo = [
        job
        for job in jobs
        if not cfg.job_path(job, "collect").exists()
    ]

    done = len(jobs) - len(todo)

    expected_posts = sum(
        expectations[
            (
                job["tier"],
                job["subreddit"],
                job["term"],
            )
        ]["above_old_cap"]
        for job in todo
    )

    modelled_items = expected_posts * (1 + CPP)

    estimated_cost = cfg.estimate_cost(
        modelled_items,
        len(todo),
    )

    max_comments_per_run = min(
        cfg.MAX_COMMENTS_PER_RUN,
        cfg.COLLECT_MAX_POSTS * cfg.MAX_COMMENTS_PER_POST,
    )

    configured_max_items_per_run = (
        cfg.COLLECT_MAX_POSTS
        + max_comments_per_run
    )

    configured_cap_cost = cfg.estimate_cost(
        configured_max_items_per_run * len(todo),
        len(todo),
    )

    already = cfg.spent_to_date()
    remaining_budget = cfg.BUDGET_USD_CAP - already

    print("[plan] SCOPE C truncation backfill")
    print(
        f"[plan] agreed queries={len(jobs)}  "
        f"already done={done}  to run={len(todo)}"
    )
    print(
        f"[plan] COLLECT_MAX_POSTS={cfg.COLLECT_MAX_POSTS}  "
        f"PROBE_MAX_POSTS={cfg.PROBE_MAX_POSTS}"
    )
    print(
        f"[plan] comments/post={cfg.MAX_COMMENTS_PER_POST}  "
        f"comments/run={cfg.MAX_COMMENTS_PER_RUN}"
    )
    print(
        f"[plan] logged spend USD {already:.2f} | "
        f"budget cap USD {cfg.BUDGET_USD_CAP:.2f} | "
        f"logged-basis remaining USD {remaining_budget:.2f}"
    )
    print(
        f"[plan] probe-observed posts above old 60-post cap "
        f"for remaining jobs={expected_posts}"
    )
    print(
        f"[plan] modelled backfill cost ~USD {estimated_cost:.2f} "
        f"(estimate only)"
    )
    print(
        f"[plan] configured-cap cost if every remaining run returned "
        f"the maximum modelled items ~USD {configured_cap_cost:.2f}"
    )

    if estimated_cost > remaining_budget:
        print(
            "[plan] WARNING: modelled backfill cost exceeds "
            "logged-basis remaining budget."
        )

    print("\n[plan] backfill jobs:")

    for n, job in enumerate(jobs, 1):
        key = (
            job["tier"],
            job["subreddit"],
            job["term"],
        )

        original = source_job(
            job["tier"],
            job["subreddit"],
            job["term"],
        )

        source_path = cfg.job_path(
            original,
            "collect",
        )

        output_path = cfg.job_path(
            job,
            "collect",
        )

        state = (
            "DONE"
            if output_path.exists()
            else "TODO"
        )

        if output_path == source_path:
            raise SystemExit(
                f"[stop] backfill output would collide with "
                f"source file: {output_path}"
            )

        print(
            f"{n:>2}. {state} | "
            f"{job['tier']} | "
            f"r/{job['subreddit']} | "
            f"{job['term']}"
        )
        print(
            f"    source:   {source_path}"
        )
        print(
            f"    backfill: "
            f"{job['start']}..{job['end']} | "
            f"probe-observed above old cap="
            f"{expectations[key]['above_old_cap']}"
        )
        print(
            f"    output:   {output_path}"
        )

        if output_path.exists():
            print_coverage(
                job,
                expectations,
            )

    if DRY_RUN:
        print(
            "\n[dry-run] nothing was called. "
            "DRY_RUN remains True."
        )
        return

    if not todo:
        print(
            "\n[done] all ten backfill files already exist; "
            "nothing to run."
        )
        return

    token = os.environ.get(
        "APIFY_API_TOKEN",
        "",
    ).strip()

    if not token:
        sys.exit(
            "[stop] No APIFY_API_TOKEN found. "
            "Put it in .env at the repo root."
        )

    from apify_client import ApifyClient

    client = ApifyClient(token)

    session_spend = 0.0
    total_items = 0
    total_comments = 0

    for n, job in enumerate(todo[:MAX_LIVE_JOBS], 1):
        cumulative = already + session_spend

        if cumulative >= cfg.BUDGET_USD_CAP:
            print(
                f"\n[stop] cumulative logged budget cap "
                f"USD {cfg.BUDGET_USD_CAP:.2f} reached "
                f"(~USD {cumulative:.2f}). "
                f"{len(todo) - n + 1} backfill job(s) not run."
            )
            break

        output_path = cfg.job_path(
            job,
            "collect",
        )

        if output_path.exists():
            print(
                f"\n[{n}/{len(todo)}] SKIP existing backfill: "
                f"{output_path}"
            )
            continue

        print(
            f"\n[{n}/{len(todo)}] BACKFILL  "
            f"r/{job['subreddit']} | "
            f"{job['term']}  "
            f"{job['start']}..{job['end']}"
        )

        try:
            run = client.actor(
                cfg.ACTOR_ID
            ).call(
                run_input=cfg.collect_input(job)
            )

            if run is None:
                print(
                    "   ! run returned None -- "
                    "skipping; rerun later to retry"
                )
                continue

            dataset_id = (
                getattr(
                    run,
                    "default_dataset_id",
                    None,
                )
                or run["defaultDatasetId"]
            )

            items = list(
                client.dataset(
                    dataset_id
                ).iterate_items()
            )

        except Exception as exc:
            print(
                f"   ! failed: "
                f"{type(exc).__name__}: {exc}"
            )
            continue

        if output_path.exists():
            raise SystemExit(
                f"[stop] refusing to overwrite "
                f"existing backfill file: {output_path}"
            )

        output_path.write_text(
            json.dumps(
                items,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        n_comments = sum(
            1
            for item in items
            if item.get("dataType") == "comment"
        )

        cost = cfg.estimate_cost(
            len(items)
        )

        session_spend += cost
        total_items += len(items)
        total_comments += n_comments

        log_run(
            job,
            len(items),
            n_comments,
            cost,
        )

        print(
            f"   {len(items)} items "
            f"({n_comments} comments)  "
            f"~USD {cost:.3f}  "
            f"(logged cumulative "
            f"~USD {already + session_spend:.2f})"
        )

        print_coverage(
            job,
            expectations,
        )

        time.sleep(1)

    remaining = [
        job
        for job in jobs
        if not cfg.job_path(
            job,
            "collect",
        ).exists()
    ]

    print(
        f"\n[done] this session: "
        f"{total_items:,} items, "
        f"{total_comments:,} comments, "
        f"~USD {session_spend:.2f}"
    )

    print(
        f"[done] logged cumulative spend "
        f"~USD {already + session_spend:.2f}"
    )

    print(
        f"[done] "
        f"{len(jobs) - len(remaining)}/"
        f"{len(jobs)} backfill jobs complete; "
        f"{len(remaining)} remaining"
    )

    if not remaining:
        print(
            "\n[coverage] final ID-level check "
            "for all ten Scope C queries:"
        )

        for job in jobs:
            print(
                f"\n{job['tier']} | "
                f"r/{job['subreddit']} | "
                f"{job['term']}"
            )

            print_coverage(
                job,
                expectations,
            )


if __name__ == "__main__":
    main()