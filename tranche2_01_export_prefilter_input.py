"""Tranche 2, step 1: check every input and export the pre-filter input file.

Checks, in order:
  - the frozen draw frame against R5 (12,166 ids and the membership hash);
  - corpus v2.2 (membership hash when the file is the full corpus; every frame id present);
  - the completed tranche 1 sheets and master key (structure, vocabulary, and every
    item's label against the recorded fingerprint);
  - that the corpus text is the text the tranche 1 annotators were shown, and that the
    subreddit and era columns agree with the tranche 1 key;
  - the calibration ids: every one must be found in the corpus, in the same form.

Writes, in data/tranche2/:
  prefilter_input.csv            id and text for all 12,166 frame items. This is the only
                                 file the scoring step needs, and the text in it is the
                                 text the annotators will be shown.
  calibration_ids_resolved.txt   the validated calibration ids, used by steps 3 and 4.
  prefilter_input_manifest.json  hashes of both, and of the eligible items.

Nothing is drawn, scored or estimated here. It is safe to run more than once.
"""
from __future__ import annotations

import csv

import pandas as pd

import tranche2_common as c


def main() -> None:
    c.setup_console()
    print("Tranche 2, step 1: input checks and pre-filter input\n")

    frame_ids = c.load_frame()
    corpus, corpus_ids = c.load_corpus(frame_ids)
    key, long, labels = c.load_tranche1()
    t1_files = c.tranche1_file_hashes()
    text_check = c.check_text_against_tranche1(corpus, long)

    # the corpus columns, checked against the tranche 1 key
    sub = dict(zip(corpus["id"], corpus["subreddit"]))
    era = dict(zip(corpus["id"], corpus["era"]))
    t1 = set(key.index)
    if not t1 <= set(frame_ids):
        c.stop("some tranche 1 ids are not in the frame")
    sub_ok = sum(sub[i].lower() == key.at[i, "subreddit"].lower() for i in key.index)
    era_ok = sum(era[i] == key.at[i, "era"] for i in key.index)
    print(f"subreddit agrees with the tranche 1 key for {sub_ok}/500 items; era agrees for {era_ok}/500")
    if sub_ok < 450:
        c.stop("the subreddit column does not agree with the tranche 1 key. Set COL_SUBREDDIT in the CONFIGURATION block.")
    if era_ok < 450:
        c.stop("the creation-time column does not agree with the tranche 1 key (wrong column, for example a scrape "
               "time). Set COL_CREATED in the CONFIGURATION block.")
    if sub_ok < 500 or era_ok < 500:
        print("  NOTE: a few items differ. These columns are descriptive in tranche 2 (the draw does not use them).")

    calibration = c.resolve_calibration(frame_ids, corpus_ids)
    overlap = t1 & set(calibration)
    if overlap:
        c.stop(f"{len(overlap)} calibration ids are also tranche 1 ids; the two sets are recorded as disjoint")
    eligible = c.eligible_ids(frame_ids, t1, calibration)
    in_frame = len(set(calibration) & set(frame_ids))
    print(f"eligible for tranche 2: {len(eligible):,} = {c.FRAME_N:,} frame - {len(t1)} tranche 1 - {in_frame} calibration")

    # every frame comment must fit in a workbook cell: checked now, before anything is committed
    # or drawn, because the draw is made once and no drawn item may be replaced
    longest = int(corpus["text"].map(c.excel_len).max())
    if longest > c.EXCEL_CELL_LIMIT:
        too_long = corpus.loc[corpus["text"].map(c.excel_len) > c.EXCEL_CELL_LIMIT, "id"].tolist()
        c.stop(f"{len(too_long)} frame comment(s) are longer than a workbook cell can hold "
               f"({c.EXCEL_CELL_LIMIT:,} characters): {too_long[:10]}. Record how they are handled before the draw.")
    print(f"longest comment: {longest:,} characters (a workbook cell holds {c.EXCEL_CELL_LIMIT:,})")

    # write and read back
    c.OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = corpus[["id", "text"]].sort_values("id").reset_index(drop=True)
    out.to_csv(c.PREFILTER_INPUT, index=False, encoding="utf-8", lineterminator="\n", quoting=csv.QUOTE_ALL)
    back = pd.read_csv(c.PREFILTER_INPUT, dtype=str, keep_default_na=False, encoding="utf-8")
    if back["id"].tolist() != out["id"].tolist() or back["text"].tolist() != out["text"].tolist():
        bad = [i for i, a, b in zip(out["id"], out["text"], back["text"]) if a != b][:5]
        c.stop(f"the pre-filter input does not read back as written (first ids: {bad}). Nothing further was written.")
    with open(c.CALIBRATION_RESOLVED, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(calibration) + "\n")

    words = out["text"].str.split().str.len()
    manifest = {
        "created": c.now_iso(),
        "file": c.PREFILTER_INPUT.name,
        "file_sha256": c.file_sha256(c.PREFILTER_INPUT),
        "rows": int(len(out)),
        "ids_sha256": c.ids_sha256(out["id"]),
        "text_column": c.COL_TEXT,
        "items_with_control_characters_removed": int(corpus["text_altered"].sum()),
        "words_per_comment": {"mean": round(float(words.mean()), 1), "median": float(words.median()),
                              "max": int(words.max())},
        "text_check_against_tranche1_sheets": text_check,
        "tranche1_label_counts": {k: int((labels == k).sum()) for k in c.LABELS},
        "tranche1_labels_sha256": c.TRANCHE1_LABELS_SHA256,
        "tranche1_files": t1_files,
        "calibration_ids": len(calibration),
        "calibration_ids_in_frame": in_frame,
        "calibration_ids_sha256": c.ids_sha256(calibration),
        "eligible_for_tranche2": len(eligible),
        "eligible_ids_sha256": c.ids_sha256(eligible),
        "versions": c.versions(),
    }
    c.write_json(c.PREFILTER_INPUT_MANIFEST, manifest)

    print(f"\nwrote {c.PREFILTER_INPUT}  ({len(out):,} rows; reads back identically)")
    print(f"      SHA-256 {manifest['file_sha256']}")
    if manifest["items_with_control_characters_removed"]:
        print(f"      control characters removed from {manifest['items_with_control_characters_removed']} comment(s); "
              f"the model and the annotators get the same cleaned text")
    print("\nAll input checks passed. Next: step 2 (scoring), on a GPU:")
    print("  python tranche2_02_score_prefilter.py --input prefilter_input.csv --output prefilter_scores.csv")
    print(f"then put prefilter_scores.csv and prefilter_scores_manifest.json in {c.OUT_DIR}")


if __name__ == "__main__":
    main()
