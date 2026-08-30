"""
check_capture_rate.py -- DIAGNOSTIC. No network, no cost.

Measures what fraction of comments on sampled Reddit threads were captured.

Reddit's post record contains `commentsCount`, which is used as the reported
thread-size denominator. Final audit showed that this value is not an exact
ground-truth denominator at the individual-thread level:

    95 of 2,237 sampled threads (4.2%) contained more unique captured comments
    than the stored commentsCount value.

The discrepancies were small:
    total excess = 128 comments
    maximum excess on one thread = 4 comments

All 95 inconsistent threads contained enough [deleted] and/or [removed] comment
nodes to numerically cover the excess. This is consistent with Reddit's treatment
of deleted/removed comments contributing to the discrepancy, but it does not prove
the exact internal semantics of commentsCount.

For a conservative denominator this script therefore uses:

    effective denominator = max(commentsCount, unique comments captured)

This guarantees that capture cannot exceed 100% on any thread while making the
smallest correction supported directly by the observed data.

WHY IT MATTERS
--------------
MAX_COMMENTS_PER_POST = 15 caps comments per thread per scraper run, so capture
rate falls sharply as thread size increases. Collected comment volume is therefore
a function of the sampling configuration rather than a direct measure of discourse
volume.

Longitudinal estimands must consequently be share-based rather than based on raw
comment counts.

Run:
    (.venv active) python check_capture_rate.py

Input:
    data/raw/*.json

The glob is deliberately non-recursive and matches 02_preprocess.py.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd


RAW_DIR = Path("data/raw")

BUCKETS = [
    -1,
    0,
    5,
    15,
    50,
    200,
    1000,
    10**9,
]

LABELS = [
    "0",
    "1-5",
    "6-15",
    "16-50",
    "51-200",
    "201-1000",
    "1000+",
]


def main() -> None:
    files = sorted(
        RAW_DIR.glob("*.json")
    )

    if not files:
        raise SystemExit(
            f"[stop] no *.json files in {RAW_DIR}"
        )

    # Reddit-reported thread size.
    # Same post may occur in several collection files, so retain the maximum
    # observed commentsCount for that post.
    posts: dict[str, int] = {}

    # Unique captured comment IDs per post.
    captured_ids: dict[
        str,
        set[str],
    ] = defaultdict(set)

    # Body status is retained only to test [deleted] / [removed] behaviour.
    comment_bodies: dict[
        str,
        dict[str, str],
    ] = defaultdict(dict)

    for path in files:
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
                        f"[stop] non-numeric commentsCount "
                        f"in {path.name}"
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

                captured_ids[
                    post_id
                ].add(
                    comment_id
                )

                if (
                    comment_id
                    not in comment_bodies[
                        post_id
                    ]
                ):
                    comment_bodies[
                        post_id
                    ][
                        comment_id
                    ] = str(
                        record.get(
                            "body"
                        )
                        or ""
                    ).strip().lower()

    if not posts:
        raise SystemExit(
            "[stop] no post records found"
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
                {}
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

                "captured":
                    captured_count,

                "effective":
                    effective_denominator,

                "excess":
                    excess,

                "deleted":
                    deleted_count,

                "removed":
                    removed_count,
            }
        )

    df = pd.DataFrame(
        rows
    )

    df[
        "bucket"
    ] = pd.cut(
        df[
            "reported"
        ],
        BUCKETS,
        labels=LABELS,
    )

    # ------------------------------------------------------------------
    # OVERALL TOTALS
    # ------------------------------------------------------------------

    total_reported = int(
        df[
            "reported"
        ].sum()
    )

    total_effective = int(
        df[
            "effective"
        ].sum()
    )

    total_captured = int(
        df[
            "captured"
        ].sum()
    )

    denominator_adjustment = (
        total_effective
        - total_reported
    )

    original_rate = (
        100
        * total_captured
        / total_reported
        if total_reported
        else float("nan")
    )

    corrected_rate = (
        100
        * total_captured
        / total_effective
        if total_effective
        else float("nan")
    )

    # ------------------------------------------------------------------
    # THREADS WHERE CAPTURED > commentsCount
    # ------------------------------------------------------------------

    inconsistent = df[
        df[
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
        / len(df)
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

    deleted_in_inconsistent = int(
        inconsistent[
            "deleted"
        ].sum()
    )

    removed_in_inconsistent = int(
        inconsistent[
            "removed"
        ].sum()
    )

    deleted_removed_total = (
        deleted_in_inconsistent
        + removed_in_inconsistent
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

    unexplained_after_deleted_removed = int(
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

    # ------------------------------------------------------------------
    # BY-SIZE TABLE
    # ------------------------------------------------------------------

    grouped = (
        df
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
            df[
                "effective"
            ]
            == 0
        ).sum()
    )

    # ------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------

    print(
        "=" * 74
    )

    print(
        "CAPTURE RATE AGAINST REDDIT-REPORTED THREAD SIZE"
    )

    print(
        "=" * 74
    )

    print(
        f"\nsampled threads               "
        f"{len(df):,}"
    )

    print(
        f"reported commentsCount total   "
        f"{total_reported:,}"
    )

    print(
        f"effective denominator total    "
        f"{total_effective:,}"
    )

    print(
        f"denominator adjustment         "
        f"{denominator_adjustment:,}"
    )

    print(
        f"unique comments captured       "
        f"{total_captured:,}"
    )

    print(
        f"original capture rate          "
        f"{original_rate:.3f}%"
    )

    print(
        f"CORRECTED OVERALL CAPTURE RATE "
        f"{corrected_rate:.3f}%"
    )

    print(
        "\nDENOMINATOR CONSISTENCY"
    )

    print(
        f"threads where captured > "
        f"commentsCount     "
        f"{inconsistent_threads:,} "
        f"({inconsistent_pct:.1f}%)"
    )

    print(
        f"total denominator correction   "
        f"{total_excess:,}"
    )

    print(
        f"maximum correction one thread  "
        f"{maximum_excess}"
    )

    print(
        f"[deleted] comments in those "
        f"threads        "
        f"{deleted_in_inconsistent:,}"
    )

    print(
        f"[removed] comments in those "
        f"threads        "
        f"{removed_in_inconsistent:,}"
    )

    print(
        f"deleted + removed              "
        f"{deleted_removed_total:,}"
    )

    print(
        f"threads where deleted/removed "
        f"cover excess  "
        f"{fully_covered:,} of "
        f"{inconsistent_threads:,}"
    )

    print(
        f"unexplained excess after "
        f"deleted/removed       "
        f"{unexplained_after_deleted_removed:,}"
    )

    print(
        "\nBY THREAD SIZE"
    )

    print()

    print(
        grouped.to_string()
    )

    print(
        f"\nthreads with no comments at all: "
        f"{zero_threads:,} "
        f"({100 * zero_threads / len(df):.0f}% "
        f"of sampled posts)"
    )

    print(
        "\nINTERPRETATION"
    )

    print(
        "`commentsCount` is a Reddit-reported thread-size "
        "measure, not a verified"
    )

    print(
        "ground-truth count of retrievable comments."
    )

    print(
        "Where observed unique captured comments exceed "
        "`commentsCount`, the"
    )

    print(
        "effective denominator is corrected upward to the "
        "observed captured count."
    )

    print(
        "All observed discrepancies are numerically covered "
        "by [deleted] and/or"
    )

    print(
        "[removed] comments on those threads. This is "
        "consistent with deletion/"
    )

    print(
        "removal status contributing to the discrepancy, "
        "but does not prove Reddit's"
    )

    print(
        "internal counting semantics."
    )

    print(
        "\nThe corrected denominator guarantees per-thread "
        "capture <= 100% and makes"
    )

    print(
        "the smallest adjustment supported directly by "
        "the observed data."
    )


if __name__ == "__main__":
    main()