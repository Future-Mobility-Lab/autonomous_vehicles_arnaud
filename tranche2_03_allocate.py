"""Tranche 2, step 3: pre-filter hit rates on tranche 1, the allocation, and the gate.

Implements Deviation 5 as made precise by Deviation 10.

  Hit rates.  For each predicted label p (CONCERN, ENDORSEMENT, OTHER), the
              design-weighted share of tranche 1 items with each tranche 1 label c
              (N, CONCERN, ENDORSEMENT, OTHER), using the R1 weights in the tranche 1
              master key. The tranche 1 label is the gold label for reliability items
              (Deviation 2) and the single rating otherwise.

  Objective.  T_c  = tranche 1 count of class c (unweighted), c in the three classes.
              a_p  = items drawn with predicted label p; a_p >= 0, sum = 500,
                     a_p <= eligible items with predicted label p, and a_p = 0
                     where no tranche 1 item has predicted label p.
              F_c  = T_c + sum_p a_p * h[p][c]        (expected final count)
              Choose the allocation that maximises the smallest F_c; ties are
              broken by the larger second-smallest F_c, then the larger largest
              F_c, then the smaller a_CONCERN, then the smaller a_ENDORSEMENT.
              Expected counts are compared after rounding to six decimal places.
              Found by exhaustive enumeration of every allocation.

  Gate.       The draw goes ahead only if the smallest F_c is at least 200. A second
              natural tranche would be expected to leave the smallest class near 164,
              and a pre-filter unrelated to the labels gives about 178 on average
              (tranche2_gate_null_simulation.py). Below 200 this script stops and
              nothing is drawn under Deviation 10.

Nothing is drawn here. The allocation is a deterministic function of the
tranche 1 labels and the frozen pre-filter scores.

SEALED OUTPUT. The author is annotator A. So that no annotator knows the class
mix of tranche 2 while labelling it, this script displays checks, the gate result
and SHA-256 values only. The figures go to files in data/tranche2/ that stay
unopened until all three sheets are returned, their hashes are recorded and any
Deviation 2 adjudication is entered. --show prints them, for use after that.
"""
from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd

import tranche2_common as c
from tranche2_02_score_prefilter import (HYPOTHESES, LOGIT_COLS, MODEL_ID, RELEVANCE_THRESHOLD, derive)

CL = c.CLASSES


def load_scores(frame_ids: list[str], step1: dict) -> tuple[pd.DataFrame, dict]:
    if not c.PREFILTER_SCORES.exists() or not c.PREFILTER_SCORES_MANIFEST.exists():
        c.stop(f"put prefilter_scores.csv and prefilter_scores_manifest.json in {c.OUT_DIR} first (step 2).")
    man = c.read_json(c.PREFILTER_SCORES_MANIFEST)
    sha = c.file_sha256(c.PREFILTER_SCORES)
    if sha != man["output_sha256"]:
        c.stop("prefilter_scores.csv does not match the SHA-256 in its manifest. "
               "Copy the file again; do not open and re-save it in Excel.")
    if step1["file_sha256"] != man["input_sha256"]:
        c.stop("the scores were computed from a different prefilter_input.csv than the one step 1 wrote here.")
    spec_ok = (man.get("model") == MODEL_ID and man.get("hypotheses") == HYPOTHESES
               and float(man.get("relevance_threshold", -1)) == RELEVANCE_THRESHOLD
               and bool(man.get("model_commit_hash")))
    if not spec_ok and not c.ALLOW_OTHER_PREFILTER_SPEC:
        c.stop("the scores were not produced with the model, wording and threshold in the committed "
               "tranche2_02_score_prefilter.py, or the model commit was not recorded. Re-run step 2 with the committed file.")
    s = pd.read_csv(c.PREFILTER_SCORES, dtype={"id": str}, keep_default_na=False, encoding="utf-8")
    if set(s["id"]) != set(frame_ids) or len(s) != c.FRAME_N:
        c.stop("the scores file does not cover exactly the 12,166 frame items")
    again = derive(s[["id"] + LOGIT_COLS], threshold=float(man["relevance_threshold"]))
    if not (again["pred_label"].to_numpy() == s["pred_label"].to_numpy()).all():
        c.stop("predicted labels in the scores file cannot be re-derived from its own logits")
    if not np.allclose(again["p_relevant"], s["p_relevant"].astype(float), atol=2e-6):
        c.stop("p_relevant in the scores file cannot be re-derived from its own logits")
    print(f"scores: {len(s):,} items; file matches its manifest; predicted labels re-derived from the logits")
    print(f"        model {man['model']} at commit {man.get('model_commit_hash')}; "
          + ("model, wording and threshold match the committed script" if spec_ok
             else "NOT the committed specification (override in force)"))
    return s.set_index("id"), man


def _feasible(pool: np.ndarray, allowed: np.ndarray, total: int) -> np.ndarray:
    a0, a1 = np.meshgrid(np.arange(total + 1), np.arange(total + 1), indexing="ij")
    a0, a1 = a0.ravel(), a1.ravel()
    a2 = total - a0 - a1
    ok = a2 >= 0
    A = np.stack([a0[ok], a1[ok], a2[ok]], axis=1)
    return A[(A <= np.where(allowed, pool, 0)).all(axis=1)]


def leximin(T: np.ndarray, H: np.ndarray, pool: np.ndarray, allowed: np.ndarray, total: int):
    """Exhaustive search. T: (3,) tranche 1 counts. H: (3, 3) hit rates h[p][c] over the three classes.
    pool: (3,) eligible items by predicted label. allowed: (3,) bool. Returns (allocation, number examined)."""
    A = _feasible(pool, allowed, total)
    if len(A) == 0:
        return None, 0
    S = np.sort(np.round(T[None, :] + A @ H, 6), axis=1)        # ascending: smallest, middle, largest
    # np.lexsort sorts by the LAST key first; every key ascending, so negate what is maximised
    order = np.lexsort((A[:, 1], A[:, 0], -S[:, 2], -S[:, 1], -S[:, 0]))
    return A[order[0]], len(A)


def least_spread(T: np.ndarray, H: np.ndarray, pool: np.ndarray, allowed: np.ndarray, total: int):
    """For comparison only (never used for the draw): the allocation with the smallest gap between the
    largest and smallest expected final counts; ties by larger smallest count, then a_CONCERN, a_ENDORSEMENT."""
    A = _feasible(pool, allowed, total)
    S = np.sort(np.round(T[None, :] + A @ H, 6), axis=1)
    order = np.lexsort((A[:, 1], A[:, 0], -S[:, 0], np.round(S[:, 2] - S[:, 0], 6)))
    return A[order[0]]


def main() -> None:
    c.setup_console()
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true",
                    help="display the hit rates and the allocation (only once the files may be unsealed)")
    ap.add_argument("--force", action="store_true", help="overwrite an existing allocation that differs")
    args = ap.parse_args()
    print("Tranche 2, step 3: hit rates, allocation and gate\n")

    step1 = c.step1_manifest()
    frame_ids = c.load_frame()
    key, long, labels = c.load_tranche1()
    calibration = c.load_resolved_calibration(step1)
    scores, man = load_scores(frame_ids, step1)

    # ---- hit rates on tranche 1 --------------------------------------------------
    t1 = pd.DataFrame({"gold": labels, "pred": scores.loc[key.index, "pred_label"], "w": key["weight"]})
    raw = pd.crosstab(t1["pred"], t1["gold"]).reindex(index=c.LABELS, columns=c.LABELS, fill_value=0)
    wsum = t1.pivot_table(index="pred", columns="gold", values="w", aggfunc="sum", fill_value=0.0)
    wsum = wsum.reindex(index=c.LABELS, columns=c.LABELS, fill_value=0.0)
    row_tot = wsum.sum(axis=1)
    hit = wsum.div(row_tot.where(row_tot > 0), axis=0)          # NaN row where no tranche 1 item has predicted label p
    T = np.array([int((labels == k).sum()) for k in CL])

    y = (t1["gold"] != "N").to_numpy()
    p = (t1["pred"] != "N").to_numpy()
    w = t1["w"].to_numpy()
    prec = float((w * (y & p)).sum() / (w * p).sum()) if p.any() else float("nan")
    rec = float((w * (y & p)).sum() / (w * y).sum())

    # ---- pools and allocation ----------------------------------------------------
    eligible = c.eligible_ids(frame_ids, key.index, calibration, step1)
    pool_counts = scores.loc[eligible, "pred_label"].value_counts().reindex(c.LABELS, fill_value=0)
    allowed = np.array([row_tot[k] > 0 for k in CL])
    H = hit.loc[CL, CL].fillna(0.0).to_numpy()
    pool = pool_counts[CL].to_numpy()
    best, n_feasible = leximin(T.astype(float), H, pool, allowed, c.TRANCHE2_N)
    if best is None:
        c.stop(f"no allocation of {c.TRANCHE2_N} is possible: too few eligible items are predicted relevant with a "
               f"label that has a measured hit rate. Nothing is drawn under Deviation 10; record a further deviation.")
    a = {k: int(v) for k, v in zip(CL, best)}
    add = best @ H
    final = T + add
    exp_not_relevant = float(best @ hit.loc[CL, "N"].fillna(0.0).to_numpy())
    thin = [k for k in CL if allowed[CL.index(k)] and raw.loc[k].sum() < 20]
    unmeasured = [k for k in CL if not allowed[CL.index(k)]]
    # compared after rounding to six decimal places, like every expected count (Deviation 10)
    gate_pass = bool(round(float(final.min()), 6) >= c.GATE_MIN_EXPECTED_SMALLEST)
    alt = least_spread(T.astype(float), H, pool, allowed, c.TRANCHE2_N)
    alt_final = T + alt @ H

    payload = {
        "created": c.now_iso(),
        "rule": "Deviation 5 as specified by Deviation 10 (maximise the smallest expected final class count)",
        "gate": {"minimum_expected_smallest": c.GATE_MIN_EXPECTED_SMALLEST,
                 "expected_smallest": round(float(final.min()), 3), "result": "PASS" if gate_pass else "FAIL"},
        "tranche1_label_counts": {k: int((labels == k).sum()) for k in c.LABELS},
        "tranche1_by_predicted_and_gold_raw": {p_: {g: int(raw.at[p_, g]) for g in c.LABELS} for p_ in c.LABELS},
        "hit_rates_design_weighted": {p_: {g: (None if pd.isna(hit.at[p_, g]) else round(float(hit.at[p_, g]), 6))
                                           for g in c.LABELS} for p_ in c.LABELS},
        "stage1_prefilter_on_tranche1": {"precision": round(prec, 6), "recall": round(rec, 6)},
        "eligible_items": len(eligible),
        "eligible_by_predicted_label": {k: int(pool_counts[k]) for k in c.LABELS},
        "allocations_examined": int(n_feasible),
        "allocation": a,
        "inclusion_probability_by_predicted_label": {
            k: (round(a[k] / int(pool_counts[k]), 6) if pool_counts[k] else None) for k in CL},
        "expected_final_counts": {k: round(float(v), 3) for k, v in zip(CL, final)},
        "expected_not_relevant": round(exp_not_relevant, 3),
        "predicted_labels_with_no_tranche1_items": unmeasured,
        "predicted_labels_with_fewer_than_20_tranche1_items": thin,
        "comparison_only_least_spread": {"allocation": {k: int(v) for k, v in zip(CL, alt)},
                                         "expected_final_counts": {k: round(float(v), 3) for k, v in zip(CL, alt_final)}},
        "inputs": {
            "frame_sha256": c.FRAME_SHA256,
            "scores_sha256": man["output_sha256"],
            "scores_manifest_sha256": c.file_sha256(c.PREFILTER_SCORES_MANIFEST),
            "model": man["model"], "model_commit_hash": man.get("model_commit_hash"),
            "hypotheses": man["hypotheses"], "relevance_threshold": man["relevance_threshold"],
            "tranche1_labels_sha256": c.TRANCHE1_LABELS_SHA256,
            "tranche1_files": c.tranche1_file_hashes(verbose=False),
            "calibration_ids_sha256": c.ids_sha256(calibration), "calibration_ids": len(calibration),
            "eligible_ids_sha256": step1["eligible_ids_sha256"],
        },
        "versions": c.versions(),
    }

    write = True
    if c.ALLOCATION_JSON.exists():
        old = c.read_json(c.ALLOCATION_JSON)
        same = (old.get("allocation") == a and old["inputs"]["scores_sha256"] == man["output_sha256"]
                and old.get("eligible_by_predicted_label") == payload["eligible_by_predicted_label"]
                and old["inputs"].get("eligible_ids_sha256") == step1["eligible_ids_sha256"])
        if same:
            write = False
            print(f"\n{c.ALLOCATION_JSON.name} already exists and this run reproduces it exactly; left unchanged.")
        elif not args.force:
            c.stop(f"{c.ALLOCATION_JSON.name} exists and differs from this result. A frozen allocation is not "
                   f"overwritten silently: record why, then rerun with --force.")
    if write:
        c.write_json(c.ALLOCATION_JSON, payload)
        out = raw.add_prefix("n_gold_").join(hit.round(6).add_prefix("h_gold_"))
        out.index.name = "predicted_label"
        out.to_csv(c.HIT_RATES_CSV, encoding="utf-8", lineterminator="\n")
    alloc_sha = c.file_sha256(c.ALLOCATION_JSON)

    # ---- register text: figures (sealed) -----------------------------------------
    hr = lambda p_, g: ("n/a" if pd.isna(hit.at[p_, g]) else f"{100 * hit.at[p_, g]:.1f}%")
    figures = [
        "### Tranche 2 allocation: measured figures",
        "",
        "Unsealed under the Blinding clause of Deviation 10. Produced by `tranche2_03_allocate.py`;",
        "the file hashes were recorded before the draw.",
        "",
        "- Tranche 1 items by predicted label: " + ", ".join(f"{k} {int(raw.loc[k].sum())}" for k in c.LABELS) + ".",
        "- Design-weighted hit rates: the share of tranche 1 items with each predicted label whose",
        "  tranche 1 label is CONCERN / ENDORSEMENT / OTHER / not relevant:",
    ]
    for k in CL:
        figures.append(f"    - predicted {k}: {hr(k, 'CONCERN')} / {hr(k, 'ENDORSEMENT')} / {hr(k, 'OTHER')} / "
                       f"{hr(k, 'N')} ({int(raw.loc[k].sum())} items)")
    figures += [
        f"- Stage 1 pre-filter against the tranche 1 labels, design-weighted: precision {100 * prec:.1f}%, "
        f"recall {100 * rec:.1f}%.",
        f"- Eligible items: {len(eligible):,}; by predicted label "
        + ", ".join(f"{k} {int(pool_counts[k]):,}" for k in c.LABELS) + ".",
        f"- Allocations examined: {n_feasible:,}.",
        "- Allocation on predicted label: " + ", ".join(f"{k} {a[k]}" for k in CL) + f" (sum {sum(a.values())}).",
        "- Expected final counts: " + ", ".join(f"{k} {final[j]:.1f}" for j, k in enumerate(CL))
        + f"; expected not relevant among the 500: {exp_not_relevant:.1f}.",
        f"- Gate: expected smallest final count {final.min():.1f} against the minimum of "
        f"{c.GATE_MIN_EXPECTED_SMALLEST}: {'PASS' if gate_pass else 'FAIL'}.",
        "- For comparison only, the least-spread allocation: " + ", ".join(f"{k} {int(alt[j])}" for j, k in enumerate(CL))
        + ", with expected final counts " + ", ".join(f"{k} {alt_final[j]:.1f}" for j, k in enumerate(CL)) + ".",
    ]
    if unmeasured:
        figures.append("- No tranche 1 item had predicted label " + ", ".join(unmeasured)
                       + ", so it had no measurable hit rate and received no allocation.")
    if thin:
        figures.append("- The hit rate rests on fewer than 20 tranche 1 items for predicted label " + ", ".join(thin) + ".")
    with open(c.SEALED_ALLOCATION_TEXT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(figures) + "\n")

    # ---- what is shown now: the gate and hashes, nothing else ------------------------
    print(f"\ngate (expected smallest final class count at least {c.GATE_MIN_EXPECTED_SMALLEST}): "
          + ("PASS" if gate_pass else "FAIL"))
    print("\n" + c.SEALED_NOTICE)

    if args.show:
        print("\n" + "-" * 78 + "\n--show: measured figures\n" + "-" * 78)
        print("tranche 1 items by predicted label (rows) and tranche 1 label (columns):")
        print(raw.assign(total=raw.sum(axis=1)).to_string())
        print("\ndesign-weighted hit rates h[p][c]:")
        print(hit.round(4).to_string())
        print()
        print(pd.DataFrame({"tranche1_count": T, "allocated_on_predicted_label": best,
                            "expected_added": np.round(add, 1), "expected_final": np.round(final, 1)},
                           index=CL).to_string())
        print(f"expected not relevant among the {c.TRANCHE2_N}: {exp_not_relevant:.1f}")

    c.show_register_block(c.PASTE_STEP3, [
        f"- Pre-filter run: `{man['model']}` at commit `{man.get('model_commit_hash')}`; {man['rows']:,} frame items",
        f"  scored; `prefilter_scores.csv` SHA-256 `{man['output_sha256']}`.",
        f"- Allocation computed by `tranche2_03_allocate.py`; `tranche2_allocation.json` SHA-256",
        f"  `{alloc_sha}`.",
        f"- Gate (expected smallest final class count at least {c.GATE_MIN_EXPECTED_SMALLEST}): "
        + ("PASS." if gate_pass else "FAIL. Nothing is drawn under Deviation 10."),
        "- Hit rates and allocation sealed under the Blinding clause of Deviation 10.",
    ])
    if not gate_pass:
        print("\nSTOPPED: the gate failed. Step 4 will not draw. Record the result above, then record what replaces")
        print("tranche 2 as a further deviation before anything is drawn. Keep the files sealed.")
        sys.exit(1)
    print("\nNext: commit that entry, then run  python tranche2_04_draw.py")


if __name__ == "__main__":
    main()
