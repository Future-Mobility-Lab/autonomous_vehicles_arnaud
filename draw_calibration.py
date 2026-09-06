"""
draw_calibration.py

Draw the 30-item calibration round and write one sheet per annotator.

The calibration round precedes production annotation. All three annotators label
the same 30 items, every disagreement is reviewed, and the codebook may be revised
as a result. The 30 items are then DISCARDED and do not enter the annotated set.

Exclusions
----------
The calibration items are drawn from the draw frame less:

    the 500 items already drawn for tranche 1  (they must not be annotated twice,
                                                and a calibration item that later
                                                appears in production would be
                                                seen by an annotator who has
                                                already discussed it)
    the 59 codebook worked examples            (already excluded from the frame,
                                                but checked again here)

Stratification
--------------
Ten items per era, matching the era structure of the sample so that calibration
disagreement is not concentrated in one period. Calibration items carry no
inclusion probabilities: they are discarded, never analysed, and contribute to no
estimate.

What calibration must record
----------------------------
Three pre-registered decisions depend on data collected during this round, so the
recording sheet asks for more than the labels:

    per-item timing, split by stage   input to the subsystem-coverage decision
    disagreement cause, assigned      R2 branch selector; MUST be assigned before
      BEFORE agreement is computed    Krippendorff's alpha is calculated
    realised class counts             input to the tranche 2 allocation

Outputs
-------
    data/annotation/calibration_annotator_A.csv   gitignored: contains comment text
    data/annotation/calibration_annotator_B.csv
    data/annotation/calibration_annotator_C.csv
    data/annotation/calibration_review_sheet.csv  gitignored: for the disagreement review
    data/frozen/calibration_ids.txt               committed
    data/frozen/calibration_manifest.txt          committed

Usage
-----
    python draw_calibration.py

Author: Arnaud Dorasamy (24916660)
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd

CORPUS = Path("data/clean_v2_2/corpus.parquet")
FRAME_IDS = Path("data/frozen/draw_frame_ids.txt")
TRANCHE1_IDS = Path("data/frozen/tranche1_draw_ids.txt")
CODEBOOK_IDS = Path("data/frozen/codebook_example_ids.txt")
ANNOTATION_DIR = Path("data/annotation")
FROZEN_DIR = Path("data/frozen")

# Seed offset from the pre-registered seed, so calibration cannot collide with
# either tranche while remaining reproducible from the recorded value.
SEED = 24916660 + 100

ERAS = {"2016-2018": (2016, 2018), "2019-2021": (2019, 2021), "2022-2025": (2022, 2025)}
PER_ERA = 10
ANNOTATORS = ["A", "B", "C"]


def membership_sha256(ids) -> str:
    return hashlib.sha256("\n".join(sorted(ids)).encode("utf-8")).hexdigest()


def write_lines(path: Path, lines) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines))


def read_ids(path: Path) -> set[str]:
    if not path.exists():
        sys.exit(f"[FAIL] missing {path}")
    return {ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()}


def main() -> None:
    frame_ids = read_ids(FRAME_IDS)
    tranche1 = read_ids(TRANCHE1_IDS)
    codebook = read_ids(CODEBOOK_IDS)

    print(f"[pool] draw frame            {len(frame_ids):,}")
    print(f"[pool] less tranche 1        {len(tranche1 & frame_ids):,}")
    print(f"[pool] less codebook examples "
          f"{len(codebook & frame_ids):,}  (expected 0 -- already excluded)")

    eligible = frame_ids - tranche1 - codebook
    print(f"[pool] eligible for calibration {len(eligible):,}\n")

    corpus = pd.read_parquet(CORPUS)
    pool = corpus[corpus.id.isin(eligible)].sort_values("id", kind="mergesort")

    def era_of(year: int) -> str:
        for name, (lo, hi) in ERAS.items():
            if lo <= year <= hi:
                return name
        raise ValueError(f"year {year} outside declared eras")

    pool = pool.copy()
    pool["era"] = pool.year.map(era_of)

    rng = np.random.default_rng(SEED)
    picked = []
    print("[draw] era          pool    n")
    for era in ERAS:
        stratum = pool[pool.era == era].sort_values("id", kind="mergesort")
        idx = rng.choice(len(stratum), size=PER_ERA, replace=False)
        picked.append(stratum.iloc[np.sort(idx)])
        print(f"       {era}  {len(stratum):6,} {PER_ERA:4d}")

    cal = pd.concat(picked, ignore_index=True)
    cal_hash = membership_sha256(cal.id.astype(str))
    print(f"[draw] calibration items: {len(cal)}")
    print(f"[draw] sha256: {cal_hash}\n")

    assert not (set(cal.id) & tranche1), "calibration overlaps tranche 1"
    assert not (set(cal.id) & codebook), "calibration overlaps codebook examples"
    print("[check] no overlap with tranche 1 or codebook examples  PASS\n")

    # ---- annotator sheets --------------------------------------------------
    ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)
    rng2 = np.random.default_rng(SEED + 1)

    for a in ANNOTATORS:
        items = cal.iloc[rng2.permutation(len(cal))].reset_index(drop=True)
        sheet = pd.DataFrame({
            "row": range(1, len(items) + 1),
            "id": items.id.values,
            "subreddit": items.subreddit.values,
            "comment": items.clean_body.values,
            "stage1_relevant": "",
            "stage1_seconds": "",
            "stage2_class": "",
            "stage2_seconds": "",
            "subsystem": "",
            "subsystem_seconds": "",
            "skip": "",
            "notes": "",
        })
        path = ANNOTATION_DIR / f"calibration_annotator_{a}.csv"
        sheet.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"[write] {path}  ({len(sheet)} items)")

    # ---- disagreement review sheet ----------------------------------------
    # Filled during the group review, AFTER all three have annotated
    # independently and BEFORE Krippendorff's alpha is computed.
    review = pd.DataFrame({
        "id": sorted(cal.id.astype(str)),
        "label_A": "", "label_B": "", "label_C": "",
        "disagreement": "",          # stage1 / stage2 / none
        "cause": "",                 # a = missing context, b = codebook ambiguity,
                                     # c = misapplication   (R2)
        "agreed_label": "",
        "codebook_change_needed": "",
        "review_notes": "",
    })
    rpath = ANNOTATION_DIR / "calibration_review_sheet.csv"
    review.to_csv(rpath, index=False, encoding="utf-8-sig")
    print(f"[write] {rpath}  (fill during the group review)")

    # ---- frozen record -----------------------------------------------------
    write_lines(FROZEN_DIR / "calibration_ids.txt", sorted(cal.id.astype(str)))
    write_lines(FROZEN_DIR / "calibration_manifest.txt", [
        "# Calibration round manifest -- R2, corpus v2.2",
        f"seed                      {SEED}",
        f"eligible_pool             {len(eligible)}",
        f"items                     {len(cal)}",
        f"per_era                   {PER_ERA}",
        f"membership_sha256         {cal_hash}",
        "overlap_tranche1          0",
        "overlap_codebook          0",
        "",
        "# These items are DISCARDED after the calibration round.",
        "# They do not enter the annotated set and contribute to no estimate.",
    ])
    print(f"[write] {FROZEN_DIR / 'calibration_ids.txt'}")
    print(f"[write] {FROZEN_DIR / 'calibration_manifest.txt'}")

    print("\n[done] Send the three calibration sheets with the codebook.")
    print("       Do NOT send the production sheets until the review is complete.")


if __name__ == "__main__":
    main()
