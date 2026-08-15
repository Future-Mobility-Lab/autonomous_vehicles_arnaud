"""
Walking-skeleton pipeline for the CAV-concern Reddit capstone.

Purpose: prove the ENTIRE pipeline runs end to end on a tiny sample, in one file,
before building the full modular version. It:
  1. scrapes a small set of comments from Reddit via the Apify actor
     harshmaur/reddit-scraper (or loads a cached scrape so you don't pay twice),
  2. cleans and filters them (known traps handled: comment-only, deleted/removed,
     bots, blockquotes, language, 20-word floor, dedup),
  3. runs three-class sentiment with cardiffnlp/twitter-roberta-base-sentiment,
     with a label sanity-check that HALTS if the negative/positive mapping is wrong,
  4. writes a de-identified per-comment CSV (no usernames) to outputs/,
  5. plots a monthly concern-share / mean-polarity chart to outputs/.

This is a proof of pipeline, not a proof of findings. A one-day scrape of a single
subreddit lands in a single month, so the plot will show one period -- that is
expected. Meaningful multi-year trajectories come from the dated historical pulls
(postedAfter / postedBefore) in the real collection stage.

Run:  (.venv active)  python skeleton_pipeline.py
Token: put  APIFY_API_TOKEN=...  in a file named .env in the repo root (git-ignored).
"""

from __future__ import annotations
import os
import re
import sys
import json
import html
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# CONFIG -- edit these; everything below can stay as-is
# ---------------------------------------------------------------------------
ACTOR_ID = "harshmaur/reddit-scraper"

# Tiny test scrape. Caps kept low so a misconfigured run cannot burn credits.
RUN_INPUT = {
    "startUrls": [{"url": "https://www.reddit.com/r/SelfDrivingCars/"}],
    "crawlCommentsPerPost": True,
    "maxPostsCount": 5,
    "maxCommentsPerPost": 40,
    "maxCommentsCount": 200,
    "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
}

FORCE_SCRAPE = False        # True = ignore cache and pay for a fresh scrape
WORD_FLOOR = 20             # keep comments with >= this many words (proposal: 20-token floor)
CONCERN_THRESHOLD = 0.50    # PLACEHOLDER: concern = P(negative) >= this.
#                             The real flag is calibrated against your manual
#                             validation set -- do not treat this number as final.

SENTIMENT_MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
# Documented label order for THIS checkpoint (it lives on the model card; the
# config only returns LABEL_0/1/2). Verified at runtime by the sanity check.
LABEL_MAP = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}

# Non-human accounts to drop. Deliberately conservative: matching every name that
# ends in "bot" would catch real users, so we only list known utility accounts.
KNOWN_BOTS = {"automoderator", "autotldr", "sneakpeekbot", "remindmebot",
              "b0trank", "wikitextbot", "gifv-bot", "totesmessenger"}

RAW_DIR = Path("data/raw")
OUT_DIR = Path("outputs")
RAW_CACHE = RAW_DIR / "skeleton_scrape.json"
CLASSIFIED_CSV = OUT_DIR / "skeleton_classified.csv"
FUNNEL_CSV = OUT_DIR / "skeleton_funnel.csv"
PLOT_PNG = OUT_DIR / "skeleton_monthly.png"


# ---------------------------------------------------------------------------
# 0. tiny .env reader (avoids adding a dependency)
# ---------------------------------------------------------------------------
def load_env(path: str = ".env") -> None:
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


# ---------------------------------------------------------------------------
# 1. scrape (or load cache)
# ---------------------------------------------------------------------------
def scrape_or_load() -> list[dict]:
    if RAW_CACHE.exists() and not FORCE_SCRAPE:
        print(f"[scrape] using cached scrape: {RAW_CACHE}")
        return json.loads(RAW_CACHE.read_text(encoding="utf-8"))

    token = os.environ.get("APIFY_API_TOKEN", "").strip()
    if not token:
        sys.exit("[scrape] No APIFY_API_TOKEN found. Put it in a .env file "
                 "(APIFY_API_TOKEN=...) in the repo root, then re-run.")

    from apify_client import ApifyClient  # imported here so cleaning runs without it
    print(f"[scrape] running actor {ACTOR_ID} (this costs a small amount) ...")
    client = ApifyClient(token)
    run = client.actor(ACTOR_ID).call(run_input=RUN_INPUT)
    if run is None:
        sys.exit("[scrape] actor run did not complete (returned None).")
    # apify-client >= 3 returns a Run OBJECT (attribute access); older versions
    # returned a dict. Support both so a version bump doesn't break this line.
    dataset_id = getattr(run, "default_dataset_id", None) or run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RAW_CACHE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[scrape] fetched {len(items)} items, cached to {RAW_CACHE}")
    return items


# ---------------------------------------------------------------------------
# 2. clean + filter
# ---------------------------------------------------------------------------
URL_RE = re.compile(r"https?://\S+")
BLOCKQUOTE_RE = re.compile(r"^\s*>.*$", re.MULTILINE)        # reddit markdown quote lines
MD_ESCAPE_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!>])")     # \[ -> [  etc.
WS_RE = re.compile(r"\s+")
DELETED = {"[deleted]", "[removed]", ""}


def clean_body(text: str) -> str:
    """Strip quoted parent text, URLs and markdown; unescape HTML entities;
    collapse whitespace. Emoji are kept (the tokenizer handles them)."""
    if not text:
        return ""
    text = BLOCKQUOTE_RE.sub(" ", text)   # remove quoted parent text BEFORE analysis
    text = URL_RE.sub(" ", text)
    text = html.unescape(text)            # &amp; -> &  (harmless if already clean)
    text = MD_ESCAPE_RE.sub(r"\1", text)
    text = text.replace("*", "").replace("#", "")   # light emphasis strip
    text = WS_RE.sub(" ", text).strip()
    return text


def preprocess(items: list[dict]):
    """Return (dataframe, funnel) where funnel is a list of (stage, count)."""
    funnel = [("raw items", len(items))]

    rows = [it for it in items if it.get("dataType") == "comment"]
    funnel.append(("comments", len(rows)))

    # Two deletion patterns exist in the data:
    #   (A) body == "[deleted]"/"[removed]"  -> the TEXT is gone; MUST drop.
    #   (B) authorName == "[deleted]" but body is real text -> the user deleted
    #       their ACCOUNT, not the comment; the text survives and is public.
    #       We KEEP it and treat the author as anonymous. Dropping it would discard
    #       valid text and worsen early-period sparsity, because account deletions
    #       accrue with age and hit your 2016-2020 window hardest.
    rows = [r for r in rows if (r.get("body") or "").strip() not in DELETED]
    funnel.append(("after body-deleted removed", len(rows)))

    # match bots on authorName -- the true author key. NOTE: on comments authorId is
    # the comment's OWN fullname (t1_<id>), not the author, so never key on it.
    rows = [r for r in rows if (r.get("authorName") or "").lower() not in KNOWN_BOTS]
    funnel.append(("after bot filter", len(rows)))

    df = pd.DataFrame(rows)
    if df.empty:
        return df, funnel
    df["clean_body"] = df["body"].map(clean_body)

    # English only; deterministic seed so the same text always classifies the same way
    from langdetect import detect, DetectorFactory, LangDetectException
    DetectorFactory.seed = 0

    def is_en(t: str) -> bool:
        try:
            return detect(t) == "en"
        except LangDetectException:
            return False

    df = df[df["clean_body"].map(is_en)]
    funnel.append(("after English filter", len(df)))

    # word floor on the CLEANED text (after quotes removed, so a comment isn't kept
    # on the strength of text it was only quoting)
    df["clean_wordcount"] = df["clean_body"].str.split().map(len)
    df = df[df["clean_wordcount"] >= WORD_FLOOR]
    funnel.append((f"after >= {WORD_FLOOR}-word floor", len(df)))

    df = df.drop_duplicates(subset="id", keep="first")
    funnel.append(("after dedup", len(df)))

    df["created"] = pd.to_datetime(df["commentCreatedAt"], utc=True, errors="coerce")
    df = df.dropna(subset=["created"])

    return df.reset_index(drop=True), funnel


# ---------------------------------------------------------------------------
# 3. sentiment (three-class) with a label sanity check that HALTS on failure
# ---------------------------------------------------------------------------
def run_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    import torch
    from transformers import pipeline

    device = 0 if torch.cuda.is_available() else -1
    where = "GPU" if device == 0 else "CPU"
    print(f"[sentiment] loading {SENTIMENT_MODEL} on {where} "
          "(first run downloads the model, ~500 MB) ...")
    clf = pipeline("sentiment-analysis", model=SENTIMENT_MODEL,
                   top_k=None, device=device, truncation=True, max_length=512)

    def scores_for(text: str) -> dict:
        out = clf(text)[0]                       # list of {label, score}
        return {LABEL_MAP[d["label"]]: d["score"] for d in out}

    # --- SANITY CHECK: prove negative and positive are not swapped ----------
    pos = scores_for("This is wonderful, I love it, absolutely fantastic.")
    neg = scores_for("This is terrible, I hate it, absolutely awful.")
    if not (pos["positive"] > pos["negative"] and neg["negative"] > neg["positive"]):
        sys.exit("[sentiment] LABEL SANITY CHECK FAILED -- mapping is wrong. "
                 f"positive probe={pos}, negative probe={neg}. "
                 "Fix LABEL_MAP before trusting any results.")
    print("[sentiment] label sanity check passed "
          f"(pos probe P(pos)={pos['positive']:.2f}, neg probe P(neg)={neg['negative']:.2f})")

    # --- classify the corpus (batched) -------------------------------------
    results = clf(df["clean_body"].tolist(), batch_size=16)
    p_neg, p_neu, p_pos = [], [], []
    for out in results:
        s = {LABEL_MAP[d["label"]]: d["score"] for d in out}
        p_neg.append(s["negative"]); p_neu.append(s["neutral"]); p_pos.append(s["positive"])

    df = df.copy()
    df["p_neg"], df["p_neu"], df["p_pos"] = p_neg, p_neu, p_pos
    df["polarity"] = df["p_pos"] - df["p_neg"]                # + positive, - negative
    df["predicted_class"] = (df[["p_neg", "p_neu", "p_pos"]].values.argmax(axis=1))
    df["predicted_class"] = df["predicted_class"].map({0: "negative", 1: "neutral", 2: "positive"})
    df["concern_flag"] = (df["p_neg"] >= CONCERN_THRESHOLD).astype(int)   # PLACEHOLDER rule
    return df


# ---------------------------------------------------------------------------
# 4. export (de-identified) + 5. plot
# ---------------------------------------------------------------------------
def export_and_plot(df: pd.DataFrame, funnel) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # the funnel is your data-quality table in miniature
    pd.DataFrame(funnel, columns=["stage", "items"]).to_csv(FUNNEL_CSV, index=False)

    # de-identified analysis table: NO usernames; short body preview only
    out = df.copy()
    out["body_preview"] = out["clean_body"].str.slice(0, 80)
    cols = ["id", "created", "subredditName", "clean_wordcount",
            "p_neg", "p_neu", "p_pos", "polarity", "predicted_class",
            "concern_flag", "body_preview"]
    out[cols].to_csv(CLASSIFIED_CSV, index=False)
    print(f"[export] wrote {len(out)} rows to {CLASSIFIED_CSV} (no usernames)")

    out["month"] = out["created"].dt.tz_convert(None).dt.to_period("M").dt.to_timestamp()
    monthly = (out.groupby("month")
               .agg(n=("id", "size"),
                    concern_share=("concern_flag", "mean"),
                    mean_polarity=("polarity", "mean"))
               .reset_index())

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    ax1.bar(monthly["month"], monthly["concern_share"], width=20)
    ax1.set_ylabel("concern share")
    ax1.set_ylim(0, 1)
    ax1.set_title("Skeleton run -- monthly concern share and mean polarity")
    ax2.plot(monthly["month"], monthly["mean_polarity"], marker="o")
    ax2.axhline(0, color="grey", linewidth=0.8)
    ax2.set_ylabel("mean polarity")
    ax2.set_xlabel("month")
    fig.tight_layout()
    fig.savefig(PLOT_PNG, dpi=120)
    print(f"[plot]   wrote {PLOT_PNG}")

    print("\n[funnel]")
    for stage, n in funnel:
        print(f"   {stage:<28} {n}")
    print(f"\n[note] {monthly['month'].nunique()} month(s) present. A single-day scrape "
          "lands in one month; multi-year trajectories need dated historical pulls.")


def main() -> None:
    load_env()
    items = scrape_or_load()
    df, funnel = preprocess(items)
    if df.empty:
        sys.exit("[stop] no comments survived preprocessing -- check the scrape/filters.")
    df = run_sentiment(df)
    export_and_plot(df, funnel)
    print("\n[done] skeleton pipeline completed.")


if __name__ == "__main__":
    main()
