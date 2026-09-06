"""
reconcile_bot_filters.py

Reconcile the author-based and content-based bot filters against the final v2.2
corpus before freezing it.

The two bot filters are complementary but neither is complete on its own.

The author-based filter removes comments from accounts explicitly listed in
KNOWN_BOTS. The content-based filter removes automated or moderator-
administrative text using textual patterns.

The v1 content-filter audit identified seven account names:

    amputatorbot
    otherampbot
    civilservantbot
    futurologybot
    code-sloth
    privacy-modteam
    cars-modteam

Five of those accounts are now deliberately included in KNOWN_BOTS.

Two are deliberately NOT included:

    futurologybot
        r/Futurology uses this account to relay a human-written submission
        statement. The wrapper is stripped downstream and the human-written
        body is retained.

    code-sloth
        The audit did not establish this account as an automated account, so
        it is not excluded merely because one of its comments matched a
        content-based pattern.

Those two accounts are therefore expected to appear in CHECK 1 if qualifying
comments survive the downstream preprocessing. Their presence is not treated
as bot residue.

The script performs three checks:

  CHECK 1
      Finds corpus rows authored by any of the seven content-discovered
      accounts. Rows from EXPECTED_UNLISTED are reported as expected.
      Any row from an account currently in KNOWN_BOTS is a failure because the
      author-stage filter should have removed it.

  CHECK 2
      Screens for account names that look automated but are on neither
      KNOWN_BOTS nor the content-discovered list. This is deliberately broad
      and is a review screen only. A bot-shaped name is not treated as proof
      that an account is automated.

  CHECK 3
      Reports the top 25 account names by surviving comment count. This checks
      for unusually high-volume accounts that may not advertise automation in
      either their name or their text.

Run after regenerating and membership-verifying v2.2, but before freezing the
corpus.

Usage:
    python reconcile_bot_filters.py

In:
    data/raw/*.json
    data/clean_v2_2/corpus.parquet
    02_preprocess.py

Out:
    data/clean_v2_2/bot_reconciliation.csv
    printed reconciliation report
"""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

RAW_DIR = Path("data/raw")
CORPUS_PATH = Path("data/clean_v2_2/corpus.parquet")
OUTPUT_CSV = Path("data/clean_v2_2/bot_reconciliation.csv")
PREPROCESS_PATH = Path("02_preprocess.py")


# ---------------------------------------------------------------------------
# Reconciliation configuration
# ---------------------------------------------------------------------------

# Accounts identified during the v1 content-filter audit.
DISCOVERED = {
    "amputatorbot",
    "otherampbot",
    "civilservantbot",
    "futurologybot",
    "code-sloth",
    "privacy-modteam",
    "cars-modteam",
}

# These two discovered accounts are deliberately not in KNOWN_BOTS.
#
# futurologybot relays human-written r/Futurology submission statements, which
# are handled downstream by wrapper stripping and relay-deduplication.
#
# code-sloth was not established as an automated account by the audit.
EXPECTED_UNLISTED = {
    "futurologybot",
    "code-sloth",
}

# Deliberately broad name-based screen. This is a diagnostic only, not a
# filtering rule.
#
# Non-capturing group avoids pandas' warning about regex match groups.
BOT_SHAPED = (
    r"(?:bot$|^auto|_bot|-bot|modteam$|^mod[_-]|bot[_-]|^u/bot)"
)

TOP_N = 25


# ---------------------------------------------------------------------------
# Raw author recovery
# ---------------------------------------------------------------------------

def load_raw_authors() -> pd.DataFrame:
    """
    Map comment id -> authorName from the first raw occurrence.

    The sorted file order and keep='first' behaviour match the deduplication
    convention used by 02_preprocess.py.
    """
    files = sorted(RAW_DIR.glob("*.json"))

    if not files:
        sys.exit(f"[FAIL] no raw JSON in {RAW_DIR}")

    rows: list[dict[str, str]] = []

    for path in files:
        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as exc:
            print(
                f"[WARN] skipping unreadable {path.name}: {exc}"
            )
            continue

        if not isinstance(data, list):
            continue

        for item in data:
            if (
                isinstance(item, dict)
                and item.get("dataType") == "comment"
            ):
                rows.append(
                    {
                        "id": str(item.get("id")),
                        "author": (
                            item.get("authorName") or ""
                        ).lower(),
                    }
                )

    raw = pd.DataFrame(rows)

    if raw.empty:
        sys.exit(
            "[FAIL] no comment records found in raw JSON"
        )

    raw = raw.drop_duplicates(
        subset="id",
        keep="first",
    )

    print(
        f"[load] {len(raw):,} unique comment ids "
        f"from {len(files)} raw file(s)"
    )

    return raw


# ---------------------------------------------------------------------------
# Main reconciliation
# ---------------------------------------------------------------------------

def main() -> None:
    # ------------------------------------------------------------------
    # Preconditions
    # ------------------------------------------------------------------

    if not CORPUS_PATH.exists():
        sys.exit(
            f"[FAIL] missing corpus: {CORPUS_PATH}"
        )

    if not PREPROCESS_PATH.exists():
        sys.exit(
            f"[FAIL] missing preprocessing script: "
            f"{PREPROCESS_PATH}"
        )

    config = runpy.run_path(
        str(PREPROCESS_PATH),
        run_name="reconcile_config",
    )

    if "KNOWN_BOTS" not in config:
        sys.exit(
            "[FAIL] 02_preprocess.py does not define KNOWN_BOTS"
        )

    known_bots = {
        str(account).lower()
        for account in config["KNOWN_BOTS"]
    }

    print(
        f"[config] KNOWN_BOTS currently holds "
        f"{len(known_bots)} accounts"
    )

    # The deliberately retained accounts must not accidentally be present
    # in KNOWN_BOTS.
    unexpected_overlap = (
        EXPECTED_UNLISTED & known_bots
    )

    if unexpected_overlap:
        print(
            "\n[FAIL] accounts deliberately expected to remain unlisted "
            "are currently present in KNOWN_BOTS:"
        )

        for account in sorted(unexpected_overlap):
            print(f"   {account}")

        sys.exit(1)

    # ------------------------------------------------------------------
    # Load corpus and recover raw authors
    # ------------------------------------------------------------------

    corpus = pd.read_parquet(
        CORPUS_PATH
    )

    raw = load_raw_authors()

    required_columns = {
        "id",
        "subreddit",
        "year",
        "clean_wordcount",
    }

    missing_columns = (
        required_columns
        - set(corpus.columns)
    )

    if missing_columns:
        sys.exit(
            "[FAIL] corpus missing required column(s): "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    joined = corpus[
        [
            "id",
            "subreddit",
            "year",
            "clean_wordcount",
        ]
    ].merge(
        raw,
        on="id",
        how="left",
    )

    missing_raw = int(
        joined["author"]
        .isna()
        .sum()
    )

    if missing_raw:
        sys.exit(
            f"[FAIL] {missing_raw} corpus rows had no raw "
            "author match -- reconciliation is incomplete"
        )

    joined["author"] = (
        joined["author"]
        .fillna("")
        .astype(str)
        .str.lower()
    )

    print(
        f"[join] {len(joined):,} corpus rows matched "
        f"to an author\n"
    )

    # ==================================================================
    # CHECK 1
    # ==================================================================

    hit_discovered = joined[
        joined["author"].isin(
            DISCOVERED
        )
    ].copy()

    expected_unlisted_rows = hit_discovered[
        hit_discovered["author"].isin(
            EXPECTED_UNLISTED
        )
    ].copy()

    known_bot_residue = hit_discovered[
        hit_discovered["author"].isin(
            known_bots
        )
    ].copy()

    unexpected_discovered = hit_discovered[
        ~hit_discovered["author"].isin(
            EXPECTED_UNLISTED | known_bots
        )
    ].copy()

    print("=" * 70)

    print(
        "CHECK 1 -- rows in the corpus posted by "
        "content-discovered accounts"
    )

    print("=" * 70)

    if hit_discovered.empty:
        print(
            "  none of the seven content-discovered accounts "
            "appear in the final corpus."
        )
    else:
        print(
            hit_discovered["author"]
            .value_counts()
            .to_string()
        )

    print(
        "\n  Deliberately unlisted accounts "
        "(expected if present):"
    )

    if expected_unlisted_rows.empty:
        print(
            "  <none present>"
        )
    else:
        print(
            expected_unlisted_rows["author"]
            .value_counts()
            .to_string()
        )

    print(
        "\n  Rows from accounts currently in KNOWN_BOTS:"
    )

    if known_bot_residue.empty:
        print(
            "  none. PASS"
        )
    else:
        print(
            known_bot_residue["author"]
            .value_counts()
            .to_string()
        )

        print(
            "\n  FAIL: these rows should have been removed "
            "by the author-based filter."
        )

    if not unexpected_discovered.empty:
        print(
            "\n  Unexpected content-discovered accounts "
            "that are neither KNOWN_BOTS nor "
            "EXPECTED_UNLISTED:"
        )

        print(
            unexpected_discovered["author"]
            .value_counts()
            .to_string()
        )

    check1_ok = (
        known_bot_residue.empty
        and unexpected_discovered.empty
    )

    print(
        f"\n  CHECK 1 result: "
        f"{'PASS' if check1_ok else 'FAIL'}"
    )

    print()

    # ==================================================================
    # CHECK 2
    # ==================================================================

    shaped = joined[
        joined["author"].str.contains(
            BOT_SHAPED,
            regex=True,
            na=False,
        )
    ].copy()

    new_shaped = shaped[
        ~shaped["author"].isin(
            DISCOVERED | known_bots
        )
    ].copy()

    print("=" * 70)

    print(
        "CHECK 2 -- rows posted by bot-shaped account names"
    )

    print("=" * 70)

    print(
        f"  matching any bot-shaped name: "
        f"{len(shaped)} rows, "
        f"{shaped['author'].nunique()} accounts"
    )

    if new_shaped.empty:
        print(
            "  none that are outside KNOWN_BOTS and "
            "the content-discovered list."
        )
    else:
        print(
            "\n  NOT on KNOWN_BOTS and NOT on the "
            "content-discovered list:"
        )

        print(
            new_shaped["author"]
            .value_counts()
            .to_string()
        )

        print(
            "\n  Review only. A bot-shaped account name is "
            "a hint, not evidence that the account is automated."
        )

    print()

    # ==================================================================
    # CHECK 3
    # ==================================================================

    print("=" * 70)

    print(
        f"CHECK 3 -- top {TOP_N} accounts by comment count"
    )

    print("=" * 70)

    print(
        "  A bot need not advertise itself in its name or "
        "its text. An account"
    )

    print(
        "  with an implausible share of the corpus is worth "
        "reading.\n"
    )

    top = (
        joined[
            joined["author"] != ""
        ]["author"]
        .value_counts()
        .head(TOP_N)
    )

    for name, n in top.items():
        flag = ""

        if name in known_bots:
            flag = "  [KNOWN_BOTS]"

        elif name in EXPECTED_UNLISTED:
            flag = "  [expected-unlisted]"

        elif name in DISCOVERED:
            flag = "  [content-discovered]"

        print(
            f"   {name:<28} "
            f"{int(n):>5}  "
            f"({100 * int(n) / len(joined):.2f}%)"
            f"{flag}"
        )

    print()

    # ==================================================================
    # Verdict
    # ==================================================================

    print("=" * 70)

    if check1_ok:
        print(
            "VERDICT: no further residue found on either axis."
        )

        if not new_shaped.empty:
            print(
                "CHECK 2 returned name-based review candidates, "
                "but name shape alone is not treated as confirmed "
                "bot residue."
            )

        print(
            "The deliberately retained Futurology relay account "
            "and code-sloth are not counted as failures."
        )

    else:
        print(
            "VERDICT: unexpected residue found in CHECK 1."
        )

        print(
            "Do not freeze the corpus until the author-filter "
            "mismatch is investigated."
        )

    print("=" * 70)

    # ==================================================================
    # Audit output
    # ==================================================================

    output_frames: list[pd.DataFrame] = []

    if not expected_unlisted_rows.empty:
        output_frames.append(
            expected_unlisted_rows.assign(
                check=(
                    "content_discovered_expected_unlisted"
                )
            )
        )

    if not known_bot_residue.empty:
        output_frames.append(
            known_bot_residue.assign(
                check="known_bot_residue"
            )
        )

    if not unexpected_discovered.empty:
        output_frames.append(
            unexpected_discovered.assign(
                check="unexpected_discovered_account"
            )
        )

    if not new_shaped.empty:
        output_frames.append(
            new_shaped.assign(
                check="bot_shaped_name_unlisted"
            )
        )

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if output_frames:
        audit = pd.concat(
            output_frames,
            ignore_index=True,
        )
    else:
        audit = pd.DataFrame(
            columns=[
                "id",
                "subreddit",
                "year",
                "clean_wordcount",
                "author",
                "check",
            ]
        )

    audit.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"\n[write] {OUTPUT_CSV}"
    )

    if not check1_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()