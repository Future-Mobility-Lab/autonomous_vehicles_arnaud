"""
02_preprocess.py -- build the cleaned, de-identified corpus for the CAV-concern study.

Reads every raw scrape file in data/raw/ (produced by 01_scrape.py), cleans and
filters the comments, and writes a single analysis-ready corpus to data/clean/.
This is the proven skeleton logic promoted to a real corpus stage, with four
deliberate changes over the skeleton:

  1. FLOOR BEFORE LANGUAGE. langdetect is unreliable on short text (it flagged
     "Yeah" as Turkish in the skeleton run). We now apply the 20-word floor FIRST
     and run langdetect only on comments that already clear it, where it is
     reliable. Same output on the skeleton data, safer on the real corpus.
  2. STUDY-WINDOW FILTER. Only comments dated 2016-01-01 .. 2025-04-30 are kept,
     so diagnostic/out-of-window scrapes are excluded from the final corpus
     (matches the proposal). Toggle with APPLY_STUDY_WINDOW for smoke tests.
  3. CROSS-FILE DEDUP. The real collection scrapes overlapping searches, so the
     same comment id can appear in several files; we dedup by comment id.
  4. DE-IDENTIFIED OUTPUT + TIER LABELS. Usernames are dropped from the corpus;
     each row is tagged with its subreddit tier and year for later stratified
     sampling. Corpus lives under data/ (git-ignored), never in the repo.

Deletion handling (unchanged, and important): body-deleted comments ([deleted]/
[removed] in `body`) are dropped; author-deleted-but-text-intact comments are
KEPT as anonymous, because their text is valid and dropping them worsens
early-period sparsity.

Run:  (.venv active)  python 02_preprocess.py
In:   data/raw/*.json
Out:  data/clean/corpus.parquet, data/clean/corpus.csv, data/clean/preprocess_funnel.csv
"""

from __future__ import annotations
import re
import sys
import json
import html
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/clean")
CORPUS_PARQUET = CLEAN_DIR / "corpus.parquet"
CORPUS_CSV = CLEAN_DIR / "corpus.csv"
FUNNEL_CSV = CLEAN_DIR / "preprocess_funnel.csv"

WORD_FLOOR = 20                      # keep comments with >= this many CLEANED words

APPLY_STUDY_WINDOW = True            # set False to smoke-test on out-of-window caches
STUDY_START = "2016-01-01"           # inclusive
STUDY_END_EXCL = "2025-05-01"        # exclusive -> includes all of 2025-04-30

# subreddit -> tier (proposal's three-tier frame). Keys are lower-case, no "r/".
TIER_MAP = {
    # Tier 1 -- CAV-focused
    "selfdrivingcars": "Tier 1", "teslamotors": "Tier 1",
    "realtesla": "Tier 1", "waymo": "Tier 1",
    # Tier 2 -- technology-adjacent
    "electricvehicles": "Tier 2", "cars": "Tier 2",
    "technology": "Tier 2", "futurology": "Tier 2",
    # Tier 3 -- issue-public
    "privacy": "Tier 3", "cybersecurity": "Tier 3",
}

# Non-human accounts to drop (conservative: only known utility accounts, matched
# on authorName -- NEVER on authorId, which on comments is the comment's own id).
KNOWN_BOTS = {"automoderator", "autotldr", "sneakpeekbot", "remindmebot",
              "b0trank", "wikitextbot", "gifv-bot", "totesmessenger"}

DELETED = {"[deleted]", "[removed]", ""}


# ---------------------------------------------------------------------------
# text cleaning (unchanged from the skeleton; already tested)
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://\S+")
BLOCKQUOTE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)       # reddit markdown quote lines
MD_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!>])")    # \[ -> [  etc.
WS_RE = re.compile(r"\s+")


def clean_body(text: str) -> str:
    """Strip quoted parent text, URLs and markdown; unescape HTML entities;
    collapse whitespace. Emoji are kept (the tokenizer handles them)."""
    if not text:
        return ""
    text = BLOCKQUOTE_RE.sub(" ", text)   # remove quoted parent text BEFORE analysis
    text = URL_RE.sub(" ", text)
    text = html.unescape(text)
    text = MD_ESCAPE_RE.sub(r"\1", text)
    text = text.replace("*", "").replace("#", "")
    text = WS_RE.sub(" ", text).strip()
    return text


def assign_tier(subreddit: str) -> str:
    return TIER_MAP.get((subreddit or "").lower(), "untiered")


# ---------------------------------------------------------------------------
# load every raw file
# ---------------------------------------------------------------------------
def load_raw(raw_dir: Path = RAW_DIR) -> list[dict]:
    files = sorted(raw_dir.glob("*.json"))
    if not files:
        sys.exit(f"[load] no *.json files in {raw_dir} -- run 01_scrape.py first.")
    items: list[dict] = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"[load] skipping unreadable {f.name}: {e}")
            continue
        if isinstance(data, list):
            items.extend(data)
            print(f"[load] {f.name}: {len(data)} items")
        else:
            print(f"[load] skipping {f.name}: expected a JSON list")
    print(f"[load] total raw items: {len(items)} from {len(files)} file(s)")
    return items


# ---------------------------------------------------------------------------
# preprocess -> (dataframe, funnel)
# ---------------------------------------------------------------------------
def preprocess(items: list[dict]):
    funnel = [("raw items", len(items))]

    rows = [it for it in items if it.get("dataType") == "comment"]
    funnel.append(("comments", len(rows)))

    df = pd.DataFrame(rows)
    if df.empty:
        return df, funnel

    # cross-file dedup by comment id (same comment can appear under several searches)
    df = df.drop_duplicates(subset="id", keep="first")
    funnel.append(("after dedup", len(df)))

    # deletion: drop body-deleted only; keep author-deleted-with-text as anonymous
    df = df[~df["body"].fillna("").str.strip().isin(DELETED)]
    funnel.append(("after body-deleted removed", len(df)))

    # bots: match on authorName (never authorId)
    df = df[~df["authorName"].fillna("").str.lower().isin(KNOWN_BOTS)]
    funnel.append(("after bot filter", len(df)))

    # timestamp -> tz-aware UTC; drop anything unparseable
    df["created"] = pd.to_datetime(df["commentCreatedAt"], utc=True, errors="coerce")
    df = df.dropna(subset=["created"])
    funnel.append(("after timestamp parse", len(df)))

    # study window (diagnostics / out-of-window scrapes excluded)
    if APPLY_STUDY_WINDOW:
        start = pd.Timestamp(STUDY_START, tz="UTC")
        end = pd.Timestamp(STUDY_END_EXCL, tz="UTC")
        df = df[(df["created"] >= start) & (df["created"] < end)]
        funnel.append((f"after study window {STUDY_START}..{STUDY_END_EXCL}", len(df)))

    # clean text
    df["clean_body"] = df["body"].map(clean_body)

    # (1) word floor FIRST, on cleaned text
    df["clean_wordcount"] = df["clean_body"].str.split().map(len)
    df = df[df["clean_wordcount"] >= WORD_FLOOR]
    funnel.append((f"after >= {WORD_FLOOR}-word floor", len(df)))

    # (2) language SECOND, only on comments that already cleared the floor
    from langdetect import detect, DetectorFactory, LangDetectException
    DetectorFactory.seed = 0

    def is_en(t: str) -> bool:
        try:
            return detect(t) == "en"
        except LangDetectException:
            return False

    df = df[df["clean_body"].map(is_en)]
    funnel.append(("after English filter", len(df)))

    # Any stage above can legitimately empty the frame (e.g. an out-of-window
    # diagnostic scrape). An empty DataFrame has no columns, so the metadata
    # assignment below would raise KeyError. Return early with the funnel intact
    # so main() can print the stage counts and exit cleanly.
    if df.empty:
        return df, funnel

    # metadata for downstream stages
    df["subreddit"] = df["subredditName"]
    df["tier"] = df["subreddit"].map(assign_tier)
    df["year"] = df["created"].dt.year

    return df.reset_index(drop=True), funnel


# ---------------------------------------------------------------------------
# write de-identified corpus + funnel
# ---------------------------------------------------------------------------
CORPUS_COLS = ["id", "created", "year", "subreddit", "tier", "score",
               "depth", "parentKind", "parsedPostId",
               "clean_wordcount", "body", "clean_body"]


def write_outputs(df: pd.DataFrame, funnel) -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(funnel, columns=["stage", "items"]).to_csv(FUNNEL_CSV, index=False)

    # keep only columns that exist (robust if a field is absent in some scrape)
    cols = [c for c in CORPUS_COLS if c in df.columns]
    out = df[cols].copy()

    # NO usernames leave this stage. Guard against accidental leakage.
    for banned in ("authorName", "authorId", "authorFullname", "parsedAuthorId"):
        assert banned not in out.columns, f"{banned} would leak into the corpus"

    out.to_parquet(CORPUS_PARQUET, index=False)
    out.to_csv(CORPUS_CSV, index=False, encoding="utf-8-sig")
    print(f"[write] corpus rows: {len(out)}")
    print(f"[write] {CORPUS_PARQUET}")
    print(f"[write] {CORPUS_CSV}")
    print(f"[write] {FUNNEL_CSV}")


def main() -> None:
    items = load_raw()
    df, funnel = preprocess(items)

    print("\n[funnel]")
    for stage, n in funnel:
        print(f"   {stage:<40} {n}")

    if df.empty:
        sys.exit("\n[stop] no comments survived preprocessing. If you ran this on a "
                 "diagnostic scrape dated outside 2016..2025, that is expected -- set "
                 "APPLY_STUDY_WINDOW = False to smoke-test the other stages.")

    write_outputs(df, funnel)

    # brief composition summary (useful going into annotation sampling)
    print("\n[summary] comments per tier:")
    print(df["tier"].value_counts().to_string())
    print("\n[summary] comments per year:")
    print(df["year"].value_counts().sort_index().to_string())
    print("\n[done] preprocessing complete.")


if __name__ == "__main__":
    main()
