"""Model comparison, step 5 (on the PC): the evaluation of record.

From the repository folder, with the virtual environment active (no GPU, no internet):
    python models_05_evaluate.py --preflight
        Before the commit. Checks every input against the record and reads the files of record,
        the keys and the manifests, without setting any prediction against a label: nothing is
        scored and no result is shown.
    python models_05_evaluate.py --confirm-committed
        After this file is committed and its SHA-256 recorded. The evaluation of record. It runs
        once: it refuses to start if its results already exist.

This is the first and only place where a model's predictions are set against the gold labels.
Every rule it applies was fixed before any prediction was scored: R5 and Deviation 12 of
docs/analysis_preregistration.md, models_config.py (committed at bb3fbfe) and, where the committed
text is silent, the rules stated below, committed with this file. Before it scores anything it
checks every input against the SHA-256 recorded for it in docs/decision_register.md, and it stops
at the first difference.

Item sets
  - Stage 2 primary item set: the items of both tranches that are relevant in the gold set, each
    with its gold Stage 2 class (598 items). Fine-tuned models: their cross-validated predictions
    (each item predicted by the fold model that did not see it). Zero-shot configurations: their
    one prediction of every item.
  - Stage 1: every item with a gold Stage 1 label (1,000 items), cross-validated predictions.

Stage 2 (Deviation 12)
  - Macro-F1 (the mean of the three per-class F1) and per-class F1 of the eight configurations,
    unweighted. A refusal is scored as an error: a miss for the item's gold class, and a
    prediction of no class (so it is no class's false positive).
  - Family B: the ten pairwise comparisons of macro-F1 among DistilBERT, RoBERTa and the three
    zero-shot models under the universal schema, each by R5's item-level permutation test, with
    Holm-Bonferroni across the ten at 0.05.
  - Family C (exploratory, uncorrected): the nine of those comparisons that involve a zero-shot
    model, with the zero-shot models under the domain-specific schema; the ten comparisons within
    each tranche; and each zero-shot model's universal against its domain-specific schema.
    Per-class F1 is reported for every configuration, pooled and for each tranche, untested.
  - Deployment: the highest CONCERN-class F1; a configuration is tied with it if a two-sided
    item-level permutation test of the difference in CONCERN-class F1 gives p >= 0.05 (no
    adjustment; this only defines ties and is not a reported comparison); among the leader and
    those tied with it, the larger TPR - FPR for CONCERN against the other two classes, weighted
    by the pooled design weights of Deviation 11; then the lower measured cost per 1,000 comments;
    then the first in the order DistilBERT, RoBERTa, BART-MNLI, Haiku, Sonnet, universal before
    domain-specific.
  - Prevalence correction: TPR and FPR for CONCERN against the other two classes, weighted by
    the pooled design weights, from the cross-validated predictions on the primary item set, for
    the deployed configuration (and, for reference, every configuration).
  - The two predictions of Deviation 12, each confirmed or not confirmed.

Stage 1 (Deviation 12, Deviation 1)
  - Balanced accuracy of DistilBERT and RoBERTa (input: subreddit and comment); the higher is
    deployed, an exact tie going to the lower cost (models_config.COST_RULE: neither has an API
    charge, so the one with fewer parameters, DistilBERT). Accuracy for each class and each
    subreddit, for both candidates and for the text-only variant of the deployed type. The
    text-only variant of the other type is checked like every input but not scored.

Reliability (Deviation 12)
  - Krippendorff's alpha (nominal) at Stage 1 and Stage 2, for the 200 reliability items in one
    matrix and for each tranche's 100, overall and for each Stage 2 class against the rest, from
    every item with two or more ratings, with intervals by the method of Deviation 4 (10,000
    item-level bootstrap resamples of the items, seed 24916660, all five alphas on the same
    resamples; 95% percentile interval and the share of resamples below 0.7). The tranche 1
    figures must reproduce those recorded in September (Deviation 4).

Success criteria (Deviation 12): 1, 2 and 6 are settled here; 3, 4 and 5 by later analyses.

The permutation test (R5, Deviation 12). Two-sided, N = 10,000, gold labels never permuted, seeded
with 24916660. As in the reference study whose test R5 follows (Lee et al. 2026, Social Network
Analysis and Mining, Appendix E.1): each permutation flips a fair coin for every item and swaps
the two configurations' predictions of that item where it shows 1; p is the share of the
permutations whose absolute difference is at least the observed one, floored at 1/N. The coins:
numpy.random.default_rng(24916660).integers(0, 2, size=(10000, n), dtype=numpy.int8), a fresh
generator for every test, rows the permutations, columns the items in id order. Wherever floating
point could decide a comparison, it is made in exact rational arithmetic.

Rules fixed with this file, where the committed text is silent
  1. p-value: as the reference study computes it (above). As there, a comparison is significant
     when its Holm-adjusted p is below 0.05, and otherwise "not demonstrably significant"; as
     Deviation 12 says, a configuration is tied when its unadjusted p is 0.05 or more.
  2. Family C: as listed above.
  3. A refusal counts as "not CONCERN" in the CONCERN rates (a miss on a CONCERN item, never a
     false positive): a deployed configuration's refusals on the corpus would not be counted as
     CONCERN either, so the rates match the count they correct.
  4. Success criterion 6 uses the weighted TPR - FPR, the rates the correction uses; the
     unweighted figure is reported beside it.
  5. Exact ties: if two configurations share the highest CONCERN-class F1 exactly, the first in
     the committed order is the reference for the tie test. In the first prediction, "chosen by
     macro-F1" takes the first in the committed order on an exact tie, and "largest for CONCERN"
     means strictly larger than both other gaps (gap = fine-tuned minus zero-shot, signed). In
     the second, "lowest" means strictly lower than both other classes.
  6. Descriptive extras, not tested: the mean and standard deviation (n - 1) of macro-F1 and
     per-class F1 over the five folds; Wilson 95% intervals for the Stage 1 accuracies.
  7. Cost per 1,000 comments: a Claude configuration's measured cost as recorded at a7ad389 (all
     1,000 items were run, so its cost per 1,000 comments is its cost); every other configuration
     zero (models_config.COST_RULE).

Writes, in data/models/evaluation/ (not committed):
  evaluation_results.json    every figure and decision (no timestamp: a rerun gives the same bytes)
  evaluation_report.md       the same, as tables
  stage2_metrics.csv, pairwise_tests.csv, stage1_metrics.csv, reliability_alpha.csv
  evaluation_manifest.json   time, versions, the SHA-256 of every input and output
  PASTE_evaluation_block.txt the register lines (hashes and decisions)
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

import models_01_prepare as prep
import models_common as mc
import models_config as cfg

EVAL_DIR = cfg.MODELS_DIR / "evaluation"
N_PERM = 10_000
LEVEL = Fraction(1, 20)                       # 0.05: Holm (Family B) and the Stage 2 tie test
CRITERION6_BAR = Fraction(1, 4)               # success criterion 6: TPR - FPR >= 0.25
RELIABILITY_BAR = Fraction(7, 10)             # success criterion 1: alpha >= 0.7
Z95 = 1.959963984540054

# =============================================================================
# THE RECORD: what every input must be (docs/decision_register.md)
# =============================================================================
SCRIPTS_OF_RECORD = {                          # committed at bb3fbfe; imported by this script
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
}
FOLD_FILES_SHA256 = {                          # committed at bb3fbfe
    1: "a3a7a23acdd98a7fcb7be639f49cd614c8ca27ffeefe783898f1a7cd11a627c3",
    2: "1026d74f8566bd08576adb220cb57a335ab8c333702eafc544cac8a8d953d324",
}
TRANCHE2_LABELS_SHA256 = "d934aadf914d677085d1d75c0d9a284aabe6871e1da72dad9a793f1d4727e89b"   # bb3fbfe
TRANCHE2_KEY_SHA256 = "ae116f8df5f33bfc9231b35519db7a992c6acd7ae5f5bb23bf50ef2524c22d5e"   # the draw, c7edc7f
INPUTS_SHA256 = {                              # bb3fbfe
    "zero_shot_input.csv": "2f8d48c3c66ac608d557cc03eb5c2070b357e8f0bd8fdd01b43bce380a7a181f",
    "finetune_input.csv": "bcae83e718ebfa16b2f66b640f23acb5e091d775c2d53e549fa15a424e25d702",
}
GOLD_ITEMS = {"stage1": 1000, "stage2": 598}   # bb3fbfe: 1,000 with a gold Stage 1 label, 598 with a class
# Pooled design weights (Deviation 11): N_h / n_h, N_h the frame size of the era, n_h the pooled draw.
ERAS = {"2016-2018": (2495, 334), "2019-2021": (3633, 334), "2022-2025": (6038, 332)}
# Tranche 1 agreement recorded in September (Deviation 4, as Deviation 10 cites it; Deviation 12 quotes the
# CONCERN and OTHER figures), to three decimals.
TRANCHE1_ALPHA_RECORDED = {"Stage 1": "0.959", "Stage 2": "0.739", "CONCERN against the rest": "0.836",
                           "ENDORSEMENT against the rest": "0.797", "OTHER against the rest": "0.547"}

# Predictions: the SHA-256 recorded for each file (docs/decision_register.md, a7ad389 and this commit).
RECORDED_PREDICTIONS_SHA256 = {
    "haiku-universal": "56d4dac6e9fdef0755df5a57e6595bfa3ea01aa529e9be43da7a71cd8d7d51fd",       # a7ad389
    "haiku-domain": "1381ea3de49f61c5ff2beadd04469766715b177bfdf168ab1cc8a6f1b7906cd2",          # a7ad389
    "sonnet-universal": "d421907b0a87800834b6379b667c88fca945c1cd6ad937ccfe3fbd67ad3afbf3",      # a7ad389
    "sonnet-domain": "71b56f7270545d131a6cfe5649a1162a1b244b5f91298ff770e1ac80a4abbbaa",         # a7ad389
    "bart-universal": "c7f6b1eccc433cd805b96a322ea3c82d086d016b2b8440feb6bb7b90e88be5e5",   # Colab, 11 Oct
    "bart-domain": "9e9280679dc6696332c896f763b33bd64fabc3eabe82a35aa5806e2accbe5e10",            # 11 Oct, PC
    "distilbert": "985b45605edf54fa9e95d311a3a9f86eea11e599eb49e8c350b0778feb93a6db",       # Colab, 11 Oct
    "roberta": "b17357f25060ed91ad2d9a9a51ea093b85afc9a2210db491c2e107811cac1597",          # Colab, 11 Oct
    "stage1-distilbert": "ae59ab2d9b29f539744056da9fbd4dec3826beefa07d1d50b9ed9d4b046e6cfd", # Colab, 11 Oct
    "stage1-roberta": "7258458df43c047ff8b8088fa8a855468acd1e6b8835dddcd42e85c3d8502b57",   # Colab, 11 Oct
    "stage1-distilbert-textonly": "2c3bb9ed8dcd7e71617df2c31f85ca8544cbc7db6898d9e50d6212d6f7dd400b", # Colab, 11 Oct
    "stage1-roberta-textonly": "24d8e3a0de3e8d03d1c6be09fc162b74ff3a51265859bd7248580d0a8c40d94e", # Colab, 11 Oct
}
# Claude runs as recorded at a7ad389: refusals, calls and cost (US$) of each configuration.
RECORDED_CLAUDE = {
    "haiku-universal": {"refusals": 3, "calls": 1003, "cost_usd": "0.201084"},
    "haiku-domain": {"refusals": 8, "calls": 1008, "cost_usd": "0.267972"},
    "sonnet-universal": {"refusals": 0, "calls": 1000, "cost_usd": "0.604656"},
    "sonnet-domain": {"refusals": 0, "calls": 1000, "cost_usd": "0.799461"},
}

# =============================================================================
# configurations (Deviation 12)
# =============================================================================
CLASSES = list(cfg.CLASSES)                    # CONCERN, ENDORSEMENT, OTHER -> 0, 1, 2
CONCERN = 0
STAGE2 = ["distilbert", "roberta", "bart-universal", "bart-domain", "haiku-universal", "haiku-domain",
          "sonnet-universal", "sonnet-domain"]          # also the last tie-break order of Deviation 12
NAMES = {"distilbert": "DistilBERT", "roberta": "RoBERTa", "bart-universal": "BART-MNLI (universal)",
         "bart-domain": "BART-MNLI (domain-specific)", "haiku-universal": "Claude Haiku 4.5 (universal)",
         "haiku-domain": "Claude Haiku 4.5 (domain-specific)", "sonnet-universal": "Claude Sonnet 4.6 (universal)",
         "sonnet-domain": "Claude Sonnet 4.6 (domain-specific)",
         "stage1-distilbert": "DistilBERT (subreddit + comment)", "stage1-roberta": "RoBERTa (subreddit + comment)",
         "stage1-distilbert-textonly": "DistilBERT (comment only)", "stage1-roberta-textonly": "RoBERTa (comment only)"}
FINE_TUNED = ["distilbert", "roberta"]
ZERO_SHOT_UNIVERSAL = ["bart-universal", "haiku-universal", "sonnet-universal"]
ZERO_SHOT_DOMAIN = ["bart-domain", "haiku-domain", "sonnet-domain"]
FAMILY_B = FINE_TUNED + ZERO_SHOT_UNIVERSAL
SCHEMA_PAIRS = list(zip(ZERO_SHOT_UNIVERSAL, ZERO_SHOT_DOMAIN))
STAGE1 = ["stage1-distilbert", "stage1-roberta"]       # committed candidates, in the order of cost
TEXT_ONLY = ["stage1-distilbert-textonly", "stage1-roberta-textonly"]
STAGE1_LABELS = ["N", "Y"]                             # N -> 0, Y -> 1

RUNS = {   # name -> where its files are and what its manifest must say
    "distilbert": {"kind": "finetune", "run": "stage2_distilbert", "model": "distilbert", "stage": 2, "text_only": False},
    "roberta": {"kind": "finetune", "run": "stage2_roberta", "model": "roberta", "stage": 2, "text_only": False},
    "bart-universal": {"kind": "bart", "schema": "universal"},
    "bart-domain": {"kind": "bart", "schema": "domain"},
    "haiku-universal": {"kind": "claude", "family": "haiku", "schema": "universal"},
    "haiku-domain": {"kind": "claude", "family": "haiku", "schema": "domain"},
    "sonnet-universal": {"kind": "claude", "family": "sonnet", "schema": "universal"},
    "sonnet-domain": {"kind": "claude", "family": "sonnet", "schema": "domain"},
    "stage1-distilbert": {"kind": "finetune", "run": "stage1_distilbert", "model": "distilbert", "stage": 1, "text_only": False},
    "stage1-roberta": {"kind": "finetune", "run": "stage1_roberta", "model": "roberta", "stage": 1, "text_only": False},
    "stage1-distilbert-textonly": {"kind": "finetune", "run": "stage1_distilbert_textonly", "model": "distilbert",
                                   "stage": 1, "text_only": True},
    "stage1-roberta-textonly": {"kind": "finetune", "run": "stage1_roberta_textonly", "model": "roberta",
                                "stage": 1, "text_only": True},
}


# =============================================================================
# small helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


def fr(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"


def fl(x, digits: int = 6):
    if x is None:
        return None
    return round(float(x), digits)


def check_sha(path: Path, want: str, what: str) -> str:
    if not path.exists():
        stop(f"{what}: not found at {path}")
    got = mc.sha256_file(path)
    if got != want:
        stop(f"{what}: SHA-256 {got[:16]}... is not the recorded {want[:16]}... ({path}). Take this message to Claude.")
    return got


def text_sha256(path: Path) -> str:
    """SHA-256 of a committed text file with its line endings as committed (LF): a checkout that
    turned them into CRLF changes nothing that is read."""
    return mc.text_sha256(path.read_bytes().decode("utf-8").replace("\r\n", "\n"))


def check_text_sha(path: Path, want: str, what: str) -> str:
    if not path.exists():
        stop(f"{what}: not found at {path}")
    got = text_sha256(path)
    if got != want:
        stop(f"{what} is not the committed file (SHA-256 {got[:16]}..., recorded {want[:16]}...). "
             f"Take this message to Claude.")
    return got


def as_fraction(x):
    """A recorded number as an exact fraction; None if it is missing or not a number."""
    try:
        return Fraction(str(x))
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def same_model(requested: str, returned: str) -> bool:
    return re.fullmatch(re.escape(requested) + r"(-\d{8})?", returned or "") is not None


def json_normal(x):
    return json.loads(json.dumps(x, default=str))


def strip_private(x):
    if isinstance(x, dict):
        return {k: strip_private(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, list):
        return [strip_private(v) for v in x]
    return x


# =============================================================================
# the record and the inputs
# =============================================================================
def check_record_complete() -> None:
    missing = [k for k, v in RECORDED_PREDICTIONS_SHA256.items() if not v]
    if TRANCHE2_KEY_SHA256 is None:
        missing.append("tranche2_master_key.csv")
    if missing:
        stop(f"the SHA-256 of these files is not yet in the record: {', '.join(missing)}. This copy of the script "
             f"is not the one to run. Take this message to Claude.")
    values = list(RECORDED_PREDICTIONS_SHA256.values())
    if len(set(values)) != len(values):
        stop("two prediction files have the same recorded SHA-256. Take this message to Claude.")


def check_libraries() -> dict:
    import sklearn
    found = {"numpy": np.__version__, "scikit-learn": sklearn.__version__}
    want = {"numpy": cfg.FOLD_LIBRARY_VERSIONS["numpy"], "scikit-learn": cfg.FOLD_LIBRARY_VERSIONS["scikit-learn"]}
    if found != want:
        stop(f"the permutation coins are drawn with NumPy {want['numpy']} (the version R5 fixes), and the run uses "
             f"scikit-learn {want['scikit-learn']}; found NumPy {found['numpy']}, scikit-learn {found['scikit-learn']}.\n"
             f"  Install them with:  python -m pip install numpy=={want['numpy']} scikit-learn=={want['scikit-learn']}")
    return found


def check_scripts() -> dict:
    """The modules actually imported must be the files committed at bb3fbfe."""
    out = {}
    for module in (cfg, mc, prep):
        path = Path(module.__file__).resolve()
        out[path.name] = check_text_sha(path, SCRIPTS_OF_RECORD[path.name], f"{path.name} (committed at bb3fbfe)")
    return out


def load_gold() -> tuple[pd.DataFrame, dict]:
    """gold_labels.csv, checked against the recorded label fingerprints and the committed folds."""
    path = cfg.MODELS_DIR / "gold_labels.csv"
    if not path.exists():
        stop(f"{path} not found (models_01_prepare.py writes it)")
    g = read_csv(path)
    need = ["id", "tranche", "item", "gold_stage1", "gold_stage2", "label4", "fold"]
    if any(c not in g.columns for c in need) or g["id"].duplicated().any():
        stop(f"{path.name} must have the columns {need} and one row per id")
    g = g.set_index("id")
    for t, want in ((1, cfg.TRANCHE1_LABELS_SHA256), (2, TRANCHE2_LABELS_SHA256)):
        part = g[g["tranche"] == str(t)]
        if len(part) != 500 or mc.pairs_sha256(part["label4"].to_dict()) != want:
            stop(f"the tranche {t} gold labels in {path.name} are not those recorded (four-way label fingerprint). "
                 f"Take this message to Claude.")
    if len(g) != 1000:
        stop(f"{path.name} must hold the 1,000 annotated items; it holds {len(g)}")
    four = {"N": ("N", "")} | {c: ("Y", c) for c in CLASSES}
    for i, r in g.iterrows():
        if r["label4"] not in four or (r["gold_stage1"], r["gold_stage2"]) != four[r["label4"]]:
            stop(f"{path.name}: item {i} has inconsistent gold labels ({r['label4']!r}, {r['gold_stage1']!r}, "
                 f"{r['gold_stage2']!r})")
    shas = {}
    for t in (1, 2):
        fpath = cfg.SPLITS_DIR / f"tranche{t}_folds.csv"
        shas[f"tranche{t}_folds.csv"] = check_text_sha(fpath, FOLD_FILES_SHA256[t], f"splits/tranche{t}_folds.csv")
        folds = read_csv(fpath)
        if list(folds.columns) != ["id", "fold"]:
            stop(f"{fpath.name} must have the columns id,fold")
        mine = g[g["tranche"] == str(t)]
        if set(folds["id"]) != set(mine.index) or (folds.set_index("id")["fold"] != mine["fold"].reindex(folds["id"])).any():
            stop(f"the folds in {path.name} are not those of the committed {fpath.name}")
    if not set(g["fold"]) <= {"1", "2", "3", "4", "5"}:
        stop(f"{path.name}: every gold item must have a fold from 1 to 5")
    for t in ("1", "2"):
        counts = Counter(g.loc[g["tranche"] == t, "gold_stage2"])
        if any(counts[c] == 0 for c in CLASSES):
            stop(f"{path.name}: tranche {t} lacks a Stage 2 class; every evaluated item set must hold all three")
    n1 = int(g["gold_stage1"].isin(["Y", "N"]).sum())
    n2 = int(g["gold_stage2"].isin(CLASSES).sum())
    if (n1, n2) != (GOLD_ITEMS["stage1"], GOLD_ITEMS["stage2"]):
        stop(f"{path.name}: {n1} items with a gold Stage 1 label and {n2} with a gold Stage 2 class; the record "
             f"has {GOLD_ITEMS['stage1']} and {GOLD_ITEMS['stage2']}")
    shas["gold_labels.csv"] = mc.sha256_file(path)
    return g, shas


def load_inputs(gold: pd.DataFrame) -> tuple[pd.Series, dict]:
    shas = {}
    zs_path = cfg.MODELS_DIR / "zero_shot_input.csv"
    shas["zero_shot_input.csv"] = check_sha(zs_path, INPUTS_SHA256["zero_shot_input.csv"], "zero_shot_input.csv")
    zs = read_csv(zs_path)
    if list(zs.columns) != ["id", "text"] or set(zs["id"]) != set(gold.index) or len(zs) != len(gold):
        stop("zero_shot_input.csv does not hold the 1,000 annotated items")
    ft_path = cfg.MODELS_DIR / "finetune_input.csv"
    shas["finetune_input.csv"] = check_sha(ft_path, INPUTS_SHA256["finetune_input.csv"], "finetune_input.csv")
    ft = read_csv(ft_path)
    if "subreddit" not in ft.columns or ft["id"].duplicated().any():
        stop("finetune_input.csv must have a subreddit column and one row per id")
    ft = ft.set_index("id")
    cols = ["gold_stage1", "gold_stage2", "label4", "fold", "tranche"]
    if set(ft.index) != set(gold.index) or (ft[cols] != gold.loc[ft.index, cols]).any().any():
        stop("finetune_input.csv and gold_labels.csv disagree on an item's labels, tranche or fold")
    return ft["subreddit"], shas


def load_keys() -> tuple:
    """Both master keys and the ratings (via models_01_prepare, which checks the files of record and the
    memberships), the tranche 2 key against its recorded SHA-256, and the pooled design weights."""
    prep.check_files_of_record()
    sha2 = check_sha(cfg.TRANCHE2_KEY, TRANCHE2_KEY_SHA256, "tranche2_master_key.csv")
    key1, long1 = prep.load_tranche(1)
    key2, long2 = prep.load_tranche(2)
    for key, need, what in ((key1, ["era", "stratum_size"], "tranche 1 key"),
                            (key2, ["era", "pooled_draw", "pooled_weight"], "tranche 2 key")):
        missing = [c for c in need if c not in key.columns]
        if missing:
            stop(f"the {what} lacks the columns {missing}. Take this message to Claude.")
    return key1, long1, key2, long2, pooled_weights(key1, key2), sha2


def pooled_weights(key1: pd.DataFrame, key2: pd.DataFrame) -> dict:
    eras1, eras2 = key1["era"].str.strip(), key2["era"].str.strip()
    if not set(eras1) | set(eras2) <= set(ERAS):
        stop(f"an item's era is not one of {list(ERAS)}: found {sorted(set(eras1) | set(eras2))}")
    c1, c2 = Counter(eras1), Counter(eras2)
    for e, (_, n_h) in ERAS.items():
        if c1[e] + c2[e] != n_h:
            stop(f"era {e}: the two keys hold {c1[e]} + {c2[e]} items; the pooled draw is {n_h}")
    if (key1["stratum_size"].astype(int) != eras1.map(lambda e: ERAS[e][0])).any():
        stop("the tranche 1 key's stratum sizes are not the frame sizes of R1")
    if (key2["pooled_draw"].astype(int) != eras2.map(lambda e: ERAS[e][1])).any() \
            or ((key2["pooled_weight"].astype(float) - eras2.map(lambda e: ERAS[e][0] / ERAS[e][1])).abs() > 1e-9).any():
        stop("the tranche 2 key's pooled draw or pooled weight differs from N_h / n_h of Deviation 11")
    w = {i: Fraction(*ERAS[e]) for i, e in eras1.items()}
    w.update({i: Fraction(*ERAS[e]) for i, e in eras2.items()})
    return w


# =============================================================================
# prediction files: manifest and SHA-256 first, then the file's structure (never a label)
# =============================================================================
def open_run(name: str) -> tuple[Path, dict, str]:
    spec = RUNS[name]
    if spec["kind"] == "claude":
        folder, pred_name, man_name = cfg.MODELS_DIR / "claude", f"{name}_predictions.csv", f"{name}_manifest.json"
    elif spec["kind"] == "bart":
        folder = cfg.MODELS_DIR / "bart"
        pred_name, man_name = f"bart_{spec['schema']}_predictions.csv", f"bart_{spec['schema']}_manifest.json"
    else:
        folder, pred_name, man_name = cfg.MODELS_DIR / "finetune", f"{spec['run']}_predictions.csv", f"{spec['run']}_manifest.json"
    man_path, pred_path = folder / man_name, folder / pred_name
    if not man_path.exists():
        stop(f"{name}: manifest not found at {man_path}")
    man = mc.read_json(man_path)
    sha = check_sha(pred_path, RECORDED_PREDICTIONS_SHA256[name], f"{name} predictions")
    if (man.get("predictions") or {}).get("sha256") != sha:
        stop(f"{name}: the manifest gives a different SHA-256 for the predictions. Take this message to Claude.")
    problems = {"claude": manifest_claude, "bart": manifest_bart, "finetune": manifest_finetune}[spec["kind"]](name, man)
    if problems:
        stop(f"{name}: the manifest does not match the record ({'; '.join(problems)}). Take this message to Claude.")
    return pred_path, man, sha


def manifest_claude(name: str, man: dict) -> list:
    spec, rec = RUNS[name], RECORDED_CLAUDE[name]
    model = cfg.CLAUDE_MODELS[spec["family"]]
    problems = []
    if man.get("config") != name or man.get("schema") != spec["schema"] or man.get("model") != model:
        problems.append("configuration, schema or model")
    if not man.get("answered_by") or not all(same_model(model, m) for m in man["answered_by"]):
        problems.append("the identifiers that answered")
    if (man.get("input") or {}).get("sha256") != INPUTS_SHA256["zero_shot_input.csv"] or man.get("items") != 1000:
        problems.append("input")
    cost = Fraction(rec["cost_usd"])
    if man.get("refusals") != rec["refusals"] or man.get("calls") != rec["calls"] \
            or as_fraction(man.get("cost_usd")) != cost or as_fraction(man.get("cost_usd_per_1000_comments")) != cost:
        problems.append("refusals, calls or cost recorded at a7ad389")
    if man.get("settings") != json_normal(cfg.CLAUDE_SETTINGS) or man.get("labels") != cfg.SCHEMAS[spec["schema"]]:
        problems.append("settings or labels")
    return problems


def manifest_bart(name: str, man: dict) -> list:
    schema = RUNS[name]["schema"]
    commit = cfg.CHECKPOINTS["bart_mnli"]["commit"]
    hyps = {c: cfg.BART_HYPOTHESIS.format(label=cfg.SCHEMAS[schema][c]) for c in CLASSES}
    problems = []
    if man.get("input_sha256") != INPUTS_SHA256["zero_shot_input.csv"] or man.get("items") != 1000:
        problems.append("input")
    if man.get("hypotheses") != hyps:
        problems.append("hypotheses")
    if schema == "universal":
        if man.get("test_model") is not False or man.get("model_commit_pinned") != commit \
                or man.get("model_commit_loaded") not in (None, commit) or man.get("model") != cfg.CHECKPOINTS["bart_mnli"]["repo"]:
            problems.append("model or commit")
    elif (man.get("frozen_scores") or {}).get("sha256") != cfg.PREFILTER_SCORES_SHA256 \
            or man.get("frozen_model_commit") != cfg.PREFILTER_MODEL_COMMIT:
        problems.append("frozen pre-filter scores or their model commit")
    return problems


def manifest_finetune(name: str, man: dict) -> list:
    spec = RUNS[name]
    ck = cfg.CHECKPOINTS[spec["model"]]
    labels = CLASSES if spec["stage"] == 2 else STAGE1_LABELS
    items = GOLD_ITEMS["stage2"] if spec["stage"] == 2 else GOLD_ITEMS["stage1"]
    problems = []
    if man.get("run") != spec["run"] or man.get("stage") != spec["stage"] or man.get("text_only") is not spec["text_only"]:
        problems.append("run, stage or input")
    if man.get("test_model") is not False or man.get("model") != ck["repo"] or man.get("model_commit_pinned") != ck["commit"]:
        problems.append("model or commit")
    if man.get("labels") != labels or man.get("items") != items or man.get("seed") != cfg.SEED:
        problems.append("labels, items or seed")
    if man.get("settings") != json_normal(cfg.FINETUNE):
        problems.append("fine-tuning settings")
    if (man.get("input") or {}).get("sha256") != INPUTS_SHA256["finetune_input.csv"]:
        problems.append("input")
    folds = man.get("folds") if isinstance(man.get("folds"), list) else []
    numbers = [f.get("fold") if isinstance(f, dict) else None for f in folds]
    if not all(isinstance(k, int) for k in numbers) or sorted(numbers) != list(range(1, cfg.N_FOLDS + 1)):
        problems.append("folds")
    elif not {f.get("model_commit_loaded") for f in folds} <= {None, ck["commit"]}:
        problems.append("the model commit loaded")
    elif not all(isinstance(f.get("best_epoch"), (int, float)) and f.get("best_epoch") > 0 for f in folds):
        problems.append("best epochs")
    return problems


def parse_run(name: str, path: Path, man: dict, gold: pd.DataFrame) -> dict:
    """The predictions as written by the model scripts: one per item of the run's item set, a class (or, for
    Claude, a recorded refusal), and for fine-tuned runs the committed fold of each item. No label is read."""
    spec = RUNS[name]
    df = read_csv(path)
    if spec["kind"] == "claude":
        rec = RECORDED_CLAUDE[name]
        if list(df.columns[:3]) != ["id", "pred_class", "status"] or df["id"].duplicated().any() \
                or set(df["id"]) != set(gold.index):
            stop(f"{name}: the predictions file does not hold the 1,000 annotated items as models_02_claude.py writes them")
        ok = (df["status"] == "ok") & df["pred_class"].isin(CLASSES)
        refused = (df["status"] == "refusal") & (df["pred_class"] == "")
        if not (ok | refused).all() or int(refused.sum()) != rec["refusals"]:
            stop(f"{name}: a prediction is neither a class nor a refusal, or the refusals differ from the record")
        return {"pred": df.set_index("id")["pred_class"], "cost_per_1000": Fraction(rec["cost_usd"]),
                "refusals_all_items": int(refused.sum()), "items_run": 1000, "compute_minutes": None}
    if spec["kind"] == "bart":
        if "id" not in df.columns or "pred_class" not in df.columns or df["id"].duplicated().any() \
                or set(df["id"]) != set(gold.index) or not df["pred_class"].isin(CLASSES).all():
            stop(f"{name}: the predictions file does not hold one class for each of the 1,000 annotated items")
        return {"pred": df.set_index("id")["pred_class"], "cost_per_1000": Fraction(0), "refusals_all_items": 0,
                "items_run": 1000, "compute_minutes": man.get("runtime_minutes"),
                "truncated_items": man.get("truncated_items")}
    labels = CLASSES if spec["stage"] == 2 else STAGE1_LABELS
    items = gold[gold["gold_stage2"].isin(CLASSES)] if spec["stage"] == 2 else gold[gold["gold_stage1"].isin(STAGE1_LABELS)]
    if list(df.columns[:3]) != ["id", "fold", "pred"] or df["id"].duplicated().any() or set(df["id"]) != set(items.index):
        stop(f"{name}: the predictions file does not hold the {len(items)} items of Stage {spec['stage']}")
    if (df.set_index("id")["fold"] != items["fold"].reindex(df["id"]).to_numpy()).any():
        stop(f"{name}: an item was predicted by a fold model other than the one its committed fold gives")
    if not df["pred"].isin(labels).all():
        stop(f"{name}: a prediction is not one of {labels}")
    best = [f["best_epoch"] for f in sorted(man["folds"], key=lambda f: f["fold"])]
    return {"pred": df.set_index("id")["pred"], "cost_per_1000": Fraction(0), "refusals_all_items": 0,
            "items_run": len(items), "compute_minutes": man.get("minutes"), "best_epochs": best}


def verify(gold: pd.DataFrame) -> tuple[dict, dict]:
    """Every prediction file: manifest, SHA-256 and structure. Returns the parsed runs and their SHA-256."""
    runs, shas = {}, {}
    for name in STAGE2 + STAGE1 + TEXT_ONLY:
        path, man, sha = open_run(name)
        runs[name] = {**parse_run(name, path, man, gold), "sha256": sha}
        shas[f"{name} predictions"] = sha
    return runs, shas


# =============================================================================
# metrics (exact)
# =============================================================================
def encode(pred: pd.Series, ids: list, labels: list) -> np.ndarray:
    """Label indices in the order of ids; -1 for a prediction of no class (a refusal)."""
    idx = {c: j for j, c in enumerate(labels)}
    return np.array([idx.get(pred.at[i], -1) for i in ids], dtype=np.int64)


def class_counts(p: np.ndarray, g: np.ndarray, k: int) -> tuple[list, list, list]:
    tp = [int(((p == c) & (g == c)).sum()) for c in range(k)]
    pp = [int((p == c).sum()) for c in range(k)]
    gg = [int((g == c).sum()) for c in range(k)]
    return tp, pp, gg


def f1_exact(tp: int, pp: int, gg: int) -> Fraction:
    if gg == 0:
        stop("a class has no gold item in an evaluated item set")
    return Fraction(2 * tp, pp + gg)


def stage2_metrics(p: np.ndarray, g: np.ndarray) -> dict:
    tp, pp, gg = class_counts(p, g, 3)
    f1 = [f1_exact(tp[c], pp[c], gg[c]) for c in range(3)]
    per = {}
    for c, name in enumerate(CLASSES):
        per[name] = {"f1": fl(f1[c]), "f1_exact": fr(f1[c]),
                     "precision": fl(Fraction(tp[c], pp[c])) if pp[c] else None,
                     "recall": fl(Fraction(tp[c], gg[c])), "tp": tp[c], "fp": pp[c] - tp[c], "fn": gg[c] - tp[c],
                     "support": gg[c]}
    macro = sum(f1, Fraction(0)) / 3
    confusion = {CLASSES[a]: {**{CLASSES[b]: int(((g == a) & (p == b)).sum()) for b in range(3)},
                              "no class": int(((g == a) & (p == -1)).sum())} for a in range(3)}
    return {"items": int(len(g)), "macro_f1": fl(macro), "macro_f1_exact": fr(macro),
            "accuracy": fl(Fraction(sum(tp), len(g))), "refusals": int((p == -1).sum()),
            "per_class": per, "confusion_gold_by_predicted": confusion, "_f1": f1, "_macro": macro}


def concern_rates(p: np.ndarray, g: np.ndarray, w: list | None) -> dict:
    """TPR and FPR for CONCERN against the other two classes. A refusal is not a CONCERN prediction."""
    pos, hit = (g == CONCERN), (p == CONCERN)
    if w is None:
        w = [Fraction(1)] * len(g)
    sp = sum((w[j] for j in range(len(g)) if pos[j]), Fraction(0))
    sn = sum((w[j] for j in range(len(g)) if not pos[j]), Fraction(0))
    tpr = sum((w[j] for j in range(len(g)) if pos[j] and hit[j]), Fraction(0)) / sp
    fpr = sum((w[j] for j in range(len(g)) if not pos[j] and hit[j]), Fraction(0)) / sn
    return {"tpr": fl(tpr), "fpr": fl(fpr), "tpr_minus_fpr": fl(tpr - fpr), "tpr_minus_fpr_exact": fr(tpr - fpr),
            "_j": tpr - fpr}


def wilson(k: int, n: int) -> dict:
    if n == 0:
        return {"accuracy": None, "wilson95_low": None, "wilson95_high": None}
    phat = k / n
    den = 1 + Z95 ** 2 / n
    centre = (phat + Z95 ** 2 / (2 * n)) / den
    half = Z95 * math.sqrt(phat * (1 - phat) / n + Z95 ** 2 / (4 * n * n)) / den
    return {"accuracy": fl(phat), "wilson95_low": fl(centre - half), "wilson95_high": fl(centre + half)}


def stage1_metrics(p: np.ndarray, g: np.ndarray, subs: list) -> dict:
    tp = int(((p == 1) & (g == 1)).sum())
    tn = int(((p == 0) & (g == 0)).sum())
    ny, nn = int((g == 1).sum()), int((g == 0).sum())
    ba = (Fraction(tp, ny) + Fraction(tn, nn)) / 2
    per_class = {"Y": dict(correct=tp, items=ny, **wilson(tp, ny)), "N": dict(correct=tn, items=nn, **wilson(tn, nn))}
    by_sub = {}
    for s in sorted(set(subs)):
        m = np.array([x == s for x in subs])
        k, n = int((p[m] == g[m]).sum()), int(m.sum())
        by_sub[s] = dict(correct=k, items=n, **wilson(k, n))
    return {"items": int(len(g)), "balanced_accuracy": fl(ba), "balanced_accuracy_exact": fr(ba),
            "accuracy": fl(Fraction(tp + tn, len(g))), "accuracy_by_class": per_class, "accuracy_by_subreddit": by_sub,
            "_ba": ba}


def fold_descriptives(p: np.ndarray, g: np.ndarray, folds: np.ndarray) -> dict:
    vals = {"macro_f1": []} | {c: [] for c in CLASSES}
    for k in range(1, cfg.N_FOLDS + 1):
        m = folds == k
        tp, pp, gg = class_counts(p[m], g[m], 3)
        f1 = [float(Fraction(2 * tp[c], pp[c] + gg[c])) if pp[c] + gg[c] else 0.0 for c in range(3)]
        vals["macro_f1"].append(sum(f1) / 3)
        for c, name in enumerate(CLASSES):
            vals[name].append(f1[c])
    return {k: {"mean": fl(np.mean(v)), "sd": fl(np.std(v, ddof=1)), "folds": [fl(x) for x in v]}
            for k, v in vals.items()}


# =============================================================================
# the permutation test
# =============================================================================
def coins(n: int) -> np.ndarray:
    return np.random.default_rng(cfg.SEED).integers(0, 2, size=(N_PERM, n), dtype=np.int8)


def permutation_test(pa: np.ndarray, pb: np.ndarray, g: np.ndarray, classes: list[int]) -> dict:
    """Two-sided item-level permutation test of the difference (a - b) in the mean F1 over `classes`
    (all three: macro-F1; [CONCERN]: CONCERN-class F1). Gold labels are never permuted."""
    n, k = len(g), len(classes)
    gg = [int((g == c).sum()) for c in classes]
    if min(gg) == 0:
        stop("a class has no gold item in an evaluated item set")
    tpa = np.stack([((pa == c) & (g == c)) for c in classes], 1).astype(np.int64)
    ppa = np.stack([(pa == c) for c in classes], 1).astype(np.int64)
    tpb = np.stack([((pb == c) & (g == c)) for c in classes], 1).astype(np.int64)
    ppb = np.stack([(pb == c) for c in classes], 1).astype(np.int64)
    d_tp, d_pp = (tpb - tpa).astype(np.float64), (ppb - ppa).astype(np.float64)
    tpa0, ppa0, tpb0, ppb0 = tpa.sum(0), ppa.sum(0), tpb.sum(0), ppb.sum(0)

    def stat(tp, pp):
        return sum((Fraction(2 * int(tp[j]), int(pp[j]) + gg[j]) for j in range(k)), Fraction(0)) / k

    observed = stat(tpa0, ppa0) - stat(tpb0, ppb0)
    target = abs(observed)
    flips = coins(n)
    gv = np.array(gg, dtype=np.float64)
    count, exact_checks = 0, 0
    for start in range(0, N_PERM, 2500):
        s = flips[start:start + 2500].astype(np.float64)
        s_tp, s_pp = s @ d_tp, s @ d_pp                    # exact small integers in float64
        tp_a, pp_a = tpa0 + s_tp, ppa0 + s_pp
        tp_b, pp_b = tpb0 - s_tp, ppb0 - s_pp
        diff = np.abs((2 * tp_a / (pp_a + gv)).mean(1) - (2 * tp_b / (pp_b + gv)).mean(1))
        above, below = diff > float(target) + 1e-9, diff < float(target) - 1e-9
        count += int(above.sum())
        for r in np.nonzero(~above & ~below)[0]:          # too close for floating point: decide exactly
            exact_checks += 1
            d = stat(np.rint(tp_a[r]), np.rint(pp_a[r])) - stat(np.rint(tp_b[r]), np.rint(pp_b[r]))
            count += abs(d) >= target
    p = Fraction(max(count, 1), N_PERM)
    return {"items": n, "difference": fl(observed), "difference_exact": fr(observed),
            "permutations_at_least_as_extreme": count, "p": fl(p, 4), "p_exact": fr(p), "_p": p,
            "exact_comparisons": exact_checks}


def holm(ps: list[Fraction]) -> list[Fraction]:
    m = len(ps)
    order = sorted(range(m), key=lambda j: (ps[j], j))
    adj, running = [None] * m, Fraction(0)
    for rank, j in enumerate(order):
        running = max(running, min(Fraction(1), (m - rank) * ps[j]))
        adj[j] = running
    return adj


def pairwise(models: list[str], enc: dict, g: np.ndarray, family: str, scope: str, correct: bool) -> list[dict]:
    rows = []
    for a, b in combinations(models, 2):
        t = permutation_test(enc[a], enc[b], g, [0, 1, 2])
        rows.append({"family": family, "scope": scope, "a": a, "b": b, "statistic": "macro-F1", **t})
    if correct:
        for r, adj in zip(rows, holm([r["_p"] for r in rows])):
            r["p_holm"], r["p_holm_exact"] = fl(adj, 4), fr(adj)
            r["result"] = "significant" if adj < LEVEL else "not demonstrably significant"
    return rows


# =============================================================================
# Krippendorff's alpha (nominal)
# =============================================================================
def item_matrices(units: list[list[str]], cats: list[str]) -> np.ndarray:
    """Each item's contribution to the coincidence matrix (zero for an item with fewer than two values)."""
    idx = {c: j for j, c in enumerate(cats)}
    mats = np.zeros((len(units), len(cats), len(cats)))
    for u, vals in enumerate(units):
        m = len(vals)
        if m < 2:
            continue
        v = np.zeros(len(cats))
        for x in vals:
            v[idx[x]] += 1
        mats[u] = (np.outer(v, v) - np.diag(v)) / (m - 1)
    return mats


def alpha_exact(units: list[list[str]], cats: list[str]):
    """Nominal alpha from the coincidence matrix, exactly; None if there is no variation."""
    o = {(a, b): Fraction(0) for a in cats for b in cats}
    for vals in units:
        m = len(vals)
        if m < 2:
            continue
        cnt = Counter(vals)
        for a in cnt:
            for b in cnt:
                o[(a, b)] += Fraction(cnt[a] * (cnt[b] - (a == b)), m - 1)
    n_c = {a: sum(o[(a, b)] for b in cats) for a in cats}
    n = sum(n_c.values())
    disagree = sum(o[(a, b)] for a in cats for b in cats if a != b)
    expected = n * n - sum(x * x for x in n_c.values())
    if n == 0 or expected == 0:
        return None
    return 1 - (n - 1) * disagree / expected


def alpha_batch(o: np.ndarray) -> np.ndarray:
    """alpha for a batch of coincidence matrices (B x K x K); NaN where it is undefined."""
    n_c = o.sum(-1)
    n = n_c.sum(-1)
    disagree = o.sum((-2, -1)) - np.trace(o, axis1=-2, axis2=-1)
    expected = n * n - (n_c ** 2).sum(-1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(expected > 0, 1 - (n - 1) * disagree / expected, np.nan)


def reliability_units(key: pd.DataFrame, long: pd.DataFrame) -> tuple[list, list]:
    """Stage 1 and Stage 2 values of each reliability item, one per rating that is not missing, items in id order."""
    ids = sorted(key.index[key["is_reliability"]])
    if len(ids) != 100:
        stop("each tranche must have 100 reliability items")
    s1, s2 = [], []
    for i in ids:
        r = long[(long["id"] == i) & (~long["missing"])]
        s1.append(r["stage1_relevant"].tolist())
        s2.append([x for x, y in zip(r["stage2_class"], r["stage1_relevant"]) if y == "Y" and x])
    return s1, s2


def measures(s1: list, s2: list) -> list:
    return [("Stage 1", s1, ["N", "Y"]), ("Stage 2", s2, CLASSES)] + \
           [(f"{c} against the rest", [["1" if x == c else "0" for x in v] for v in s2], ["0", "1"]) for c in CLASSES]


def alpha_rows(s1: list, s2: list, intervals: bool = True) -> dict:
    """The five alphas of one set of reliability items. Intervals by the method of Deviation 4: 10,000
    item-level bootstrap resamples of the items, drawn with seed 24916660
    (numpy.random.default_rng(24916660).integers(0, n, size=(10000, n)), items in id order), all five alphas
    computed on the same resamples; the 95% percentile interval (2.5th and 97.5th percentiles, numpy's
    linear interpolation) and the share of resamples below 0.7. A resample on which an alpha is undefined (no
    variation) is counted and left out of that alpha's interval and share."""
    rows = {}
    n = len(s1)
    if intervals:
        draws = np.random.default_rng(cfg.SEED).integers(0, n, size=(N_PERM, n))
        counts = np.bincount((draws + n * np.arange(N_PERM)[:, None]).ravel(),
                             minlength=N_PERM * n).reshape(N_PERM, n).astype(np.float64)
    for name, units, cats in measures(s1, s2):
        a = alpha_exact(units, cats)
        pairable = [u for u in units if len(u) >= 2]
        rows[name] = {"alpha": fl(a, 4) if a is not None else None, "alpha_exact": fr(a) if a is not None else None,
                      "units": len(pairable), "pairable_values": int(sum(len(u) for u in pairable)), "_alpha": a}
        if intervals:
            k = len(cats)
            boot = alpha_batch((counts @ item_matrices(units, cats).reshape(n, k * k)).reshape(N_PERM, k, k))
            ok = boot[~np.isnan(boot)]
            rows[name]["interval95"] = {
                "low": fl(np.percentile(ok, 2.5)) if ok.size else None,
                "high": fl(np.percentile(ok, 97.5)) if ok.size else None,
                "share_of_resamples_below_0.7": fl(float((ok < 0.7).mean()), 4) if ok.size else None,
                "resamples_undefined": int(np.isnan(boot).sum())}
    return rows


def check_tranche1_alpha(key1, long1) -> None:
    """The alpha code must reproduce the tranche 1 agreement recorded in September."""
    got = alpha_rows(*reliability_units(key1, long1), intervals=False)
    found = {k: (f"{float(v['_alpha']):.3f}" if v["_alpha"] is not None else None) for k, v in got.items()}
    if found != TRANCHE1_ALPHA_RECORDED:
        stop(f"the tranche 1 agreement does not reproduce the figures recorded in September: {found}. "
             f"Take this message to Claude.")


def reliability(key1, long1, key2, long2) -> dict:
    u11, u12 = reliability_units(key1, long1)
    u21, u22 = reliability_units(key2, long2)
    return {"both tranches (200 items)": alpha_rows(u11 + u21, u12 + u22),
            "tranche 1 (100 items)": alpha_rows(u11, u12),
            "tranche 2 (100 items)": alpha_rows(u21, u22)}


# =============================================================================
# the evaluation
# =============================================================================
def evaluate(gold, subreddit, runs, weights, key1, long1, key2, long2) -> dict:
    # ---- reliability first: it reads no prediction -----------------------------------------
    rel = reliability(key1, long1, key2, long2)

    # ---- Stage 2 --------------------------------------------------------------------------
    prim = sorted(gold.index[gold["gold_stage2"].isin(CLASSES)])
    g2 = np.array([CLASSES.index(gold.at[i, "gold_stage2"]) for i in prim], dtype=np.int64)
    tr = np.array([int(gold.at[i, "tranche"]) for i in prim])
    fo = np.array([int(gold.at[i, "fold"]) for i in prim])
    w2 = [weights[i] for i in prim]
    enc = {n: encode(runs[n]["pred"], prim, CLASSES) for n in STAGE2}
    from sklearn.metrics import f1_score                      # a second implementation, as a check
    m2 = {}
    for n in STAGE2:
        pooled = stage2_metrics(enc[n], g2)
        check = f1_score(g2, enc[n], labels=[0, 1, 2], average=None, zero_division=0)
        if np.abs(check - np.array([float(x) for x in pooled["_f1"]])).max() > 1e-12:
            stop(f"{n}: the two F1 implementations disagree. Take this message to Claude.")
        m2[n] = {"name": NAMES[n], "pooled": pooled,
                 "tranche1": stage2_metrics(enc[n][tr == 1], g2[tr == 1]),
                 "tranche2": stage2_metrics(enc[n][tr == 2], g2[tr == 2]),
                 "folds": fold_descriptives(enc[n], g2, fo),
                 "concern_rates_weighted": concern_rates(enc[n], g2, w2),
                 "concern_rates_unweighted": concern_rates(enc[n], g2, None),
                 "cost_usd_per_1000_comments": fl(runs[n]["cost_per_1000"]), "_cost": runs[n]["cost_per_1000"],
                 "refusals_all_items": runs[n]["refusals_all_items"],
                 "refusal_rate_all_items": fl(Fraction(runs[n]["refusals_all_items"], runs[n]["items_run"])),
                 "items_run": runs[n]["items_run"], "compute_minutes": runs[n]["compute_minutes"],
                 "truncated_items": runs[n].get("truncated_items")}

    family_b = pairwise(FAMILY_B, enc, g2, "B", "both tranches, universal schema", correct=True)
    family_c = [r for r in pairwise(FINE_TUNED + ZERO_SHOT_DOMAIN, enc, g2, "C", "both tranches, domain-specific schema",
                                    False) if not (r["a"] in FINE_TUNED and r["b"] in FINE_TUNED)]
    for t in (1, 2):
        sub = {n: enc[n][tr == t] for n in FAMILY_B}
        family_c += pairwise(FAMILY_B, sub, g2[tr == t], "C", f"tranche {t}, universal schema", False)
    for a, b in SCHEMA_PAIRS:
        family_c.append({"family": "C", "scope": "both tranches, universal against domain-specific", "a": a, "b": b,
                         "statistic": "macro-F1", **permutation_test(enc[a], enc[b], g2, [0, 1, 2])})

    # deployment
    f1c = {n: m2[n]["pooled"]["_f1"][CONCERN] for n in STAGE2}
    top = max(f1c.values())
    leaders = [n for n in STAGE2 if f1c[n] == top]
    leader = leaders[0]
    tie_tests = []
    for n in STAGE2:
        if n == leader:
            continue
        t = permutation_test(enc[leader], enc[n], g2, [CONCERN])
        tie_tests.append({"family": "tie test (defines ties only; not a reported comparison)", "scope": "both tranches",
                          "a": leader, "b": n, "statistic": "CONCERN-class F1", **t, "tied": t["_p"] >= LEVEL})
    tied = [n for n in STAGE2 if n == leader or any(r["b"] == n and r["tied"] for r in tie_tests)]
    best_j = max(m2[n]["concern_rates_weighted"]["_j"] for n in tied)
    step1 = [n for n in tied if m2[n]["concern_rates_weighted"]["_j"] == best_j]
    low_cost = min(m2[n]["_cost"] for n in step1)
    step2 = [n for n in step1 if m2[n]["_cost"] == low_cost]
    deployed2 = step2[0]
    decided_by = ("CONCERN-class F1 (no configuration tied)" if len(tied) == 1 else
                  "weighted TPR - FPR for CONCERN" if len(step1) == 1 else
                  "cost per 1,000 comments" if len(step2) == 1 else "the committed order")
    deployment2 = {"leader": leader, "leader_concern_f1": fl(top), "leader_concern_f1_exact": fr(top),
                   "configurations_sharing_the_highest_value": leaders, "tied_with_leader": tied,
                   "after_weighted_tpr_minus_fpr": step1, "after_cost": step2, "deployed": deployed2,
                   "decided_by": decided_by}
    rates = m2[deployed2]["concern_rates_weighted"]
    correction = {"configuration": deployed2, "weighted": strip_private(rates),
                  "unweighted": strip_private(m2[deployed2]["concern_rates_unweighted"]),
                  "note": "The same items choose the deployed classifier and supply its error rates, so the rates "
                          "are somewhat optimistic (Deviation 12)."}
    if deployed2 in FINE_TUNED:
        correction["final_retraining_epochs"] = sorted(runs[deployed2]["best_epochs"])[2]

    # the two predictions
    macro = {n: m2[n]["pooled"]["_macro"] for n in STAGE2}
    ft_best = [n for n in FINE_TUNED if macro[n] == max(macro[x] for x in FINE_TUNED)][0]
    zs_best = [n for n in ZERO_SHOT_UNIVERSAL if macro[n] == max(macro[x] for x in ZERO_SHOT_UNIVERSAL)][0]
    gaps = {c: m2[ft_best]["pooled"]["_f1"][j] - m2[zs_best]["pooled"]["_f1"][j] for j, c in enumerate(CLASSES)}
    p1 = all(gaps["CONCERN"] > gaps[c] for c in CLASSES if c != "CONCERN")
    other_lowest = {n: all(m2[n]["pooled"]["_f1"][2] < m2[n]["pooled"]["_f1"][j] for j in (0, 1)) for n in FAMILY_B}
    p2 = sum(other_lowest.values()) >= 3
    predictions = {
        "1": {"better_fine_tuned_model": ft_best, "best_zero_shot_model_universal": zs_best,
              "gap_in_f1_fine_tuned_minus_zero_shot": {c: fl(v) for c, v in gaps.items()},
              "largest_gap": [c for c in CLASSES if gaps[c] == max(gaps.values())],
              "classes_where_zero_shot_is_better": [c for c in CLASSES if gaps[c] < 0],
              "result": "confirmed" if p1 else "not confirmed"},
        "2": {"other_has_the_lowest_f1": other_lowest, "models": int(sum(other_lowest.values())),
              "result": "confirmed" if p2 else "not confirmed"},
    }

    # ---- Stage 1 --------------------------------------------------------------------------
    s1_ids = sorted(gold.index[gold["gold_stage1"].isin(STAGE1_LABELS)])
    g1 = np.array([STAGE1_LABELS.index(gold.at[i, "gold_stage1"]) for i in s1_ids], dtype=np.int64)
    subs = [subreddit.at[i] for i in s1_ids]
    m1 = {n: {"name": NAMES[n], **stage1_metrics(encode(runs[n]["pred"], s1_ids, STAGE1_LABELS), g1, subs)}
          for n in STAGE1}
    top1 = max(m1[n]["_ba"] for n in STAGE1)
    cands = [n for n in STAGE1 if m1[n]["_ba"] == top1]
    deployed1 = cands[0]
    variant = deployed1 + "-textonly"
    m1[variant] = {"name": NAMES[variant], **stage1_metrics(encode(runs[variant]["pred"], s1_ids, STAGE1_LABELS), g1, subs)}
    deployment1 = {"deployed": deployed1, "balanced_accuracy": {n: m1[n]["balanced_accuracy"] for n in STAGE1},
                   "decided_by": "balanced accuracy" if len(cands) == 1 else
                   "an exact tie, to the lower cost (fewer parameters: DistilBERT)",
                   "text_only_variant": variant,
                   "final_retraining_epochs": sorted(runs[deployed1]["best_epochs"])[2]}

    # ---- success criteria ----------------------------------------------------------------
    both = rel["both tranches (200 items)"]
    s1a, s2a = both["Stage 1"]["_alpha"], both["Stage 2"]["_alpha"]
    below = [f"{k} {v['alpha']}" for k, v in both.items() if k.endswith("the rest") and v["_alpha"] is not None
             and v["_alpha"] < RELIABILITY_BAR]
    criteria = {
        "1": {"text": "Krippendorff's alpha is at least 0.7 at Stage 1 and at Stage 2 on the 200 reliability items.",
              "stage1_alpha": fl(s1a, 4), "stage2_alpha": fl(s2a, 4),
              "result": "met" if s1a is not None and s2a is not None and s1a >= RELIABILITY_BAR and s2a >= RELIABILITY_BAR
              else "not met", "per_class_alpha_below_0.7": below},
        "2": {"text": "The model comparison is completed under R5 and Deviation 12, with a measured cost and refusal "
                      "rate for every configuration.",
              "result": "met" if all(m2[n]["cost_usd_per_1000_comments"] is not None
                                     and m2[n]["refusal_rate_all_items"] is not None for n in STAGE2) else "not met"},
        "6": {"text": "The deployed Stage 2 classifier has a TPR - FPR for CONCERN of at least 0.25 on the primary "
                      "item set (weighted by the pooled design weights, as the correction uses it).",
              "configuration": deployed2, "weighted": rates["tpr_minus_fpr"],
              "unweighted": m2[deployed2]["concern_rates_unweighted"]["tpr_minus_fpr"],
              "result": "met" if rates["_j"] >= CRITERION6_BAR else
              "not met: the uncorrected series is reported beside the corrected one and the instability is stated"},
        "3, 4, 5": "settled by later analyses (prevalence, temporal calibration check, relevance rate)",
    }
    return {
        "specification": "R5 and Deviation 12 (docs/analysis_preregistration.md); models_config.py at bb3fbfe; "
                         "models_05_evaluate.py",
        "permutation_test": {"permutations": N_PERM, "seed": cfg.SEED, "two_sided": True,
                             "p": "share of permutations with |difference| >= |observed|, floored at 1/N"},
        "item_sets": {"stage2_primary": {"items": len(prim), "tranche1": int((tr == 1).sum()),
                                         "tranche2": int((tr == 2).sum()),
                                         "by_class": {c: int((g2 == j).sum()) for j, c in enumerate(CLASSES)}},
                      "stage1": {"items": len(s1_ids), "Y": int((g1 == 1).sum()), "N": int((g1 == 0).sum())}},
        "stage2": {"configurations": m2, "family_b": family_b, "family_c": family_c,
                   "deployment": deployment2, "deployment_tie_tests": tie_tests,
                   "prevalence_correction_error_rates": correction, "predictions": predictions},
        "stage1": {"configurations": m1, "deployment": deployment1},
        "reliability": rel,
        "success_criteria": criteria,
    }


# =============================================================================
# main
# =============================================================================
def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="The evaluation of record (Deviation 12).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="check every input; read no label against a prediction")
    mode.add_argument("--confirm-committed", action="store_true",
                      help="the evaluation of record: this file is committed and its SHA-256 recorded")
    args = ap.parse_args()
    print("Model comparison, step 5: the evaluation of record (Deviation 12)\n")
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit: checks the inputs, scores nothing) or --confirm-committed "
             "(after the commit: the evaluation of record).")
    me = text_sha256(Path(__file__).resolve())
    print(f"this script: models_05_evaluate.py SHA-256 {me}")
    check_record_complete()
    if (EVAL_DIR / "evaluation_results.json").exists():
        stop(f"the evaluation has already been run: its results are in {EVAL_DIR}. It is run once. "
             f"Take this message to Claude.")
    versions = check_libraries()
    scripts = check_scripts()
    print(f"scripts of record: {', '.join(scripts)} match bb3fbfe")
    gold, shas = load_gold()
    subreddit, more = load_inputs(gold)
    shas.update(more)
    print(f"gold labels: both tranches match the recorded fingerprints; folds match the committed fold files; "
          f"{GOLD_ITEMS['stage1']} items with a Stage 1 label, {GOLD_ITEMS['stage2']} with a Stage 2 class")
    runs, more = verify(gold)
    shas.update(more)
    print(f"predictions: all {len(runs)} files match the SHA-256 recorded for them; their manifests and structure "
          f"are as the model scripts write them")
    key1, long1, key2, long2, weights, key2_sha = load_keys()
    shas["tranche2_master_key.csv"] = key2_sha
    print("pooled design weights: N_h / n_h with n_h = 334 / 334 / 332 (Deviation 11); the tranche 2 key matches its "
          "recorded SHA-256")
    check_tranche1_alpha(key1, long1)
    print("agreement: the alpha code reproduces the tranche 1 figures recorded in September")
    if args.preflight:
        print("\nPREFLIGHT PASSED: every input is in place and matches the record. No prediction was set against a "
              "label, nothing was scored and no result was written.")
        return
    print()
    results = evaluate(gold, subreddit, runs, weights, key1, long1, key2, long2)
    results["inputs_sha256"] = shas
    write_outputs(strip_private(results), me, versions)


# =============================================================================
# outputs
# =============================================================================
OUTPUT_FILES = ("evaluation_report.md", "stage2_metrics.csv", "pairwise_tests.csv", "stage1_metrics.csv",
                "reliability_alpha.csv")


def write_outputs(results: dict, me: str, versions: dict) -> None:
    """Every output is written to a work folder first and moved into place, evaluation_results.json
    last: a run that fails part-way leaves no results file, so it can simply be run again (it gives the
    same bytes)."""
    work = EVAL_DIR.parent / "evaluation_in_progress"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    write_files(work, results)
    outputs = {name: mc.sha256_file(work / name) for name in ("evaluation_results.json",) + OUTPUT_FILES}
    mc.write_json(work / "evaluation_manifest.json", {
        "created": mc.now_iso(), "script_sha256": me, "versions": {**mc.versions("numpy", "pandas", "sklearn"), **versions},
        "inputs_sha256": results["inputs_sha256"], "outputs_sha256": outputs})
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    for name in OUTPUT_FILES + ("evaluation_manifest.json", "evaluation_results.json"):
        mc.replace_patiently(work / name, EVAL_DIR / name)
    shutil.rmtree(work, ignore_errors=True)
    print_summary(results)
    s2 = results["stage2"]
    d2, d1 = s2["deployment"], results["stage1"]["deployment"]
    mc.show_register_block(EVAL_DIR / "PASTE_evaluation_block.txt", [
        f"- `models_05_evaluate.py` (SHA-256 `{me}`) run {mc.now_iso()}; every input matched its recorded SHA-256.",
        f"- `evaluation_results.json` SHA-256 `{outputs['evaluation_results.json']}`; "
        f"`evaluation_report.md` `{outputs['evaluation_report.md']}`.",
        f"- Deployed Stage 2 classifier: {NAMES[d2['deployed']]} (decided by {d2['decided_by']}).",
        f"- Deployed Stage 1 classifier: {NAMES[d1['deployed']]} (decided by {d1['decided_by']}).",
        f"- Prediction 1: {s2['predictions']['1']['result']}; prediction 2: {s2['predictions']['2']['result']}.",
        f"- Success criteria: 1 {results['success_criteria']['1']['result']}; 2 "
        f"{results['success_criteria']['2']['result']}; 6 {results['success_criteria']['6']['result']}.",
    ])


def write_files(out: Path, results: dict) -> None:
    mc.write_json(out / "evaluation_results.json", results)
    s2 = results["stage2"]
    rows = []
    for n, m in s2["configurations"].items():
        for scope in ("pooled", "tranche1", "tranche2"):
            x = m[scope]
            rows.append([n, scope, x["items"], x["macro_f1"]] + [x["per_class"][c]["f1"] for c in CLASSES]
                        + [x["accuracy"], x["refusals"]]
                        + ([m["concern_rates_weighted"]["tpr"], m["concern_rates_weighted"]["fpr"],
                            m["concern_rates_weighted"]["tpr_minus_fpr"], m["cost_usd_per_1000_comments"],
                            m["refusal_rate_all_items"]] if scope == "pooled" else ["", "", "", "", ""]))
    mc.write_rows_csv(out / "stage2_metrics.csv",
                      ["configuration", "item_set", "items", "macro_f1", "f1_concern", "f1_endorsement", "f1_other",
                       "accuracy", "refusals_on_items", "weighted_tpr_concern", "weighted_fpr_concern",
                       "weighted_tpr_minus_fpr", "cost_usd_per_1000", "refusal_rate_all_items"], rows)
    tests = s2["family_b"] + s2["family_c"] + s2["deployment_tie_tests"]
    mc.write_rows_csv(out / "pairwise_tests.csv",
                      ["family", "scope", "a", "b", "statistic", "items", "difference", "p", "p_holm", "result"],
                      [[t["family"], t["scope"], t["a"], t["b"], t["statistic"], t["items"], t["difference"], t["p"],
                        t.get("p_holm", ""), t.get("result", "tied" if t.get("tied") else
                                                   ("not tied" if "tied" in t else ""))] for t in tests])
    s1 = results["stage1"]["configurations"]
    mc.write_rows_csv(out / "stage1_metrics.csv",
                      ["configuration", "group", "correct", "items", "accuracy", "wilson95_low", "wilson95_high"],
                      [[n, f"class {c}", v["correct"], v["items"], v["accuracy"], v["wilson95_low"], v["wilson95_high"]]
                       for n, m in s1.items() for c, v in m["accuracy_by_class"].items()]
                      + [[n, f"r/{s}", v["correct"], v["items"], v["accuracy"], v["wilson95_low"], v["wilson95_high"]]
                         for n, m in s1.items() for s, v in m["accuracy_by_subreddit"].items()])
    mc.write_rows_csv(out / "reliability_alpha.csv",
                      ["items", "measure", "alpha", "units", "pairable_values", "interval95_low", "interval95_high",
                       "share_of_resamples_below_0.7"],
                      [[k, name, v["alpha"], v["units"], v["pairable_values"], v["interval95"]["low"],
                        v["interval95"]["high"], v["interval95"]["share_of_resamples_below_0.7"]]
                       for k, d in results["reliability"].items() for name, v in d.items()])
    with open(out / "evaluation_report.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(render_report(results))


def pfmt(t: dict) -> str:
    """A p-value for the tables; the floor 1/N is marked."""
    return f"{t['p']:.4f}" + (" (floor: no permutation reached it)" if t["permutations_at_least_as_extreme"] == 0 else "")


def render_report(r: dict) -> str:
    s2, s1 = r["stage2"], r["stage1"]
    L = ["# Evaluation of record (Deviation 12)", "",
         f"Primary item set: {r['item_sets']['stage2_primary']['items']} items "
         f"(tranche 1 {r['item_sets']['stage2_primary']['tranche1']}, tranche 2 {r['item_sets']['stage2_primary']['tranche2']}; "
         + ", ".join(f"{c} {n}" for c, n in r['item_sets']['stage2_primary']['by_class'].items()) + ").", "",
         "## Stage 2: the eight configurations (both tranches, unweighted)", "",
         "| Configuration | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | Refusals (primary items) | "
         "Refusal rate (all items run) | Weighted TPR - FPR (CONCERN) | Cost per 1,000 (US$) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for n, m in s2["configurations"].items():
        x = m["pooled"]
        L.append(f"| {m['name']} | {x['macro_f1']:.3f} | " + " | ".join(f"{x['per_class'][c]['f1']:.3f}" for c in CLASSES)
                 + f" | {x['refusals']} | {m['refusal_rate_all_items']:.3f} | "
                 f"{m['concern_rates_weighted']['tpr_minus_fpr']:.3f} | {m['cost_usd_per_1000_comments']:.4f} |")
    L += ["", "Per tranche (macro-F1; per-class F1 in evaluation_results.json):", "",
          "| Configuration | Tranche 1 | Tranche 2 | Mean over the five folds (SD) |", "|---|---|---|---|"]
    for n, m in s2["configurations"].items():
        fo = m["folds"]["macro_f1"]
        L.append(f"| {m['name']} | {m['tranche1']['macro_f1']:.3f} | {m['tranche2']['macro_f1']:.3f} | "
                 f"{fo['mean']:.3f} ({fo['sd']:.3f}) |")
    L += ["", "## Family B (Holm-Bonferroni across ten, 0.05)", "",
          "| Comparison | Difference in macro-F1 | p | p (Holm) | Result |", "|---|---|---|---|---|"]
    for t in s2["family_b"]:
        L.append(f"| {NAMES[t['a']]} vs {NAMES[t['b']]} | {t['difference']:+.3f} | {pfmt(t)} | {t['p_holm']:.4f} | "
                 f"{t['result']} |")
    L += ["", "## Family C (exploratory, uncorrected)", "", "| Scope | Comparison | Difference in macro-F1 | p |",
          "|---|---|---|---|"]
    for t in s2["family_c"]:
        L.append(f"| {t['scope']} | {NAMES[t['a']]} vs {NAMES[t['b']]} | {t['difference']:+.3f} | {pfmt(t)} |")
    d = s2["deployment"]
    L += ["", "## Stage 2 deployment", "",
          f"Highest CONCERN-class F1: {NAMES[d['leader']]} ({d['leader_concern_f1']:.3f}). The tests below only define "
          f"ties (Deviation 12); they are not reported comparisons.", "",
          "| Against | Difference in CONCERN F1 | p | Tied (p >= 0.05) |", "|---|---|---|---|"]
    for t in s2["deployment_tie_tests"]:
        L.append(f"| {NAMES[t['b']]} | {t['difference']:+.3f} | {pfmt(t)} | {'yes' if t['tied'] else 'no'} |")
    L += ["", f"Tied set: {', '.join(NAMES[n] for n in d['tied_with_leader'])}. "
              f"**Deployed: {NAMES[d['deployed']]}**, decided by {d['decided_by']}.", ""]
    c = s2["prevalence_correction_error_rates"]
    L += ["## Error rates for adjusted classify-and-count (deployed configuration)", "",
          f"Weighted: TPR {c['weighted']['tpr']:.4f}, FPR {c['weighted']['fpr']:.4f}, TPR - FPR "
          f"{c['weighted']['tpr_minus_fpr']:.4f}. Unweighted: TPR {c['unweighted']['tpr']:.4f}, FPR "
          f"{c['unweighted']['fpr']:.4f}, TPR - FPR {c['unweighted']['tpr_minus_fpr']:.4f}. {c['note']}", ""]
    p = s2["predictions"]
    neg = p["1"]["classes_where_zero_shot_is_better"]
    L += ["## The two predictions", "",
          f"1. Better fine-tuned model {NAMES[p['1']['better_fine_tuned_model']]}, best zero-shot "
          f"{NAMES[p['1']['best_zero_shot_model_universal']]}; gaps in F1 (fine-tuned minus zero-shot) "
          + ", ".join(f"{k} {v:+.3f}" for k, v in p['1']['gap_in_f1_fine_tuned_minus_zero_shot'].items())
          + f": **{p['1']['result']}**." + (f" The zero-shot model is better on {', '.join(neg)}." if neg else ""),
          f"2. OTHER has the lowest per-class F1 for {p['2']['models']} of the five models: **{p['2']['result']}**.", ""]
    d1 = s1["deployment"]
    L += ["## Stage 1", "", "| Model | Balanced accuracy | Accuracy, Y | Accuracy, N |", "|---|---|---|---|"]
    for n, m in s1["configurations"].items():
        L.append(f"| {m['name']} | {m['balanced_accuracy']:.3f} | {m['accuracy_by_class']['Y']['accuracy']:.3f} | "
                 f"{m['accuracy_by_class']['N']['accuracy']:.3f} |")
    L += ["", f"**Deployed: {NAMES[d1['deployed']]}**, decided by {d1['decided_by']}. Text-only variant: "
              f"{NAMES[d1['text_only_variant']]}.", "", "Accuracy by subreddit (correct / items, Wilson 95% interval):", "",
          "| Subreddit | " + " | ".join(m["name"] for m in s1["configurations"].values()) + " |",
          "|---|" + "---|" * len(s1["configurations"])]
    for s in sorted({s for m in s1["configurations"].values() for s in m["accuracy_by_subreddit"]}):
        cells = []
        for m in s1["configurations"].values():
            v = m["accuracy_by_subreddit"][s]
            cells.append(f"{v['correct']}/{v['items']} ({v['wilson95_low']:.2f} to {v['wilson95_high']:.2f})")
        L.append(f"| r/{s} | " + " | ".join(cells) + " |")
    L += ["", "## Reliability (Krippendorff's alpha, nominal)", "",
          "| Items | Measure | Alpha | 95% interval | Share of resamples below 0.7 | Units | Pairable values |",
          "|---|---|---|---|---|---|---|"]
    for k, dd in r["reliability"].items():
        for name, v in dd.items():
            iv = v["interval95"]
            span = f"{iv['low']:.3f} to {iv['high']:.3f}" if iv["low"] is not None else "n/a"
            alpha = f"{v['alpha']:.3f}" if v["alpha"] is not None else "n/a"
            below = iv["share_of_resamples_below_0.7"]
            L.append(f"| {k} | {name} | {alpha} | {span} | {below if below is not None else 'n/a'} | {v['units']} | "
                     f"{v['pairable_values']} |")
    sc = r["success_criteria"]
    L += ["", "## Success criteria", "",
          f"1. {sc['1']['result']}: Stage 1 alpha {sc['1']['stage1_alpha']}, Stage 2 alpha {sc['1']['stage2_alpha']} "
          "on the 200 reliability items" +
          (f"; per-class alpha below 0.7: {', '.join(sc['1']['per_class_alpha_below_0.7'])}"
           if sc['1']['per_class_alpha_below_0.7'] else "; no per-class alpha below 0.7") + ".",
          f"2. {sc['2']['result']}.",
          f"6. {sc['6']['result']}: weighted TPR - FPR {sc['6']['weighted']:.4f} (unweighted "
          f"{sc['6']['unweighted']:.4f}) for {NAMES[sc['6']['configuration']]}.",
          f"3, 4, 5: {sc['3, 4, 5']}.", ""]
    return "\n".join(L)


def print_summary(r: dict) -> None:
    s2, s1 = r["stage2"], r["stage1"]
    print("Stage 2, both tranches (macro-F1 | F1 CONCERN, ENDORSEMENT, OTHER):")
    for n, m in s2["configurations"].items():
        x = m["pooled"]
        print(f"  {m['name']:<36} {x['macro_f1']:.3f} | " + ", ".join(f"{x['per_class'][c]['f1']:.3f}" for c in CLASSES))
    print("Family B (Holm across ten):")
    for t in s2["family_b"]:
        print(f"  {t['a']} vs {t['b']}: {t['difference']:+.3f}, p {t['p']:.4f}, p(Holm) {t['p_holm']:.4f}, {t['result']}")
    d = s2["deployment"]
    print(f"Stage 2 deployed: {NAMES[d['deployed']]} (decided by {d['decided_by']})")
    c = s2["prevalence_correction_error_rates"]["weighted"]
    print(f"  weighted TPR {c['tpr']:.4f}, FPR {c['fpr']:.4f}, TPR - FPR {c['tpr_minus_fpr']:.4f}")
    print(f"Prediction 1: {s2['predictions']['1']['result']}; prediction 2: {s2['predictions']['2']['result']}")
    print(f"Stage 1 deployed: {NAMES[s1['deployment']['deployed']]} (decided by {s1['deployment']['decided_by']})")
    sc = r["success_criteria"]
    print(f"Success criteria: 1 {sc['1']['result']}; 2 {sc['2']['result']}; 6 {sc['6']['result']}")
    print(f"\nWritten to {EVAL_DIR}: evaluation_results.json, evaluation_report.md, four CSV tables, the manifest.")


if __name__ == "__main__":
    main()
