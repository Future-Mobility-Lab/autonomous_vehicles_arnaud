"""
01c_recover_probe_posts.py -- direct recovery of the probe posts omitted from
the original 60-post Tier 1/2 production runs.

The old "missing posts are the oldest tail" assumption was falsified by ID-level
comparison: 29 of 132 absent probe IDs post-date the earliest held post in their
query. Therefore this script does not use date-tail backfills. It reconstructs
the 132 query-level missing probe IDs, removes the 8 already present elsewhere
in top-level data/raw/*.json, and directly targets the remaining 124 stored
postUrl values.

Recovery is grouped into the same ten affected (tier, subreddit, term) groups.

For each batch, limits are derived from len(urls):

    maxPostsCount = len(urls)
    maxCommentsPerPost = cfg.MAX_COMMENTS_PER_POST
    maxCommentsCount = len(urls) * cfg.MAX_COMMENTS_PER_POST

The script refuses a batch if maxCommentsCount exceeds MAX_COMMENTS_PER_RUN.

Recovery files use:

    data/raw/<subreddit>__<term>__recovery.json

so they cannot collide with standard date-range job filenames. They remain
visible to 02_preprocess.py but outside 01_scrape.py's standard resume logic.

scrape_log.csv stays at ten columns. Recovery rows use:

    start = "recovery"
    end = "direct_url"
    blocked = False

A separate data/raw/recovery_manifest.csv records the status of all 132
query-level missing IDs. It is a CSV, so 02_preprocess.py ignores it.

DRY_RUN=True makes no Apify calls and writes no recovery/manifest/log files.

MAX_LIVE_BATCHES limits paid batches per execution. Batches are ordered from
smallest to largest for cautious live validation.

The direct recovery keeps maxCommentsPerPost at the project cap of 15. After
final preprocessing, separately verify that the maximum comments per
parsedPostId remains <= 15.

This script does not run prospective Tier 3 and does not implement C2.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

import config as cfg


# ---------------------------------------------------------------------------
DRY_RUN = True
MAX_LIVE_BATCHES = 1
# ---------------------------------------------------------------------------

OLD_COLLECT_MAX_POSTS = 60
CPP = 9.4

EXPECTED_QUERY_LEVEL_MISSING = 132
EXPECTED_UNIQUE_QUERY_TARGETS = 132
EXPECTED_ALREADY_PRESENT_ELSEWHERE = 8
EXPECTED_GLOBAL_RECOVERY_TARGETS = 124

MANIFEST_CSV = cfg.RAW_DIR / "recovery_manifest.csv"

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


def load_json_list(path: Path, label: str) -> list[dict]:
    if not path.exists():
        raise SystemExit(
            f"[stop] {label} file does not exist: {path}"
        )

    try:
        data = json.loads(
            path.read_text(encoding="utf-8")
        )
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
    return [
        item
        for item in items
        if isinstance(item, dict)
        and str(item.get("dataType", "")).lower() == "post"
    ]


def post_ids(items: list[dict]) -> set[str]:
    return {
        str(item.get("id")).strip()
        for item in post_records(items)
        if item.get("id") is not None
        and str(item.get("id")).strip()
    }


def source_job(
    tier: str,
    subreddit: str,
    term: str,
) -> dict:
    return {
        "tier": tier,
        "subreddit": subreddit,
        "term": term,
        "start": cfg.STUDY_START,
        "end": cfg.STUDY_END,
        "blocked": False,
    }


def recovery_path(
    subreddit: str,
    term: str,
) -> Path:
    return cfg.RAW_DIR / (
        f"{cfg.slug(subreddit)}__"
        f"{cfg.slug(term)}__recovery.json"
    )


def validate_log_schema() -> None:
    if not cfg.LOG_CSV.exists():
        return

    try:
        columns = pd.read_csv(
            cfg.LOG_CSV,
            nrows=0,
        ).columns.tolist()
    except Exception as exc:
        raise SystemExit(
            f"[stop] could not inspect {cfg.LOG_CSV}: "
            f"{type(exc).__name__}: {exc}"
        )

    if columns != LOG_COLUMNS:
        raise SystemExit(
            "[stop] scrape_log.csv is not the expected "
            "ten-column schema.\n"
            f"expected={LOG_COLUMNS}\n"
            f"found={columns}"
        )


def log_run(
    batch: dict,
    n_items: int,
    n_comments: int,
    cost: float,
) -> None:
    validate_log_schema()

    row = {
        "timestamp": datetime.now().isoformat(
            timespec="seconds"
        ),
        "tier": batch["tier"],
        "subreddit": batch["subreddit"],
        "term": batch["term"],
        "start": "recovery",
        "end": "direct_url",
        "blocked": False,
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


def derive_query_missing() -> list[dict]:
    if not cfg.PROBE_REPORT.exists():
        raise SystemExit(
            f"[stop] missing probe report: "
            f"{cfg.PROBE_REPORT}"
        )

    report = pd.read_csv(
        cfg.PROBE_REPORT
    )

    required = {
        "tier",
        "subreddit",
        "term",
        "posts_found",
    }

    missing_columns = required - set(
        report.columns
    )

    if missing_columns:
        raise SystemExit(
            f"[stop] probe report missing columns: "
            f"{sorted(missing_columns)}"
        )

    rows: list[dict] = []

    for tier, subreddit, term in AFFECTED:
        match = report[
            (report["tier"] == tier)
            & (report["subreddit"] == subreddit)
            & (report["term"] == term)
        ]

        if len(match) != 1:
            raise SystemExit(
                f"[stop] expected one probe-report row for "
                f"{tier} | r/{subreddit} | {term}; "
                f"found {len(match)}"
            )

        posts_found = int(
            match.iloc[0]["posts_found"]
        )

        if not (
            OLD_COLLECT_MAX_POSTS
            <= posts_found
            < cfg.PROBE_MAX_POSTS
        ):
            raise SystemExit(
                f"[stop] query is no longer in the "
                f"original 60-99 band: "
                f"{tier} | r/{subreddit} | {term} | "
                f"posts_found={posts_found}"
            )

        job = source_job(
            tier,
            subreddit,
            term,
        )

        probe_path = cfg.job_path(
            job,
            "probe",
        )

        source_path = cfg.job_path(
            job,
            "collect",
        )

        probe = load_json_list(
            probe_path,
            "probe",
        )

        source = load_json_list(
            source_path,
            "source production",
        )

        probe_posts = post_records(
            probe
        )

        source_posts = post_records(
            source
        )

        if len(probe_posts) != posts_found:
            raise SystemExit(
                f"[stop] probe report/file mismatch for "
                f"{tier} | r/{subreddit} | {term}: "
                f"report={posts_found}, "
                f"JSON={len(probe_posts)}"
            )

        if len(source_posts) != OLD_COLLECT_MAX_POSTS:
            raise SystemExit(
                f"[stop] expected 60 source posts for "
                f"{tier} | r/{subreddit} | {term}; "
                f"found {len(source_posts)}"
            )

        held_ids = post_ids(
            source
        )

        for post in probe_posts:
            post_id = str(
                post.get("id", "")
            ).strip()

            if not post_id:
                raise SystemExit(
                    f"[stop] probe post without id in "
                    f"{tier} | r/{subreddit} | {term}"
                )

            if post_id in held_ids:
                continue

            post_url = str(
                post.get("postUrl", "")
            ).strip()

            if not post_url:
                raise SystemExit(
                    f"[stop] missing postUrl for "
                    f"target {post_id}"
                )

            parsed_id = (
                post_id[3:]
                if post_id.startswith("t3_")
                else post_id
            )

            if (
                f"/comments/"
                f"{parsed_id.lower()}/"
                not in post_url.lower()
            ):
                raise SystemExit(
                    f"[stop] postUrl does not match "
                    f"target id {post_id}: "
                    f"{post_url}"
                )

            rows.append(
                {
                    "tier": tier,
                    "subreddit": subreddit,
                    "term": term,
                    "post_id": post_id,
                    "post_url": post_url,
                    "probe_created_at": post.get(
                        "createdAt"
                    ),
                }
            )

    if (
        len(rows)
        != EXPECTED_QUERY_LEVEL_MISSING
    ):
        raise SystemExit(
            f"[stop] expected "
            f"{EXPECTED_QUERY_LEVEL_MISSING} "
            f"query-level missing IDs; "
            f"found {len(rows)}"
        )

    unique_ids = {
        row["post_id"]
        for row in rows
    }

    if (
        len(unique_ids)
        != EXPECTED_UNIQUE_QUERY_TARGETS
    ):
        raise SystemExit(
            f"[stop] expected "
            f"{EXPECTED_UNIQUE_QUERY_TARGETS} "
            f"unique query-level target IDs; "
            f"found {len(unique_ids)}"
        )

    return rows


def baseline_global_ids() -> tuple[
    set[str],
    list[Path],
]:
    """
    Reconstruct the pre-recovery top-level corpus.

    Existing *__recovery.json files are excluded so resumed
    runs retain the same original baseline.
    """

    files = sorted(
        path
        for path in cfg.RAW_DIR.glob("*.json")
        if not path.name.endswith(
            "__recovery.json"
        )
    )

    ids: set[str] = set()

    for path in files:
        items = load_json_list(
            path,
            "top-level raw",
        )

        ids.update(
            post_ids(items)
        )

    return ids, files


def classify_targets(
    query_missing: list[dict],
) -> tuple[
    list[dict],
    list[dict],
]:
    baseline_ids, _ = (
        baseline_global_ids()
    )

    already_elsewhere: list[dict] = []
    recovery_targets: list[dict] = []

    for row in query_missing:
        present = (
            row["post_id"]
            in baseline_ids
        )

        row[
            "baseline_present_elsewhere"
        ] = present

        if present:
            already_elsewhere.append(
                row
            )
        else:
            recovery_targets.append(
                row
            )

    if (
        len(already_elsewhere)
        != EXPECTED_ALREADY_PRESENT_ELSEWHERE
    ):
        raise SystemExit(
            f"[stop] expected "
            f"{EXPECTED_ALREADY_PRESENT_ELSEWHERE} "
            f"IDs already present elsewhere; "
            f"found {len(already_elsewhere)}"
        )

    if (
        len(recovery_targets)
        != EXPECTED_GLOBAL_RECOVERY_TARGETS
    ):
        raise SystemExit(
            f"[stop] expected "
            f"{EXPECTED_GLOBAL_RECOVERY_TARGETS} "
            f"globally absent targets; "
            f"found {len(recovery_targets)}"
        )

    return (
        already_elsewhere,
        recovery_targets,
    )


def build_batches(
    recovery_targets: list[dict],
) -> list[dict]:
    grouped: dict[
        tuple[str, str, str],
        list[dict],
    ] = defaultdict(list)

    for row in recovery_targets:
        key = (
            row["tier"],
            row["subreddit"],
            row["term"],
        )

        grouped[key].append(
            row
        )

    batches: list[dict] = []

    for tier, subreddit, term in AFFECTED:
        rows = sorted(
            grouped[
                (
                    tier,
                    subreddit,
                    term,
                )
            ],
            key=lambda row: (
                str(
                    row.get(
                        "probe_created_at"
                    )
                    or ""
                ),
                row["post_id"],
            ),
        )

        if not rows:
            raise SystemExit(
                f"[stop] no recovery targets "
                f"for {tier} | "
                f"r/{subreddit} | {term}"
            )

        urls = [
            row["post_url"]
            for row in rows
        ]

        if len(set(urls)) != len(urls):
            raise SystemExit(
                f"[stop] duplicate postUrl "
                f"in {tier} | "
                f"r/{subreddit} | {term}"
            )

        n_targets = len(
            urls
        )

        max_comments = (
            n_targets
            * cfg.MAX_COMMENTS_PER_POST
        )

        if (
            max_comments
            > cfg.MAX_COMMENTS_PER_RUN
        ):
            raise SystemExit(
                f"[stop] derived "
                f"maxCommentsCount="
                f"{max_comments} exceeds "
                f"MAX_COMMENTS_PER_RUN="
                f"{cfg.MAX_COMMENTS_PER_RUN}"
            )

        batches.append(
            {
                "tier": tier,
                "subreddit": subreddit,
                "term": term,
                "targets": rows,
                "target_ids": {
                    row["post_id"]
                    for row in rows
                },
                "urls": urls,
                "n_targets": n_targets,
                "max_posts": n_targets,
                "max_comments": max_comments,
                "output": recovery_path(
                    subreddit,
                    term,
                ),
            }
        )

    if len(batches) != len(AFFECTED):
        raise SystemExit(
            f"[stop] expected "
            f"{len(AFFECTED)} batches; "
            f"built {len(batches)}"
        )

    # Smallest batches first for
    # low-cost live validation.
    return sorted(
        batches,
        key=lambda batch: (
            batch["n_targets"],
            batch["tier"],
            batch["subreddit"].lower(),
            batch["term"].lower(),
        ),
    )


def batch_status(
    batch: dict,
) -> dict:
    output = batch["output"]

    if not output.exists():
        return {
            "state": "PENDING",
            "recovered": set(),
            "missing": set(
                batch["target_ids"]
            ),
            "extras": set(),
            "posts": 0,
            "comments": 0,
        }

    items = load_json_list(
        output,
        "recovery output",
    )

    returned_ids = post_ids(
        items
    )

    target_ids = set(
        batch["target_ids"]
    )

    recovered = (
        returned_ids
        & target_ids
    )

    missing = (
        target_ids
        - returned_ids
    )

    extras = (
        returned_ids
        - target_ids
    )

    state = (
        "DONE"
        if not missing
        else "PARTIAL"
    )

    comments = sum(
        1
        for item in items
        if isinstance(item, dict)
        and str(
            item.get(
                "dataType",
                "",
            )
        ).lower() == "comment"
    )

    return {
        "state": state,
        "recovered": recovered,
        "missing": missing,
        "extras": extras,
        "posts": len(
            post_records(items)
        ),
        "comments": comments,
    }


def build_run_input(
    batch: dict,
) -> dict:
    n_targets = len(
        batch["urls"]
    )

    max_comments = (
        n_targets
        * cfg.MAX_COMMENTS_PER_POST
    )

    if n_targets != batch["n_targets"]:
        raise SystemExit(
            "[stop] target/url count mismatch"
        )

    if (
        max_comments
        > cfg.MAX_COMMENTS_PER_RUN
    ):
        raise SystemExit(
            "[stop] derived comment cap "
            "exceeds MAX_COMMENTS_PER_RUN"
        )

    return {
        "startUrls": [
            {
                "url": url
            }
            for url in batch["urls"]
        ],
        "crawlCommentsPerPost": True,
        "maxPostsCount": n_targets,
        "maxCommentsPerPost":
            cfg.MAX_COMMENTS_PER_POST,
        "maxCommentsCount":
            max_comments,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": [
                "RESIDENTIAL"
            ],
        },
    }


def manifest_dataframe(
    query_missing: list[dict],
    batches: list[dict],
) -> pd.DataFrame:
    batch_map = {
        (
            batch["tier"],
            batch["subreddit"],
            batch["term"],
        ): batch
        for batch in batches
    }

    rows: list[dict] = []

    for target in query_missing:
        baseline_present = bool(
            target[
                "baseline_present_elsewhere"
            ]
        )

        recovery_required = (
            not baseline_present
        )

        recovered = False
        output = ""

        if baseline_present:
            status = (
                "already_present_elsewhere"
            )

        else:
            key = (
                target["tier"],
                target["subreddit"],
                target["term"],
            )

            batch = batch_map[key]

            output = str(
                batch["output"]
            )

            state = batch_status(
                batch
            )

            if state["state"] == "PENDING":
                status = "pending"

            elif (
                target["post_id"]
                in state["recovered"]
            ):
                recovered = True
                status = "recovered"

            else:
                status = (
                    "unaccounted_in_"
                    "recovery_file"
                )

        rows.append(
            {
                "tier": target["tier"],
                "subreddit":
                    target["subreddit"],
                "term": target["term"],
                "post_id":
                    target["post_id"],
                "post_url":
                    target["post_url"],
                "probe_created_at":
                    target[
                        "probe_created_at"
                    ],
                "baseline_present_elsewhere":
                    baseline_present,
                "recovery_required":
                    recovery_required,
                "recovery_file":
                    output,
                "recovered_by_direct":
                    recovered,
                "status":
                    status,
            }
        )

    return pd.DataFrame(
        rows
    )


def write_manifest(
    query_missing: list[dict],
    batches: list[dict],
) -> None:
    MANIFEST_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    manifest_dataframe(
        query_missing,
        batches,
    ).to_csv(
        MANIFEST_CSV,
        index=False,
    )


def print_batch(
    number: int,
    batch: dict,
) -> None:
    state = batch_status(
        batch
    )

    print(
        f"{number:>2}. "
        f"{state['state']:<7} | "
        f"{batch['tier']} | "
        f"r/{batch['subreddit']} | "
        f"{batch['term']} | "
        f"targets={batch['n_targets']} | "
        f"maxPosts={batch['max_posts']} | "
        f"maxComments={batch['max_comments']}"
    )

    print(
        f"    output: "
        f"{batch['output']}"
    )

    if state["state"] != "PENDING":
        print(
            f"    recovered="
            f"{len(state['recovered'])}/"
            f"{batch['n_targets']} | "
            f"posts={state['posts']} | "
            f"comments={state['comments']} | "
            f"extra post IDs="
            f"{len(state['extras'])}"
        )


def main() -> None:
    cfg.load_env()

    cfg.RAW_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    validate_log_schema()

    query_missing = (
        derive_query_missing()
    )

    (
        already_elsewhere,
        recovery_targets,
    ) = classify_targets(
        query_missing
    )

    batches = build_batches(
        recovery_targets
    )

    partial = [
        batch
        for batch in batches
        if batch_status(
            batch
        )["state"] == "PARTIAL"
    ]

    pending = [
        batch
        for batch in batches
        if batch_status(
            batch
        )["state"] == "PENDING"
    ]

    done = [
        batch
        for batch in batches
        if batch_status(
            batch
        )["state"] == "DONE"
    ]

    pending_targets = sum(
        batch["n_targets"]
        for batch in pending
    )

    modelled_cost = (
        cfg.estimate_cost(
            pending_targets
            * (1 + CPP),
            len(pending),
        )
    )

    ceiling_cost = (
        cfg.estimate_cost(
            pending_targets
            * (
                1
                + cfg.MAX_COMMENTS_PER_POST
            ),
            len(pending),
        )
    )

    already_spent = (
        cfg.spent_to_date()
    )

    _, baseline_files = (
        baseline_global_ids()
    )

    print(
        "[plan] DIRECT "
        "probe-post recovery"
    )

    print(
        f"[plan] baseline top-level "
        f"raw JSON files="
        f"{len(baseline_files)}"
    )

    print(
        f"[plan] query-level missing "
        f"probe IDs="
        f"{len(query_missing)}"
    )

    print(
        f"[plan] already present "
        f"elsewhere="
        f"{len(already_elsewhere)}"
    )

    print(
        f"[plan] globally absent "
        f"recovery targets="
        f"{len(recovery_targets)}"
    )

    print(
        f"[plan] batches="
        f"{len(batches)} | "
        f"done={len(done)} | "
        f"partial={len(partial)} | "
        f"pending={len(pending)}"
    )

    print(
        f"[plan] pending targets="
        f"{pending_targets}"
    )

    print(
        f"[plan] logged spend "
        f"USD {already_spent:.2f} | "
        f"budget cap "
        f"USD {cfg.BUDGET_USD_CAP:.2f} | "
        f"logged-basis remaining "
        f"USD "
        f"{cfg.BUDGET_USD_CAP - already_spent:.2f}"
    )

    print(
        "[plan] NOTE: logged spend "
        "excludes probe/test runs "
        "not written to scrape_log.csv."
    )

    print(
        f"[plan] modelled pending "
        f"recovery cost "
        f"~USD {modelled_cost:.2f} "
        f"(CPP={CPP}, estimate only)"
    )

    print(
        f"[plan] configured "
        f"15-comment ceiling "
        f"~USD {ceiling_cost:.2f}"
    )

    print(
        f"[plan] "
        f"MAX_LIVE_BATCHES="
        f"{MAX_LIVE_BATCHES}; "
        f"smallest batches run first."
    )

    print(
        "\n[plan] recovery batches:"
    )

    for number, batch in enumerate(
        batches,
        1,
    ):
        print_batch(
            number,
            batch,
        )

    if partial:
        print(
            "\n[stop] PARTIAL recovery "
            "file(s) exist. They will "
            "not be overwritten or "
            "automatically retried."
        )

        for batch in partial:
            state = batch_status(
                batch
            )

            print(
                f"   {batch['tier']} | "
                f"r/{batch['subreddit']} | "
                f"{batch['term']} | "
                f"missing="
                f"{sorted(state['missing'])}"
            )

        return

    if DRY_RUN:
        print(
            "\n[dry-run] nothing was "
            "called or written. "
            "DRY_RUN remains True."
        )
        return

    if not pending:
        write_manifest(
            query_missing,
            batches,
        )

        print(
            f"\n[done] all batches "
            f"complete. Manifest: "
            f"{MANIFEST_CSV}"
        )

        return

    token = os.environ.get(
        "APIFY_API_TOKEN",
        "",
    ).strip()

    if not token:
        sys.exit(
            "[stop] No APIFY_API_TOKEN "
            "found in .env"
        )

    from apify_client import (
        ApifyClient
    )

    client = ApifyClient(
        token
    )

    session_spend = 0.0
    session_items = 0
    session_comments = 0

    live_batches = pending[
        :MAX_LIVE_BATCHES
    ]

    for number, batch in enumerate(
        live_batches,
        1,
    ):
        if batch["output"].exists():
            raise SystemExit(
                f"[stop] refusing to "
                f"overwrite: "
                f"{batch['output']}"
            )

        payload = build_run_input(
            batch
        )

        batch_ceiling = (
            cfg.estimate_cost(
                batch["n_targets"]
                * (
                    1
                    + cfg.MAX_COMMENTS_PER_POST
                ),
                1,
            )
        )

        cumulative = (
            already_spent
            + session_spend
        )

        if (
            cumulative
            + batch_ceiling
            > cfg.BUDGET_USD_CAP
        ):
            print(
                f"\n[stop] next batch "
                f"ceiling "
                f"~USD {batch_ceiling:.2f} "
                f"would exceed the "
                f"logged budget cap."
            )

            break

        print(
            f"\n[{number}/"
            f"{len(live_batches)}] "
            f"DIRECT RECOVERY | "
            f"{batch['tier']} | "
            f"r/{batch['subreddit']} | "
            f"{batch['term']}"
        )

        print(
            f"   targets="
            f"{batch['n_targets']} | "
            f"maxPostsCount="
            f"{payload['maxPostsCount']} | "
            f"maxCommentsCount="
            f"{payload['maxCommentsCount']}"
        )

        try:
            run = client.actor(
                cfg.ACTOR_ID
            ).call(
                run_input=payload
            )

            if run is None:
                print(
                    "   ! run returned None; "
                    "no file written"
                )

                continue

            dataset_id = (
                getattr(
                    run,
                    "default_dataset_id",
                    None,
                )
                or run[
                    "defaultDatasetId"
                ]
            )

            items = list(
                client.dataset(
                    dataset_id
                ).iterate_items()
            )

        except Exception as exc:
            print(
                f"   ! failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            continue

        if batch["output"].exists():
            raise SystemExit(
                f"[stop] refusing to "
                f"overwrite: "
                f"{batch['output']}"
            )

        batch["output"].write_text(
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
            if isinstance(
                item,
                dict,
            )
            and str(
                item.get(
                    "dataType",
                    "",
                )
            ).lower() == "comment"
        )

        cost = cfg.estimate_cost(
            len(items)
        )

        session_spend += cost
        session_items += len(items)
        session_comments += n_comments

        log_run(
            batch,
            len(items),
            n_comments,
            cost,
        )

        state = batch_status(
            batch
        )

        print(
            f"   returned items="
            f"{len(items)} | "
            f"posts={state['posts']} | "
            f"comments={n_comments} | "
            f"~USD {cost:.3f}"
        )

        print(
            f"   recovered="
            f"{len(state['recovered'])}/"
            f"{batch['n_targets']} | "
            f"missing="
            f"{len(state['missing'])} | "
            f"extra post IDs="
            f"{len(state['extras'])}"
        )

        write_manifest(
            query_missing,
            batches,
        )

        if state["missing"]:
            print(
                "   [stop] recovery file "
                "is PARTIAL. Preserving it "
                "without automatic retry."
            )

            print(
                f"   missing target IDs="
                f"{sorted(state['missing'])}"
            )

            break

        time.sleep(1)

    refreshed = [
        batch_status(batch)
        for batch in batches
    ]

    print(
        f"\n[done] this session: "
        f"{session_items:,} items, "
        f"{session_comments:,} comments, "
        f"~USD {session_spend:.2f}"
    )

    print(
        f"[done] logged cumulative "
        f"spend ~USD "
        f"{already_spent + session_spend:.2f}"
    )

    print(
        f"[done] complete="
        f"{sum(1 for state in refreshed if state['state'] == 'DONE')}/"
        f"{len(batches)} | "
        f"partial="
        f"{sum(1 for state in refreshed if state['state'] == 'PARTIAL')} | "
        f"pending="
        f"{sum(1 for state in refreshed if state['state'] == 'PENDING')}"
    )

    if MANIFEST_CSV.exists():
        print(
            f"[done] recovery manifest: "
            f"{MANIFEST_CSV}"
        )


if __name__ == "__main__":
    main()