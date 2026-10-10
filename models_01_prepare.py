"""Model comparison, step 1 (on the PC): gold labels, fold files and the inputs of the model runs.

Run from the repository folder, with the virtual environment active:
    python models_01_prepare.py

It reads the files of record, each checked against its recorded SHA-256, forms the gold
labels of both tranches by the committed rules, assigns the folds and writes the inputs of
the model runs. It runs no model and sets no prediction against a label.

Rules (docs/analysis_preregistration.md):
  - gold Stage 1 and Stage 2 labels: Deviation 2 (majority of three; the author's
    adjudications recorded on 10 October 2026), with the missing-rating rules of Deviation 11;
  - gold primary subsystem: Deviation 7, with Deviation 11 for missing ratings;
  - folds: R5 and Deviation 12, within each tranche, on the four-way gold label.

Writes:
  splits/tranche1_folds.csv, splits/tranche2_folds.csv   id and fold only; these are committed
  data/models/gold_labels.csv                           gold labels of both tranches
  data/models/zero_shot_input.csv                       id and text of the 1,000 annotated items
  data/models/finetune_input.csv                        id, tranche, subreddit, text, labels, fold
  data/models/prepare_manifest.json
  data/models/PASTE_models_prepare_block.txt            the register lines (hashes only)
"""
from __future__ import annotations

import re
from collections import Counter

import numpy as np
import pandas as pd

import models_common as mc
import models_config as cfg

TRANCHE1_SHEET_COLUMNS = ["row", "id", "subreddit", "comment", "stage1_relevant", "stage2_class", "skip", "notes"]
TRANCHE2_SHEET_COLUMNS = ["row", "id", "subreddit", "comment", "stage1_relevant", "stage2_class", "subsystem",
                          "subsystem_secondary", "skip", "notes"]
SUBSYSTEM_SHEET_COLUMNS = ["row", "id", "subreddit", "comment", "stage2_class", "subsystem", "subsystem_secondary",
                           "notes"]


# =============================================================================
# reading
# =============================================================================
def cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        if np.isnan(value):
            return ""
        if value.is_integer():
            return str(int(value))
    return str(value).strip()


def read_sheet(path, columns: list[str], what: str) -> pd.DataFrame:
    df = pd.read_excel(path, dtype=object, keep_default_na=False)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in columns if c not in df.columns]
    if missing:
        mc.stop(f"{what} lacks the columns {missing} ({path})")
    out = pd.DataFrame({c: [cell(v) for v in df[c].tolist()] for c in columns})
    return out[out["id"] != ""].reset_index(drop=True)


def read_key(path, what: str) -> pd.DataFrame:
    key = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    key.columns = [str(c).strip() for c in key.columns]
    need = {"id", "subreddit", "is_reliability", "assigned_to"}
    if not need <= set(key.columns):
        mc.stop(f"{what} lacks the columns {sorted(need - set(key.columns))}")
    key = key.assign(**{c: key[c].str.strip() for c in ["id", "subreddit", "is_reliability", "assigned_to"]})
    rel = key["is_reliability"].str.lower().map({"true": True, "false": False})
    if rel.isna().any():
        mc.stop(f"{what}: is_reliability must be True or False")
    key["is_reliability"] = rel.astype(bool)
    if key["id"].duplicated().any():
        mc.stop(f"{what} has duplicate ids")
    return key.set_index("id")


def check_files_of_record() -> None:
    files = {f"tranche1_annotator_{a}": cfg.TRANCHE1_SHEETS[a] for a in cfg.ANNOTATORS}
    files["tranche1_master_key"] = cfg.TRANCHE1_KEY
    files.update({f"tranche1_subsystem_{a}": cfg.TRANCHE1_SUBSYSTEM_SHEETS[a] for a in cfg.ANNOTATORS})
    files.update({f"tranche2_annotator_{a}": cfg.TRANCHE2_SHEETS[a] for a in cfg.ANNOTATORS})
    problems = []
    for name, path in files.items():
        if not path.exists():
            problems.append(f"{name}: not found at {path}")
            continue
        got = mc.sha256_file(path)
        want = cfg.RECORDED_SHA256[name]
        if got != want:
            problems.append(f"{name}: SHA-256 {got[:8]}... is not the recorded {want[:8]}... ({path.name})")
    for path, what in ((cfg.TRANCHE2_KEY, "tranche 2 master key"), (cfg.PREFILTER_INPUT, "pre-filter input"),
                       (cfg.PREFILTER_INPUT_MANIFEST, "pre-filter input manifest")):
        if not path.exists():
            problems.append(f"{what}: not found at {path}")
    if not problems:
        got = mc.sha256_file(cfg.PREFILTER_INPUT)
        if got != cfg.PREFILTER_INPUT_SHA256:
            problems.append(f"prefilter_input.csv: SHA-256 {got[:8]}... is not the {cfg.PREFILTER_INPUT_SHA256[:8]}... "
                            f"printed when it was exported on 4 October 2026")
    if problems:
        mc.stop("the files of record are not all in place:\n  " + "\n  ".join(problems))
    print("files of record: all ten match their recorded SHA-256; the tranche 2 key is present")
    print(f"comment text: prefilter_input.csv matches the SHA-256 printed by its export on 4 October 2026 "
          f"({cfg.PREFILTER_INPUT_SHA256[:16]}...)")


def check_fold_libraries() -> None:
    import sklearn
    found = {"scikit-learn": sklearn.__version__, "numpy": np.__version__}
    if found != cfg.FOLD_LIBRARY_VERSIONS:
        want = cfg.FOLD_LIBRARY_VERSIONS
        mc.stop(f"R5 fixes scikit-learn {want['scikit-learn']} and NumPy {want['numpy']} for the folds; found "
                f"scikit-learn {found['scikit-learn']} and NumPy {found['numpy']}.\n"
                f"  Install them with:  python -m pip install scikit-learn=={want['scikit-learn']} "
                f"numpy=={want['numpy']}\n  then run this step again.")
    print(f"fold libraries: scikit-learn {found['scikit-learn']}, NumPy {found['numpy']} (as R5 fixes)")


# =============================================================================
# ratings
# =============================================================================
def validate_ratings(df: pd.DataFrame, sheet: str, with_subsystem: bool) -> list[str]:
    problems = []
    for r in df.itertuples(index=False):
        tag = f"{sheet} row {r.row} ({r.id})"
        skip = r.skip.upper()
        if skip not in ("", "Y"):
            problems.append(f"{tag}: skip={r.skip!r}")
        if skip == "Y":
            continue                                      # a skipped rating is missing (Deviation 11)
        if r.stage1_relevant not in ("Y", "N", ""):
            problems.append(f"{tag}: stage1_relevant={r.stage1_relevant!r}")
        if r.stage1_relevant in ("N", "") and r.stage2_class != "":
            problems.append(f"{tag}: a Stage 2 class without Stage 1 = Y")
        if r.stage1_relevant == "Y" and r.stage2_class not in cfg.CLASSES + [""]:
            problems.append(f"{tag}: stage2_class={r.stage2_class!r}")
        if with_subsystem:
            if r.stage1_relevant != "Y" and (r.subsystem or r.subsystem_secondary):
                problems.append(f"{tag}: a subsystem without Stage 1 = Y")
            if r.subsystem not in cfg.PRIMARY_SUBSYSTEMS + [""]:
                problems.append(f"{tag}: subsystem={r.subsystem!r}")
            if r.subsystem_secondary not in cfg.SUBSYSTEMS + [""]:
                problems.append(f"{tag}: subsystem_secondary={r.subsystem_secondary!r}")
            if r.subsystem_secondary and (not r.subsystem or r.subsystem_secondary == r.subsystem):
                problems.append(f"{tag}: secondary subsystem without a different primary")
    return problems


def label4(s1: str, s2: str) -> str:
    """Four-way label of one rating; '' when the rating is missing."""
    if s1 == "N":
        return "N"
    if s1 == "Y":
        return s2 if s2 else cfg.NO_STAGE2
    return ""


def load_tranche(tranche: int):
    """Return (key, ratings) for one tranche. ratings: one row per (id, annotator)."""
    if tranche == 1:
        key = read_key(cfg.TRANCHE1_KEY, "tranche 1 master key")
        if mc.ids_sha256(key.index) != cfg.TRANCHE1_IDS_SHA256:
            mc.stop("the tranche 1 master key does not hold the 500 tranche 1 ids")
        sheets, columns = cfg.TRANCHE1_SHEETS, TRANCHE1_SHEET_COLUMNS
    else:
        key = read_key(cfg.TRANCHE2_KEY, "tranche 2 master key")
        if mc.ids_sha256(key.index) != cfg.TRANCHE2_IDS_SHA256:
            mc.stop("the tranche 2 master key does not hold the 500 tranche 2 ids recorded at c7edc7f")
        if mc.ids_sha256(key.index[key["is_reliability"]]) != cfg.TRANCHE2_RELIABILITY_IDS_SHA256:
            mc.stop("the tranche 2 master key does not mark the 100 reliability items recorded at c7edc7f")
        sheets, columns = cfg.TRANCHE2_SHEETS, TRANCHE2_SHEET_COLUMNS
    frames, problems = [], []
    for a in cfg.ANNOTATORS:
        df = read_sheet(sheets[a], columns, f"tranche {tranche} sheet {a}")
        if df["id"].duplicated().any():
            mc.stop(f"tranche {tranche} sheet {a} lists an id twice")
        if tranche == 2 and mc.ids_sha256(df["id"]) != cfg.TRANCHE2_SHEET_IDS_SHA256[a]:
            mc.stop(f"tranche 2 sheet {a} does not hold the items recorded for it at c7edc7f")
        if tranche == 1:
            df["subsystem"], df["subsystem_secondary"] = "", ""
        problems += validate_ratings(df, f"tranche {tranche} sheet {a}", with_subsystem=(tranche == 2))
        df["annotator"] = a
        frames.append(df)
    if problems:
        mc.stop(f"tranche {tranche} sheets fail validation:\n  " + "\n  ".join(problems[:30]))
    long = pd.concat(frames, ignore_index=True)
    rel_ids = set(key.index[key["is_reliability"]])
    who = long.groupby("id")["annotator"].agg(lambda s: "".join(sorted(s)))
    if set(who.index) != set(key.index):
        mc.stop(f"the ids in the tranche {tranche} sheets are not the ids of the master key")
    for i, w in who.items():
        if i in rel_ids and w != "ABC":
            mc.stop(f"tranche {tranche} reliability item {i} is not in all three sheets")
        if i not in rel_ids and w != key.at[i, "assigned_to"]:
            mc.stop(f"tranche {tranche} item {i} is assigned to {key.at[i, 'assigned_to']!r} but is in sheet(s) {w}")
    texts = long.groupby("id")["subreddit"].nunique()
    if (texts > 1).any():
        mc.stop(f"tranche {tranche}: a shared item shows different subreddits in different sheets")
    sub_key = key["subreddit"].str.replace(r"^/?r/", "", regex=True).str.lower()
    sub_sheet = long.groupby("id")["subreddit"].first().str.replace(r"^/?r/", "", regex=True).str.lower()
    if (sub_key.reindex(sub_sheet.index) != sub_sheet).any():
        mc.stop(f"tranche {tranche}: the sheets and the master key disagree on a subreddit")
    long["missing"] = (long["skip"].str.upper() == "Y") | (long["stage1_relevant"] == "")
    long["label4"] = [("" if m else label4(s1, s2)) for m, s1, s2 in
                      zip(long["missing"], long["stage1_relevant"], long["stage2_class"])]
    long["is_reliability"] = long["id"].isin(rel_ids)
    return key, long


def attach_tranche1_subsystems(long: pd.DataFrame) -> pd.DataFrame:
    """Copy the tranche 1 subsystem retrofit labels onto the ratings (same annotator, same item)."""
    long = long.copy()
    problems = []
    for a in cfg.ANNOTATORS:
        sub = read_sheet(cfg.TRANCHE1_SUBSYSTEM_SHEETS[a], SUBSYSTEM_SHEET_COLUMNS, f"tranche 1 subsystem sheet {a}")
        if sub["id"].duplicated().any():
            mc.stop(f"tranche 1 subsystem sheet {a} lists an id twice")
        mine = long[(long["annotator"] == a)]
        relevant = set(mine.loc[mine["stage1_relevant"] == "Y", "id"])
        if set(sub["id"]) != relevant:
            mc.stop(f"tranche 1 subsystem sheet {a} does not hold exactly the items {a} coded relevant "
                    f"({len(set(sub['id']) - relevant)} extra, {len(relevant - set(sub['id']))} missing)")
        cls = dict(zip(mine["id"], mine["stage2_class"]))
        for r in sub.itertuples(index=False):
            tag = f"tranche 1 subsystem sheet {a} row {r.row} ({r.id})"
            if r.stage2_class != cls[r.id]:
                problems.append(f"{tag}: class {r.stage2_class!r} differs from the tranche 1 sheet ({cls[r.id]!r})")
            if r.subsystem not in cfg.PRIMARY_SUBSYSTEMS + [""]:
                problems.append(f"{tag}: subsystem={r.subsystem!r}")
            if r.subsystem_secondary not in cfg.SUBSYSTEMS + [""]:
                problems.append(f"{tag}: subsystem_secondary={r.subsystem_secondary!r}")
            if r.subsystem_secondary and (not r.subsystem or r.subsystem_secondary == r.subsystem):
                problems.append(f"{tag}: secondary subsystem without a different primary")
        idx = long.index[long["annotator"] == a]
        prim = dict(zip(sub["id"], sub["subsystem"]))
        sec = dict(zip(sub["id"], sub["subsystem_secondary"]))
        long.loc[idx, "subsystem"] = [prim.get(i, "") for i in long.loc[idx, "id"]]
        long.loc[idx, "subsystem_secondary"] = [sec.get(i, "") for i in long.loc[idx, "id"]]
    if problems:
        mc.stop("tranche 1 subsystem sheets fail validation:\n  " + "\n  ".join(problems[:30]))
    return long


# =============================================================================
# gold labels
# =============================================================================
def gold_stage(labels: list[str], reliability: bool):
    """(gold label4 or '', status) from the non-missing four-way ratings of one item."""
    if not labels:
        return "", "no rating"
    if not reliability or len(labels) == 1:
        return labels[0], "single rating"                     # Deviation 11: one rating -> that rating
    if len(labels) == 2:                                      # Deviation 11: two ratings
        a, b = labels
        if a == b:
            return a, "two ratings agree"
        if a != "N" and b != "N":
            return cfg.NO_STAGE2, "two ratings agree at Stage 1 only"
        return "", "two ratings differ at Stage 1"
    yes = [x for x in labels if x != "N"]                     # Deviation 2: three ratings
    if len(yes) < 2:
        return "N", "majority"
    classes = [x for x in yes if x != cfg.NO_STAGE2]
    top = Counter(classes).most_common(1)
    if top and top[0][1] >= 2:
        return top[0][0], "majority"
    return None, "split"                                       # resolved by the author, never by code


def form_gold(tranche: int, key: pd.DataFrame, long: pd.DataFrame) -> pd.DataFrame:
    adj_s2 = cfg.ADJUDICATED_STAGE2 if tranche == 2 else {}
    adj_sub = cfg.ADJUDICATED_SUBSYSTEM if tranche == 2 else {}
    rows, splits_s2, splits_sub, notes = [], {}, {}, []
    for i in sorted(key.index):
        g = long[(long["id"] == i) & (~long["missing"])]
        rel = bool(key.at[i, "is_reliability"])
        labels = g["label4"].tolist()
        gold, status = gold_stage(labels, rel)
        raw = gold
        adjudicated = ""
        if gold is None:
            yes = sorted({x for x in labels if x not in ("N", cfg.NO_STAGE2)})
            splits_s2[i] = labels
            if i not in adj_s2:
                gold = None
            else:
                choice = adj_s2[i]
                if choice not in cfg.CLASSES:
                    mc.stop(f"the adjudicated class of {i} is not a class: {choice!r}")
                if labels.count("N") == 1 and choice not in yes:
                    mc.stop(f"{i}: Deviation 2 limits the author to the classes given ({yes}); found {choice!r}")
                if choice not in yes:
                    notes.append(f"{i}: adjudicated Stage 2 class {choice} was given by no annotator")
                gold, adjudicated, raw = choice, "Y", ""
        rows.append({"id": i, "tranche": tranche, "item": "reliability" if rel else "own",
                     "n_ratings": len(labels), "label4": gold, "label4_raw_majority": raw,
                     "stage2_adjudicated": adjudicated, "stage_status": status})
    unresolved = [i for i in splits_s2 if i not in adj_s2]
    stale = [i for i in adj_s2 if i not in splits_s2]
    if unresolved or stale:
        mc.stop(f"tranche {tranche} Stage 2 adjudication does not match the splits: needing a decision "
                f"{unresolved}; decided but not a split {stale}")
    gold = pd.DataFrame(rows).set_index("id")
    gold["gold_stage1"] = gold["label4"].map(lambda x: "" if x in ("", None) else ("N" if x == "N" else "Y"))
    gold["gold_stage2"] = gold["label4"].map(lambda x: x if x in cfg.CLASSES else "")

    # primary subsystem (Deviation 7, with Deviation 11 for missing ratings)
    sub_gold, sub_n, sub_adj, sub_given, sub_status = {}, {}, {}, {}, {}
    for i in gold.index:
        if gold.at[i, "gold_stage1"] != "Y":
            continue
        g = long[(long["id"] == i) & (~long["missing"]) & (long["stage1_relevant"] == "Y") & (long["subsystem"] != "")]
        given = g["subsystem"].tolist()
        sub_n[i] = len(given)
        if not given:
            sub_status[i] = "no label"
            continue
        if len(given) == 1:
            sub_gold[i], sub_status[i] = given[0], "single label"
            continue
        top, n = Counter(given).most_common(1)[0]
        if n >= 2:
            sub_gold[i] = top
            sub_status[i] = "unanimous" if n == len(given) else "majority"
            continue
        splits_sub[i] = given
        if i in adj_sub:
            choice = adj_sub[i]
            if choice not in cfg.PRIMARY_SUBSYSTEMS:
                mc.stop(f"the adjudicated subsystem of {i} is not a subsystem: {choice!r}")
            sub_gold[i], sub_adj[i], sub_status[i] = choice, "Y", "adjudicated"
            sub_given[i] = "Y" if choice in given else "N"
            if choice not in given:
                notes.append(f"{i}: adjudicated subsystem {choice} was given by no annotator")
    unresolved = [i for i in splits_sub if i not in adj_sub]
    stale = [i for i in adj_sub if i not in splits_sub]
    if unresolved or stale:
        mc.stop(f"tranche {tranche} subsystem adjudication does not match the splits: needing a decision "
                f"{unresolved}; decided but not a split {stale}")
    gold["gold_subsystem"] = [sub_gold.get(i, "") for i in gold.index]
    gold["n_subsystem_labels"] = [sub_n.get(i, 0) for i in gold.index]
    gold["subsystem_status"] = [sub_status.get(i, "") for i in gold.index]
    gold["subsystem_adjudicated"] = [sub_adj.get(i, "") for i in gold.index]
    gold["adjudicated_subsystem_given_by_an_annotator"] = [sub_given.get(i, "") for i in gold.index]
    gold["label4"] = gold["label4"].fillna("")
    gold.attrs["notes"] = notes
    return gold


def check_tranche1(gold: pd.DataFrame) -> None:
    single = gold["label4"].to_dict()
    counts = {k: int((gold["label4"] == k).sum()) for k in cfg.LABEL4}
    if counts != cfg.TRANCHE1_LABEL_COUNTS or mc.pairs_sha256(single) != cfg.TRANCHE1_LABELS_SHA256:
        mc.stop(f"the tranche 1 labels are not those recorded (counts {counts}); restore the files of 26 September")
    rel = gold[(gold["item"] == "reliability") & (gold["n_subsystem_labels"] >= 2)]
    found = {"two_or_more_labels": len(rel), "unanimous": int((rel["subsystem_status"] == "unanimous").sum()),
             "two_to_one": int((rel["subsystem_status"] == "majority").sum())}
    if found != cfg.TRANCHE1_SUBSYSTEM_RELIABILITY:
        mc.stop(f"tranche 1 subsystem gold does not match Deviation 7: found {found}, "
                f"recorded {cfg.TRANCHE1_SUBSYSTEM_RELIABILITY}")
    print(f"tranche 1: labels match the recorded fingerprint {counts}; subsystem gold matches Deviation 7 "
          f"({found['two_or_more_labels']} items with two or more labels: {found['unanimous']} unanimous, "
          f"{found['two_to_one']} two to one)")


# =============================================================================
# folds
# =============================================================================
def assign_folds(gold: pd.DataFrame) -> dict:
    from sklearn.model_selection import StratifiedKFold
    ids = sorted(i for i in gold.index if gold.at[i, "label4"] != "")
    y = np.array([gold.at[i, "label4"] for i in ids])
    stage1_only = [i for i in ids if gold.at[i, "label4"] == cfg.NO_STAGE2]
    if stage1_only:                                       # not one of the four strata of Deviation 12
        mc.stop(f"{len(stage1_only)} items have a gold Stage 1 label but no Stage 2 label (e.g. {stage1_only[:5]}); "
                f"Deviation 12 stratifies on four labels. Take this message to Claude.")
    skf = StratifiedKFold(n_splits=cfg.N_FOLDS, shuffle=True, random_state=cfg.SEED)
    fold = {}
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)          # a stratum smaller than five is allowed
        for k, (_, test) in enumerate(skf.split(np.zeros((len(ids), 1)), y), start=1):
            for j in test:
                fold[ids[j]] = k
    return fold


def write_fold_file(path, fold: dict) -> tuple[str, str]:
    content = "id,fold\n" + "".join(f"{i},{fold[i]}\n" for i in sorted(fold))
    data = content.encode("utf-8")
    if path.exists():
        if path.read_bytes() == data:
            return mc.sha256_file(path), "unchanged"
        mc.stop(f"{path} exists and differs from the folds computed now. A committed fold file is never "
                f"overwritten: take this message to Claude.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return mc.sha256_file(path), "written"


# =============================================================================
def main() -> None:
    mc.setup_console()
    print("Model comparison, step 1: gold labels, fold files and model inputs (no model is run)\n")
    check_fold_libraries()
    check_files_of_record()

    key1, long1 = load_tranche(1)
    long1 = attach_tranche1_subsystems(long1)
    gold1 = form_gold(1, key1, long1)
    check_tranche1(gold1)

    key2, long2 = load_tranche(2)
    gold2 = form_gold(2, key2, long2)
    counts2 = {k: int((gold2["label4"] == k).sum()) for k in cfg.LABEL4 + [cfg.NO_STAGE2, ""]}
    print(f"tranche 2: {len(gold2)} items, {int((~long2['missing']).sum())} ratings | gold labels "
          f"{ {k: v for k, v in counts2.items() if k != ''} } | without a gold label: {counts2['']}")
    print(f"tranche 2 adjudicated: Stage 2 {sorted(cfg.ADJUDICATED_STAGE2)}; subsystem "
          f"{sorted(cfg.ADJUDICATED_SUBSYSTEM)}")
    for n in gold1.attrs["notes"] + gold2.attrs["notes"]:
        print("  note: " + n)

    # ---- folds -----------------------------------------------------------------------
    folds, fold_files = {}, {}
    for t, gold in ((1, gold1), (2, gold2)):
        f = assign_folds(gold)
        folds[t] = f
        path = cfg.SPLITS_DIR / f"tranche{t}_folds.csv"
        sha, state = write_fold_file(path, f)
        sizes = Counter(f.values())
        by_stratum = {k: dict(sorted(Counter(f[i] for i in f if gold.at[i, 'label4'] == k).items()))
                      for k in sorted(set(gold.loc[list(f), 'label4']))}
        fold_files[t] = {"file": f"splits/{path.name}", "sha256": sha, "items": len(f),
                         "items_per_fold": dict(sorted(sizes.items())), "by_stratum": by_stratum}
        print(f"tranche {t} folds ({state}): {len(f)} items, per fold {dict(sorted(sizes.items()))} | "
              f"{path.name} SHA-256 {sha}")

    # ---- gold label file --------------------------------------------------------------
    gold = pd.concat([gold1, gold2])
    gold["fold"] = [folds[int(gold.at[i, 'tranche'])].get(i, "") for i in gold.index]
    cols = ["tranche", "item", "n_ratings", "gold_stage1", "gold_stage2", "label4", "label4_raw_majority",
            "stage2_adjudicated", "stage_status", "gold_subsystem", "n_subsystem_labels", "subsystem_status",
            "subsystem_adjudicated", "adjudicated_subsystem_given_by_an_annotator", "fold"]
    gold_path = cfg.MODELS_DIR / "gold_labels.csv"
    gold_sha = mc.write_rows_csv(gold_path, ["id"] + cols, [[i] + [gold.at[i, c] for c in cols] for i in gold.index])
    fp = {t: mc.pairs_sha256(g["label4"].to_dict()) for t, g in ((1, gold1), (2, gold2))}
    fp_sub = mc.pairs_sha256({i: gold.at[i, "gold_subsystem"] for i in gold.index if gold.at[i, "gold_stage1"] == "Y"})

    # ---- model inputs ----------------------------------------------------------------
    manifest_in = mc.read_json(cfg.PREFILTER_INPUT_MANIFEST)
    pin_sha = mc.sha256_file(cfg.PREFILTER_INPUT)
    if manifest_in.get("file_sha256") != pin_sha:
        mc.stop("prefilter_input.csv does not match the SHA-256 recorded in prefilter_input_manifest.json")
    pin = pd.read_csv(cfg.PREFILTER_INPUT, dtype=str, keep_default_na=False, encoding="utf-8")
    if list(pin.columns) != ["id", "text"] or pin["id"].duplicated().any():
        mc.stop("prefilter_input.csv must have the columns id,text and one row per id")
    text = dict(zip(pin["id"], pin["text"]))
    annotated = sorted(gold.index)
    if len(annotated) != 1000 or len(set(annotated)) != 1000:
        mc.stop(f"expected 1,000 distinct annotated items; found {len(annotated)}")
    absent = [i for i in annotated if i not in text or not text[i].strip()]
    if absent:
        mc.stop(f"{len(absent)} annotated items have no text in prefilter_input.csv, e.g. {absent[:5]}")
    zs_path = cfg.MODELS_DIR / "zero_shot_input.csv"
    zs_sha = mc.write_rows_csv(zs_path, ["id", "text"], [[i, text[i]] for i in annotated])
    subreddit = {**key1["subreddit"].to_dict(), **key2["subreddit"].to_dict()}
    ft_ids = [i for i in annotated if gold.at[i, "label4"] != ""]
    ft_path = cfg.MODELS_DIR / "finetune_input.csv"
    ft_sha = mc.write_rows_csv(
        ft_path, ["id", "tranche", "subreddit", "text", "gold_stage1", "gold_stage2", "label4", "fold"],
        [[i, int(gold.at[i, "tranche"]), re.sub(r"^/?r/", "", str(subreddit[i]).strip()), text[i],
          gold.at[i, "gold_stage1"], gold.at[i, "gold_stage2"], gold.at[i, "label4"], gold.at[i, "fold"]]
         for i in ft_ids])
    n_stage2 = int((gold.loc[ft_ids, "gold_stage2"] != "").sum())
    print(f"inputs: zero_shot_input.csv {len(annotated)} items (SHA-256 {zs_sha[:16]}...); finetune_input.csv "
          f"{len(ft_ids)} items with a gold Stage 1 label, {n_stage2} with a gold Stage 2 class "
          f"(SHA-256 {ft_sha[:16]}...)")

    manifest = {
        "created": mc.now_iso(),
        "specification": "Deviations 2, 7, 11 and 12, docs/analysis_preregistration.md; models_config.py",
        "seed": cfg.SEED,
        "fold_files": fold_files,
        "gold_labels_file": {"file": "data/models/gold_labels.csv", "sha256": gold_sha},
        "label4_fingerprint": {"tranche1": fp[1], "tranche2": fp[2]},
        "subsystem_fingerprint_relevant_items": fp_sub,
        "tranche2_label_counts": {k: v for k, v in counts2.items() if k != ""},
        "tranche2_without_gold_label": counts2[""],
        "adjudicated": {"stage2": cfg.ADJUDICATED_STAGE2, "subsystem": cfg.ADJUDICATED_SUBSYSTEM},
        "notes": gold1.attrs["notes"] + gold2.attrs["notes"],
        "inputs": {"prefilter_input_sha256": pin_sha,
                   "zero_shot_input": {"file": "data/models/zero_shot_input.csv", "items": len(annotated),
                                       "sha256": zs_sha},
                   "finetune_input": {"file": "data/models/finetune_input.csv", "items": len(ft_ids),
                                      "stage2_items": n_stage2, "sha256": ft_sha}},
        "files_of_record_sha256": cfg.RECORDED_SHA256,
        "versions": mc.versions("numpy", "pandas", "sklearn", "openpyxl"),
    }
    mc.write_json(cfg.MODELS_DIR / "prepare_manifest.json", manifest)
    n_adjudicated = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}.get(
        len(cfg.ADJUDICATED_STAGE2) + len(cfg.ADJUDICATED_SUBSYSTEM),
        str(len(cfg.ADJUDICATED_STAGE2) + len(cfg.ADJUDICATED_SUBSYSTEM)))

    mc.show_register_block(cfg.MODELS_DIR / "PASTE_models_prepare_block.txt", [
        f"- `models_01_prepare.py` run {manifest['created']} on the files of record (all ten SHA-256 checked).",
        "- Tranche 1 labels match the recorded fingerprint; tranche 2 gold labels formed by Deviations 2, 7",
        f"  and 11 with the {n_adjudicated} adjudications of 10 October: four-way label fingerprint `{fp[2]}`.",
        f"- Fold files (StratifiedKFold, five folds, seed {cfg.SEED}, scikit-learn "
        f"{cfg.FOLD_LIBRARY_VERSIONS['scikit-learn']}, NumPy {cfg.FOLD_LIBRARY_VERSIONS['numpy']}):",
        f"  `splits/tranche1_folds.csv` {fold_files[1]['items']} items, SHA-256 `{fold_files[1]['sha256']}`;",
        f"  `splits/tranche2_folds.csv` {fold_files[2]['items']} items, SHA-256 `{fold_files[2]['sha256']}`.",
        f"- Comment text from `data/tranche2/prefilter_input.csv`, SHA-256 `{pin_sha}`.",
        f"- Model inputs (not committed): `zero_shot_input.csv` {len(annotated)} items, SHA-256 `{zs_sha}`;",
        f"  `finetune_input.csv` {len(ft_ids)} items ({n_stage2} with a Stage 2 class), SHA-256 `{ft_sha}`.",
    ])
    print("\nNo model was run. Next: commit the fold files with the model scripts (see the procedure).")


if __name__ == "__main__":
    main()
