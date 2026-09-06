"""
draw_tranche1.py

Draw tranche 1 of the annotation sample and write one spreadsheet per annotator.

Implements R1 of docs/analysis_preregistration.md:

    500 items from the 12,166-item Tier 1+2 draw frame
    era-stratified 2016-2018 / 2019-2021 / 2022-2025, allocation 167 / 167 / 166
    inclusion probabilities recorded for every drawn item
    reliability subset of 100 items rated by all three annotators
    fixed random seed 24916660

Determinism
-----------
The frame is sorted by comment id before anything is drawn, so the result does not
depend on Parquet row order, file system order, or pandas version. The seed is
taken from R1. Re-running this script on the same corpus reproduces the same draw,
and the script verifies its own output against the recorded hash on every run.

What the annotators see
-----------------------
Comment text and subreddit only. Not the year, not the tier, not the thread title,
not the parent comment, not the author, not the score. This follows the annotation
protocol as amended by Deviation 1: the subreddit is shown because relevance is not
judgeable without it for a substantial minority of items, but nothing further is.

Reliability items are NOT marked in the annotator files and are shuffled through
the assignment, so that nobody annotates them more carefully than the rest.

Outputs
-------
    data/annotation/tranche1_annotator_A.csv    gitignored: contains comment text
    data/annotation/tranche1_annotator_B.csv
    data/annotation/tranche1_annotator_C.csv
    data/annotation/tranche1_master_key.csv     gitignored: assignment + probabilities
    data/frozen/tranche1_draw_ids.txt           committed: the 500 drawn ids
    data/frozen/tranche1_manifest.txt           committed: counts and hashes

Usage
-----
    python draw_tranche1.py            draw and write
    python draw_tranche1.py --verify   re-derive and check, write nothing

Author: Arnaud Dorasamy (24916660)
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Frozen parameters — R1 and R5
# ---------------------------------------------------------------------------

CORPUS = Path("data/clean_v2_2/corpus.parquet")
FRAME_IDS = Path("data/frozen/draw_frame_ids.txt")
ANNOTATION_DIR = Path("data/annotation")
FROZEN_DIR = Path("data/frozen")

SEED = 24916660

EXPECTED_FRAME_ROWS = 12_166
EXPECTED_FRAME_SHA256 = (
    "ce85a3b046fedf3648861d446832a364ab89e7b60a0e58f10272b33b1997d7b3"
)

ERAS = {
    "2016-2018": (2016, 2018),
    "2019-2021": (2019, 2021),
    "2022-2025": (2022, 2025),
}

# R1 allocation
ALLOCATION = {"2016-2018": 167, "2019-2021": 167, "2022-2025": 166}
EXPECTED_STRATUM_SIZES = {"2016-2018": 2495, "2019-2021": 3633, "2022-2025": 6038}

# Reliability subset within tranche 1, era-stratified to match the draw
RELIABILITY_ALLOCATION = {"2016-2018": 34, "2019-2021": 33, "2022-2025": 33}

ANNOTATORS = ["A", "B", "C"]


def membership_sha256(ids) -> str:
    """SHA-256 over sorted ids, newline-joined, no trailing newline."""
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def write_lines(path: Path, lines) -> None:
    """Write with LF endings explicitly, so a cited hash is platform-stable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def load_frame() -> pd.DataFrame:
    """Load the frozen draw frame and verify it against R5 before drawing."""
    if not CORPUS.exists():
        sys.exit(f"[FAIL] missing {CORPUS}")
    if not FRAME_IDS.exists():
        sys.exit(f"[FAIL] missing {FRAME_IDS} -- run emit_frozen_frame.py first")

    frame_ids = [ln.strip() for ln in FRAME_IDS.read_text(encoding="utf-8").splitlines()
                 if ln.strip()]
    frame_hash = membership_sha256(frame_ids)

    print(f"[frame] ids in file: {len(frame_ids):,}")
    print(f"[frame] sha256     : {frame_hash}")

    if len(frame_ids) != EXPECTED_FRAME_ROWS:
        sys.exit(f"[FAIL] frame has {len(frame_ids)} ids, R5 records "
                 f"{EXPECTED_FRAME_ROWS}. Stop.")
    if frame_hash != EXPECTED_FRAME_SHA256:
        sys.exit("[FAIL] frame hash does not match R5. The frame has changed and "
                 "the pre-registration no longer describes it. Stop.")
    print("[frame] matches R5  PASS\n")

    corpus = pd.read_parquet(CORPUS)
    frame = corpus[corpus.id.isin(frame_ids)].copy()
    if len(frame) != len(frame_ids):
        sys.exit(f"[FAIL] {len(frame_ids) - len(frame)} frame ids absent from the "
                 f"corpus. Frame and corpus disagree. Stop.")

    # Deterministic input order: sort by id, never rely on file order.
    frame = frame.sort_values("id", kind="mergesort").reset_index(drop=True)

    def era_of(year: int) -> str:
        for name, (lo, hi) in ERAS.items():
            if lo <= year <= hi:
                return name
        raise ValueError(f"year {year} falls outside the declared eras")

    frame["era"] = frame.year.map(era_of)
    return frame


def draw(frame: pd.DataFrame) -> pd.DataFrame:
    """Draw 500 items, era-stratified, recording inclusion probabilities."""
    rng = np.random.default_rng(SEED)
    drawn = []

    print("[draw] stratum          size   n   fraction")
    for era in ERAS:
        stratum = frame[frame.era == era].sort_values("id", kind="mergesort")
        n_stratum, n_draw = len(stratum), ALLOCATION[era]

        if n_stratum != EXPECTED_STRATUM_SIZES[era]:
            sys.exit(f"[FAIL] stratum {era} has {n_stratum} items, R1 records "
                     f"{EXPECTED_STRATUM_SIZES[era]}. Stop.")

        idx = rng.choice(n_stratum, size=n_draw, replace=False)
        picked = stratum.iloc[np.sort(idx)].copy()

        # Inclusion probability under equal-probability sampling within stratum.
        picked["stratum_size"] = n_stratum
        picked["stratum_draw"] = n_draw
        picked["inclusion_probability"] = n_draw / n_stratum
        picked["weight"] = n_stratum / n_draw

        print(f"       {era}   {n_stratum:6,} {n_draw:4d}   "
              f"{n_draw / n_stratum:.4f}")
        drawn.append(picked)

    sample = pd.concat(drawn, ignore_index=True)
    print(f"[draw] total drawn: {len(sample)}\n")
    return sample


def assign(sample: pd.DataFrame) -> pd.DataFrame:
    """Mark the reliability subset and assign every rating to an annotator."""
    rng = np.random.default_rng(SEED + 1)
    sample = sample.copy()
    sample["is_reliability"] = False

    # Reliability subset, era-stratified so agreement is not measured on a
    # temporally skewed slice.
    for era, n_rel in RELIABILITY_ALLOCATION.items():
        pool = sample.index[sample.era == era].to_numpy()
        chosen = rng.choice(pool, size=n_rel, replace=False)
        sample.loc[chosen, "is_reliability"] = True

    n_rel = int(sample.is_reliability.sum())
    print(f"[assign] reliability subset: {n_rel} items, rated by all three")

    # Remaining items split three ways, balanced within era so no annotator
    # receives a temporally skewed workload.
    sample["assigned_to"] = ""
    remainder = sample[~sample.is_reliability]

    for era in ERAS:
        pool = remainder.index[remainder.era == era].to_numpy().copy()
        rng.shuffle(pool)
        for i, row_idx in enumerate(pool):
            sample.loc[row_idx, "assigned_to"] = ANNOTATORS[i % len(ANNOTATORS)]

    counts = sample[~sample.is_reliability].assigned_to.value_counts().sort_index()
    print(f"[assign] singly-rated split: {counts.to_dict()}")
    for a in ANNOTATORS:
        print(f"[assign]   annotator {a}: {n_rel} reliability + "
              f"{counts.get(a, 0)} singly-rated = {n_rel + counts.get(a, 0)} items")
    print()
    return sample


def write_outputs(sample: pd.DataFrame, frame_hash: str) -> None:
    """Write per-annotator spreadsheets, the master key, and the frozen manifest."""
    ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED + 2)

    for a in ANNOTATORS:
        items = sample[sample.is_reliability | (sample.assigned_to == a)].copy()

        # Shuffle so reliability items are not clustered and cannot be inferred
        # from position. A per-annotator seed gives each a different order, so
        # comparing sheets side by side reveals nothing either.
        order = rng.permutation(len(items))
        items = items.iloc[order].reset_index(drop=True)

        sheet = pd.DataFrame({
            "row": range(1, len(items) + 1),
            "id": items.id.values,
            "subreddit": items.subreddit.values,
            "comment": items.clean_body.values,
            "stage1_relevant": "",
            "stage2_class": "",
            "skip": "",
            "notes": "",
        })
        path = ANNOTATION_DIR / f"tranche1_annotator_{a}.csv"
        sheet.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"[write] {path}  ({len(sheet)} items)")

    key = sample[["id", "era", "year", "tier", "subreddit", "stratum_size",
                  "stratum_draw", "inclusion_probability", "weight",
                  "is_reliability", "assigned_to"]].sort_values("id")
    key_path = ANNOTATION_DIR / "tranche1_master_key.csv"
    key.to_csv(key_path, index=False, encoding="utf-8-sig")
    print(f"[write] {key_path}  (researcher only -- do not send to annotators)")

    draw_hash = membership_sha256(sample.id.astype(str))
    write_lines(FROZEN_DIR / "tranche1_draw_ids.txt", sorted(sample.id.astype(str)))

    rel_ids = sorted(sample.loc[sample.is_reliability, "id"].astype(str))
    write_lines(FROZEN_DIR / "tranche1_manifest.txt", [
        "# Tranche 1 draw manifest -- R1, corpus v2.2",
        f"seed                        {SEED}",
        f"frame_rows                  {EXPECTED_FRAME_ROWS}",
        f"frame_membership_sha256     {frame_hash}",
        f"drawn_rows                  {len(sample)}",
        f"draw_membership_sha256      {draw_hash}",
        f"reliability_rows            {int(sample.is_reliability.sum())}",
        f"reliability_sha256          {membership_sha256(rel_ids)}",
        "",
        "# stratum, size, drawn, inclusion probability",
        *[f"{e:12s} {EXPECTED_STRATUM_SIZES[e]:6d} {ALLOCATION[e]:4d} "
          f"{ALLOCATION[e] / EXPECTED_STRATUM_SIZES[e]:.6f}" for e in ERAS],
        "",
        "# ratings per annotator",
        *[f"{a}  {int((sample.is_reliability | (sample.assigned_to == a)).sum())}"
          for a in ANNOTATORS],
    ])
    print(f"[write] {FROZEN_DIR / 'tranche1_draw_ids.txt'}")
    print(f"[write] {FROZEN_DIR / 'tranche1_manifest.txt'}")
    print(f"\n[draw] membership sha256: {draw_hash}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="re-derive the draw and report its hash without writing")
    args = ap.parse_args()

    frame = load_frame()
    frame_hash = membership_sha256(frame.id.astype(str))
    sample = assign(draw(frame))

    if args.verify:
        print(f"[verify] draw membership sha256: "
              f"{membership_sha256(sample.id.astype(str))}")
        print("[verify] nothing written.")
        return

    write_outputs(sample, frame_hash)
    print("\n[done] Send the three annotator files. Keep the master key.")


if __name__ == "__main__":
    main()
