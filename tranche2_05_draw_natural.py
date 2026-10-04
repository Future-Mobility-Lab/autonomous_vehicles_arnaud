"""Tranche 2, step 5: the natural draw that replaces the boosted tranche (Deviation 11).

The gate of Deviation 10 failed, so nothing was drawn under it. Under Deviation 11
tranche 2 is a second natural tranche, drawn as R1 draws tranche 1: a simple random
sample without replacement within each era, with no pre-filter.

  Eligible     the 12,166 frame items less the 500 tranche 1 items and the 30
               calibration items, as validated and frozen by step 1.
  Draw         within each era, a simple random sample without replacement from
               the eligible items of that era, with the tranche 1 allocation
               (167 / 167 / 166). No model output is used.
  Reliability  100 of the 500, spread across eras in proportion to the draw
               (largest remainder, exact arithmetic, ties to the earlier era:
               34 / 33 / 33), random within era.
  Assignment   the other 400 are shuffled within era and dealt A, B, C in turn.
  Sheets       as Deviation 10 specifies (Presentation, Subsystem labels): each
               annotator's 100 reliability items and own items in that annotator's
               own random order, comment text and subreddit only, with the two
               subsystem columns hidden until the first pass is done.
  Weights      the two tranches together are a simple random sample of
               334 / 334 / 332 within era, so the pooled weight of an item is the
               frame stratum size over the pooled draw of its era. The key also
               records the weight for tranche 2 on its own, the frame stratum size
               over its own draw, which is how the tranche 1 key records its weights.

Every random step uses numpy.random.default_rng([24916660, 2, component]) with the
components listed below. None of them is used by the Deviation 10 scripts.

  python tranche2_05_draw_natural.py --check    input checks only; nothing is drawn or written
  python tranche2_05_draw_natural.py            the draw (made once; never overwritten)

The pre-filter scores, hit rates and allocation of Deviation 10 are not used. The
only thing read from them is the gate result recorded in tranche2_allocation.json,
which must be FAIL. They stay sealed.

The master key and the manifest show which items are reliability items. The author
is annotator A and does not open them until all three sheets are returned.
"""
from __future__ import annotations

import argparse
import csv
import shutil

import numpy as np
import pandas as pd

import tranche2_common as c
import tranche2_04_draw as d            # workbook writer, exact largest-remainder split, patient file moves

ERAS = ["2016-2018", "2019-2021", "2022-2025"]
FRAME_BY_ERA = {"2016-2018": 2495, "2019-2021": 3633, "2022-2025": 6038}        # R1
ALLOCATION = {"2016-2018": 167, "2019-2021": 167, "2022-2025": 166}             # R1, the tranche 1 allocation
RNG_COMPONENT = {
    "draw_2016-2018": 10, "draw_2019-2021": 11, "draw_2022-2025": 12,
    "reliability": 13, "assignment": 14,
    "order_A": 15, "order_B": 16, "order_C": 17,
}
PASTE_STEP5 = c.OUT_DIR / "PASTE_step5_register_block.txt"

NOTICE = (
    "Do not open tranche2_master_key.csv, tranche2_manifest.json or another annotator's workbook until all\n"
    "three sheets are returned: they show which items are reliability items. The Deviation 10 files\n"
    "(scores, manifest, allocation, hit rates, SEALED_*.txt) stay sealed as before.")


def rng(component: str) -> np.random.Generator:
    return np.random.default_rng([c.SEED, c.TRANCHE, RNG_COMPONENT[component]])


def by_era(ids, era: pd.Series) -> dict[str, int]:
    counts = era.loc[list(ids)].value_counts()
    return {e: int(counts.get(e, 0)) for e in ERAS}


def slashes(counts: dict[str, int]) -> str:
    return " / ".join(f"{counts[e]:,}" for e in ERAS)


def main() -> None:
    c.setup_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="run the input checks only; draw and write nothing")
    args = ap.parse_args()
    print("Tranche 2, step 5: natural draw (Deviation 11)\n")

    final = {"key": c.MASTER_KEY, "manifest": c.DRAW_MANIFEST}
    final.update({a: c.workbook_path(a) for a in c.ANNOTATORS})
    existing = [p for p in final.values() if p.exists()]
    if existing:
        c.stop("tranche 2 output already exists and a frozen draw is never overwritten:\n  "
               + "\n  ".join(str(p) for p in existing)
               + "\n  If a redraw is genuinely needed, record the reason as a deviation first.")

    if set(RNG_COMPONENT.values()) & set(c.RNG_COMPONENT.values()):
        c.stop("a random-number component of this script is also used by the Deviation 10 scripts")

    # ---- inputs, as validated and frozen by step 1 -----------------------------------
    step1 = c.step1_manifest()
    frame_ids = c.load_frame()
    corpus, _ = c.load_corpus(frame_ids)
    corpus = corpus.set_index("id")
    key1, _, _ = c.load_tranche1(verbose=False)
    calibration = c.load_resolved_calibration(step1)
    eligible = c.eligible_ids(frame_ids, key1.index, calibration, step1)
    era = corpus["era"]

    # the eras are R1's strata: check them against R1 and against the tranche 1 key
    if set(era.unique()) - set(ERAS):
        c.stop(f"some frame items fall outside the three eras: {sorted(set(era.unique()) - set(ERAS))}")
    frame_era = by_era(frame_ids, era)
    if frame_era != FRAME_BY_ERA:
        c.stop(f"the frame has {slashes(frame_era)} items by era; R1 fixes {slashes(FRAME_BY_ERA)}. "
               f"The creation-time column may be the wrong one.")
    print(f"frame by era: {slashes(frame_era)} (matches R1)")
    t1_ids = list(key1.index)
    if not (era.loc[t1_ids] == key1["era"]).all():
        c.stop("the era of some tranche 1 items differs between the corpus and the tranche 1 key")
    t1_era = by_era(t1_ids, era)
    if t1_era != ALLOCATION:
        c.stop(f"tranche 1 has {slashes(t1_era)} items by era; R1 fixes {slashes(ALLOCATION)}")
    print(f"tranche 1 by era: {slashes(t1_era)} (matches R1)")
    frame_set = set(frame_ids)
    cal_in_frame = [i for i in calibration if i in frame_set]
    cal_era = by_era(cal_in_frame, era)
    print(f"calibration items by era: {slashes(cal_era)} ({len(cal_in_frame)} in the frame, excluded)")
    pools = {e: [i for i in eligible if era.at[i] == e] for e in ERAS}       # eligible is sorted, so each pool is too
    elig_era = {e: len(pools[e]) for e in ERAS}
    if any(elig_era[e] != FRAME_BY_ERA[e] - t1_era[e] - cal_era[e] for e in ERAS):
        c.stop("the eligible items by era are not the frame less tranche 1 less the calibration items")
    print(f"eligible by era: {slashes(elig_era)} = {len(eligible):,}")

    # the gate of Deviation 10 must have failed; nothing else is read from its outputs
    if not c.ALLOCATION_JSON.exists():
        c.stop("tranche2_allocation.json is missing. This draw replaces the boosted tranche only after the "
               "Deviation 10 gate has been run and has failed.")
    gate = c.read_json(c.ALLOCATION_JSON).get("gate", {}).get("result")
    allocation_sha = c.file_sha256(c.ALLOCATION_JSON)
    if gate != "FAIL":
        c.stop("the Deviation 10 gate did not fail. This draw is specified only as the replacement after a failed gate.")
    print(f"Deviation 10 gate, as recorded in {c.ALLOCATION_JSON.name}: FAIL (file SHA-256 {allocation_sha})")

    # the text shown to annotators is the cleaned text that step 1 wrote (and the pre-filter scored)
    if c.file_sha256(c.PREFILTER_INPUT) != step1["file_sha256"]:
        c.stop("prefilter_input.csv has changed since step 1 wrote it.")
    shown = pd.read_csv(c.PREFILTER_INPUT, dtype=str, keep_default_na=False, encoding="utf-8").set_index("id")["text"]
    if not (shown.reindex(corpus.index) == corpus["text"]).all():
        c.stop("the corpus text no longer matches the text step 1 wrote. The corpus file has changed since step 1.")
    print("text: prefilter_input.csv matches step 1 and the corpus")

    pooled = {e: t1_era[e] + ALLOCATION[e] for e in ERAS}
    print(f"tranche 2 allocation by era: {slashes(ALLOCATION)} | pooled draw of both tranches: {slashes(pooled)}")
    if not c.INCLUDE_SUBSYSTEM_COLUMNS:
        c.stop("INCLUDE_SUBSYSTEM_COLUMNS must be True (Deviation 10: subsystem labels in the same workbook).")
    if args.check:
        print("\nAll checks passed. Nothing was drawn (--check).")
        return

    # ---- draw: simple random sampling without replacement within era ------------------
    drawn: dict[str, list[str]] = {}
    for e in ERAS:
        pick = rng(f"draw_{e}").choice(len(pools[e]), size=ALLOCATION[e], replace=False)
        drawn[e] = [pools[e][j] for j in sorted(int(j) for j in pick)]
    ids = sorted(i for e in ERAS for i in drawn[e])

    # ---- reliability subset -----------------------------------------------------------
    quota = d.largest_remainder(c.RELIABILITY_N, {e: len(drawn[e]) for e in ERAS})
    g = rng("reliability")
    reliability: set[str] = set()
    for e in ERAS:
        pick = g.choice(len(drawn[e]), size=quota[e], replace=False)
        reliability |= {drawn[e][int(j)] for j in pick}

    # ---- assignment of the remaining items ---------------------------------------------
    g = rng("assignment")
    sequence: list[str] = []
    for e in ERAS:
        singles = [i for i in drawn[e] if i not in reliability]
        sequence += [singles[int(j)] for j in g.permutation(len(singles))]
    assigned = {i: c.ANNOTATORS[pos % len(c.ANNOTATORS)] for pos, i in enumerate(sequence)}

    # ---- sheets --------------------------------------------------------------------------
    sheets: dict[str, list[str]] = {}
    for a in c.ANNOTATORS:
        items = sorted(reliability | {i for i, who in assigned.items() if who == a})
        order = rng(f"order_{a}").permutation(len(items))
        sheets[a] = [items[int(j)] for j in order]

    # ---- self-checks before anything is written ------------------------------------------
    t1, cal = set(t1_ids), set(calibration)
    too_long = [i for i in ids if c.excel_len(shown[i]) > c.EXCEL_CELL_LIMIT]
    unclean = [i for i in ids if c.shown_text(shown[i]) != shown[i]]
    checks = {
        "500 distinct ids": len(ids) == c.TRANCHE2_N == len(set(ids)),
        "all eligible (in frame, not tranche 1, not calibration)": set(ids) <= set(eligible) and not (set(ids) & (t1 | cal)),
        "counts by era equal the allocation (167 / 167 / 166)": by_era(ids, era) == ALLOCATION,
        "100 reliability items, 34 / 33 / 33 by era": len(reliability) == c.RELIABILITY_N
                                                      and by_era(reliability, era) == {ERAS[0]: 34, ERAS[1]: 33, ERAS[2]: 33},
        "400 single items, each assigned once": len(assigned) == c.TRANCHE2_N - c.RELIABILITY_N
                                                 and not (set(assigned) & reliability),
        "reliability items in every sheet": all(reliability <= set(sheets[a]) for a in c.ANNOTATORS),
        "700 ratings in total": sum(len(v) for v in sheets.values()) == c.TRANCHE2_N + 2 * c.RELIABILITY_N,
        "every comment fits in a workbook cell and is clean": not too_long and not unclean,
    }
    for name, ok in checks.items():
        print(f"  [{'ok' if ok else 'FAIL'}] {name}")
    if not all(checks.values()):
        c.stop("a self-check failed; nothing was written.")

    # ---- write to a temporary folder, verify, then move into place ------------------------
    tmp = c.OUT_DIR / "_draw_in_progress"
    if tmp.exists():
        d.patiently(lambda: shutil.rmtree(tmp))
    d.patiently(lambda: tmp.mkdir(parents=True))
    try:
        key = pd.DataFrame({
            "id": ids,
            "era": [era.at[i] for i in ids],
            "year": [int(corpus.at[i, "year"]) for i in ids],
            "tier": [corpus.at[i, "tier"] for i in ids],
            "subreddit": [corpus.at[i, "subreddit"] for i in ids],
            "stratum_size": [FRAME_BY_ERA[era.at[i]] for i in ids],
            "eligible_in_stratum": [elig_era[era.at[i]] for i in ids],
            "stratum_draw": [ALLOCATION[era.at[i]] for i in ids],
            # as in the tranche 1 key: the frame stratum size over this tranche's own draw
            "inclusion_probability": [ALLOCATION[era.at[i]] / FRAME_BY_ERA[era.at[i]] for i in ids],
            "weight": [FRAME_BY_ERA[era.at[i]] / ALLOCATION[era.at[i]] for i in ids],
            "pooled_draw": [pooled[era.at[i]] for i in ids],
            "pooled_weight": [FRAME_BY_ERA[era.at[i]] / pooled[era.at[i]] for i in ids],
            "is_reliability": [i in reliability for i in ids],
            "assigned_to": [assigned.get(i, "") for i in ids],
            "tranche": c.TRANCHE,
        })
        key.to_csv(tmp / final["key"].name, index=False, encoding="utf-8-sig", lineterminator="\n",
                   quoting=csv.QUOTE_MINIMAL)

        for a in c.ANNOTATORS:
            rows = [{"id": i, "subreddit": corpus.at[i, "subreddit"], "comment": shown[i]} for i in sheets[a]]
            path = tmp / final[a].name
            d.write_workbook(path, a, rows)
            back = pd.read_excel(path, dtype=object, keep_default_na=False)       # read back what was written
            if back["id"].astype(str).tolist() != sheets[a] or back["row"].tolist() != list(range(1, len(rows) + 1)):
                raise RuntimeError(f"workbook {a} did not read back as written")
            same_text = sum(c.norm_ws(x) == c.norm_ws(r["comment"]) for x, r in zip(back["comment"], rows))
            if same_text != len(rows):
                raise RuntimeError(f"workbook {a}: {len(rows) - same_text} comments did not read back as written")

        manifest = {
            "created": c.now_iso(),
            "specification": "R1 and Deviation 11, docs/analysis_preregistration.md",
            "design": "natural tranche: simple random sampling without replacement within era; no pre-filter",
            "seed": c.SEED,
            "rng": "numpy.random.default_rng([seed, tranche, component])",
            "rng_components": RNG_COMPONENT,
            "frame_by_era": FRAME_BY_ERA,
            "tranche1_by_era": t1_era,
            "calibration_in_frame_by_era": cal_era,
            "eligible_by_era": elig_era,
            "allocation_by_era": ALLOCATION,
            "pooled_draw_by_era": pooled,
            "pooled_weight_by_era": {e: FRAME_BY_ERA[e] / pooled[e] for e in ERAS},
            "weights": "weight = frame stratum size / this tranche's draw, as in the tranche 1 key; "
                       "pooled_weight = frame stratum size / pooled draw of both tranches",
            "tranche2_ids_sha256": c.ids_sha256(ids),
            "reliability_ids_sha256": c.ids_sha256(reliability),
            "reliability_by_era": by_era(reliability, era),
            "annotators": {a: {"items": len(sheets[a]), "own_items": len(sheets[a]) - c.RELIABILITY_N,
                               "ids_sha256": c.ids_sha256(sheets[a]),
                               "own_by_era": by_era([i for i in sheets[a] if i not in reliability], era),
                               "workbook": final[a].name,
                               "workbook_sha256": c.file_sha256(tmp / final[a].name)} for a in c.ANNOTATORS},
            "tranche2_by_subreddit": {k: int(v) for k, v in key["subreddit"].value_counts().sort_index().items()},
            "subsystem_columns_in_workbooks": bool(c.INCLUDE_SUBSYSTEM_COLUMNS),
            "master_key": final["key"].name,
            "master_key_sha256": c.file_sha256(tmp / final["key"].name),
            "inputs": {"frame_sha256": c.FRAME_SHA256, "tranche1_ids_sha256": c.TRANCHE1_SHA256,
                       "calibration_ids_sha256": c.ids_sha256(calibration),
                       "eligible_ids_sha256": step1["eligible_ids_sha256"], "eligible_items": len(eligible),
                       "prefilter_input_sha256": step1["file_sha256"],
                       "deviation10_allocation_json_sha256": allocation_sha, "deviation10_gate_result": gate,
                       "prefilter_scores_used": False},
            "versions": c.versions(),
        }
        c.write_json(tmp / final["manifest"].name, manifest)
        m = manifest
        manifest_sha = c.file_sha256(tmp / final["manifest"].name)

        for p in final.values():                    # everything exists and was verified: move into place
            d.patiently(lambda p=p: (tmp / p.name).replace(p))
    except BaseException:
        shutil.rmtree(tmp, ignore_errors=True)
        left = [tmp] if tmp.exists() else []
        for p in final.values():                    # a failure part-way through the move leaves nothing behind
            try:
                d.patiently(lambda p=p: p.unlink(missing_ok=True), attempts=6)
            except OSError:
                left.append(p)
        if left:
            print("\nSTOPPED: writing the draw failed, and these could not be removed:")
            for p in left:
                print(f"  {p}")
            print("Delete them by hand without opening them, then run this step again. The draw is deterministic,")
            print("so the second run gives the same items.")
        else:
            print("\nSTOPPED: writing the draw failed; nothing was left behind. The draw is deterministic, so running")
            print("this step again after fixing the cause gives the same items.")
        raise
    shutil.rmtree(tmp, ignore_errors=True)

    print("\nwrote, in " + str(c.OUT_DIR) + ":")
    for a in c.ANNOTATORS:
        print(f"  {final[a].name}: {len(sheets[a])} items = {c.RELIABILITY_N} reliability + "
              f"{len(sheets[a]) - c.RELIABILITY_N} own")
    print(f"  {final['key'].name} (RESEARCHER ONLY)\n  {final['manifest'].name}")
    print("\n" + NOTICE)

    c.show_register_block(PASTE_STEP5, [
        f"- Tranche 2 (natural, Deviation 11) drawn {m['created']} by `tranche2_05_draw_natural.py`:",
        f"  500 items, {slashes(ALLOCATION)} by era, membership SHA-256",
        f"  `{m['tranche2_ids_sha256']}`.",
        f"- Reliability subset: 100 items, {slashes(m['reliability_by_era'])} by era, SHA-256",
        f"  `{m['reliability_ids_sha256']}`.",
        "- Sheets, by membership SHA-256:",
        *[f"  {a}, {m['annotators'][a]['items']} items, `{m['annotators'][a]['ids_sha256']}`"
          + (";" if a != c.ANNOTATORS[-1] else ".") for a in c.ANNOTATORS],
        f"- `tranche2_master_key.csv` SHA-256 `{m['master_key_sha256']}`;",
        f"  `tranche2_manifest.json` SHA-256 `{manifest_sha}`.",
        "  Neither file is committed to the repository. Both show which items are reliability items and are",
        "  not opened by the author until the three sheets are returned.",
        "- No pre-filter output was used. The Deviation 10 gate result was read from `tranche2_allocation.json`",
        f"  (SHA-256 `{allocation_sha}`): FAIL.",
        f"- Seed {c.SEED}, components {min(RNG_COMPONENT.values())} to {max(RNG_COMPONENT.values())}; "
        f"NumPy {np.__version__}; pandas {pd.__version__}.",
    ])
    print("\nSend each annotator only their own workbook, without opening B's or C's.")


if __name__ == "__main__":
    main()
