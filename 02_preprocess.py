"""
02_preprocess.py -- build the cleaned, de-identified v2.2 corpus for the CAV-concern study.

Reads every raw scrape file in data/raw/ (produced by 01_scrape.py), cleans and
filters the comments, and writes the regenerated v2.2 analysis-ready corpus to
data/clean_v2_2/. The existing data/clean/ v1 outputs are left untouched.

The established preprocessing order is retained, with four additional
content-based and de-identification stages inserted after clean_body is created:

  1. CONTENT BOT FILTER. remove_bot_content() removes automated boilerplate and
     moderator-administrative text that survives the earlier authorName-based
     KNOWN_BOTS filter.

  2. SUBMISSION-WRAPPER STRIPPING. strip_submission_wrapper() removes generated
     AutoModerator submission-statement headers and footers, fixed poster
     templates, separator rules and statement labels while retaining the
     human-written statement. It also records body_stripped and wrapper_source
     as an audit trail.

  3. RELAY-DUPLICATE RESOLUTION. resolve_relay_duplicates() removes duplicate
     AutoModerator relay copies where the same stripped statement also occurs
     within the same thread.

  4. USERNAME MASKING. mask_usernames() replaces in-text Reddit username
     mentions such as /u/name or u/name with /u/[user]. This preserves the
     discourse fact that a user was addressed while removing the identifier.
     The replacement does not change token count and therefore cannot move a
     comment across the word floor.

All four stages require clean_body and therefore run after it exists. Wrapper
stripping must occur before the word floor because stripping shortens text, so
the >=20-word rule must be evaluated on the stripped text. Relay-duplicate
resolution must occur after wrapper stripping because the duplicate text is
concealed by the wrapper and the resolver depends on wrapper_source. Username
masking occurs after relay resolution so it cannot interfere with duplicate
identification.

The author-based bot filter remains earlier in the pipeline and uses authorName
against KNOWN_BOTS. The original eight-account list was found to be incomplete:
a raw-data audit of the 17 automated or moderator-administrative rows identified
post hoc found that all 17 had populated authorName values, but none matched the
original list. KNOWN_BOTS therefore includes five of the seven accounts that audit
identified, while the content-based filter remains as an independent backstop.
Two accounts are deliberately excluded; the reasoning is recorded beside the set,
and the corpus changes if either is added.

The pre-existing pipeline behaviour otherwise remains unchanged:

  - CROSS-FILE DEDUPLICATION by comment id.
  - BODY-DELETED comments ([deleted], [removed], or empty body) are removed.
    Author-deleted-but-text-intact comments are retained anonymously.
  - AUTHOR-BASED BOT FILTERING uses authorName and KNOWN_BOTS.
  - TIMESTAMP PARSING removes unparseable comment timestamps.
  - STUDY-WINDOW FILTER keeps 2016-01-01 through 2025-04-30 inclusive.
  - WORD FLOOR keeps comments with at least 20 cleaned words.
  - ENGLISH-LANGUAGE FILTER runs only after the word floor.
  - SUBREDDIT TIER and calendar year are added for downstream sampling.

De-identification is enforced at write time. Raw body is not written to the
analysis corpus because it can retain usernames and generated relay text that
clean_body has removed. The output guard checks both column names and clean_body
text for residual identifiers, AutoModerator relay headers and unmasked Reddit
username mentions.

For auditability, every row modified by submission-wrapper stripping is captured
at the stripping stage before relay resolution, the word floor or language
filter can remove it. These pre-strip originals are written separately to
data/clean_v2_2/stripped_originals.csv. That file retains identifying text for
audit purposes and must remain gitignored.

Run:  (.venv active)  python 02_preprocess.py
In:   data/raw/*.json
Out:  data/clean_v2_2/corpus.parquet
      data/clean_v2_2/corpus.csv
      data/clean_v2_2/preprocess_funnel.csv
      data/clean_v2_2/stripped_originals.csv
"""

from __future__ import annotations

import html
import json
import re
import sys
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from preprocess_content_filters import (
    RELAY_HEADER,
    USERNAME_MENTION,
    mask_usernames,
    remove_bot_content,
    resolve_relay_duplicates,
    strip_submission_wrapper,
)


# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean_v2_2")
CORPUS_PARQUET = CLEAN_DIR / "corpus.parquet"
CORPUS_CSV = CLEAN_DIR / "corpus.csv"
FUNNEL_CSV = CLEAN_DIR / "preprocess_funnel.csv"
STRIPPED_AUDIT_CSV = (
    CLEAN_DIR / "stripped_originals.csv"
)  # gitignored: retains pre-strip text

WORD_FLOOR = 20  # keep comments with >= this many CLEANED words

APPLY_STUDY_WINDOW = True  # set False to smoke-test on out-of-window caches
STUDY_START = "2016-01-01"  # inclusive
STUDY_END_EXCL = "2025-05-01"  # exclusive -> includes all of 2025-04-30


# subreddit -> tier (proposal's three-tier frame). Keys are lower-case, no "r/".
TIER_MAP = {
    # Tier 1 -- CAV-focused
    "selfdrivingcars": "Tier 1",
    "teslamotors": "Tier 1",
    "realtesla": "Tier 1",
    "waymo": "Tier 1",

    # Tier 2 -- technology-adjacent
    "electricvehicles": "Tier 2",
    "cars": "Tier 2",
    "technology": "Tier 2",
    "futurology": "Tier 2",

    # Tier 3 -- issue-public
    "privacy": "Tier 3",
    "cybersecurity": "Tier 3",
}


# Non-human accounts to drop (conservative: only known utility accounts, matched
# on authorName -- NEVER on authorId, which on comments is the comment's own id).
#
# The original eight-account list left a measured residue of automated content in
# corpus v1. A raw-data audit of those rows found every authorName populated but
# none on the list, so the cause was incomplete coverage rather than missing
# metadata. Five of the seven accounts identified by that audit are added below;
# the other two are deliberately excluded for the reasons recorded immediately
# after the set. The content filter in preprocess_content_filters.py remains the
# backstop, because no account list can be assumed complete.
KNOWN_BOTS = {
    # original list
    "automoderator",
    "autotldr",
    "sneakpeekbot",
    "remindmebot",
    "b0trank",
    "wikitextbot",
    "gifv-bot",
    "totesmessenger",

    # identified by the v1 content-filter audit (diagnose_bot_authors.py)
    "amputatorbot",
    "otherampbot",
    "civilservantbot",

    # subreddit moderator team accounts
    "privacy-modteam",
    "cars-modteam",
    "electricvehicles-modteam",
}


# DELIBERATELY EXCLUDED FROM KNOWN_BOTS. Both were named by the v1 content-filter
# audit. Do not add either without re-reading this note: adding either silently
# changes the corpus.
#
#   futurologybot
#       Posts the r/Futurology submission-statement relay. The COMMENT is authored
#       by the bot, but its BODY is written verbatim by the poster. Removing it at
#       the author stage discards 28 human-written submission statements that exist
#       nowhere else in the corpus. The relay is handled downstream instead:
#       strip_submission_wrapper() removes the generated header and footer and
#       retains the body, and resolve_relay_duplicates() drops the relayed copy
#       where the poster also posted the statement directly.
#
#       This is the ONE exception to the authorship rule applied everywhere else in
#       the pipeline. The rule is: authorship of the COMMENT decides removal, except
#       where an automated account carries a human's text verbatim, in which case the
#       wrapper is stripped and the text retained.
#
#       Relayed and directly posted statements were checked to coexist across
#       2021-2025 with no year in which only one form occurs, so retaining the
#       relays introduces no temporal selection effect.
#
#   code-sloth
#       Removes no rows from the corpus and has a human-shaped account name. Not
#       added, so that a real user's entire contribution is not deleted on the
#       strength of a single pattern match.

DELETED = {"[deleted]", "[removed]", ""}


# ---------------------------------------------------------------------------
# text cleaning (unchanged from the skeleton; already tested)
# ---------------------------------------------------------------------------

URL_RE = re.compile(r"https?://\S+")
BLOCKQUOTE_RE = re.compile(
    r"^\s*>.*$",
    re.MULTILINE,
)  # reddit markdown quote lines
MD_ESCAPE_RE = re.compile(
    r"\\([\\`*_{}\[\]()#+\-.!>])"
)  # \[ -> [ etc.
WS_RE = re.compile(r"\s+")


def clean_body(text: str) -> str:
    """
    Strip quoted parent text, URLs and markdown; unescape HTML entities;
    collapse whitespace. Emoji are kept (the tokenizer handles them).
    """
    if not text:
        return ""

    # remove quoted parent text BEFORE analysis
    text = BLOCKQUOTE_RE.sub(" ", text)
    text = URL_RE.sub(" ", text)
    text = html.unescape(text)
    text = MD_ESCAPE_RE.sub(r"\1", text)
    text = text.replace("*", "").replace("#", "")
    text = WS_RE.sub(" ", text).strip()

    return text


def assign_tier(subreddit: str) -> str:
    return TIER_MAP.get(
        (subreddit or "").lower(),
        "untiered",
    )


# ---------------------------------------------------------------------------
# load every raw file
# ---------------------------------------------------------------------------

def load_raw(
    raw_dir: Path = RAW_DIR,
) -> list[dict]:
    files = sorted(raw_dir.glob("*.json"))

    if not files:
        sys.exit(
            f"[load] no *.json files in {raw_dir} -- "
            "run 01_scrape.py first."
        )

    items: list[dict] = []

    for f in files:
        try:
            data = json.loads(
                f.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as e:
            print(
                f"[load] skipping unreadable {f.name}: {e}"
            )
            continue

        if isinstance(data, list):
            items.extend(data)
            print(
                f"[load] {f.name}: {len(data)} items"
            )
        else:
            print(
                f"[load] skipping {f.name}: "
                "expected a JSON list"
            )

    print(
        f"[load] total raw items: "
        f"{len(items)} from {len(files)} file(s)"
    )

    return items


# ---------------------------------------------------------------------------
# preprocess -> (dataframe, funnel, stripped audit)
# ---------------------------------------------------------------------------

def preprocess(
    items: list[dict],
):
    funnel = [
        ("raw items", len(items))
    ]

    stripped_audit = pd.DataFrame()

    rows = [
        it
        for it in items
        if it.get("dataType") == "comment"
    ]

    funnel.append(
        ("comments", len(rows))
    )

    df = pd.DataFrame(rows)

    if df.empty:
        return (
            df,
            funnel,
            stripped_audit,
        )

    # Cross-file deduplication by comment id. The same comment can appear
    # under several search combinations.
    df = df.drop_duplicates(
        subset="id",
        keep="first",
    )

    funnel.append(
        ("after dedup", len(df))
    )

    # Deletion: drop body-deleted only; keep author-deleted-with-text
    # comments as anonymous.
    df = df[
        ~df["body"]
        .fillna("")
        .str.strip()
        .isin(DELETED)
    ]

    funnel.append(
        ("after body-deleted removed", len(df))
    )

    # Bots: match on authorName, never authorId.
    df = df[
        ~df["authorName"]
        .fillna("")
        .str.lower()
        .isin(KNOWN_BOTS)
    ]

    funnel.append(
        ("after bot filter", len(df))
    )

    # Timestamp -> tz-aware UTC; drop anything unparseable.
    df["created"] = pd.to_datetime(
        df["commentCreatedAt"],
        utc=True,
        errors="coerce",
    )

    df = df.dropna(
        subset=["created"]
    )

    funnel.append(
        ("after timestamp parse", len(df))
    )

    # Study window. Diagnostics and out-of-window scrapes are excluded.
    if APPLY_STUDY_WINDOW:
        start = pd.Timestamp(
            STUDY_START,
            tz="UTC",
        )

        end = pd.Timestamp(
            STUDY_END_EXCL,
            tz="UTC",
        )

        df = df[
            (df["created"] >= start)
            & (df["created"] < end)
        ]

        funnel.append(
            (
                f"after study window "
                f"{STUDY_START}..{STUDY_END_EXCL}",
                len(df),
            )
        )

    # ------------------------------------------------------------------
    # Clean text
    # ------------------------------------------------------------------

    df["clean_body"] = df["body"].map(
        clean_body
    )

    # ------------------------------------------------------------------
    # Content bot / moderator text filter
    # ------------------------------------------------------------------

    df, removed_bots = remove_bot_content(
        df
    )

    funnel.append(
        (
            f"after content bot filter "
            f"({len(removed_bots)} removed)",
            len(df),
        )
    )

    # ------------------------------------------------------------------
    # Submission-wrapper stripping
    # ------------------------------------------------------------------

    pre_strip_wordcount = (
        df["clean_body"]
        .str.split()
        .map(len)
    )

    pre_strip_clean_body = (
        df["clean_body"].copy()
    )

    df = strip_submission_wrapper(
        df
    )

    stripped_mask = (
        df["body_stripped"]
        .fillna(False)
    )

    # Capture every modified row at the stripping stage itself, before
    # relay resolution, the word floor or language filtering can remove it.
    stripped_audit = df.loc[
        stripped_mask,
        [
            "id",
            "subredditName",
            "created",
            "wrapper_source",
            "body",
            "clean_body",
        ],
    ].copy()

    stripped_audit["year"] = (
        stripped_audit["created"]
        .dt.year
    )

    stripped_audit[
        "pre_strip_clean_body"
    ] = pre_strip_clean_body.loc[
        stripped_audit.index
    ]

    stripped_audit = (
        stripped_audit.rename(
            columns={
                "subredditName": "subreddit",
                "clean_body": "post_strip_clean_body",
            }
        )
    )

    stripped_audit = stripped_audit[
        [
            "id",
            "subreddit",
            "year",
            "wrapper_source",
            "body",
            "pre_strip_clean_body",
            "post_strip_clean_body",
        ]
    ]

    post_strip_wordcount = (
        df["clean_body"]
        .str.split()
        .map(len)
    )

    strip_floor_failures = int(
        (
            df["body_stripped"]
            & (
                pre_strip_wordcount
                >= WORD_FLOOR
            )
            & (
                post_strip_wordcount
                < WORD_FLOOR
            )
        ).sum()
    )

    stripped_count = int(
        df["body_stripped"].sum()
    )

    funnel.append(
        (
            f"after submission wrapper strip "
            f"({stripped_count} stripped; "
            f"{strip_floor_failures} fall below word floor)",
            len(df),
        )
    )

    # ------------------------------------------------------------------
    # Relay duplicate resolution
    # ------------------------------------------------------------------

    df, removed_relays = (
        resolve_relay_duplicates(df)
    )

    funnel.append(
        (
            f"after relay duplicate resolution "
            f"({len(removed_relays)} removed)",
            len(df),
        )
    )

    # ------------------------------------------------------------------
    # Username masking
    # ------------------------------------------------------------------

    # De-identification: mask in-text /u/username mentions. Token count is
    # unchanged, so no comment can cross the word floor as a result.
    df, n_masked = mask_usernames(
        df
    )

    funnel.append(
        (
            f"after username masking "
            f"({n_masked} rows masked)",
            len(df),
        )
    )

    # ------------------------------------------------------------------
    # Word floor
    # ------------------------------------------------------------------

    # Word floor FIRST, on cleaned text.
    df["clean_wordcount"] = (
        df["clean_body"]
        .str.split()
        .map(len)
    )

    df = df[
        df["clean_wordcount"]
        >= WORD_FLOOR
    ]

    funnel.append(
        (
            f"after >= {WORD_FLOOR}-word floor",
            len(df),
        )
    )

    # ------------------------------------------------------------------
    # English-language filter
    # ------------------------------------------------------------------

    # Language SECOND, only on comments that already cleared the floor.
    from langdetect import (
        DetectorFactory,
        LangDetectException,
        detect,
    )

    DetectorFactory.seed = 0

    def is_en(
        t: str,
    ) -> bool:
        try:
            return detect(t) == "en"
        except LangDetectException:
            return False

    df = df[
        df["clean_body"].map(is_en)
    ]

    funnel.append(
        ("after English filter", len(df))
    )

    # Any stage above can legitimately empty the frame, for example an
    # out-of-window diagnostic scrape. Return early with the funnel intact
    # so main() can print the stage counts and exit cleanly.
    if df.empty:
        return (
            df,
            funnel,
            stripped_audit,
        )

    # ------------------------------------------------------------------
    # Metadata for downstream stages
    # ------------------------------------------------------------------

    df["subreddit"] = (
        df["subredditName"]
    )

    df["tier"] = (
        df["subreddit"]
        .map(assign_tier)
    )

    df["year"] = (
        df["created"]
        .dt.year
    )

    return (
        df.reset_index(drop=True),
        funnel,
        stripped_audit,
    )


# ---------------------------------------------------------------------------
# write de-identified corpus + funnel
# ---------------------------------------------------------------------------

# The raw `body` column is NOT written to the corpus. For rows carrying the
# AutoModerator submission-statement wrapper, `body` retains the generated
# header, which names the poster and would reintroduce exactly the identifier
# that strip_submission_wrapper() removed from clean_body. Nothing downstream
# reads `body`, so it is dropped rather than cleaned.
#
# The pre-strip originals are written separately to STRIPPED_AUDIT_CSV,
# which is gitignored.

CORPUS_COLS = [
    "id",
    "created",
    "year",
    "subreddit",
    "tier",
    "score",
    "depth",
    "parentKind",
    "parsedPostId",
    "clean_wordcount",
    "clean_body",
    "body_stripped",
    "wrapper_source",
]


def write_outputs(
    df: pd.DataFrame,
    funnel,
    stripped_audit: pd.DataFrame,
) -> None:
    CLEAN_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame(
        funnel,
        columns=[
            "stage",
            "items",
        ],
    ).to_csv(
        FUNNEL_CSV,
        index=False,
    )

    # Keep only columns that exist, robust if a field is absent in some scrape.
    cols = [
        c
        for c in CORPUS_COLS
        if c in df.columns
    ]

    out = df[cols].copy()

    # ------------------------------------------------------------------
    # De-identification guard
    # ------------------------------------------------------------------

    # No usernames leave this stage. The checks cover both column names and
    # clean_body text. The column check alone is insufficient because an
    # AutoModerator relay header can name the poster inside the comment text.
    for banned in (
        "authorName",
        "authorId",
        "authorFullname",
        "parsedAuthorId",
        "body",
    ):
        assert (
            banned not in out.columns
        ), f"{banned} would leak into the corpus"

    leak_header = int(
        out["clean_body"]
        .str.contains(
            RELAY_HEADER,
            na=False,
        )
        .sum()
    )

    assert (
        leak_header == 0
    ), (
        f"{leak_header} rows retain "
        "an AutoModerator relay header"
    )

    # USERNAME_MENTION does not match the /u/[user] placeholder, so any match
    # remaining here is necessarily an unmasked Reddit username. Checking the
    # pattern directly also catches a row that contains both a placeholder and
    # some other unmasked username.
    unmasked = (
        out["clean_body"]
        .str.contains(
            USERNAME_MENTION,
            na=False,
        )
    )

    assert (
        int(unmasked.sum()) == 0
    ), (
        f"{int(unmasked.sum())} rows retain "
        "an unmasked username"
    )

    print(
        "[guard] no author columns, "
        "no relay headers, "
        "no unmasked usernames"
    )

    # ------------------------------------------------------------------
    # Audit output
    # ------------------------------------------------------------------

    if not stripped_audit.empty:
        stripped_audit.to_csv(
            STRIPPED_AUDIT_CSV,
            index=False,
            encoding="utf-8-sig",
        )

        print(
            f"[write] {STRIPPED_AUDIT_CSV} "
            f"({len(stripped_audit)} pre-strip originals; "
            "gitignore this)"
        )

    # ------------------------------------------------------------------
    # Analysis corpus
    # ------------------------------------------------------------------

    out.to_parquet(
        CORPUS_PARQUET,
        index=False,
    )

    out.to_csv(
        CORPUS_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"[write] corpus rows: {len(out)}"
    )

    print(
        f"[write] {CORPUS_PARQUET}"
    )

    print(
        f"[write] {CORPUS_CSV}"
    )

    print(
        f"[write] {FUNNEL_CSV}"
    )


def main() -> None:
    print("[versions]")

    print(
        f"   pandas:     "
        f"{version('pandas')}"
    )

    print(
        f"   pyarrow:    "
        f"{version('pyarrow')}"
    )

    print(
        f"   langdetect: "
        f"{version('langdetect')}"
    )

    items = load_raw()

    (
        df,
        funnel,
        stripped_audit,
    ) = preprocess(items)

    print("\n[funnel]")

    for stage, n in funnel:
        print(
            f"   {stage:<40} {n}"
        )

    if df.empty:
        sys.exit(
            "\n[stop] no comments survived preprocessing. "
            "If you ran this on a diagnostic scrape dated "
            "outside 2016..2025, that is expected -- set "
            "APPLY_STUDY_WINDOW = False to smoke-test the "
            "other stages."
        )

    write_outputs(
        df,
        funnel,
        stripped_audit,
    )

    # Brief composition summary, useful going into annotation sampling.
    print(
        "\n[summary] comments per tier:"
    )

    print(
        df["tier"]
        .value_counts()
        .to_string()
    )

    print(
        "\n[summary] comments per year:"
    )

    print(
        df["year"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print(
        "\n[done] preprocessing complete."
    )


if __name__ == "__main__":
    main()