"""
diagnose_bot_authors.py

Diagnose why the 17 content-based bot/moderator rows that were present in the
frozen v1 corpus survived the ORIGINAL authorName-based KNOWN_BOTS filter.

The historical v1 preprocessing run used an eight-account KNOWN_BOTS set. The
current v2.2 preprocessing script uses an expanded 13-account set. These must
not be conflated: the purpose of this diagnostic is to explain what happened
under the original eight-account filter.

The script:

  1. Re-identifies the 17 rows by applying remove_bot_content() to the frozen
     v1 corpus.

  2. Scans data/raw/*.json in the same sorted file order used by
     02_preprocess.py.

  3. Reports the authorName value from the FIRST raw occurrence of each comment
     id. This is important because 02_preprocess.py deduplicates by comment id
     before applying the authorName bot filter, with keep="first".

  4. Reports every additional raw occurrence of each id so inconsistent
     authorName metadata across duplicate retrievals can be detected.

  5. Tests each occurrence against the original eight-account KNOWN_BOTS set
     that produced frozen v1.

  6. Also tests each occurrence against the current KNOWN_BOTS set loaded from
     02_preprocess.py. This is a secondary comparison only and does not replace
     the historical eight-account diagnosis.

  7. Writes an audit CSV to:
         data/clean_v2_2/bot_author_diagnostic.csv

The audit CSV contains recovered raw account names and therefore remains inside
the gitignored data directory.

This is a diagnostic only. It does not modify the corpus or raw JSON files.
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pandas as pd

from preprocess_content_filters import remove_bot_content


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

RAW_DIR = Path("data/raw")
V1_PATH = Path("data/clean/corpus.parquet")
OUTPUT_CSV = Path(
    "data/clean_v2_2/bot_author_diagnostic.csv"
)
PREPROCESS_PATH = Path("02_preprocess.py")


# ---------------------------------------------------------------------------
# Historical configuration
# ---------------------------------------------------------------------------

# Exact eight-account KNOWN_BOTS set used by the preprocessing pipeline that
# produced frozen corpus v1.
ORIGINAL_KNOWN_BOTS = {
    "automoderator",
    "autotldr",
    "sneakpeekbot",
    "remindmebot",
    "b0trank",
    "wikitextbot",
    "gifv-bot",
    "totesmessenger",
}

EXPECTED_TARGET_ROWS = 17


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def author_state(
    item: dict,
) -> tuple[str, object, str, bool]:
    """
    Describe authorName exactly as the preprocessing pipeline would see it.

    Returns:
        state
        raw_value
        filter_value
        key_present
    """
    key_present = "authorName" in item
    raw_value = item.get("authorName")

    if not key_present:
        state = "missing"
        filter_value = ""

    elif raw_value is None:
        state = "null"
        filter_value = ""

    elif str(raw_value) == "":
        state = "blank"
        filter_value = ""

    else:
        state = "present"
        filter_value = str(raw_value).lower()

    return (
        state,
        raw_value,
        filter_value,
        key_present,
    )


# ---------------------------------------------------------------------------
# Main diagnostic
# ---------------------------------------------------------------------------

def main() -> None:
    # ------------------------------------------------------------------
    # Preconditions
    # ------------------------------------------------------------------

    if not V1_PATH.exists():
        sys.exit(
            f"[FAIL] Missing frozen v1 corpus: "
            f"{V1_PATH}"
        )

    if not RAW_DIR.exists():
        sys.exit(
            f"[FAIL] Missing raw directory: "
            f"{RAW_DIR}"
        )

    if not PREPROCESS_PATH.exists():
        sys.exit(
            f"[FAIL] Missing preprocessing script: "
            f"{PREPROCESS_PATH}"
        )

    # ------------------------------------------------------------------
    # Load the CURRENT KNOWN_BOTS set for secondary comparison.
    #
    # The historical diagnosis itself uses ORIGINAL_KNOWN_BOTS above.
    # ------------------------------------------------------------------

    preprocess_globals = runpy.run_path(
        str(PREPROCESS_PATH),
        run_name="diagnostic_config",
    )

    if "KNOWN_BOTS" not in preprocess_globals:
        sys.exit(
            "[FAIL] 02_preprocess.py does not define "
            "KNOWN_BOTS"
        )

    current_known_bots = {
        str(account).lower()
        for account in preprocess_globals["KNOWN_BOTS"]
    }

    print("[config]")

    print(
        f"   original KNOWN_BOTS count: "
        f"{len(ORIGINAL_KNOWN_BOTS)}"
    )

    print(
        f"   current KNOWN_BOTS loaded from: "
        f"{PREPROCESS_PATH}"
    )

    print(
        f"   current KNOWN_BOTS count:       "
        f"{len(current_known_bots)}"
    )

    # ------------------------------------------------------------------
    # Identify the 17 rows from frozen v1.
    # ------------------------------------------------------------------

    v1 = pd.read_parquet(
        V1_PATH
    )

    if "id" not in v1.columns:
        sys.exit(
            "[FAIL] Frozen v1 corpus has no id column."
        )

    if "clean_body" not in v1.columns:
        sys.exit(
            "[FAIL] Frozen v1 corpus has no clean_body column."
        )

    _, removed = remove_bot_content(
        v1
    )

    target_ids = set(
        removed["id"].astype(str)
    )

    print("\n[target rows]")

    print(
        f"   frozen v1 rows:              "
        f"{len(v1)}"
    )

    print(
        f"   content-filter target rows:  "
        f"{len(removed)}"
    )

    print(
        f"   unique target comment ids:   "
        f"{len(target_ids)}"
    )

    if len(removed) != EXPECTED_TARGET_ROWS:
        sys.exit(
            f"\n[FAIL] Expected {EXPECTED_TARGET_ROWS} "
            f"target rows but found {len(removed)}. "
            "Do not interpret the author diagnostic until "
            "this discrepancy is resolved."
        )

    # ------------------------------------------------------------------
    # Scan raw files in the SAME ordering used by 02_preprocess.py.
    #
    # The preprocessing pipeline does:
    #
    #   files = sorted(raw_dir.glob("*.json"))
    #   items.extend(data)
    #   df.drop_duplicates(subset="id", keep="first")
    #
    # Therefore the first occurrence found here is the occurrence whose
    # authorName would have survived deduplication into the author bot filter.
    # ------------------------------------------------------------------

    files = sorted(
        RAW_DIR.glob("*.json")
    )

    if not files:
        sys.exit(
            f"[FAIL] No raw JSON files found in "
            f"{RAW_DIR}"
        )

    occurrences: dict[
        str,
        list[dict],
    ] = {
        comment_id: []
        for comment_id in target_ids
    }

    for file_order, path in enumerate(files):
        try:
            data = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except json.JSONDecodeError as exc:
            print(
                f"[WARN] skipping unreadable "
                f"{path.name}: {exc}"
            )
            continue

        if not isinstance(data, list):
            continue

        for item_order, item in enumerate(data):
            if not isinstance(item, dict):
                continue

            comment_id = item.get("id")

            if comment_id is None:
                continue

            comment_id = str(
                comment_id
            )

            if comment_id not in target_ids:
                continue

            (
                state,
                raw_value,
                filter_value,
                key_present,
            ) = author_state(
                item
            )

            occurrences[
                comment_id
            ].append(
                {
                    "file_order": file_order,
                    "item_order": item_order,
                    "file": path.name,
                    "author_key_present": key_present,
                    "author_state": state,
                    "authorName": raw_value,
                    "filter_value": filter_value,
                    "matches_original_known_bot": (
                        filter_value
                        in ORIGINAL_KNOWN_BOTS
                    ),
                    "matches_current_known_bot": (
                        filter_value
                        in current_known_bots
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Build one audit row per target id.
    # ------------------------------------------------------------------

    audit_rows: list[dict] = []

    print(
        "\n[first raw occurrence used by original "
        "dedup logic]"
    )

    for comment_id in sorted(target_ids):
        hits = occurrences[
            comment_id
        ]

        if not hits:
            audit_rows.append(
                {
                    "id": comment_id,
                    "raw_occurrences": 0,
                    "first_file": None,
                    "first_item_order": None,
                    "first_author_key_present": None,
                    "first_author_state": "not_found",
                    "first_authorName": None,
                    "first_filter_value": None,
                    "first_matches_original_known_bot": None,
                    "first_matches_current_known_bot": None,
                    "all_author_states": None,
                    "all_authorNames": None,
                    "any_occurrence_matches_original_known_bot": None,
                    "any_occurrence_matches_current_known_bot": None,
                }
            )

            print(
                f"   {comment_id}: "
                "NOT FOUND IN CURRENT RAW FILES"
            )

            continue

        first = hits[0]

        all_states = [
            hit["author_state"]
            for hit in hits
        ]

        all_names = [
            hit["authorName"]
            for hit in hits
        ]

        any_original_known_bot = any(
            hit[
                "matches_original_known_bot"
            ]
            for hit in hits
        )

        any_current_known_bot = any(
            hit[
                "matches_current_known_bot"
            ]
            for hit in hits
        )

        audit_rows.append(
            {
                "id": comment_id,
                "raw_occurrences": len(hits),
                "first_file": first["file"],
                "first_item_order": first["item_order"],
                "first_author_key_present": first[
                    "author_key_present"
                ],
                "first_author_state": first[
                    "author_state"
                ],
                "first_authorName": first[
                    "authorName"
                ],
                "first_filter_value": first[
                    "filter_value"
                ],
                "first_matches_original_known_bot": first[
                    "matches_original_known_bot"
                ],
                "first_matches_current_known_bot": first[
                    "matches_current_known_bot"
                ],
                "all_author_states": json.dumps(
                    all_states,
                    ensure_ascii=False,
                ),
                "all_authorNames": json.dumps(
                    all_names,
                    ensure_ascii=False,
                ),
                "any_occurrence_matches_original_known_bot": (
                    any_original_known_bot
                ),
                "any_occurrence_matches_current_known_bot": (
                    any_current_known_bot
                ),
            }
        )

        print(
            f"   {comment_id}: "
            f"state={first['author_state']!r}, "
            f"authorName={first['authorName']!r}, "
            f"filter_value={first['filter_value']!r}, "
            "original_KNOWN_BOTS_match="
            f"{first['matches_original_known_bot']}, "
            "current_KNOWN_BOTS_match="
            f"{first['matches_current_known_bot']}, "
            f"raw_occurrences={len(hits)}"
        )

    audit = pd.DataFrame(
        audit_rows
    )

    # ------------------------------------------------------------------
    # Summary: authorName metadata state
    # ------------------------------------------------------------------

    print(
        "\n[summary: first occurrence authorName state]"
    )

    print(
        audit[
            "first_author_state"
        ]
        .value_counts(
            dropna=False
        )
        .to_string()
    )

    # ------------------------------------------------------------------
    # Summary: ORIGINAL eight-account filter
    # ------------------------------------------------------------------

    first_original_known = int(
        audit[
            "first_matches_original_known_bot"
        ]
        .fillna(False)
        .astype(bool)
        .sum()
    )

    any_original_known = int(
        audit[
            "any_occurrence_matches_original_known_bot"
        ]
        .fillna(False)
        .astype(bool)
        .sum()
    )

    print(
        "\n[summary: ORIGINAL eight-account "
        "KNOWN_BOTS matching]"
    )

    print(
        "   first occurrence matches original "
        f"KNOWN_BOTS: {first_original_known}/{len(audit)}"
    )

    print(
        "   any raw occurrence matches original "
        f"KNOWN_BOTS: {any_original_known}/{len(audit)}"
    )

    # ------------------------------------------------------------------
    # Summary: CURRENT expanded filter
    # ------------------------------------------------------------------

    first_current_known = int(
        audit[
            "first_matches_current_known_bot"
        ]
        .fillna(False)
        .astype(bool)
        .sum()
    )

    any_current_known = int(
        audit[
            "any_occurrence_matches_current_known_bot"
        ]
        .fillna(False)
        .astype(bool)
        .sum()
    )

    print(
        "\n[secondary comparison: CURRENT "
        "KNOWN_BOTS matching]"
    )

    print(
        "   first occurrence matches current "
        f"KNOWN_BOTS: {first_current_known}/{len(audit)}"
    )

    print(
        "   any raw occurrence matches current "
        f"KNOWN_BOTS: {any_current_known}/{len(audit)}"
    )

    # ------------------------------------------------------------------
    # Historical missing-author hypothesis
    # ------------------------------------------------------------------

    missing_or_null = int(
        audit[
            "first_author_state"
        ]
        .isin(
            [
                "missing",
                "null",
                "blank",
            ]
        )
        .sum()
    )

    print(
        "\n[hypothesis test]"
    )

    print(
        "   hypothesis: authorName was missing/null/blank "
        "on the first deduplicated occurrence"
    )

    print(
        f"   rows supporting hypothesis: "
        f"{missing_or_null}/{len(audit)}"
    )

    if missing_or_null == len(audit):
        print(
            "   result: SUPPORTED FOR ALL 17 ROWS"
        )

    elif missing_or_null > 0:
        print(
            "   result: PARTIALLY SUPPORTED"
        )

    else:
        print(
            "   result: REFUTED"
        )

    # ------------------------------------------------------------------
    # Cross-file metadata consistency under the ORIGINAL filter
    # ------------------------------------------------------------------

    inconsistent_original = audit[
        (
            audit["raw_occurrences"] > 1
        )
        & (
            audit[
                "first_matches_original_known_bot"
            ].fillna(False)
            !=
            audit[
                "any_occurrence_matches_original_known_bot"
            ].fillna(False)
        )
    ]

    print(
        "\n[cross-file metadata inconsistency: "
        "ORIGINAL KNOWN_BOTS]"
    )

    print(
        "   ids where first occurrence did not match the "
        "original KNOWN_BOTS set but a later occurrence did: "
        f"{len(inconsistent_original)}"
    )

    if len(inconsistent_original):
        for comment_id in inconsistent_original[
            "id"
        ]:
            print(
                f"   {comment_id}"
            )

    # ------------------------------------------------------------------
    # Write diagnostic audit
    # ------------------------------------------------------------------

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"\n[write] {OUTPUT_CSV}"
    )

    print(
        "[done] authorName diagnostic complete."
    )


if __name__ == "__main__":
    main()