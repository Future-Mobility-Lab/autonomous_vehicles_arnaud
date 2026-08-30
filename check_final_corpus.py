"""
check_final_corpus.py -- final offline QA and corpus-freeze manifest.

Run only AFTER:
    python 02_preprocess.py

No network calls. No paid services.

PURPOSE
-------
This script audits the final cleaned Reddit corpus before it is frozen for
classification and longitudinal analysis.

It checks:

  1. The exact top-level data/raw/*.json input frame.
  2. That diagnostic/archive directories are outside the non-recursive input glob.
  3. The preprocessing funnel.
  4. Duplicate and missing Reddit comment IDs.
  5. Study-window and year consistency.
  6. Tier assignment.
  7. De-identification of the analytical output.
  8. Raw-union versus final comments-per-thread counts.
  9. Per-tier, per-year and per-subreddit composition.
 10. Current build_jobs() frame and scrape_log.csv reconciliation.
 11. Historical COLLECT_MAX_POSTS=60 files.
 12. MAX_COMMENTS_PER_POST 25 -> 15 timing against raw crawledAt timestamps.
 13. Capture rate against Reddit-reported commentsCount with conservative correction.
 14. Exact Parquet artefact SHA-256.
 15. Stable comment-ID membership SHA-256.

If any critical integrity condition fails, the script REFUSES to write an
authoritative manifest.

If all checks pass, the identical manifest is written to:

    data/README.md
        Local copy beside the data. Gitignored.

    docs/corpus_manifest.md
        De-identified, version-controlled copy.

The manifest contains no usernames, author IDs, comment text or raw Reddit
comment IDs.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

import config as cfg


# ===========================================================================
# PATHS
# ===========================================================================

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")

CORPUS_PARQUET = CLEAN_DIR / "corpus.parquet"
CORPUS_CSV = CLEAN_DIR / "corpus.csv"
FUNNEL_CSV = CLEAN_DIR / "preprocess_funnel.csv"

LOCAL_MANIFEST = Path("data/README.md")
VERSIONED_MANIFEST = Path("docs/corpus_manifest.md")


# ===========================================================================
# AUDITED FINAL COLLECTION STATE
# ===========================================================================

EXPECTED_CURRENT_JOBS = 684
EXPECTED_TOP_LEVEL_JSON_FILES = 694
EXPECTED_LOG_ROWS = 750
EXPECTED_LOGGED_SPEND = 80.25

APPROX_UNLOGGED_SPEND = 13.00
SUNK_LOGGED_SPEND = 7.07

C2_DUPLICATE_POST_RETRIEVALS = 143

COMMENTS_CAP_CHANGE_DATE = pd.Timestamp(
    "2026-08-03",
    tz="UTC",
)

EXPECTED_LOG_COLUMNS = [
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


# ===========================================================================
# DIRECTORIES THAT MUST NOT ENTER THE NON-RECURSIVE PREPROCESSING GLOB
# ===========================================================================

EXCLUDED_DIRS = [
    "_archive_tier3_v1",
    "_failed_backfill",
    "_direct_test",
    "_phrase_test",
    "_probe",
    "_archive_skeleton_test",
]


# ===========================================================================
# DE-IDENTIFICATION
# ===========================================================================

BANNED_CORPUS_COLUMNS = {
    "authorName",
    "authorId",
    "authorFullname",
    "parsedAuthorId",
}

REQUIRED_CORPUS_COLUMNS = {
    "id",
    "created",
    "year",
    "subreddit",
    "tier",
    "parsedPostId",
    "clean_wordcount",
    "body",
    "clean_body",
}


# ===========================================================================
# TEN QUERIES ORIGINALLY COLLECTED UNDER COLLECT_MAX_POSTS = 60
# ===========================================================================

OLD_CAP_FILES = [
    "selfdrivingcars__robotaxi__2016-01-01_2025-04-30.json",
    "waymo__waymo__2016-01-01_2025-04-30.json",
    "waymo__autonomous-vehicle__2016-01-01_2025-04-30.json",
    "teslamotors__lidar__2016-01-01_2025-04-30.json",
    "teslamotors__robotaxi__2016-01-01_2025-04-30.json",
    "futurology__lidar__2016-01-01_2025-04-30.json",
    "futurology__robotaxi__2016-01-01_2025-04-30.json",
    "cars__autonomous-vehicle__2016-01-01_2025-04-30.json",
    "electricvehicles__autonomous-vehicle__2016-01-01_2025-04-30.json",
    "electricvehicles__robotaxi__2016-01-01_2025-04-30.json",
]


def recovery_filename(original_filename: str) -> str:
    suffix = "__2016-01-01_2025-04-30.json"

    if not original_filename.endswith(suffix):
        raise ValueError(
            f"unexpected historical filename format: {original_filename}"
        )

    return original_filename.removesuffix(suffix) + "__recovery.json"


RECOVERY_FILES = [
    recovery_filename(name)
    for name in OLD_CAP_FILES
]


# ===========================================================================
# CAPTURE-RATE BUCKETS
# ===========================================================================

CAPTURE_BUCKETS = [
    -1,
    0,
    5,
    15,
    50,
    200,
    1000,
    10**9,
]

CAPTURE_LABELS = [
    "0",
    "1-5",
    "6-15",
    "16-50",
    "51-200",
    "201-1000",
    "1000+",
]


# ===========================================================================
# JSON HELPER
# ===========================================================================

def read_json_list(path: Path) -> list[dict]:
    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as exc:
        raise SystemExit(
            f"[stop] could not read {path}: "
            f"{type(exc).__name__}: {exc}"
        )

    if not isinstance(data, list):
        raise SystemExit(
            f"[stop] expected a JSON list in {path}"
        )

    return data


# ===========================================================================
# HASH HELPERS
# ===========================================================================

def file_sha256(path: Path) -> str:
    """
    SHA-256 of the exact stored file bytes.

    This identifies the specific Parquet artefact. It can change if identical
    logical data are serialised differently by another Parquet/PyArrow version.
    """
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(chunk)

    return digest.hexdigest()


def corpus_membership_sha256(df: pd.DataFrame) -> str:
    """
    SHA-256 of sorted final Reddit comment IDs.

    This is independent of row order and Parquet serialisation. It identifies
    corpus membership, not every field value associated with each comment.
    """
    return hashlib.sha256(
        "|".join(
            sorted(
                df["id"].astype(str)
            )
        ).encode()
    ).hexdigest()


# ===========================================================================
# MARKDOWN HELPERS
# ===========================================================================

def markdown_series_table(
    series: pd.Series,
    first_heading: str,
) -> str:
    lines = [
        f"| {first_heading} | Comments |",
        "|---|---:|",
    ]

    for key, value in series.items():
        lines.append(
            f"| {key} | {int(value):,} |"
        )

    return "\n".join(lines)


def markdown_funnel_table(
    funnel: pd.DataFrame,
) -> str:
    lines = [
        "| Stage | Comments retained |",
        "|---|---:|",
    ]

    for row in funnel.itertuples(index=False):
        stage = str(row.stage)

        if stage.startswith(
            "after study window "
        ):
            stage = "after study window"

        lines.append(
            f"| {stage} | {int(row.items):,} |"
        )

    return "\n".join(lines)


def markdown_capture_table(
    capture_table: pd.DataFrame,
) -> str:
    lines = [
        "| Reddit-reported thread size (`commentsCount`) | Threads | Reported comments | Effective denominator | Unique comments captured | Capture rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for bucket, row in capture_table.iterrows():
        capture_value = row["capture_%"]

        if pd.isna(capture_value):
            capture_text = "n/a"
        else:
            capture_text = f"{float(capture_value):.1f}%"

        lines.append(
            f"| {bucket} | "
            f"{int(row['threads']):,} | "
            f"{int(row['reported']):,} | "
            f"{int(row['effective']):,} | "
            f"{int(row['captured']):,} | "
            f"{capture_text} |"
        )

    return "\n".join(lines)


# ===========================================================================
# RAW INPUT
# ===========================================================================

def load_raw_comments(
    files: list[Path],
) -> pd.DataFrame:
    """
    Read top-level raw files and retain only raw comment metadata needed for QA.

    No usernames or comment text are copied into this QA DataFrame.
    """
    rows: list[dict] = []

    for path in files:
        data = read_json_list(
            path
        )

        for index, record in enumerate(data):
            if not isinstance(record, dict):
                continue

            if (
                str(
                    record.get(
                        "dataType",
                        "",
                    )
                ).lower()
                != "comment"
            ):
                continue

            rows.append(
                {
                    "source_file":
                        path.name,

                    "source_index":
                        index,

                    "id":
                        str(
                            record.get("id")
                            or ""
                        ).strip(),

                    "parsedPostId":
                        str(
                            record.get(
                                "parsedPostId"
                            )
                            or ""
                        ).strip(),
                }
            )

    return pd.DataFrame(rows)


# ===========================================================================
# CAPTURE RATE
# ===========================================================================

def compute_capture_rate(
    files: list[Path],
) -> tuple[
    pd.DataFrame,
    int,
    int,
    int,
    int,
    float,
    int,
    dict,
]:
    """
    Reproduce the final audited calculation in check_capture_rate.py.

    Reddit post records provide `commentsCount`, which is treated as a
    Reddit-reported thread-size measure rather than an exact ground-truth
    denominator.

    The same post may occur in several raw files, so the maximum observed
    commentsCount is retained for each post.

    Each Reddit comment ID is counted once per post.

    Where the number of unique captured comments exceeds commentsCount, the
    effective denominator is corrected conservatively to:

        max(commentsCount, unique comments captured)

    Thread-size buckets remain based on Reddit's reported commentsCount.
    """

    posts: dict[str, int] = {}

    captured_ids: dict[
        str,
        set[str],
    ] = {}

    comment_bodies: dict[
        str,
        dict[str, str],
    ] = {}

    for path in files:
        data = read_json_list(
            path
        )

        for record in data:
            if not isinstance(
                record,
                dict,
            ):
                continue

            data_type = str(
                record.get(
                    "dataType",
                    "",
                )
            ).lower()

            if data_type == "post":
                post_id = str(
                    record.get(
                        "parsedId"
                    )
                    or ""
                ).strip()

                if not post_id:
                    continue

                try:
                    reported_count = int(
                        record.get(
                            "commentsCount"
                        )
                        or 0
                    )

                except (
                    TypeError,
                    ValueError,
                ):
                    raise SystemExit(
                        "[stop] non-numeric commentsCount "
                        f"for a post in {path.name}"
                    )

                posts[
                    post_id
                ] = max(
                    posts.get(
                        post_id,
                        0,
                    ),
                    reported_count,
                )

            elif data_type == "comment":
                post_id = str(
                    record.get(
                        "parsedPostId"
                    )
                    or ""
                ).strip()

                comment_id = str(
                    record.get(
                        "id"
                    )
                    or ""
                ).strip()

                if not (
                    post_id
                    and comment_id
                ):
                    continue

                captured_ids.setdefault(
                    post_id,
                    set(),
                ).add(
                    comment_id
                )

                comment_bodies.setdefault(
                    post_id,
                    {},
                ).setdefault(
                    comment_id,
                    str(
                        record.get(
                            "body"
                        )
                        or ""
                    ).strip().lower(),
                )

    if not posts:
        raise SystemExit(
            "[stop] no post records found "
            "for capture-rate calculation"
        )

    rows: list[dict] = []

    for (
        post_id,
        reported_count,
    ) in posts.items():

        captured_count = len(
            captured_ids.get(
                post_id,
                set(),
            )
        )

        effective_denominator = max(
            reported_count,
            captured_count,
        )

        excess = max(
            0,
            captured_count
            - reported_count,
        )

        bodies = list(
            comment_bodies.get(
                post_id,
                {},
            ).values()
        )

        deleted_count = sum(
            body == "[deleted]"
            for body in bodies
        )

        removed_count = sum(
            body == "[removed]"
            for body in bodies
        )

        rows.append(
            {
                "pid":
                    post_id,

                "reported":
                    reported_count,

                "effective":
                    effective_denominator,

                "captured":
                    captured_count,

                "excess":
                    excess,

                "deleted":
                    deleted_count,

                "removed":
                    removed_count,
            }
        )

    capture_df = pd.DataFrame(
        rows
    )

    capture_df[
        "bucket"
    ] = pd.cut(
        capture_df[
            "reported"
        ],
        CAPTURE_BUCKETS,
        labels=CAPTURE_LABELS,
    )

    total_reported = int(
        capture_df[
            "reported"
        ].sum()
    )

    total_effective = int(
        capture_df[
            "effective"
        ].sum()
    )

    total_captured = int(
        capture_df[
            "captured"
        ].sum()
    )

    if total_effective <= 0:
        raise SystemExit(
            "[stop] effective capture-rate denominator "
            "is zero"
        )

    original_rate = (
        100
        * total_captured
        / total_reported
        if total_reported > 0
        else float("nan")
    )

    corrected_rate = (
        100
        * total_captured
        / total_effective
    )

    inconsistent = capture_df[
        capture_df[
            "excess"
        ]
        > 0
    ].copy()

    inconsistent_threads = len(
        inconsistent
    )

    inconsistent_pct = (
        100
        * inconsistent_threads
        / len(
            capture_df
        )
    )

    total_excess = int(
        inconsistent[
            "excess"
        ].sum()
    )

    maximum_excess = (
        int(
            inconsistent[
                "excess"
            ].max()
        )
        if inconsistent_threads
        else 0
    )

    deleted_count = int(
        inconsistent[
            "deleted"
        ].sum()
    )

    removed_count = int(
        inconsistent[
            "removed"
        ].sum()
    )

    deleted_removed_total = (
        deleted_count
        + removed_count
    )

    fully_covered = int(
        (
            (
                inconsistent[
                    "deleted"
                ]
                + inconsistent[
                    "removed"
                ]
            )
            >= inconsistent[
                "excess"
            ]
        ).sum()
    )

    unexplained_excess = int(
        (
            (
                inconsistent[
                    "excess"
                ]
                - inconsistent[
                    "deleted"
                ]
                - inconsistent[
                    "removed"
                ]
            )
            .clip(
                lower=0
            )
        ).sum()
    )

    grouped = (
        capture_df
        .groupby(
            "bucket",
            observed=True,
        )
        .agg(
            threads=(
                "pid",
                "size",
            ),

            reported=(
                "reported",
                "sum",
            ),

            effective=(
                "effective",
                "sum",
            ),

            captured=(
                "captured",
                "sum",
            ),
        )
    )

    grouped[
        "capture_%"
    ] = np.where(
        grouped[
            "effective"
        ]
        > 0,

        (
            100
            * grouped[
                "captured"
            ]
            / grouped[
                "effective"
            ]
        ).round(
            1
        ),

        np.nan,
    )

    zero_threads = int(
        (
            capture_df[
                "reported"
            ]
            == 0
        ).sum()
    )

    consistency = {
        "original_rate":
            original_rate,

        "denominator_adjustment":
            total_effective
            - total_reported,

        "inconsistent_threads":
            inconsistent_threads,

        "inconsistent_pct":
            inconsistent_pct,

        "total_excess":
            total_excess,

        "maximum_excess":
            maximum_excess,

        "deleted":
            deleted_count,

        "removed":
            removed_count,

        "deleted_removed_total":
            deleted_removed_total,

        "fully_covered":
            fully_covered,

        "unexplained_excess":
            unexplained_excess,
    }

    return (
        grouped,
        len(
            capture_df
        ),
        total_reported,
        total_effective,
        total_captured,
        corrected_rate,
        zero_threads,
        consistency,
    )

# ===========================================================================
# CRAWLED-AT VERIFICATION FOR THE 25 -> 15 COMMENT CAP CHANGE
# ===========================================================================

def verify_crawled_at(
    files: list[Path],
) -> dict:
    """
    Audit top-level production/recovery files against the 3 August 2026
    MAX_COMMENTS_PER_POST change using record-level crawledAt timestamps.

    Empty files cannot contain crawledAt timestamps, so they are reported
    explicitly rather than silently treated as verified.
    """
    earliest_timestamp: pd.Timestamp | None = None

    files_with_timestamp: set[str] = set()
    files_before_change: set[str] = set()
    files_on_change_date: set[str] = set()

    empty_files: list[str] = []
    nonempty_without_timestamp: list[str] = []

    parsed_timestamp_count = 0
    timestamps_before_change = 0

    for path in files:
        data = read_json_list(
            path
        )

        dict_records = [
            record
            for record in data
            if isinstance(
                record,
                dict,
            )
        ]

        if not dict_records:
            empty_files.append(
                path.name
            )
            continue

        file_timestamps: list[
            pd.Timestamp
        ] = []

        for record in dict_records:
            value = record.get(
                "crawledAt"
            )

            if not value:
                continue

            timestamp = pd.to_datetime(
                value,
                utc=True,
                errors="coerce",
            )

            if pd.isna(
                timestamp
            ):
                continue

            file_timestamps.append(
                timestamp
            )

            parsed_timestamp_count += 1

            if (
                earliest_timestamp
                is None
                or timestamp
                < earliest_timestamp
            ):
                earliest_timestamp = (
                    timestamp
                )

            if (
                timestamp
                < COMMENTS_CAP_CHANGE_DATE
            ):
                timestamps_before_change += 1

                files_before_change.add(
                    path.name
                )

            if (
                timestamp.date()
                == COMMENTS_CAP_CHANGE_DATE.date()
            ):
                files_on_change_date.add(
                    path.name
                )

        if file_timestamps:
            files_with_timestamp.add(
                path.name
            )

        else:
            nonempty_without_timestamp.append(
                path.name
            )

    return {
        "earliest_timestamp":
            earliest_timestamp,

        "files_with_timestamp":
            sorted(
                files_with_timestamp
            ),

        "files_before_change":
            sorted(
                files_before_change
            ),

        "files_on_change_date":
            sorted(
                files_on_change_date
            ),

        "empty_files":
            sorted(
                empty_files
            ),

        "nonempty_without_timestamp":
            sorted(
                nonempty_without_timestamp
            ),

        "parsed_timestamp_count":
            parsed_timestamp_count,

        "timestamps_before_change":
            timestamps_before_change,
    }


def crawled_at_manifest_text(
    result: dict,
) -> str:
    earliest = result[
        "earliest_timestamp"
    ]

    files_before = result[
        "files_before_change"
    ]

    same_day = result[
        "files_on_change_date"
    ]

    empty_files = result[
        "empty_files"
    ]

    no_timestamp = result[
        "nonempty_without_timestamp"
    ]

    if earliest is None:
        return (
            "No parseable `crawledAt` timestamps were present in the "
            "top-level production/recovery files. The timing of the "
            "`MAX_COMMENTS_PER_POST` change therefore cannot be verified "
            "from the raw records."
        )

    earliest_text = (
        earliest
        .isoformat()
    )

    lines: list[str] = []

    if files_before:
        lines.append(
            f"Verification found **{len(files_before)} top-level file(s)** "
            "containing at least one `crawledAt` timestamp earlier than "
            "3 August 2026. The 15-comment cap therefore cannot be described "
            "as predating all observed production crawls."
        )

        lines.append(
            f"The earliest observed `crawledAt` timestamp was "
            f"`{earliest_text}`."
        )

        lines.append(
            "Files containing pre-change crawl timestamps:"
        )

        for name in files_before:
            lines.append(
                f"- `{name}`"
            )

    else:
        lines.append(
            "No parsed `crawledAt` timestamp in the top-level "
            "production/recovery files predates the calendar date "
            "**3 August 2026**."
        )

        lines.append(
            f"The earliest observed `crawledAt` timestamp was "
            f"`{earliest_text}`."
        )

        if same_day:
            lines.append(
                f"However, **{len(same_day)} file(s)** contain at least one "
                "`crawledAt` timestamp dated 3 August itself. Because the "
                "exact clock time of the configuration change is not encoded "
                "in this audit, same-day `crawledAt` values cannot establish "
                "whether those particular crawls occurred before or after the "
                "25-to-15 edit."
            )

        else:
            lines.append(
                "All observed `crawledAt` timestamps therefore postdate "
                "the 3 August 2026 change date."
            )

    if empty_files:
        lines.append(
            f"**{len(empty_files)} empty top-level file(s)** contain no "
            "records and therefore cannot be independently dated using "
            "`crawledAt`."
        )

    if no_timestamp:
        lines.append(
            f"**{len(no_timestamp)} non-empty top-level file(s)** contain "
            "no parseable `crawledAt` value and likewise cannot be "
            "independently dated from that field."
        )

    return "\n\n".join(
        lines
    )


# ===========================================================================
# MAIN AUDIT
# ===========================================================================

def main() -> None:
    print(
        "=" * 78
    )

    print(
        "FINAL CORPUS QA AND FREEZE"
    )

    print(
        "=" * 78
    )

    failures: list[str] = []


    # -----------------------------------------------------------------------
    # REQUIRED OUTPUT FILES
    # -----------------------------------------------------------------------

    if not CORPUS_PARQUET.exists():
        raise SystemExit(
            f"[stop] missing {CORPUS_PARQUET}. "
            "Run 02_preprocess.py first."
        )

    if not CORPUS_CSV.exists():
        raise SystemExit(
            f"[stop] missing {CORPUS_CSV}. "
            "Run 02_preprocess.py first."
        )

    if not FUNNEL_CSV.exists():
        raise SystemExit(
            f"[stop] missing {FUNNEL_CSV}. "
            "Run 02_preprocess.py first."
        )


    # -----------------------------------------------------------------------
    # CURRENT JOB FRAME
    # -----------------------------------------------------------------------

    current_jobs = cfg.build_jobs()

    if len(current_jobs) != EXPECTED_CURRENT_JOBS:
        failures.append(
            f"build_jobs() returns {len(current_jobs)} jobs; "
            f"expected {EXPECTED_CURRENT_JOBS}"
        )

    current_job_paths = [
        cfg.job_path(
            job,
            "collect",
        ).resolve()
        for job in current_jobs
    ]

    if (
        len(
            set(
                current_job_paths
            )
        )
        != len(
            current_job_paths
        )
    ):
        failures.append(
            "build_jobs() contains duplicate collection paths"
        )


    # -----------------------------------------------------------------------
    # EXACT TOP-LEVEL RAW INPUT FRAME
    # -----------------------------------------------------------------------

    top_files = sorted(
        RAW_DIR.glob(
            "*.json"
        )
    )

    actual_names = {
        path.name
        for path in top_files
    }

    expected_current_names = {
        path.name
        for path in current_job_paths
    }

    expected_names = (
        expected_current_names
        | set(
            RECOVERY_FILES
        )
    )

    missing_expected = sorted(
        expected_names
        - actual_names
    )

    unexpected_files = sorted(
        actual_names
        - expected_names
    )

    print(
        f"\ntop-level JSON files     "
        f"{len(top_files)}"
    )

    print(
        f"expected top-level files "
        f"{len(expected_names)}"
    )

    print(
        "02_preprocess input glob  "
        "data/raw/*.json "
        "(non-recursive)"
    )

    if (
        len(top_files)
        != EXPECTED_TOP_LEVEL_JSON_FILES
    ):
        failures.append(
            f"top-level data/raw JSON count is "
            f"{len(top_files)}, expected "
            f"{EXPECTED_TOP_LEVEL_JSON_FILES}"
        )

    if missing_expected:
        failures.append(
            f"{len(missing_expected)} expected "
            "top-level JSON file(s) are missing"
        )

    if unexpected_files:
        failures.append(
            f"{len(unexpected_files)} unexpected "
            "top-level JSON file(s) are present"
        )

    if missing_expected:
        print(
            "\nMISSING EXPECTED TOP-LEVEL FILES:"
        )

        for name in missing_expected:
            print(
                f"  {name}"
            )

    if unexpected_files:
        print(
            "\nUNEXPECTED TOP-LEVEL FILES:"
        )

        for name in unexpected_files:
            print(
                f"  {name}"
            )


    # -----------------------------------------------------------------------
    # EXCLUDED SUBDIRECTORIES
    # -----------------------------------------------------------------------

    print(
        "\nexcluded diagnostic/archive directories:"
    )

    for name in EXCLUDED_DIRS:
        path = (
            RAW_DIR
            / name
        )

        nested_json = (
            list(
                path.rglob(
                    "*.json"
                )
            )
            if path.exists()
            else []
        )

        print(
            f"  {name:<24} "
            f"exists={str(path.exists()):<5} "
            f"JSON files={len(nested_json):>4} "
            f"excluded=YES"
        )


    # -----------------------------------------------------------------------
    # RAW COMMENT UNION
    # -----------------------------------------------------------------------

    raw = load_raw_comments(
        top_files
    )

    if raw.empty:
        failures.append(
            "no raw comments were found"
        )

        raw_missing_ids = 0

        raw_unique = raw.copy()

    else:
        raw_missing_ids = int(
            (
                raw[
                    "id"
                ]
                == ""
            ).sum()
        )

        raw_unique = (
            raw[
                raw[
                    "id"
                ]
                != ""
            ]
            .drop_duplicates(
                subset="id",
                keep="first",
            )
        )

    print(
        f"\nraw comment retrievals   "
        f"{len(raw):,}"
    )

    print(
        f"raw comments missing ID  "
        f"{raw_missing_ids}"
    )

    print(
        f"raw unique comment IDs   "
        f"{len(raw_unique):,}"
    )


    # -----------------------------------------------------------------------
    # RAW UNIQUE COMMENTS PER THREAD
    # -----------------------------------------------------------------------

    if raw_unique.empty:
        raw_thread_counts = pd.Series(
            dtype="int64"
        )

    else:
        raw_thread_rows = raw_unique[
            raw_unique[
                "parsedPostId"
            ]
            != ""
        ]

        raw_thread_counts = (
            raw_thread_rows
            .groupby(
                "parsedPostId"
            )
            .size()
        )

    raw_max_thread = (
        int(
            raw_thread_counts.max()
        )
        if len(
            raw_thread_counts
        )
        else 0
    )

    raw_threads_over_15 = int(
        (
            raw_thread_counts
            > 15
        ).sum()
    )


    # -----------------------------------------------------------------------
    # FINAL PARQUET CORPUS
    # -----------------------------------------------------------------------

    df = pd.read_parquet(
        CORPUS_PARQUET
    )

    if df.empty:
        failures.append(
            "final corpus is empty"
        )

    missing_required_columns = (
        REQUIRED_CORPUS_COLUMNS
        - set(
            df.columns
        )
    )

    if missing_required_columns:
        failures.append(
            "final corpus is missing required column(s): "
            + ", ".join(
                sorted(
                    missing_required_columns
                )
            )
        )

    pii_columns = (
        BANNED_CORPUS_COLUMNS
        & set(
            df.columns
        )
    )

    if pii_columns:
        failures.append(
            "de-identification failed; prohibited "
            "author column(s) remain: "
            + ", ".join(
                sorted(
                    pii_columns
                )
            )
        )

    if missing_required_columns:
        print(
            "\n"
            + "!" * 78
        )

        print(
            "FREEZE HALTED"
        )

        print(
            "!" * 78
        )

        for failure in failures:
            print(
                f"  * {failure}"
            )

        print(
            "\nNo manifest was written."
        )

        raise SystemExit(
            1
        )

    df = df.copy()

    df[
        "created"
    ] = pd.to_datetime(
        df[
            "created"
        ],
        utc=True,
        errors="coerce",
    )


    # -----------------------------------------------------------------------
    # FINAL ID INTEGRITY
    # -----------------------------------------------------------------------

    final_missing_ids = int(
        (
            df[
                "id"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            == ""
        ).sum()
    )

    duplicate_final_ids = int(
        df[
            "id"
        ]
        .duplicated()
        .sum()
    )

    print(
        f"\nfinal corpus rows        "
        f"{len(df):,}"
    )

    print(
        f"duplicate comment IDs    "
        f"{duplicate_final_ids}"
    )

    print(
        f"missing comment IDs      "
        f"{final_missing_ids}"
    )

    if duplicate_final_ids:
        failures.append(
            f"{duplicate_final_ids} duplicate comment ID(s) "
            "in the corpus"
        )

    if final_missing_ids:
        failures.append(
            f"{final_missing_ids} final corpus row(s) "
            "have no Reddit comment ID"
        )


    # -----------------------------------------------------------------------
    # TIMESTAMP / STUDY WINDOW
    # -----------------------------------------------------------------------

    invalid_created = int(
        df[
            "created"
        ].isna().sum()
    )

    start = pd.Timestamp(
        cfg.STUDY_START,
        tz="UTC",
    )

    end_exclusive = (
        pd.Timestamp(
            cfg.STUDY_END,
            tz="UTC",
        )
        + pd.Timedelta(
            days=1
        )
    )

    valid_created = df[
        df[
            "created"
        ].notna()
    ]

    out_of_window = int(
        (
            (
                valid_created[
                    "created"
                ]
                < start
            )
            |
            (
                valid_created[
                    "created"
                ]
                >= end_exclusive
            )
        ).sum()
    )

    if invalid_created:
        year_mismatch = 0

    else:
        year_mismatch = int(
            (
                df[
                    "year"
                ].astype(
                    "Int64"
                )
                != df[
                    "created"
                ].dt.year.astype(
                    "Int64"
                )
            ).sum()
        )

    print(
        f"invalid timestamps       "
        f"{invalid_created}"
    )

    print(
        f"out-of-window rows       "
        f"{out_of_window}"
    )

    print(
        f"year/timestamp mismatch  "
        f"{year_mismatch}"
    )

    if invalid_created:
        failures.append(
            f"{invalid_created} invalid final timestamp(s)"
        )

    if out_of_window:
        failures.append(
            f"{out_of_window} final row(s) "
            "outside the study window"
        )

    if year_mismatch:
        failures.append(
            f"{year_mismatch} final row(s) have "
            "year/timestamp disagreement"
        )


    # -----------------------------------------------------------------------
    # TIER ASSIGNMENT
    # -----------------------------------------------------------------------

    untiered = int(
        (
            df[
                "tier"
            ]
            .fillna("")
            .astype(str)
            .str.lower()
            == "untiered"
        ).sum()
    )

    missing_tier = int(
        (
            df[
                "tier"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            == ""
        ).sum()
    )

    print(
        f"untiered rows            "
        f"{untiered}"
    )

    print(
        f"missing tier rows        "
        f"{missing_tier}"
    )

    print(
        f"author-ID/name columns   "
        f"{len(pii_columns)}"
    )

    if untiered:
        failures.append(
            f"{untiered} final row(s) are untiered"
        )

    if missing_tier:
        failures.append(
            f"{missing_tier} final row(s) "
            "have no tier"
        )

    if pii_columns:
        failures.append(
            "author-identifying columns remain "
            "in the analytical corpus"
        )


    # -----------------------------------------------------------------------
    # CSV / PARQUET CONSISTENCY
    # -----------------------------------------------------------------------

    csv_df = pd.read_csv(
        CORPUS_CSV
    )

    if (
        len(
            csv_df
        )
        != len(
            df
        )
    ):
        failures.append(
            f"corpus.csv has {len(csv_df)} rows but "
            f"corpus.parquet has {len(df)}"
        )

    parquet_ids = sorted(
        df[
            "id"
        ].astype(str)
    )

    csv_ids = sorted(
        csv_df[
            "id"
        ].astype(str)
    )

    if parquet_ids != csv_ids:
        failures.append(
            "corpus.csv and corpus.parquet "
            "do not contain the same comment IDs"
        )


    # -----------------------------------------------------------------------
    # PREPROCESSING FUNNEL
    # -----------------------------------------------------------------------

    funnel = pd.read_csv(
        FUNNEL_CSV
    )

    required_funnel_columns = {
        "stage",
        "items",
    }

    if not (
        required_funnel_columns
        <= set(
            funnel.columns
        )
    ):
        failures.append(
            "preprocess_funnel.csv does not contain "
            "the required stage/items columns"
        )

    elif funnel.empty:
        failures.append(
            "preprocess_funnel.csv is empty"
        )

    else:
        funnel[
            "items"
        ] = pd.to_numeric(
            funnel[
                "items"
            ],
            errors="coerce",
        )

        if funnel[
            "items"
        ].isna().any():
            failures.append(
                "preprocessing funnel contains "
                "a non-numeric item count"
            )

        else:
            funnel_counts = [
                int(value)
                for value
                in funnel[
                    "items"
                ]
            ]

            if any(
                later
                > earlier
                for (
                    earlier,
                    later,
                )
                in zip(
                    funnel_counts,
                    funnel_counts[
                        1:
                    ],
                )
            ):
                failures.append(
                    "preprocessing funnel increases at "
                    "one or more filtering stages"
                )

            funnel_final = int(
                funnel_counts[
                    -1
                ]
            )

            if funnel_final != len(df):
                failures.append(
                    f"preprocessing funnel ends at "
                    f"{funnel_final} rows but corpus "
                    f"contains {len(df)}"
                )


    # -----------------------------------------------------------------------
    # SCRAPE LOG
    # -----------------------------------------------------------------------

    if not cfg.LOG_CSV.exists():
        failures.append(
            "scrape_log.csv is missing"
        )

        log = pd.DataFrame()

        logged_spend = float(
            "nan"
        )

    else:
        log = pd.read_csv(
            cfg.LOG_CSV
        )

        if (
            list(
                log.columns
            )
            != EXPECTED_LOG_COLUMNS
        ):
            failures.append(
                "scrape_log.csv schema differs "
                "from the audited ten-column schema"
            )

        if len(log) != EXPECTED_LOG_ROWS:
            failures.append(
                f"scrape_log.csv contains "
                f"{len(log)} rows; expected "
                f"{EXPECTED_LOG_ROWS}"
            )

        logged_spend = float(
            log[
                "est_usd"
            ].sum()
        )

        if (
            round(
                logged_spend,
                2,
            )
            != EXPECTED_LOGGED_SPEND
        ):
            failures.append(
                f"logged spend is USD "
                f"{logged_spend:.2f}; expected "
                f"USD {EXPECTED_LOGGED_SPEND:.2f}"
            )

    print(
        f"\ncurrent build_jobs()     "
        f"{len(current_jobs)}"
    )

    print(
        f"scrape_log.csv rows      "
        f"{len(log)}"
    )

    if not log.empty:
        print(
            f"logged spend             "
            f"USD {logged_spend:.2f}"
        )


    # -----------------------------------------------------------------------
    # HISTORICAL 60-POST FILES
    # -----------------------------------------------------------------------

    missing_old_cap_files = [
        name
        for name in OLD_CAP_FILES
        if not (
            RAW_DIR
            / name
        ).exists()
    ]

    missing_recovery_files = [
        name
        for name in RECOVERY_FILES
        if not (
            RAW_DIR
            / name
        ).exists()
    ]

    if missing_old_cap_files:
        failures.append(
            f"{len(missing_old_cap_files)} known "
            "old-60-cap production file(s) are missing"
        )

    if missing_recovery_files:
        failures.append(
            f"{len(missing_recovery_files)} direct "
            "recovery file(s) are missing"
        )


    # -----------------------------------------------------------------------
    # CAPTURE RATE
    # -----------------------------------------------------------------------

    (
        capture_table,
        sampled_threads,
        comments_reported,
        comments_effective,
        comments_captured,
        overall_capture_rate,
        zero_comment_threads,
        capture_consistency,
    ) = compute_capture_rate(
        top_files
    )

    print(
        "\ncapture rate:"
    )

    print(
        f"  sampled threads               "
        f"{sampled_threads:,}"
    )

    print(
        f"  reported commentsCount total  "
        f"{comments_reported:,}"
    )

    print(
        f"  effective denominator total   "
        f"{comments_effective:,}"
    )

    print(
        f"  denominator adjustment        "
        f"{capture_consistency['denominator_adjustment']:,}"
    )

    print(
        f"  unique comments captured      "
        f"{comments_captured:,}"
    )

    print(
        f"  original capture rate         "
        f"{capture_consistency['original_rate']:.3f}%"
    )

    print(
        f"  CORRECTED OVERALL CAPTURE RATE "
        f"{overall_capture_rate:.3f}%"
    )

    print(
        "\n  denominator consistency:"
    )

    print(
        f"    captured > commentsCount    "
        f"{capture_consistency['inconsistent_threads']:,} "
        f"threads "
        f"({capture_consistency['inconsistent_pct']:.1f}%)"
    )

    print(
        f"    total correction            "
        f"{capture_consistency['total_excess']:,}"
    )

    print(
        f"    maximum one-thread correction "
        f"{capture_consistency['maximum_excess']}"
    )

    print(
        f"    [deleted] comments          "
        f"{capture_consistency['deleted']:,}"
    )

    print(
        f"    [removed] comments          "
        f"{capture_consistency['removed']:,}"
    )

    print(
        f"    deleted + removed           "
        f"{capture_consistency['deleted_removed_total']:,}"
    )

    print(
        f"    threads fully covered       "
        f"{capture_consistency['fully_covered']:,} of "
        f"{capture_consistency['inconsistent_threads']:,}"
    )

    print(
        f"    unexplained excess          "
        f"{capture_consistency['unexplained_excess']:,}"
    )

    print(
        "\n  BY THREAD SIZE"
    )

    print(
        capture_table.to_string()
    )

    print(
        f"\n  threads with no comments "
        f"at all: {zero_comment_threads:,}"
    )


    # -----------------------------------------------------------------------
    # CRAWLED-AT AUDIT FOR MAX_COMMENTS_PER_POST 25 -> 15
    # -----------------------------------------------------------------------

    crawl_audit = verify_crawled_at(
        top_files
    )

    earliest_crawl = crawl_audit[
        "earliest_timestamp"
    ]

    print(
        "\nMAX_COMMENTS_PER_POST 25 -> 15 "
        "crawledAt verification:"
    )

    print(
        f"  parsed crawledAt values     "
        f"{crawl_audit['parsed_timestamp_count']:,}"
    )

    print(
        f"  files with crawledAt        "
        f"{len(crawl_audit['files_with_timestamp']):,}"
    )

    print(
        f"  files before 2026-08-03     "
        f"{len(crawl_audit['files_before_change']):,}"
    )

    print(
        f"  files dated 2026-08-03      "
        f"{len(crawl_audit['files_on_change_date']):,}"
    )

    print(
        f"  empty files, not dateable   "
        f"{len(crawl_audit['empty_files']):,}"
    )

    print(
        f"  non-empty without crawledAt "
        f"{len(crawl_audit['nonempty_without_timestamp']):,}"
    )

    if earliest_crawl is None:
        print(
            "  earliest crawledAt           NONE"
        )

    else:
        print(
            f"  earliest crawledAt           "
            f"{earliest_crawl.isoformat()}"
        )


    # -----------------------------------------------------------------------
    # HARD STOP
    # -----------------------------------------------------------------------

    if failures:
        print(
            "\n"
            + "!" * 78
        )

        print(
            "FREEZE HALTED"
        )

        print(
            "!" * 78
        )

        for failure in failures:
            print(
                f"  * {failure}"
            )

        print(
            "\nNo manifest was written."
        )

        print(
            "Fix the failed condition before "
            "freezing the corpus."
        )

        raise SystemExit(
            1
        )


    # -----------------------------------------------------------------------
    # FINAL UNIQUE COMMENTS PER THREAD
    # -----------------------------------------------------------------------

    final_thread_rows = df[
        df[
            "parsedPostId"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        != ""
    ]

    final_thread_counts = (
        final_thread_rows
        .groupby(
            "parsedPostId"
        )
        .size()
    )

    final_max_thread = (
        int(
            final_thread_counts.max()
        )
        if len(
            final_thread_counts
        )
        else 0
    )

    final_threads_over_15 = int(
        (
            final_thread_counts
            > 15
        ).sum()
    )

    print(
        "\nthread-depth QA:"
    )

    print(
        f"  RAW UNION maximum unique "
        f"comments/thread   "
        f"{raw_max_thread}"
    )

    print(
        f"  RAW UNION threads >15 "
        f"unique comments      "
        f"{raw_threads_over_15}"
    )

    print(
        f"  FINAL maximum surviving "
        f"comments/thread    "
        f"{final_max_thread}"
    )

    print(
        f"  FINAL threads >15 "
        f"surviving comments       "
        f"{final_threads_over_15}"
    )


    # -----------------------------------------------------------------------
    # COMPOSITION
    # -----------------------------------------------------------------------

    tier_counts = (
        df[
            "tier"
        ]
        .value_counts()
        .sort_index()
    )

    year_counts = (
        df[
            "year"
        ]
        .value_counts()
        .sort_index()
    )

    print(
        "\ncomments per tier:"
    )

    print(
        tier_counts.to_string()
    )

    print(
        "\ncomments per year:"
    )

    print(
        year_counts.to_string()
    )


    # -----------------------------------------------------------------------
    # SUBREDDIT COVERAGE
    # -----------------------------------------------------------------------

    required_years = set(
        range(
            2016,
            2026,
        )
    )

    coverage_rows: list[
        dict
    ] = []

    for (
        subreddit,
        group,
    ) in df.groupby(
        "subreddit"
    ):
        years = sorted(
            int(year)
            for year
            in group[
                "year"
            ]
            .dropna()
            .unique()
        )

        missing_years = sorted(
            required_years
            - set(
                years
            )
        )

        coverage_rows.append(
            {
                "subreddit":
                    subreddit,

                "comments":
                    len(group),

                "first":
                    group[
                        "created"
                    ]
                    .min()
                    .date()
                    .isoformat(),

                "last":
                    group[
                        "created"
                    ]
                    .max()
                    .date()
                    .isoformat(),

                "years":
                    ",".join(
                        map(
                            str,
                            years,
                        )
                    ),

                "missing":
                    (
                        ",".join(
                            map(
                                str,
                                missing_years,
                            )
                        )
                        if missing_years
                        else "none"
                    ),
            }
        )

    coverage = (
        pd.DataFrame(
            coverage_rows
        )
        .sort_values(
            "subreddit"
        )
    )

    print(
        "\nsubreddit coverage:"
    )

    print(
        coverage[
            [
                "subreddit",
                "comments",
                "first",
                "last",
                "years",
                "missing",
            ]
        ].to_string(
            index=False
        )
    )

    incomplete = coverage[
        coverage[
            "missing"
        ]
        != "none"
    ]

    print(
        "\nsubreddits without comments "
        "in every study year 2016-2025:"
    )

    if incomplete.empty:
        print(
            "  none"
        )

    else:
        for row in (
            incomplete.itertuples()
        ):
            print(
                f"  r/{row.subreddit}: "
                f"missing {row.missing}"
            )


    # -----------------------------------------------------------------------
    # FUNNEL DISPLAY
    # -----------------------------------------------------------------------

    print(
        "\npreprocessing funnel:"
    )

    print(
        funnel.to_string(
            index=False
        )
    )


    # -----------------------------------------------------------------------
    # HISTORICAL CAP DISPLAY
    # -----------------------------------------------------------------------

    print(
        "\nknown production files originally "
        "collected under COLLECT_MAX_POSTS=60:"
    )

    for name in OLD_CAP_FILES:
        print(
            f"  {name}"
        )


    # -----------------------------------------------------------------------
    # HASHES
    # -----------------------------------------------------------------------

    artifact_hash = file_sha256(
        CORPUS_PARQUET
    )

    membership_hash = (
        corpus_membership_sha256(
            df
        )
    )

    date_start = (
        df[
            "created"
        ]
        .min()
        .date()
        .isoformat()
    )

    date_end = (
        df[
            "created"
        ]
        .max()
        .date()
        .isoformat()
    )

    true_spend_approx = (
        logged_spend
        + APPROX_UNLOGGED_SPEND
    )

    print(
        f"\nParquet file SHA-256     "
        f"{artifact_hash}"
    )

    print(
        f"Corpus membership SHA-256 "
        f"{membership_hash}"
    )

    print(
        f"approx true spend        "
        f"~USD {true_spend_approx:.2f}"
    )

    print(
        f"sunk logged spend        "
        f"USD {SUNK_LOGGED_SPEND:.2f}"
    )


    # -----------------------------------------------------------------------
    # MARKDOWN COMPONENTS
    # -----------------------------------------------------------------------

    coverage_markdown = [
        "| Subreddit | Comments | First | Last | Missing study years |",
        "|---|---:|---|---|---|",
    ]

    for row in (
        coverage.itertuples()
    ):
        coverage_markdown.append(
            f"| r/{row.subreddit} | "
            f"{row.comments:,} | "
            f"{row.first} | "
            f"{row.last} | "
            f"{row.missing} |"
        )

    old_cap_markdown = "\n".join(
        f"- `{name}`"
        for name in OLD_CAP_FILES
    )

    funnel_markdown = (
        markdown_funnel_table(
            funnel
        )
    )

    capture_markdown = (
        markdown_capture_table(
            capture_table
        )
    )

    crawl_verification_text = (
        crawled_at_manifest_text(
            crawl_audit
        )
    )


    # -----------------------------------------------------------------------
    # AUTHORITATIVE MANIFEST
    # -----------------------------------------------------------------------

    manifest = f"""# CAV Reddit Corpus Manifest

## Frozen analysis corpus

Canonical analytical artefact:

`data/clean/corpus.parquet`

This manifest contains aggregate dataset metadata only. It contains no Reddit
usernames, author identifiers, comment text or raw Reddit comment IDs.

- Final corpus rows: {len(df):,}
- Observed date range: {date_start} to {date_end}
- Top-level raw JSON files read by preprocessing: {len(top_files):,}
- Parquet file SHA-256: `{artifact_hash}`
- Corpus membership SHA-256: `{membership_hash}`

The two hashes serve different purposes.

The **Parquet file SHA-256** identifies the exact stored artefact. It may change
if the same logical dataset is serialised under a different Parquet/PyArrow
environment.

The **Corpus membership SHA-256** is calculated from the sorted final Reddit
comment IDs. It therefore identifies comment membership independently of row
order and Parquet serialisation. It does not detect changes to other fields when
the comment-ID membership remains unchanged.

## Sampling configuration at freeze

- `PROBE_MAX_POSTS = {cfg.PROBE_MAX_POSTS}`
- `COLLECT_MAX_POSTS = {cfg.COLLECT_MAX_POSTS}`
- `MAX_POSTS_PER_BLOCK = {cfg.MAX_POSTS_PER_BLOCK}`
- `MAX_POSTS_PER_SUPP_BLOCK = {cfg.MAX_POSTS_PER_SUPP_BLOCK}`
- `MAX_COMMENTS_PER_POST = {cfg.MAX_COMMENTS_PER_POST}`
- `MAX_COMMENTS_PER_RUN = {cfg.MAX_COMMENTS_PER_RUN}`
- `BLOCKING_MODE = "{cfg.BLOCKING_MODE}"`
- Study window: `{cfg.STUDY_START}` to `{cfg.STUDY_END}`

### Sampling intensity is uneven by design

A saturated query receives at most 48 posts (10 annual blocks x 3, plus 9
supplementary blocks x 2). An unsaturated query receives up to 100 posts in a
single window. High-volume query-subreddit pairs are therefore sampled less
densely than low-volume ones.

All longitudinal estimands must consequently be share-based. Comment and post
counts are a function of the sampling configuration and must not be interpreted as
measures of discourse volume.

## Comment capture rate

Reddit's `commentsCount` field stored on each sampled post provides a
Reddit-reported measure of thread size. It is not treated as an exact
ground-truth count of retrievable comments.

For each sampled thread, the capture denominator is defined conservatively as:

`max(commentsCount, unique comments captured)`

This guarantees that estimated capture cannot exceed 100% for an individual
thread while making the smallest correction supported directly by the observed
data.

- Sampled threads with a post record: **{sampled_threads:,}**
- Reddit-reported `commentsCount` total: **{comments_reported:,}**
- Effective denominator after correction: **{comments_effective:,}**
- Denominator adjustment: **{capture_consistency['denominator_adjustment']:,} comments**
- Unique comments captured from those threads: **{comments_captured:,}**
- Original uncorrected capture rate: **{capture_consistency['original_rate']:.3f}%**
- Corrected overall capture rate: **{overall_capture_rate:.3f}%**

### Denominator consistency check

On **{capture_consistency['inconsistent_threads']:,} of {sampled_threads:,} threads
({capture_consistency['inconsistent_pct']:.1f}%)**, the number of unique comments
actually captured exceeded the stored `commentsCount`.

The total excess was **{capture_consistency['total_excess']:,} comments**, with a
maximum excess of **{capture_consistency['maximum_excess']} comments on any one
thread**.

Those inconsistent threads contained
**{capture_consistency['deleted']:,} `[deleted]`** and
**{capture_consistency['removed']:,} `[removed]`** comments. In
**{capture_consistency['fully_covered']:,} of
{capture_consistency['inconsistent_threads']:,} threads**, the number of
deleted/removed comments was sufficient to numerically cover the observed excess.
The remaining unexplained excess after allowing for deletion/removal status was
**{capture_consistency['unexplained_excess']:,} comments**.

This is consistent with Reddit's treatment of deleted and removed comment nodes
contributing to the discrepancy, but it does not establish Reddit's exact internal
counting semantics.

The reported capture rate is therefore a slight **overestimate** of true capture
against a complete denominator: the denominator undercounts the retrievable set,
so the ratio is inflated.

This discrepancy is detectable only where capture approaches 100%, which is why
the effective and reported denominators differ solely in the 1-5 and 6-15 thread
buckets. On a thread where 0.7% of comments are retrieved, an undercounted
denominator cannot be observed at all. The
**{capture_consistency['inconsistent_pct']:.1f}%** figure is therefore a **lower
bound** on how often `commentsCount` is unreliable, not an estimate of it.


### Capture rate by Reddit-reported thread size

{capture_markdown}

Thread-size categories are based on Reddit's reported `commentsCount`, while the
capture denominator within each category uses the conservative corrected value
defined above.

Capture falls sharply as Reddit-reported thread size increases because
`MAX_COMMENTS_PER_POST = {cfg.MAX_COMMENTS_PER_POST}` limits comments retrieved
from each thread per scraper run. The same strong size-dependent pattern was
reproduced on the complete collection frame.

This provides direct evidence that collected comment counts are a function of the
sampling configuration and must not be interpreted as measures of discourse
volume. Longitudinal estimands are therefore share-based rather than count-based.

## Corpus composition by tier

{markdown_series_table(tier_counts, "Tier")}

## Corpus composition by year

{markdown_series_table(year_counts, "Year")}

## Subreddit temporal coverage

{chr(10).join(coverage_markdown)}

A subreddit with no surviving comments in one or more study years cannot
independently support a complete 2016-2025 annual longitudinal series. The study
window itself ends on 30 April 2025, so 2025 is a partial calendar year by design.

## Preprocessing

`02_preprocess.py` reads the non-recursive glob:

`data/raw/*.json`

The following diagnostic and archive directories are therefore outside the
analytical input:

- `data/raw/_archive_tier3_v1/`
- `data/raw/_failed_backfill/`
- `data/raw/_direct_test/`
- `data/raw/_phrase_test/`
- `data/raw/_probe/`
- `data/raw/_archive_skeleton_test/`

The skeleton test file was moved into `_archive_skeleton_test` before the final
preprocessing run. Its records were dated in July 2026 and had already been
removed by the study-window filter, so this archival move changed the raw-input
count but did not change the final 2016-2025 corpus.

The final analytical corpus contains no Reddit author-name or author-ID columns.

Duplicate Reddit comment IDs after preprocessing: **{duplicate_final_ids}**

### Preprocessing funnel

{funnel_markdown}

The **20-word floor is the largest single filter** in the frozen preprocessing
run. The English filter is effectively inert in this corpus: all comments that
reached that stage were retained. `langdetect` runs only on comments that have
already cleared the 20-word floor, where language identification is more reliable,
so the English filter should not be presented as a material source of attrition.

Raw-union maximum unique comments per Reddit thread: **{raw_max_thread}**

Raw-union threads exceeding 15 unique comments: **{raw_threads_over_15}**

Final maximum surviving comments per Reddit thread: **{final_max_thread}**

Final threads exceeding 15 surviving comments: **{final_threads_over_15}**

The 15-comment collection cap applied per scraper run, not globally to a Reddit
thread. Overlapping search jobs can therefore produce more than 15 unique raw
comments for one thread. The final thread count is measured after cross-file
deduplication, body/deletion filtering, bot filtering, the study-window filter,
the 20-word floor and the English-language filter. Any final maximum of 15 or
less is therefore an observed preprocessing outcome rather than a globally
enforced collection constraint.

The raw-union maximum was only **{raw_max_thread} unique comments per thread**,
with only **{raw_threads_over_15} thread** exceeding 15, despite
**{C2_DUPLICATE_POST_RETRIEVALS} duplicate post retrievals during C2**. This is
evidence that repeat crawls of the same Reddit thread returned a near-identical
set of comments rather than accumulating substantially different comment samples.

## Excluded collection: Tier 3 v1

535 comments collected under five multi-word Tier 3 search terms were archived to
`data/raw/_archive_tier3_v1/` and excluded from the analytical corpus.

Measured cause: the scraper does not phrase-match unquoted search terms of three
or more tokens. Across 78 collected files, 0% of posts returned by 3-token terms
contained the search phrase and 7% of those returned by 4-token terms did, against
87-98% for 1-2 token terms. The retrieved posts were consequently off-topic.

Controlled test, 16 August 2026, USD 0.16: quotation marks are passed to Reddit's
search endpoint verbatim, and a quoted 2-token search returned 25 posts at 100%
phrase precision. Tier 3 was redesigned so the subreddit carries the privacy and
security framing while the search term carries only the CAV framing.

Files retained for audit. Logged expenditure USD 7.02.

## Historical collection-cap note

`job_path()` encodes subreddit, search term and date range but does not encode
collection caps. A filename therefore does not, by itself, identify the cap that
was in force when that file was originally collected.

`COLLECT_MAX_POSTS` was raised from 60 to 100 on 16 August 2026.

The ten production files originally collected under the former 60-post cap were:

{old_cap_markdown}

Their known probe/production discrepancy was subsequently addressed through the
documented direct URL recovery workflow. The original cap setting remains part
of the corpus audit history.

### MAX_COMMENTS_PER_POST 25 -> 15 verification

`MAX_COMMENTS_PER_POST` was changed from 25 to 15 on 3 August 2026. The frozen
raw files were checked directly using their record-level `crawledAt` timestamps
rather than assuming that the new cap predated production.

{crawl_verification_text}

## Current frame versus scrape log

The final current production frame generated by `build_jobs()` contains
**{len(current_jobs):,} jobs**.

`scrape_log.csv` contains **{len(log):,} rows** because it is an append-only
execution and expenditure record, not a corpus manifest.

The audited log composition is:

| Log component | Rows |
|---|---:|
| Current standard frame before C2 | 387 |
| Tier 3 v1, subsequently archived | 55 |
| C2 supplementary sampling | 297 |
| Direct URL recovery | 10 |
| Failed date-tail backfill | 1 |
| **Total** | **750** |

The difference between **750 log rows** and **684 current jobs** is therefore
intentional.

## Collection expenditure

- Logged collection expenditure: **USD {logged_spend:.2f}**
- Approximate probe and diagnostic expenditure outside `scrape_log.csv`:
  **~USD {APPROX_UNLOGGED_SPEND:.2f}**
- Approximate true collection-stage expenditure:
  **~USD {true_spend_approx:.2f}**
- Logged expenditure attributable to archived or failed work:
  **USD {SUNK_LOGGED_SPEND:.2f}**
- Configured safety ceiling:
  **USD {cfg.BUDGET_USD_CAP:.2f}**

The budget cap was a safety ceiling, not a spending target.

## C2 supplementary sampling

C2 added nine January-June supplementary blocks for each of the 33 saturated
query pairs, producing 297 supplementary jobs.

The supplementary cap was two posts per block. C2 collected 467 posts and 5,600
comments, 6,067 items in total, at a logged cost of USD 18.07 against a pre-run
prediction of USD 18.30.

On the complete current annual-block frame, the pre-C2 within-year
sampling-position slope was **+0.0256/year (p = 0.0075)**.

After C2, using the deduplicated effective sample, the slope was
**+0.0133/year (p = 0.0209)**.

C2 therefore reduced the slope magnitude by approximately **48%**, but the
residual drift remained statistically distinguishable from zero.

The earlier 181-post diagnostic that triggered C2 measured **+0.044/year
(p = 0.0055)**. Relative to the complete annual-frame value of +0.0256/year, the
subsample overstated the slope magnitude by roughly 70%. The temporal defect was
real, but materially less severe than the original diagnostic indicated.

Annual/supplementary overlaps are deduplicated in the primary C2 diagnostic
because duplicate retrieval of the same Reddit thread is not an independent
sampling event and identical Reddit comment IDs are deduplicated by
`02_preprocess.py`. This deduplication rule was selected on methodological
grounds before its effect on the drift estimate was known.

The raw-overlap sensitivity result was **+0.0190/year (p = 0.0098)**.

The final within-year sample remains boundary-weighted rather than uniform.
Accordingly, the sampling design supports annual longitudinal analysis and does
not support quarterly-resolution claims.

## Planned seasonality sensitivity check

After concern classification is complete, concern share will be compared between
H1 (January-June) and H2 (July-December) for the complete calendar years
2016-2024.

The residual sampling-position slope corresponds to an approximately 0.10-year
shift across the study span, roughly five weeks later in the calendar in later
years.

This can bias the longitudinal concern estimate only if concern itself varies
materially by season.

If the H1-H2 concern difference is small relative to the observed longitudinal
effect, the residual sampling drift will be bounded as unlikely to be materially
consequential despite its statistical significance.

If a material H1-H2 difference exists, seasonality will remain an explicit
limitation and an additional sensitivity analysis will be applied to the
longitudinal result.
"""


    # -----------------------------------------------------------------------
    # WRITE BOTH MANIFEST COPIES
    # -----------------------------------------------------------------------

    LOCAL_MANIFEST.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    VERSIONED_MANIFEST.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOCAL_MANIFEST.write_text(
        manifest,
        encoding="utf-8",
    )

    VERSIONED_MANIFEST.write_text(
        manifest,
        encoding="utf-8",
    )


    # -----------------------------------------------------------------------
    # VERIFY BOTH COPIES ARE IDENTICAL
    # -----------------------------------------------------------------------

    local_text = (
        LOCAL_MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    versioned_text = (
        VERSIONED_MANIFEST.read_text(
            encoding="utf-8"
        )
    )

    if local_text != versioned_text:
        raise SystemExit(
            "[stop] local and version-controlled "
            "manifest copies differ after writing."
        )


    # -----------------------------------------------------------------------
    # SUCCESS
    # -----------------------------------------------------------------------

    print(
        f"\n[write] local manifest      "
        f"{LOCAL_MANIFEST}"
    )

    print(
        f"[write] versioned manifest  "
        f"{VERSIONED_MANIFEST}"
    )

    print(
        "\n[PASS] final corpus QA passed."
    )

    print(
        "[PASS] no duplicate final comment IDs."
    )

    print(
        "[PASS] study-window and tier checks passed."
    )

    print(
        "[PASS] analytical corpus contains no "
        "author-name or author-ID columns."
    )

    print(
        "[PASS] capture-rate statistics written "
        "to the manifest."
    )

    print(
        "[PASS] MAX_COMMENTS_PER_POST timing audit "
        "written to the manifest."
    )

    print(
        "[PASS] both manifest copies are identical."
    )

    print(
        "[done] corpus freeze complete."
    )


if __name__ == "__main__":
    main()
