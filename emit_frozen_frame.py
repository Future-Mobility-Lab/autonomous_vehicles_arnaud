"""
emit_frozen_frame.py

Write the frozen annotation draw frame and verify it against the hash recorded in
docs/analysis_preregistration.md (R5).

The frame is derived from corpus v2.2 by a rule, not by hand:

    corpus v2.2                                   12,778
      less codebook worked examples surviving        -59
    = annotatable pool                            12,719
      less organic duplicate-text rows               -8
      less remaining Tier 3 items                   -543
    = Tier 1+2 draw frame                         12,168

Duplicate rule: among rows sharing identical clean_body, retain the row with the
lexicographically smallest comment id. Applies to the DRAW only -- all such rows
are retained in the analysis corpus.

The script FAILS LOUDLY if the frame hash does not match the pre-registered value.
A mismatch means the corpus or the derivation has changed and the pre-registration
no longer describes the data.

Run BEFORE committing the pre-registration, so that the committed hash is one that
has actually been reproduced.

Usage:
    python emit_frozen_frame.py

In:
    data/clean_v2_2/corpus.parquet
    data/clean/corpus.parquet
    data/clean/corpus_annotatable.parquet

Out:
    data/frozen/draw_frame_ids.txt
    data/frozen/excluded_duplicate_text.txt
    data/frozen/frame_manifest.txt
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

CORPUS_V22 = Path("data/clean_v2_2/corpus.parquet")
CORPUS_V1 = Path("data/clean/corpus.parquet")
ANNOTATABLE_V1 = Path("data/clean/corpus_annotatable.parquet")
FROZEN_DIR = Path("data/frozen")


# ---------------------------------------------------------------------------
# Frozen expected values
# ---------------------------------------------------------------------------

EXPECTED_FRAME_ROWS = 12_166

EXPECTED_FRAME_SHA256 = (
    "ce85a3b046fedf3648861d446832a364ab89e7b60a0e58f10272b33b1997d7b3"
)

EXPECTED_CORPUS_SHA256 = (
    "d187adac10d98ccda1f0145713139f008705349ea6e0b4921092b1ad099559d4"
)

EXPECTED_BOUNDARY = "2021-12-29T21:39:22+00:00"

EXPECTED_EARLY = 6_083
EXPECTED_LATE = 6_083

EXPECTED_ERAS = {
    "2016-2018": 2495,
    "2019-2021": 3633,
    "2022-2025": 6038,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def membership_sha256(ids) -> str:
    """
    SHA-256 over sorted ids, newline-joined, with no trailing newline.
    """
    return hashlib.sha256(
        "\n".join(
            sorted(ids)
        ).encode("utf-8")
    ).hexdigest()


def write_lines(
    path: Path,
    lines,
) -> None:
    """
    Write with LF endings explicitly.

    On Windows the default may otherwise be CRLF, which changes the bytes of
    any file whose hash or exact content is cited.
    """
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        path,
        "w",
        encoding="utf-8",
        newline="\n",
    ) as fh:
        fh.write(
            "\n".join(lines)
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # ------------------------------------------------------------------
    # Preconditions
    # ------------------------------------------------------------------

    for path in (
        CORPUS_V22,
        CORPUS_V1,
        ANNOTATABLE_V1,
    ):
        if not path.exists():
            sys.exit(
                f"[FAIL] missing {path}"
            )

    # ------------------------------------------------------------------
    # Load source corpora
    # ------------------------------------------------------------------

    corpus = pd.read_parquet(
        CORPUS_V22
    )

    v1 = pd.read_parquet(
        CORPUS_V1
    )

    ann_v1 = pd.read_parquet(
        ANNOTATABLE_V1
    )

    worked_examples = (
        set(v1.id)
        - set(ann_v1.id)
    )

    # ------------------------------------------------------------------
    # Verify corpus v2.2 membership
    # ------------------------------------------------------------------

    corpus_hash = membership_sha256(
        corpus.id.astype(str)
    )

    print(
        f"[corpus] rows {len(corpus):,}  "
        f"sha256 {corpus_hash}"
    )

    if corpus_hash != EXPECTED_CORPUS_SHA256:
        sys.exit(
            "[FAIL] corpus membership hash does not match R5. "
            "Stop: the pre-registration does not describe this corpus."
        )

    print(
        "[corpus] matches R5  PASS\n"
    )

    # ------------------------------------------------------------------
    # Derive annotation frame
    # ------------------------------------------------------------------

    surviving = (
        worked_examples
        & set(corpus.id)
    )

    annotatable = corpus[
        ~corpus.id.isin(
            worked_examples
        )
    ]

    print(
        f"[frame] worked examples: "
        f"{len(worked_examples)} drawn, "
        f"{len(surviving)} surviving into v2.2"
    )

    print(
        f"[frame] annotatable pool: "
        f"{len(annotatable):,}"
    )

    # Duplicate-text rule:
    # sort by id so keep="first" retains the lexicographically smallest id.
    ordered = annotatable.sort_values(
        "id",
        kind="mergesort",
    )

    duplicates = ordered[
        ordered.clean_body.duplicated(
            keep="first"
        )
    ]

    deduped = ordered[
        ~ordered.id.isin(
            duplicates.id
        )
    ]

    frame = (
        deduped[
            deduped.tier != "Tier 3"
        ]
        .sort_values("id")
    )

    tier3_dropped = int(
        (
            deduped.tier == "Tier 3"
        ).sum()
    )

    print(
        f"[frame] duplicate-text rows dropped: "
        f"{len(duplicates)}"
    )

    print(
        f"[frame] Tier 3 rows dropped: "
        f"{tier3_dropped}"
    )

    print(
        f"[frame] draw frame: "
        f"{len(frame):,}"
    )

    # ------------------------------------------------------------------
    # Verify frozen frame
    # ------------------------------------------------------------------

    frame_hash = membership_sha256(
        frame.id.astype(str)
    )

    ok = True

    # ---- row count ----------------------------------------------------

    rows_ok = (
        len(frame)
        == EXPECTED_FRAME_ROWS
    )

    print(
        f"\n[verify] rows      "
        f"actual {len(frame):,}  "
        f"expected {EXPECTED_FRAME_ROWS:,}  "
        f"{'PASS' if rows_ok else 'FAIL'}"
    )

    ok &= rows_ok

    # ---- membership hash ---------------------------------------------

    hash_ok = (
        frame_hash
        == EXPECTED_FRAME_SHA256
    )

    print(
        f"[verify] sha256    "
        f"{frame_hash}"
    )

    print(
        f"[verify] expected  "
        f"{EXPECTED_FRAME_SHA256}  "
        f"{'PASS' if hash_ok else 'FAIL'}"
    )

    ok &= hash_ok

    # ---- temporal boundary and split ---------------------------------

    by_created = frame.sort_values(
        "created"
    )

    boundary = (
        by_created.created.iloc[
            len(by_created) // 2
        ]
    )

    boundary_iso = (
        boundary.isoformat()
    )

    early = int(
        (
            frame.created < boundary
        ).sum()
    )

    late = int(
        (
            frame.created >= boundary
        ).sum()
    )

    boundary_ok = (
        boundary_iso
        == EXPECTED_BOUNDARY
    )

    split_ok = (
        early == EXPECTED_EARLY
        and late == EXPECTED_LATE
    )

    print(
        f"[verify] boundary  "
        f"{boundary_iso}  "
        f"{'PASS' if boundary_ok else 'FAIL'}"
    )

    print(
        f"[verify] split     "
        f"actual {early:,} / {late:,}  "
        f"expected {EXPECTED_EARLY:,} / {EXPECTED_LATE:,}  "
        f"{'PASS' if split_ok else 'FAIL'}"
    )

    ok &= boundary_ok
    ok &= split_ok

    # ---- era counts ---------------------------------------------------

    eras = pd.cut(
        frame.year,
        [
            2015,
            2018,
            2021,
            2025,
        ],
        labels=[
            "2016-2018",
            "2019-2021",
            "2022-2025",
        ],
    )

    actual_eras = (
        eras.value_counts()
        .sort_index()
        .to_dict()
    )

    era_ok = (
        actual_eras
        == EXPECTED_ERAS
    )

    print(
        f"[verify] eras      "
        f"{actual_eras}  "
        f"{'PASS' if era_ok else 'FAIL'}"
    )

    ok &= era_ok

    # ------------------------------------------------------------------
    # Hard stop on any mismatch
    # ------------------------------------------------------------------

    if not ok:
        sys.exit(
            "\n[FAIL] frame does not match the pre-registered values. "
            "Do not commit. Resolve the discrepancy first."
        )

    # ------------------------------------------------------------------
    # Write frozen artefacts
    # ------------------------------------------------------------------

    write_lines(
        FROZEN_DIR
        / "draw_frame_ids.txt",
        sorted(
            frame.id.astype(str)
        ),
    )

    write_lines(
        FROZEN_DIR
        / "excluded_duplicate_text.txt",
        [
            (
                "# dropped from the annotation draw only; "
                "retained in the analysis corpus"
            ),
            (
                "# rule: among rows with identical clean_body, "
                "retain the smallest id"
            ),
        ]
        + sorted(
            duplicates.id.astype(str)
        ),
    )

    write_lines(
        FROZEN_DIR
        / "frame_manifest.txt",
        [
            "# Annotation draw frame manifest -- corpus v2.2",
            (
                f"corpus_rows                "
                f"{len(corpus)}"
            ),
            (
                f"corpus_membership_sha256   "
                f"{corpus_hash}"
            ),
            (
                f"annotatable_pool           "
                f"{len(annotatable)}"
            ),
            (
                f"duplicate_rows_dropped     "
                f"{len(duplicates)}"
            ),
            (
                f"tier3_rows_dropped         "
                f"{tier3_dropped}"
            ),
            (
                f"draw_frame_rows            "
                f"{len(frame)}"
            ),
            (
                f"frame_membership_sha256    "
                f"{frame_hash}"
            ),
            (
                f"temporal_fold_boundary     "
                f"{boundary_iso}"
            ),
            (
                f"temporal_split             "
                f"{early} / {late}"
            ),
            (
                f"era_2016_2018              "
                f"{actual_eras['2016-2018']}"
            ),
            (
                f"era_2019_2021              "
                f"{actual_eras['2019-2021']}"
            ),
            (
                f"era_2022_2025              "
                f"{actual_eras['2022-2025']}"
            ),
            (
                "random_seed                "
                "24916660"
            ),
        ],
    )

    print(
        f"\n[write] "
        f"{FROZEN_DIR / 'draw_frame_ids.txt'}"
    )

    print(
        f"[write] "
        f"{FROZEN_DIR / 'excluded_duplicate_text.txt'}"
    )

    print(
        f"[write] "
        f"{FROZEN_DIR / 'frame_manifest.txt'}"
    )

    print(
        "\n[done] frame matches the pre-registration. "
        "Safe to commit."
    )


if __name__ == "__main__":
    main()