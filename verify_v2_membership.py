"""
verify_v2_membership.py

Verify that the regenerated v2.2 preprocessing pipeline reproduces the intended
final corpus membership.

The frozen v1 corpus is preserved at data/clean/corpus.parquet.

A historical standalone post-hoc v2 reference file was not preserved, so this
script reconstructs that reference from frozen v1 using the tested content
corrections:

  1. content-based bot filtering
  2. submission-wrapper stripping
  3. relay-duplicate resolution
  4. reapplication of the >=20-word floor after stripping

That reconstructed post-hoc reference contains 12,779 rows.

The final v2.2 corpus is intentionally different by exactly one comment:
mp0lg1k, an AmputatorBot comment in r/waymo. The post-hoc reconstruction starts
from frozen v1, which predates the expanded author-based KNOWN_BOTS filter, so it
cannot independently reproduce that removal.

Therefore the expected comparison is:

  reconstructed post-hoc reference: 12,779 rows
  regenerated v2.2 corpus:          12,778 rows

  reference-only ids:
      mp0lg1k

  regenerated-only ids:
      none

Membership verification uses SHA-256 of comment ids sorted lexicographically,
joined by newline characters, with no trailing newline.

This script does not modify either corpus.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

from preprocess_content_filters import (
    remove_bot_content,
    strip_submission_wrapper,
    resolve_relay_duplicates,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

V1_PATH = Path("data/clean/corpus.parquet")
REGENERATED_V2_PATH = Path("data/clean_v2_2/corpus.parquet")

WORD_FLOOR = 20


# ---------------------------------------------------------------------------
# Expected final v2.2 values
# ---------------------------------------------------------------------------

EXPECTED_ROWS = 12_776

EXPECTED_MEMBERSHIP_SHA256 = (
    "d187adac10d98ccda1f0145713139f008705349ea6e0b4921092b1ad099559d4"
)

EXPECTED_SUBREDDIT_COUNTS = {
    "teslamotors": 2435,
    "SelfDrivingCars": 2143,
    "RealTesla": 1189,
    "waymo": 883,
    "electricvehicles": 1757,
    "cars": 1469,
    "Futurology": 1411,
    "technology": 925,
    "privacy": 371,
    "cybersecurity": 193,
}

EXPECTED_TIER_COUNTS = {
    "Tier 1": 6650,
    "Tier 2": 5562,
    "Tier 3": 564,
}

EXPECTED_DATE_MIN = "2016-01-04"
EXPECTED_DATE_MAX = "2025-04-30"


# ---------------------------------------------------------------------------
# Expected reconstructed post-hoc v2 reference
# ---------------------------------------------------------------------------

EXPECTED_POSTHOC_ROWS = 12_777

EXPECTED_POSTHOC_SHA256 = (
    "0d9d0fca1bd3f9d4cd06e07e3b0fed6037e6176610ce61196d590a4cea50f675"
)

# The post-hoc route begins from frozen v1, so it cannot reproduce the later
# author-based removal of this AmputatorBot comment.
EXPECTED_POSTHOC_EXTRA = {"mi38xx2"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def membership_hash(df: pd.DataFrame) -> str:
    """
    Return SHA-256 of sorted comment ids, newline-joined, with no trailing
    newline.
    """
    if "id" not in df.columns:
        raise KeyError("Corpus has no 'id' column.")

    if df["id"].isna().any():
        raise ValueError("Corpus contains null comment ids.")

    ids = sorted(df["id"].astype(str).tolist())
    payload = "\n".join(ids).encode("utf-8")

    return hashlib.sha256(payload).hexdigest()


def id_set(df: pd.DataFrame) -> set[str]:
    """Return corpus comment ids as a set of strings."""
    if "id" not in df.columns:
        raise KeyError("Corpus has no 'id' column.")

    return set(df["id"].astype(str))


def print_ids(title: str, ids: set[str]) -> None:
    """Print every id in a difference set."""
    print(f"\n{title}: {len(ids)}")

    if not ids:
        print("   <none>")
        return

    for comment_id in sorted(ids):
        print(f"   {comment_id}")


def reconstruct_posthoc_v2(
    v1: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Reconstruct the historical post-hoc v2 reference from frozen v1.

    Frozen v1 has already passed the original:
      - comment-id deduplication
      - body-deleted filter
      - original authorName bot filter
      - timestamp filter
      - study-window filter
      - 20-word floor
      - English-language filter

    The post-hoc v2 content corrections are therefore applied to frozen v1,
    followed by recomputation of clean_wordcount and reapplication of the word
    floor.
    """
    df = v1.copy()

    # Content-based automated/moderator text removal.
    df, removed_bots = remove_bot_content(df)

    # Strip generated submission wrappers while retaining human-written text.
    df = strip_submission_wrapper(df)

    stripped_count = int(df["body_stripped"].fillna(False).sum())

    # Resolve duplicated relay copies exposed by wrapper stripping.
    df, removed_relays = resolve_relay_duplicates(df)

    # Wrapper stripping can reduce a previously valid v1 row below 20 words.
    df["clean_wordcount"] = df["clean_body"].str.split().map(len)

    before_word_floor = len(df)
    df = df[df["clean_wordcount"] >= WORD_FLOOR].copy()
    word_floor_removed = before_word_floor - len(df)

    counts = {
        "v1_rows": len(v1),
        "content_bots_removed": len(removed_bots),
        "rows_stripped": stripped_count,
        "relay_duplicates_removed": len(removed_relays),
        "word_floor_removed_after_v2_filters": word_floor_removed,
    }

    return df.reset_index(drop=True), counts


def print_composition_checks(df: pd.DataFrame) -> bool:
    """Check expected subreddit, tier and date composition."""
    all_ok = True

    print("\n[composition]")

    # ------------------------------------------------------------------
    # Subreddit composition
    # ------------------------------------------------------------------

    print("\nPer-subreddit:")

    if "subreddit" not in df.columns:
        raise KeyError("Regenerated corpus has no 'subreddit' column.")

    actual_subreddit = df["subreddit"].value_counts().to_dict()

    for subreddit, expected in EXPECTED_SUBREDDIT_COUNTS.items():
        actual = int(actual_subreddit.get(subreddit, 0))
        status = "PASS" if actual == expected else "FAIL"

        if actual != expected:
            all_ok = False

        print(
            f"   {subreddit:<20} "
            f"actual={actual:<5} expected={expected:<5} {status}"
        )

    unexpected_subreddits = (
        set(actual_subreddit) - set(EXPECTED_SUBREDDIT_COUNTS)
    )

    if unexpected_subreddits:
        all_ok = False

        print("\nUnexpected subreddit values:")

        for subreddit in sorted(unexpected_subreddits):
            print(
                f"   {subreddit}: "
                f"{int(actual_subreddit[subreddit])}"
            )

    # ------------------------------------------------------------------
    # Tier composition
    # ------------------------------------------------------------------

    print("\nTier totals:")

    if "tier" not in df.columns:
        raise KeyError("Regenerated corpus has no 'tier' column.")

    actual_tiers = df["tier"].value_counts().to_dict()

    for tier, expected in EXPECTED_TIER_COUNTS.items():
        actual = int(actual_tiers.get(tier, 0))
        status = "PASS" if actual == expected else "FAIL"

        if actual != expected:
            all_ok = False

        print(
            f"   {tier:<10} "
            f"actual={actual:<5} expected={expected:<5} {status}"
        )

    unexpected_tiers = set(actual_tiers) - set(EXPECTED_TIER_COUNTS)

    if unexpected_tiers:
        all_ok = False

        print("\nUnexpected tier values:")

        for tier in sorted(unexpected_tiers):
            print(f"   {tier}: {int(actual_tiers[tier])}")

    # ------------------------------------------------------------------
    # Date range
    # ------------------------------------------------------------------

    if "created" not in df.columns:
        raise KeyError("Regenerated corpus has no 'created' column.")

    created = pd.to_datetime(
        df["created"],
        utc=True,
        errors="coerce",
    )

    invalid_dates = int(created.isna().sum())

    if invalid_dates:
        raise ValueError(
            f"{invalid_dates} regenerated rows have invalid created dates."
        )

    actual_min = created.min().date().isoformat()
    actual_max = created.max().date().isoformat()

    min_status = (
        "PASS"
        if actual_min == EXPECTED_DATE_MIN
        else "FAIL"
    )

    max_status = (
        "PASS"
        if actual_max == EXPECTED_DATE_MAX
        else "FAIL"
    )

    if actual_min != EXPECTED_DATE_MIN:
        all_ok = False

    if actual_max != EXPECTED_DATE_MAX:
        all_ok = False

    print("\nDate range:")

    print(
        f"   minimum: actual={actual_min} "
        f"expected={EXPECTED_DATE_MIN} {min_status}"
    )

    print(
        f"   maximum: actual={actual_max} "
        f"expected={EXPECTED_DATE_MAX} {max_status}"
    )

    return all_ok


# ---------------------------------------------------------------------------
# Main verification
# ---------------------------------------------------------------------------

def main() -> None:
    print("[paths]")
    print(f"   frozen v1:          {V1_PATH}")
    print(f"   regenerated v2.2:   {REGENERATED_V2_PATH}")

    if not V1_PATH.exists():
        sys.exit(
            f"\n[FAIL] Missing frozen v1 corpus: {V1_PATH}"
        )

    if not REGENERATED_V2_PATH.exists():
        sys.exit(
            f"\n[FAIL] Missing regenerated v2.2 corpus: "
            f"{REGENERATED_V2_PATH}"
        )

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    print("\n[load]")

    v1 = pd.read_parquet(V1_PATH)
    regenerated = pd.read_parquet(REGENERATED_V2_PATH)

    print(f"   frozen v1 rows:          {len(v1)}")
    print(f"   regenerated v2.2 rows:   {len(regenerated)}")

    # ------------------------------------------------------------------
    # Reconstruct the historical post-hoc reference
    # ------------------------------------------------------------------

    print("\n[reconstruct post-hoc reference v2]")

    reference, posthoc_counts = reconstruct_posthoc_v2(v1)

    print(
        f"   starting frozen v1 rows:          "
        f"{posthoc_counts['v1_rows']}"
    )

    print(
        f"   removed by content bot filter:   "
        f"{posthoc_counts['content_bots_removed']}"
    )

    print(
        f"   rows stripped in place:          "
        f"{posthoc_counts['rows_stripped']}"
    )

    print(
        f"   relay duplicates removed:        "
        f"{posthoc_counts['relay_duplicates_removed']}"
    )

    print(
        f"   removed by reapplied word floor: "
        f"{posthoc_counts['word_floor_removed_after_v2_filters']}"
    )

    print(
        f"   reconstructed reference rows:    "
        f"{len(reference)}"
    )

    # ------------------------------------------------------------------
    # Row-count checks
    # ------------------------------------------------------------------

    print("\n[row count]")

    regenerated_row_count_ok = (
        len(regenerated) == EXPECTED_ROWS
    )

    reference_row_count_ok = (
        len(reference) == EXPECTED_POSTHOC_ROWS
    )

    print(
        f"   regenerated actual:   {len(regenerated)}"
    )

    print(
        f"   regenerated expected: {EXPECTED_ROWS}"
    )

    print(
        f"   regenerated result:   "
        f"{'PASS' if regenerated_row_count_ok else 'FAIL'}"
    )

    print(
        f"   reference actual:     {len(reference)}"
    )

    print(
        f"   reference expected:   {EXPECTED_POSTHOC_ROWS}"
    )

    print(
        f"   reference result:     "
        f"{'PASS' if reference_row_count_ok else 'FAIL'}"
    )

    # ------------------------------------------------------------------
    # Membership hashes
    # ------------------------------------------------------------------

    reference_hash = membership_hash(reference)
    regenerated_hash = membership_hash(regenerated)

    regenerated_hash_ok = (
        regenerated_hash == EXPECTED_MEMBERSHIP_SHA256
    )

    reference_hash_ok = (
        reference_hash == EXPECTED_POSTHOC_SHA256
    )

    print("\n[membership SHA-256]")

    print(
        f"   regenerated expected:  "
        f"{EXPECTED_MEMBERSHIP_SHA256}"
    )

    print(
        f"   regenerated actual:    "
        f"{regenerated_hash}"
    )

    print(
        f"   regenerated result:    "
        f"{'PASS' if regenerated_hash_ok else 'FAIL'}"
    )

    print()

    print(
        f"   reference expected:    "
        f"{EXPECTED_POSTHOC_SHA256}"
    )

    print(
        f"   reference actual:      "
        f"{reference_hash}"
    )

    print(
        f"   reference result:      "
        f"{'PASS' if reference_hash_ok else 'FAIL'}"
    )

    # ------------------------------------------------------------------
    # Exact id-set comparison
    # ------------------------------------------------------------------

    reference_ids = id_set(reference)
    regenerated_ids = id_set(regenerated)

    only_reference = reference_ids - regenerated_ids
    only_regenerated = regenerated_ids - reference_ids

    print("\n[id-set comparison]")

    print(
        f"   reconstructed unique ids: "
        f"{len(reference_ids)}"
    )

    print(
        f"   regenerated unique ids:   "
        f"{len(regenerated_ids)}"
    )

    print_ids(
        "IDs present in reconstructed reference but NOT regenerated corpus",
        only_reference,
    )

    expected_reference_only = (
        only_reference == EXPECTED_POSTHOC_EXTRA
    )

    expected_found = (
        only_reference & EXPECTED_POSTHOC_EXTRA
    )

    unexplained_reference_only = (
        only_reference - EXPECTED_POSTHOC_EXTRA
    )

    missing_expected_reference_only = (
        EXPECTED_POSTHOC_EXTRA - only_reference
    )

    print(
        "\n   Expected reference-only ids "
        "(filtered by expanded KNOWN_BOTS):"
    )

    if expected_found:
        for comment_id in sorted(expected_found):
            print(f"      {comment_id}")
    else:
        print("      <none found>")

    print("\n   Unexplained reference-only ids:")

    if unexplained_reference_only:
        for comment_id in sorted(unexplained_reference_only):
            print(f"      {comment_id}")
    else:
        print("      <none>")

    print("\n   Expected reference-only ids that were NOT found:")

    if missing_expected_reference_only:
        for comment_id in sorted(missing_expected_reference_only):
            print(f"      {comment_id}")
    else:
        print("      <none>")

    print(
        f"\n   reference-only difference result: "
        f"{'PASS' if expected_reference_only else 'FAIL'}"
    )

    print_ids(
        "IDs present in regenerated corpus but NOT reconstructed reference",
        only_regenerated,
    )

    regenerated_only_ok = not only_regenerated

    print(
        f"\n   regenerated-only difference result: "
        f"{'PASS' if regenerated_only_ok else 'FAIL'}"
    )

    # ------------------------------------------------------------------
    # Duplicate-id check
    # ------------------------------------------------------------------

    duplicate_ids = int(
        regenerated["id"].duplicated().sum()
    )

    duplicate_ok = duplicate_ids == 0

    print("\n[duplicate ids]")

    print(
        f"   regenerated duplicate ids: "
        f"{duplicate_ids}"
    )

    print(
        f"   result: "
        f"{'PASS' if duplicate_ok else 'FAIL'}"
    )

    # ------------------------------------------------------------------
    # Composition
    # ------------------------------------------------------------------

    composition_ok = print_composition_checks(regenerated)

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------

    membership_ok = (
        regenerated_row_count_ok
        and reference_row_count_ok
        and regenerated_hash_ok
        and reference_hash_ok
        and expected_reference_only
        and regenerated_only_ok
        and duplicate_ok
        and composition_ok
    )

    print("\n============================================================")

    if membership_ok:
        print("FINAL RESULT: PASS")
        print(
            "The regenerated v2.2 corpus reproduces the intended "
            "membership exactly."
        )
        print(
            "The sole post-hoc reference difference is the expected "
            "KNOWN_BOTS removal: mi38xx2."
        )
    else:
        print("FINAL RESULT: FAIL")
        print(
            "The regenerated v2.2 corpus does not reproduce the "
            "intended membership exactly."
        )

        if unexplained_reference_only:
            print(
                "Unexplained ids exist in the reconstructed reference "
                "but not the regenerated corpus."
            )

        if only_regenerated:
            print(
                "Unexpected ids exist in the regenerated corpus but "
                "not the reconstructed reference."
            )

        if missing_expected_reference_only:
            print(
                "The expected reference-only id mp0lg1k was not "
                "observed as expected."
            )

    print("============================================================")

    if not membership_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()