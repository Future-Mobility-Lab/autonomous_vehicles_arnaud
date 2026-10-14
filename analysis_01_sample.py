"""Sample analyses of record (on the PC): the analyses of the 1,000 annotated items that Deviation 13 of
docs/analysis_preregistration.md assigns to "the sample-analysis script".

From the repository folder, with the virtual environment active (no GPU, no internet):
    python analysis_01_sample.py --preflight
        Before the commit. Checks every input that has a record against it, reproduces the figures of record that
        rest on these inputs, and compares four previews with what this script computes. It then runs every
        analysis once as a dry run on the real inputs with each item's era, temporal block and design weight taken
        from another item, so that the code is exercised without computing any figure by the real era or block,
        and discards the result unseen. The lexical proxy uses none of the three, so the dry run computes it on the
        real items and discards it unseen with the rest; the annotators' tranche 1 sheets keep their own eras, and
        no figure by era is formed from them. It shows no rate by temporal block and writes nothing. For each
        preview it prints "same", or,
        if the preview differs, the values this script computes (all four previews are figures the author has
        already seen; two of them, the tranche 1 pi_s and decomposition, are computed by era, as they were then).
    python analysis_01_sample.py --confirm-committed
        After this file is committed and its SHA-256 recorded. The run of record. It runs once: it refuses to
        start if this file's results already exist (the SHA-256 is that of the file with LF line endings, as the
        register records script hashes).

It runs no model and reads no output of a corpus run. Its inputs are the files of record of both tranches (read
through models_01_prepare.py), the gold labels, the cross-validated and zero-shot predictions of the evaluation of
record and the model inputs (read through models_05_evaluate.py, which checks each against its recorded SHA-256),
the evaluation output of record, corpus v2.2 (each annotated item's creation time, year, subreddit, tier and text),
the frozen draw frame, and config.py for the term list of the lexical proxy. Every rule it applies is in R1, R5 and Deviations 1 to 14 of
docs/analysis_preregistration.md, or is stated below.

What it computes (exploratory figures are labelled so in the results and the report, as R5 requires for Family C)
  1. Prevalence (Deviations 3 and 11): the design-weighted relevance rate overall and by era, and the class
     shares among relevant items, on the pooled sample with the pooled weights N_h / n_h; the same for each
     tranche with N_h over its own draw; and the difference between the tranches.
  2. RQ4 (Deviations 3, 8 and 11): the relevance rate in 2022-2025 minus 2016-2018, with its interval, its
     direction and the overlap of the two era intervals; the composition check of Deviation 8 on the pooled sample
     (seven subreddit groups, r/waymo merged with r/SelfDrivingCars, and the two-group version beside it; era rates
     standardised to the pooled frame mix), exploratory. The tranche 1 decomposition is recomputed beside it.
  3. Text-only sensitivity (Deviations 12 and 13), exploratory: the design-weighted era rates (a) from the
     cross-validated predictions of the text-only Stage 1 variant and (b) from the gold labels of the items in the
     six subreddits where relevance is judged from the text, each decomposed by the method of Deviation 8.
  4. The lexical proxy against the gold Stage 1 label, item by item and by subreddit (Deviations 13 and 14).
  5. Subsystem agreement and D28 (Deviations 6, 7, 9, 10 and 11): primary-subsystem alpha on the reliability items
     of both tranches pooled, in the two forms recorded on 30 September 2026, and for each tranche; D28 Rule 1 and
     condition (i) of Rule 2 on the lower pooled figure; condition (ii) of Rule 2 on the design-weighted shares
     pi_s among CONCERN items of the pooled sample (V2X as a count, R5); the tranche 1 outcome beside it, and
     whether the pooled sample changes the outcome recorded on tranche 1. The annotators' secondary subsystem
     labels, described (Deviations 7, 9 and 13).
  6. The tranche 1 checks of Deviations 3 and 4: the concentration of Stage 2 disagreement by class pair; and,
     exploratory, alpha on the 76 reliability items whose text was not mis-decoded, the class distribution from
     each annotator's sheet, and the bootstrap intervals of alpha (of record in the evaluation output; copied).
  7. Deviation 2: every adjudicated item listed, and the estimates of this script that rest on the adjudicated
     labels and feed later figures recomputed on the raw-majority set (rule 9).
  8. Error rates of the deployed classifiers (Deviations 12 and 13): the weighted CONCERN rates of record,
     recomputed exactly and checked; the weighted three-class rates M_ij; the relevance-error shares e_in and e_out
     by era; the two figures on the misclassified items; the three-way comparison of the CONCERN share.
  9. The temporal calibration check (R5, Deviations 11, 12 and 13): the weighted TPR and FPR for CONCERN in the
     early and late blocks, on both tranches and on each alone, with the late-minus-early differences, 95%
     percentile intervals from the 2,000 item resamples and Wilson intervals on the unweighted counts; macro-F1 and
     per-class F1 of the deployed Stage 2 classifier by block, and the deployed Stage 1 classifier's accuracy on
     each class and balanced accuracy by block, on both tranches (description). The SHA-256 of the item index
     arrays is printed for the register.
 10. Counts the record requires: the tranche 2 class counts on single-rated items by annotator (Deviations 10 and
     11), and the items without a gold label or without a gold subsystem, by era, tranche and annotator
     (Deviation 11).

Rules fixed with this file (where the committed text is silent, or to say how a committed rule is applied)
  1. Intervals of Deviation 3, as the tranche 1 previews computed them (register, 4 October 2026): stratified
     simple random sampling without replacement within era, finite population correction 1 - n_h / N_h; a share
     is a ratio estimate sum(w y) / sum(w x) over every item of the sample, with x = 1 for a rate over all items
     (a share within a subset is a domain estimate: y and x are zero outside it), and its variance is the
     linearised (Taylor) variance; the interval is computed on the logit scale with the delta-method standard
     error and the t quantile on n - H degrees of freedom (n the items of the sample, H the strata), or n_h - 1
     within one era. A share of exactly 0 or 1 has no logit interval and none is reported. The difference
     between two eras uses a Wald interval with the t quantile on n_1 + n_3 - 2 degrees of freedom. Two intervals
     overlap unless the lower limit of one exceeds the upper limit of the other.
  2. Missing labels (Deviation 11): an item without a gold Stage 1 label is left out of every estimate, so n_h is
     the number of items of the era that have one; class shares are taken over the relevant items that have a
     Stage 2 label, and pi_s over the CONCERN items that have a gold primary subsystem (the numbers without are
     reported). The gold labels, the primary subsystem included, are formed again from the files of record by
     models_01_prepare.form_gold (Deviations 2, 7 and 11) and must equal those in data/models/gold_labels.csv.
  3. The difference between the tranches (Deviation 11: "a difference between the two annotation rounds is
     reported"): tranche 2 minus tranche 1 for the relevance rate overall and by era and for the class shares,
     each tranche with its own-draw weights, with a Wald interval for two disjoint random samples of one frame
     (Deviation 11): the variance of the difference is the sum of the two variances without the finite
     population correction, which the negative covariance of disjoint samples cancels; t on n_1 + n_2 - 2H
     degrees of freedom, or n_1h + n_2h - 2 within an era. Description: it is not used to choose between them.
  4. Deviation 8's decomposition (Kitagawa): with m the share of an era's items in a subreddit group and r the
     relevance rate in that group, the difference of the era rates is split into a mix part,
     sum_g (m3_g - m1_g)(r1_g + r3_g) / 2, and a within-group part, sum_g (r3_g - r1_g)(m1_g + m3_g) / 2. Within an
     era the design weights are equal, so m and r are sample shares. A group with no item in one of the two eras
     takes the other era's rate there (it then adds nothing to the within-group part) and is flagged. The
     standardised era rate is sum_g M_g r_e,g / sum_g M_g over the groups that have items in all three eras (a
     group missing from any era is left out of all three and flagged), with M_g the pooled frame mix
     sum_e S_e m_e,g / sum_e S_e, the within-era mix estimated from the sample as on 4 October 2026; S_e is the
     estimated number of frame comments of era e in the population analysed (N_e for all items; N_e times the
     sample share of the six subreddits for the six-subreddit analysis, whose groups are its six subreddits).
  5. D28 (Deviations 10 and 11), as applied on 30 September and 4 October 2026: Rule 1 and condition (i) of Rule 2
     use the lower of the two pooled alphas (the defined one if the other is undefined). In condition (ii), V2X
     and none are eligible for neither first nor second place; the two largest eligible shares are taken in order
     of their exact estimate, an exact tie going to the earlier subsystem in models_config's order; the condition is met when the
     lower limit of the largest exceeds the upper limit of the second, and cannot be evaluated when either has no
     interval. Rule 2 is not met when either condition fails. The outcome recorded on tranche 1 (Rule 1 did not
     fire; Rule 2 was met, with sensing in first place) is the reference for "changes an outcome"; second place
     and the intervals are reported but are not part of the outcome. An outcome that cannot be evaluated counts
     as requiring a further deviation, because no committed rule covers it.
  6. Secondary labels (Deviations 7 and 9: "reported descriptively"): on every rating that gives a primary
     subsystem, the number of ratings giving each subsystem as primary, as secondary and as either, and the table
     of primary against secondary; on all such ratings and on those whose own Stage 2 class is CONCERN; for each
     tranche and both together. Counts only.
  7. Concentration of Stage 2 disagreement (Deviation 3): on each tranche 1 reliability item, every pair of the
     Stage 2 classes given by annotators who coded it relevant; the headline is the count of disagreeing pairs
     for each class pair; beside it, the observed and chance-expected coincidences of Krippendorff's nominal alpha
     for each class pair (expected = n_c n_k / (n - 1) over the pairable values, both orders summed). Disagreement
     concentrates at CONCERN/OTHER rather than CONCERN/ENDORSEMENT when the CONCERN/OTHER figure is the larger:
     by count, and by the ratio of observed to expected coincidences.
  8. Annotator sensitivity (Deviation 4): for each annotator, the items of their tranche 1 sheet (the 100
     reliability items and their own items) with their own ratings, weighted by N_h over the number of their
     sheet's rated items in era h; the relevance share and the class shares among the items they coded relevant
     with a class. Point estimates and counts, beside the design-weighted tranche 1 figures.
  9. Deviation 2's raw-majority set: an item whose Stage 2 class was adjudicated keeps its Stage 1 label (the
     Stage 1 majority stands) and has no Stage 2 class; an item whose primary subsystem was adjudicated has no
     gold subsystem. The adjudicated items are listed with the labels the annotators gave. Recomputed on that set:
     the class shares (pooled and tranche 2), the weighted CONCERN rates, the three-class rates M_ij, pi_s and D28
     condition (ii). Not recomputed: the block rates, F1 and resample intervals of the temporal check, the
     relevance-error figures, the three-way comparison, and the model comparison of the evaluation of record
     (models_05_evaluate.py, which uses the adjudicated set only; Deviation 14).
 10. Relevance-error shares (Deviation 13): for each era, e_in = items classified relevant by the cross-validated
     Stage 1 prediction that are not relevant in the gold set, over items classified relevant; e_out = items
     classified not relevant that are relevant, over items classified not relevant. Wilson intervals are given
     beside them as description; they do not enter the relevance-error series, which carry no interval.
 11. The third figure of the three-way comparison is clipped to [0, 1] with the raw value beside it (R5).
 12. The block of an item is set by its creation time in corpus v2.2 against 2021-12-29T21:39:22Z (before: early;
     at or after: late); its era by the master key, checked against its calendar year in UTC.
 13. A Stage 2 refusal counts as not CONCERN in the CONCERN rates (register, 11 October 2026), as OTHER in the
     three-class rates M_ij (Deviation 13) and as an error in F1 (Deviation 12). A class with no gold item in a
     block has no F1 there, and macro-F1 is then not given.
 14. Item resamples (Deviation 13): each drawn copy of an item carries the pooled design weight of its era; a rate
     with an empty denominator in a resample has no value there; the percentiles are numpy.nanpercentile's
     default (linear) over the resamples with a value, and no interval is given when more than 100 lack one.
 15. Previews and checks: a figure of record that rests on these inputs (the evaluation output's rates, confusion
     table, item sets and Stage 1 accuracies) must be reproduced exactly, or the script stops. A preview (the
     tranche 1 subsystem alpha of 30 September, pi_s of 4 October, the decomposition of Deviation 8 and the pooled
     subsystem alpha of 10 October 2026) is compared at the precision it was recorded with, and a difference is
     reported, not removed (Deviation 13).
 16. The lexical proxy (Deviation 14: the eight terms of CORE_TERMS in config.py as committed at be001c7, each
     matched as a whole word in any letter case on clean_body of corpus v2.2), on the items with a gold Stage 1
     label. For each subreddit and overall: the table of proxy against gold, the agreement, and the shares of
     gold-relevant items it matches and of matched items that are relevant, with Wilson intervals on the
     unweighted counts (description). Beside it: the number of the 1,000 items whose clean_body differs from the
     text given to the models (data/models/zero_shot_input.csv), and the number of items with a gold Stage 1
     label on which that text gives another proxy result.

Writes, in data/analysis/sample/run_<first 12 hex digits of this file's SHA-256>/ (data/ is not committed):
  sample_results.json       every figure (no timestamp: a rerun on the same inputs gives the same bytes)
  sample_report.md          the main figures, as tables
  sample_manifest.json      time, versions, and the SHA-256 of every input file and of the two files above
  PASTE_sample_block.txt    the register lines (hashes and the index-array SHA-256)
After the run, sample_results.json and sample_report.md are copied to results/ and committed with the register
entry, so that every figure is in a results file committed to the repository (Deviation 13).
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import shutil
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import numpy as np
import pandas as pd

import models_01_prepare as prep
import models_05_evaluate as ev
import models_common as mc
import models_config as cfg

# =============================================================================
# THE RECORD
# =============================================================================
OUT_ROOT = cfg.REPO / "data" / "analysis" / "sample"
EVALUATION_SCRIPT_SHA256 = "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734"    # 34403e6
EVALUATION_RESULTS = ev.EVAL_DIR / "evaluation_results.json"
EVALUATION_RESULTS_SHA256 = "411f6c23ef6525b077c74fec15b8e5a06c59c550a8f3f2d15e99eb7d354d32e4"   # 11 October
CORPUS = cfg.REPO / "data" / "clean_v2_2" / "corpus.parquet"
CORPUS_MEMBERSHIP_SHA256 = "d187adac10d98ccda1f0145713139f008705349ea6e0b4921092b1ad099559d4"     # R5
CORPUS_ROWS = 12776                                                                               # R5
R5_SUBREDDIT_COUNTS = {"teslamotors": 2435, "selfdrivingcars": 2143, "realtesla": 1189, "waymo": 883,   # R5
                       "electricvehicles": 1757, "cars": 1469, "futurology": 1411, "technology": 925,
                       "privacy": 371, "cybersecurity": 193}
R5_TIER_COUNTS = {"Tier 1": 6650, "Tier 2": 5562, "Tier 3": 564}                                  # R5
FRAME_IDS = cfg.REPO / "data" / "frozen" / "draw_frame_ids.txt"
FRAME_MEMBERSHIP_SHA256 = "ce85a3b046fedf3648861d446832a364ab89e7b60a0e58f10272b33b1997d7b3"      # R5
FRAME_ROWS = 12166                                                                                # R5
BOUNDARY = pd.Timestamp("2021-12-29T21:39:22Z")                                                   # R5
FRAME_SPLIT = (6083, 6083)                                                                        # R5

ERAS = ev.ERAS                                  # era -> (N_h frame size, n_h pooled draw), Deviation 11
ERA_ORDER = ["2016-2018", "2019-2021", "2022-2025"]
FIRST, LAST = "2016-2018", "2022-2025"
ERA_YEARS = {"2016-2018": (2016, 2018), "2019-2021": (2019, 2021), "2022-2025": (2022, 2025)}
OWN_DRAW = {"2016-2018": 167, "2019-2021": 167, "2022-2025": 166}   # each tranche's own draw (R1, Deviation 11)
N_FRAME = {h: ERAS[h][0] for h in ERA_ORDER}
CLASSES = list(cfg.CLASSES)
SUBSYSTEMS = list(cfg.PRIMARY_SUBSYSTEMS)       # the seven primary values, in models_config's order

DEPLOYED_STAGE2 = "sonnet-domain"               # evaluation of record, 11 October 2026
DEPLOYED_STAGE1 = "stage1-roberta"
TEXT_ONLY = "stage1-roberta-textonly"
RATES_OF_RECORD = {"tpr": 0.946922, "fpr": 0.237641,                       # Deviation 13; evaluation_results.json
                   "tpr_minus_fpr_exact": "2368170585210576/3338832495498181"}

N_RESAMPLES = 2000                              # Deviation 13
ITEM_GENERATOR = [cfg.SEED, 3, 1]               # Deviation 13: numpy.random.default_rng([24916660, 3, 1])
DRY_RUN_GENERATORS = {"shuffle": [cfg.SEED, 3, 98], "resamples": [cfg.SEED, 3, 99]}   # the preflight's dry run only
MAX_UNDEFINED = 100                             # Deviation 13: no interval if more resamples than this lack a value

SUBREDDITS = ["teslamotors", "selfdrivingcars", "realtesla", "waymo",
              "electricvehicles", "cars", "futurology", "technology"]
NARROW = ["selfdrivingcars", "waymo"]          # relevance may be inferred from the subreddit (Deviation 1)
SEVEN_GROUPS = {s: ("selfdrivingcars+waymo" if s in NARROW else s) for s in SUBREDDITS}     # Deviation 8
SEVEN_NAMES = ["teslamotors", "selfdrivingcars+waymo", "realtesla", "electricvehicles", "cars", "futurology",
               "technology"]
TWO_GROUPS = {s: ("narrow" if s in NARROW else "broad") for s in SUBREDDITS}                 # register, 4 October
SIX = [s for s in SUBREDDITS if s not in NARROW]
EXPLORATORY = "exploratory (Family C, R5)"

# Tranche 1 reliability items whose text was mis-decoded in annotator C's workbook (register, 26 September 2026).
ENCODING_AFFECTED = """ds21b4y dw7geu4 dwocqws fbz20u9 fgo2xaz fho1pgo fos7eho fowxn1d ghmx30k gir0isd gqa1dm9
gqsqbb7 hwd5iin j0mfukj jnqo9ty kerb4rm kyxo91r lq3tkav lym5o6h m39gk6k me7mbuk mhamb4s movxknc mp4k05p""".split()

D28_RULE1_BAR = Fraction(6, 10)                 # D28 Rule 1: alpha below 0.6
D28_RULE2_BAR = Fraction(7, 10)                 # D28 Rule 2, condition (i): alpha at least 0.7
D28_TRANCHE1_OUTCOME = {"rule1_fires": False, "rule2_met": True, "first_place": "sensing"}   # 30 Sep, 4 Oct 2026

# Previews (register and Deviation 8), compared with what this script computes; they are not figures of record.
PREVIEW_TRANCHE1_SUBSYSTEM_ALPHA = {"two_or_more_labels": ("0.868", 59, 175),        # 30 September: alpha, units,
                                    "all_three_annotators": ("0.867", 57, 171)}      # pairable values
PREVIEW_TRANCHE1_PI_S = {      # register, 4 October 2026: percent, 95% interval, items (120 CONCERN items)
    "shares": {"sensing": ("27.8", "20.3", "36.8"), "in_vehicle_networks": ("3.7", "1.5", "8.8"),
               "privacy": ("0.7", "0.1", "4.8"), "none": ("63.5", "54.2", "71.8")},
    "items": {"sensing": 35, "in_vehicle_networks": 5, "v2x": 6, "cybersecurity": 0, "privacy": 1,
              "data_governance": 0, "none": 73},
    "concern_items": 120}
PREVIEW_TRANCHE1_DECOMPOSITION = {"difference": "+7.0", "mix": "+6.1", "within": "+0.9"}   # Deviation 8, points
PREVIEW_POOLED_SUBSYSTEM_ALPHA = {"two_or_more_labels": "0.779", "all_three_annotators": "0.769"}   # 10 October

# =============================================================================
# THE LEXICAL PROXY (Deviations 13 and 14)
# =============================================================================
# Deviation 13 takes the term list from the repository as it stood at be001c7: CORE_TERMS in config.py, read here
# from the file without running it, after the file is checked against its SHA-256 at that commit (LF line endings).
# Deviation 14 fixes the matching rule: a comment carries a CAV term if its clean_body contains one of the eight terms
# as a whole word, in any letter case; the words of a term may be joined by a hyphen, a space or nothing, and a final
# "s" is allowed. PROXY_PATTERNS are the patterns of Deviation 14, word for word, used with re.IGNORECASE.
PROXY_SOURCE = {"file": "config.py", "commit": "be001c7",
                "sha256_lf": "92ebb86e725d86c08344862ec7dba2c6dcfe3834af079a8a632ccf46505abb61",
                "term_list": "CORE_TERMS", "rule": "Deviation 14 of docs/analysis_preregistration.md"}
PROXY_TERMS = ["self-driving", "autonomous vehicle", "robotaxi", "Autopilot", "FSD", "Waymo", "V2X", "LiDAR"]
PROXY_PATTERNS = [r"\bself[- ]?drivings?\b", r"\bautonomous[- ]?vehicles?\b", r"\brobotaxis?\b", r"\bautopilots?\b",
                  r"\bfsds?\b", r"\bwaymos?\b", r"\bv2xs?\b", r"\blidars?\b"]


def proxy_pattern(term: str) -> str:
    """Deviation 14: the term lower-cased and split at hyphens and spaces; its words joined by an optional hyphen or
    space; an optional final "s"; the whole between word boundaries."""
    return r"\b" + r"[- ]?".join(re.escape(w) for w in re.split(r"[- ]", term.lower())) + r"s?\b"


PROXY_RE = re.compile("|".join(PROXY_PATTERNS), re.IGNORECASE)


def proxy_matches(text: str) -> bool:
    return PROXY_RE.search(text) is not None


# =============================================================================
# small helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


def fl(x, digits: int = 6):
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        return None
    return round(x, digits)


def fr(x) -> str | None:
    return None if x is None else f"{x.numerator}/{x.denominator}"


def tq(df: int) -> float:
    from scipy.stats import t
    return float(t.ppf(0.975, df))


def wilson(k: int, n: int) -> dict:
    out = ev.wilson(int(k), int(n))
    return {"k": int(k), "n": int(n), "share": out["accuracy"], "wilson95_low": out["wilson95_low"],
            "wilson95_high": out["wilson95_high"]}


def era_of_year(year: int) -> str:
    for e, (a, b) in ERA_YEARS.items():
        if a <= year <= b:
            return e
    stop(f"year {year} is outside 2016-2025")


def strip(x):
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items() if not str(k).startswith("_")}
    if isinstance(x, list):
        return [strip(v) for v in x]
    return x


def pct1(x) -> str | None:
    return None if x is None else f"{100 * float(x):.1f}"


def overlap(a: dict, b: dict) -> bool | None:
    """Whether two intervals overlap (rule 1), on the unrounded limits."""
    if None in (a["_low"], a["_high"], b["_low"], b["_high"]):
        return None
    return not (a["_low"] > b["_high"] or b["_low"] > a["_high"])


def run_folder(me: str) -> Path:
    return OUT_ROOT / f"run_{me[:12]}"


# =============================================================================
# inputs
# =============================================================================
def check_evaluation_script() -> str:
    return ev.check_text_sha(Path(ev.__file__).resolve(), EVALUATION_SCRIPT_SHA256,
                             "models_05_evaluate.py (committed at 34403e6)")


def load_evaluation_results() -> tuple[dict, str]:
    sha = ev.check_sha(EVALUATION_RESULTS, EVALUATION_RESULTS_SHA256, "evaluation_results.json (the evaluation of record)")
    with open(EVALUATION_RESULTS, encoding="utf-8") as f:
        res = json.load(f)
    pc = res["stage2"]["prevalence_correction_error_rates"]
    if pc["configuration"] != DEPLOYED_STAGE2 or res["stage2"]["deployment"]["deployed"] != DEPLOYED_STAGE2 \
            or res["stage1"]["deployment"]["deployed"] != DEPLOYED_STAGE1 \
            or res["stage1"]["deployment"]["text_only_variant"] != TEXT_ONLY:
        stop("the evaluation output of record does not name the deployed classifiers this script expects")
    w = pc["weighted"]
    if (w["tpr"], w["fpr"], w["tpr_minus_fpr_exact"]) != (RATES_OF_RECORD["tpr"], RATES_OF_RECORD["fpr"],
                                                           RATES_OF_RECORD["tpr_minus_fpr_exact"]):
        stop("the evaluation output does not hold the rates of record")
    return res, sha


def check_gold(gold: pd.DataFrame, key1, long1, key2, long2) -> None:
    """The gold labels formed now from the files of record by the committed rules (models_01_prepare.form_gold:
    Deviations 2, 7 and 11 with the adjudications of 10 October 2026) must be those in gold_labels.csv, the
    primary subsystem and the adjudication flags included."""
    cols = ["label4", "label4_raw_majority", "stage2_adjudicated", "gold_subsystem", "subsystem_adjudicated"]
    missing = [c for c in cols if c not in gold.columns]
    if missing:
        stop(f"gold_labels.csv lacks the columns {missing} (models_01_prepare.py writes them)")
    g1 = prep.form_gold(1, key1, long1)
    prep.check_tranche1(g1)
    g2 = prep.form_gold(2, key2, long2)
    formed = pd.concat([g1, g2])
    if set(formed.index) != set(gold.index):
        stop("the gold labels formed from the files of record do not cover the items of gold_labels.csv")
    for c in cols:
        a = formed[c].reindex(gold.index).fillna("").astype(str)
        if (a != gold[c].astype(str)).any():
            bad = list(gold.index[a != gold[c].astype(str)][:5])
            stop(f"gold_labels.csv: {c} differs from the value formed from the files of record, e.g. {bad}. "
                 f"Report this message before going further.")
    rel = gold["gold_stage1"] == "Y"
    if not gold.loc[rel, "gold_subsystem"].isin(SUBSYSTEMS + [""]).all() or (gold.loc[~rel, "gold_subsystem"] != "").any():
        stop("gold_labels.csv: a gold subsystem is not one of the seven values, or an item that is not relevant has one")


def load_corpus_items(ids: list[str]) -> tuple[pd.DataFrame, dict]:
    """Corpus v2.2 and the frame, each checked against R5 (membership SHA-256, size, subreddit and tier counts, and
    the split of the frame at the boundary); then each annotated item's creation time, year, subreddit, tier and
    text."""
    if not CORPUS.exists():
        stop(f"corpus v2.2 not found at {CORPUS}")
    try:
        corpus = pd.read_parquet(CORPUS, columns=["id", "created", "year", "subreddit", "tier", "clean_body"])
    except Exception as e:                                  # noqa: BLE001 - reported, not handled
        stop(f"corpus v2.2 could not be read with the columns id, created, year, subreddit, tier, clean_body ({e})")
    corpus["id"] = corpus["id"].astype(str)
    if len(corpus) != CORPUS_ROWS or corpus["id"].duplicated().any() \
            or mc.ids_sha256(corpus["id"]) != CORPUS_MEMBERSHIP_SHA256:
        stop("corpus v2.2: the membership does not match R5 (SHA-256 of the sorted ids). Report this message before going further.")
    subs = corpus["subreddit"].astype(str).str.strip().str.replace(r"^/?r/", "", regex=True).str.lower()
    if dict(Counter(subs)) != R5_SUBREDDIT_COUNTS or dict(Counter(corpus["tier"].astype(str))) != R5_TIER_COUNTS:
        stop("corpus v2.2: the counts by subreddit or by tier differ from R5. Report this message before going further.")
    created = pd.to_datetime(corpus["created"], utc=True, errors="coerce")
    if created.isna().any():
        stop("corpus v2.2: a comment has no creation time that can be read")
    year = pd.to_numeric(corpus["year"], errors="coerce")
    if year.isna().any():
        stop("corpus v2.2: a comment has no year")
    corpus["year"] = year.astype(int)
    if corpus["clean_body"].isna().any() or (corpus["clean_body"].astype(str).str.strip() == "").any():
        stop("corpus v2.2: a comment has no text")
    corpus = corpus.assign(created=created).set_index("id")
    if not FRAME_IDS.exists():
        stop(f"the frame id list was not found at {FRAME_IDS} (emit_frozen_frame.py writes it)")
    try:
        frame = [x for x in FRAME_IDS.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n") if x]
    except UnicodeDecodeError:
        stop("draw_frame_ids.txt is not UTF-8 text (emit_frozen_frame.py writes it as UTF-8)")
    if len(frame) != FRAME_ROWS or len(set(frame)) != FRAME_ROWS or mc.ids_sha256(frame) != FRAME_MEMBERSHIP_SHA256:
        stop("draw_frame_ids.txt: the membership does not match R5. Report this message before going further.")
    if not set(frame) <= set(corpus.index):
        stop("draw_frame_ids.txt lists a comment that is not in corpus v2.2")
    ft = corpus.loc[frame, "created"]
    split = (int((ft < BOUNDARY).sum()), int((ft >= BOUNDARY).sum()))
    if split != FRAME_SPLIT:
        stop(f"the frame splits {split[0]} / {split[1]} at the boundary; R5 records {FRAME_SPLIT[0]} / {FRAME_SPLIT[1]}")
    frame_set = set(frame)
    missing = [i for i in ids if i not in frame_set]
    if missing:
        stop(f"{len(missing)} annotated items are not frame comments of corpus v2.2, e.g. {missing[:5]}")
    items = corpus.loc[ids].copy()
    if not items["tier"].isin(["Tier 1", "Tier 2"]).all():
        stop("an annotated item is not a Tier 1 or Tier 2 comment")
    if (items["year"].astype(int) != items["created"].dt.year).any():
        stop("corpus v2.2: a comment's year is not the calendar year of its creation time in UTC")
    items["subreddit_key"] = items["subreddit"].astype(str).str.strip().str.replace(r"^/?r/", "", regex=True).str.lower()
    items["block"] = np.where(items["created"] < BOUNDARY, "early", "late")
    info = {"corpus_rows": CORPUS_ROWS, "corpus_membership_sha256": CORPUS_MEMBERSHIP_SHA256,
            "corpus_counts_by_subreddit_and_tier": "as in R5", "frame_rows": FRAME_ROWS,
            "frame_membership_sha256": FRAME_MEMBERSHIP_SHA256, "frame_split_at_boundary": list(split),
            "corpus_file_sha256": mc.sha256_file(CORPUS), "frame_file_sha256": mc.sha256_file(FRAME_IDS),
            "note": "R5 records the corpus and the frame by their membership; the files' own SHA-256 are recorded here"}
    return items, info


def load_all() -> dict:
    """Every input, each checked against the record. Sets no prediction against a label."""
    me_eval = check_evaluation_script()
    ev.check_record_complete()
    versions = ev.check_libraries()
    scripts = ev.check_scripts()
    scripts["models_05_evaluate.py"] = me_eval
    gold, shas = ev.load_gold()
    subreddit, more = ev.load_inputs(gold)
    shas.update(more)
    runs, more = ev.verify(gold)
    shas.update(more)
    key1, long1, key2, long2, weights, key2_sha = ev.load_keys()
    shas["tranche2_master_key.csv"] = key2_sha
    long1 = prep.attach_tranche1_subsystems(long1)
    ev.check_tranche1_alpha(key1, long1)
    check_gold(gold, key1, long1, key2, long2)
    evaluation, shas["evaluation_results.json"] = load_evaluation_results()
    shas.update({f"{k} (file of record)": v for k, v in cfg.RECORDED_SHA256.items()})     # checked by models_01_prepare
    shas["prefilter_input.csv"] = cfg.PREFILTER_INPUT_SHA256                               # checked by models_01_prepare
    ids = sorted(gold.index)
    items, corpus_info = load_corpus_items(ids)
    shas["corpus.parquet (membership checked against R5)"] = corpus_info["corpus_file_sha256"]
    shas["draw_frame_ids.txt (membership checked against R5)"] = corpus_info["frame_file_sha256"]

    era = pd.concat([key1["era"].str.strip(), key2["era"].str.strip()])
    if era.index.duplicated().any() or set(era.index) != set(ids):
        stop("the two master keys do not hold exactly the 1,000 annotated items")
    era = era.reindex(ids)
    if not set(era) <= set(ERAS):
        stop("an annotated item has no era of R1 in the master keys")
    by_year = items["year"].astype(int).map(era_of_year)
    if (by_year != era).any():
        stop(f"the master key's era differs from the calendar year of the comment in corpus v2.2, e.g. "
             f"{list(era.index[by_year != era][:5])}")
    subs = subreddit.reindex(ids).astype(str).str.strip().str.replace(r"^/?r/", "", regex=True).str.lower()
    if (subs != items["subreddit_key"]).any() or not set(subs) <= set(SUBREDDITS):
        stop("finetune_input.csv and corpus v2.2 disagree on an item's subreddit, or a subreddit is not one of the eight")
    counts = Counter(era)
    for e, (_, n_h) in ERAS.items():
        if counts[e] != n_h:
            stop(f"era {e}: {counts[e]} annotated items; the pooled draw is {n_h}")
    tranche = gold["tranche"].reindex(ids).astype(int)
    for t in (1, 2):
        got = Counter(era[tranche == t])
        if any(got[e] != OWN_DRAW[e] for e in ERA_ORDER):
            stop(f"tranche {t} does not hold its own draw of {OWN_DRAW} items by era")
    s1 = runs[DEPLOYED_STAGE1]["pred"]
    s1t = runs[TEXT_ONLY]["pred"]
    g = gold.reindex(ids)
    has1 = g["gold_stage1"].isin(["Y", "N"])
    if set(s1.index) != set(g.index[has1]) or set(s1t.index) != set(g.index[has1]):
        stop("the Stage 1 predictions do not cover exactly the items with a gold Stage 1 label")
    s2 = runs[DEPLOYED_STAGE2]["pred"]
    if set(s2.index) != set(ids):
        stop("the deployed Stage 2 classifier's predictions do not cover the 1,000 annotated items")
    zs = ev.read_csv(cfg.MODELS_DIR / "zero_shot_input.csv").set_index("id")["text"]   # its SHA-256 checked above

    def col(series, fill=""):
        return series.reindex(ids).fillna(fill).astype(str).to_numpy(dtype=object)

    data = {
        "ids": ids,
        "era": era.to_numpy(dtype=object), "tranche": tranche.to_numpy(), "sub": subs.to_numpy(dtype=object),
        "block": items["block"].to_numpy(dtype=object), "text": items["clean_body"].astype(str).to_numpy(dtype=object),
        "model_text": col(zs),
        "text_differs_from_model_text": int((items["clean_body"].astype(str).to_numpy() != col(zs)).sum()),
        "g1": col(g["gold_stage1"]), "g2": col(g["gold_stage2"]), "gsub": col(g["gold_subsystem"]),
        "s2adj": col(g["stage2_adjudicated"]) == "Y", "subadj": col(g["subsystem_adjudicated"]) == "Y",
        "s1": col(s1), "s1t": col(s1t), "s2": col(s2),
        "w": np.array([weights[i] for i in ids], dtype=object),
        "key1": key1, "key2": key2, "long1": long1, "long2": long2, "evaluation": evaluation,
    }
    data["has1"] = np.isin(data["g1"], ["Y", "N"])
    data["rel"] = data["g1"] == "Y"
    data["prim"] = np.isin(data["g2"], CLASSES)             # the primary item set (Deviation 12)
    if (data["prim"] & ~data["rel"]).any():
        stop("an item has a gold Stage 2 class but is not relevant in the gold set")
    return {"data": data, "shas": shas, "versions": versions, "scripts": scripts, "corpus": corpus_info}


# =============================================================================
# design-based estimates (rule 1)
# =============================================================================
def ratio_estimate(y, x, strata, N: dict, within: str | None = None, fpc: bool = True) -> dict:
    """sum(w y) / sum(w x) under stratified SRSWOR, w = N_h / n_h with n_h the items of stratum h passed in; the
    linearised variance with finite population correction (without it if fpc is False: rule 3); a logit interval
    with the t quantile on n - H degrees of freedom (n_h - 1 when `within` names one stratum). The point estimate
    is exact."""
    y = np.asarray(y, dtype=np.int64)
    x = np.asarray(x, dtype=np.int64)
    strata = np.asarray(strata, dtype=object)
    if within is not None:
        keep = strata == within
        y, x, strata = y[keep], x[keep], strata[keep]
    if ((y != 0) & (x == 0)).any():
        stop("a ratio estimate has an item in the numerator that is not in the denominator")
    hs = [h for h in ERA_ORDER if (strata == h).any()]
    num = den = Fraction(0)
    n_h = {}
    for h in hs:
        m = strata == h
        n_h[h] = int(m.sum())
        num += Fraction(N[h] * int(y[m].sum()), n_h[h])
        den += Fraction(N[h] * int(x[m].sum()), n_h[h])
    out = {"items": int(len(y)), "denominator_items": int(x.sum()), "numerator_items": int(y.sum())}
    empty = {"estimate": None, "estimate_exact": None, "se": None, "low": None, "high": None, "df": None,
             "_r": None, "_var": None, "_low": None, "_high": None}
    if den == 0:
        return {**out, **empty}
    r = num / den
    rf = float(r)
    var = 0.0
    for h in hs:
        m = strata == h
        nh = n_h[h]
        if nh < 2:
            stop(f"stratum {h} has fewer than two items in an estimate")
        d = y[m] - rf * x[m]
        var += N[h] ** 2 * ((1 - nh / N[h]) if fpc else 1.0) * float(np.var(d, ddof=1)) / nh
    se = math.sqrt(var) / float(den)
    df = (len(y) - len(hs)) if within is None else (n_h[within] - 1)
    low = high = None
    if 0 < r < 1 and se > 0:
        lr = math.log(rf / (1 - rf))
        half = tq(df) * se / (rf * (1 - rf))
        low, high = 1 / (1 + math.exp(-(lr - half))), 1 / (1 + math.exp(-(lr + half)))
    return {**out, "estimate": fl(r), "estimate_exact": fr(r), "se": fl(se), "low": fl(low), "high": fl(high),
            "df": int(df), "_r": r, "_var": se ** 2, "_low": low, "_high": high}


def wald_difference(a: dict, b: dict, df: int) -> dict:
    """b minus a, two independent estimates: variances added, t quantile on df."""
    if a["_r"] is None or b["_r"] is None:
        return {"difference": None, "difference_exact": None, "se": None, "low": None, "high": None, "df": None}
    d = b["_r"] - a["_r"]
    se = math.sqrt(a["_var"] + b["_var"])
    half = tq(df) * se
    return {"difference": fl(d), "difference_exact": fr(d), "se": fl(se), "low": fl(float(d) - half),
            "high": fl(float(d) + half), "df": int(df)}


def era_difference(y, x, era, N: dict) -> dict:
    """Wald interval for the 2022-2025 rate minus the 2016-2018 rate, the eras sampled independently (Deviation 3)."""
    a = ratio_estimate(y, x, era, N, within=FIRST)
    b = ratio_estimate(y, x, era, N, within=LAST)
    out = wald_difference(a, b, a["items"] + b["items"] - 2)
    if out["difference"] is not None:
        d = b["_r"] - a["_r"]
        out["direction"] = "higher in 2022-2025" if d > 0 else "lower in 2022-2025" if d < 0 else "no difference"
        out["era_intervals_overlap"] = overlap(a, b)
    return out


def rates_by_era(y, x, era, N: dict, fpc: bool = True) -> dict:
    out = {"overall": ratio_estimate(y, x, era, N, fpc=fpc)}
    for e in ERA_ORDER:
        out[e] = ratio_estimate(y, x, era, N, within=e, fpc=fpc)
    return out


def prevalence(data: dict, mask: np.ndarray, fpc: bool = True) -> dict:
    """Relevance rate overall and by era, class shares among relevant items, and the RQ4 era difference, on the
    items selected by mask that have a gold Stage 1 label (rule 2), with N_h the frame sizes and n_h their items."""
    s = mask & data["has1"]
    era = data["era"][s]
    rel = data["rel"][s]
    ones = np.ones(int(s.sum()), dtype=np.int64)
    has2 = data["prim"][s]
    return {"items": int(s.sum()), "relevance_rate": rates_by_era(rel, ones, era, N_FRAME, fpc),
            "relevant_items_without_a_stage2_label": int((rel & ~has2).sum()),
            "class_shares_among_relevant": {c: ratio_estimate(data["g2"][s] == c, has2, era, N_FRAME, fpc=fpc)
                                            for c in CLASSES},
            "era_difference_2022_2025_minus_2016_2018": era_difference(rel, ones, era, N_FRAME)}


def tranche_difference(p1: dict, p2: dict) -> dict:
    """Tranche 2 minus tranche 1 (rule 3); p1 and p2 are the tranche estimates without the finite population
    correction."""
    out = {}
    for k in ["overall"] + ERA_ORDER:
        a, b = p1["relevance_rate"][k], p2["relevance_rate"][k]
        df = a["items"] + b["items"] - (2 * len(ERA_ORDER) if k == "overall" else 2)
        out[f"relevance_rate_{k}"] = {"tranche1": a["estimate"], "tranche2": b["estimate"], **wald_difference(a, b, df)}
    for c in CLASSES:
        a, b = p1["class_shares_among_relevant"][c], p2["class_shares_among_relevant"][c]
        out[f"{c}_share_among_relevant"] = {"tranche1": a["estimate"], "tranche2": b["estimate"],
                                            **wald_difference(a, b, a["items"] + b["items"] - 2 * len(ERA_ORDER))}
    out["note"] = "description: tranche 2 minus tranche 1; not used to choose between the tranches (Deviation 11)"
    return out


# =============================================================================
# Deviation 8's decomposition (rule 4)
# =============================================================================
def decomposition(y, era, groups, names: list[str], sizes: dict | None = None) -> dict:
    """Kitagawa decomposition of the 2022-2025 minus 2016-2018 difference over the groups, and the era rates
    standardised to the pooled frame mix. y, era and groups cover the items analysed; sizes gives S_e, the
    estimated number of frame comments of era e in the population analysed (default: the frame sizes)."""
    y = np.asarray(y, dtype=np.int64)
    era = np.asarray(era, dtype=object)
    groups = np.asarray(groups, dtype=object)
    sizes = sizes or {e: Fraction(N_FRAME[e]) for e in ERA_ORDER}
    m, r, n = {}, {}, {}
    for e in ERA_ORDER:
        me = era == e
        n[e] = int(me.sum())
        if n[e] == 0:
            stop(f"the composition check has no item in era {e}")
        m[e], r[e] = {}, {}
        for gname in names:
            mg = me & (groups == gname)
            m[e][gname] = Fraction(int(mg.sum()), n[e])
            r[e][gname] = Fraction(int(y[mg].sum()), int(mg.sum())) if mg.sum() else None
    rate = {e: Fraction(int(y[era == e].sum()), n[e]) for e in ERA_ORDER}
    flags = []
    mix = within = Fraction(0)
    for gname in names:
        r1, r3 = r[FIRST][gname], r[LAST][gname]
        if r1 is None and r3 is None:
            continue
        if r1 is None:
            flags.append(f"{gname} has no item in {FIRST}; in the decomposition it takes the {LAST} rate")
            r1 = r3
        if r3 is None:
            flags.append(f"{gname} has no item in {LAST}; in the decomposition it takes the {FIRST} rate")
            r3 = r1
        mix += (m[LAST][gname] - m[FIRST][gname]) * (r1 + r3) / 2
        within += (r3 - r1) * (m[FIRST][gname] + m[LAST][gname]) / 2
    if mix + within != rate[LAST] - rate[FIRST]:
        stop("the decomposition does not add up to the difference of the era rates")
    total = sum(sizes.values(), Fraction(0))
    M = {gname: sum((sizes[e] * m[e][gname] for e in ERA_ORDER), Fraction(0)) / total for gname in names}
    common = [gname for gname in names if all(r[e][gname] is not None for e in ERA_ORDER)]
    if len(common) < len(names):
        flags.append(f"the standardised era rates are over the {len(common)} of {len(names)} groups that have items "
                     f"in every era: {', '.join(common)}")
    tot = sum((M[gname] for gname in common), Fraction(0))
    standardised = {e: (fl(sum((M[gname] * r[e][gname] for gname in common), Fraction(0)) / tot) if tot else None)
                    for e in ERA_ORDER}
    return {"era_rates": {e: fl(rate[e]) for e in ERA_ORDER}, "items_by_era": n,
            "difference_2022_2025_minus_2016_2018": fl(rate[LAST] - rate[FIRST]),
            "mix_part": fl(mix), "within_group_part": fl(within),
            "standardised_era_rates_pooled_frame_mix": standardised,
            "pooled_frame_mix": {gname: fl(M[gname]) for gname in names},
            "groups": {gname: {e: {"items": int(((era == e) & (groups == gname)).sum()), "share_of_era": fl(m[e][gname]),
                                   "rate": fl(r[e][gname])} for e in ERA_ORDER} for gname in names},
            "flags": flags, "_difference": rate[LAST] - rate[FIRST], "_mix": mix, "_within": within}


def composition_check(y, era, subs) -> dict:
    g7 = np.array([SEVEN_GROUPS[s] for s in subs], dtype=object)
    g2 = np.array([TWO_GROUPS[s] for s in subs], dtype=object)
    return {"status": EXPLORATORY, "seven_groups": decomposition(y, era, g7, SEVEN_NAMES),
            "two_groups": decomposition(y, era, g2, ["narrow", "broad"])}


# =============================================================================
# the lexical proxy (Deviations 13 and 14)
# =============================================================================
def proxy_hits(texts) -> np.ndarray:
    return np.array([bool(proxy_matches(t)) for t in texts], dtype=bool)


def lexical_proxy(data: dict) -> dict:
    """The proxy against the gold Stage 1 label, item by item, on the items with a gold Stage 1 label: for each
    subreddit and overall, the table of proxy against gold, the agreement, and the shares of gold-relevant items
    the proxy finds and of proxy matches that are relevant (Wilson intervals on the unweighted counts)."""
    s = data["has1"]
    hit = proxy_hits(data["text"][s])
    other = proxy_hits(data["model_text"][s])
    gold = data["rel"][s]
    subs = data["sub"][s]
    out = {}
    for name, m in [(sub, subs == sub) for sub in SUBREDDITS] + [("all eight subreddits", np.ones(len(subs), bool))]:
        hy, hn = hit & m, ~hit & m
        out[name] = {"items": int(m.sum()),
                     "proxy_and_gold_relevant": int((hy & gold).sum()), "proxy_only": int((hy & ~gold).sum()),
                     "gold_only": int((hn & gold).sum()), "neither": int((hn & ~gold).sum()),
                     "agreement": wilson(int(((hit == gold) & m).sum()), int(m.sum())),
                     "gold_relevant_items_matched": wilson(int((hy & gold).sum()), int((m & gold).sum())),
                     "matched_items_relevant": wilson(int((hy & gold).sum()), int(hy.sum()))}
    return {"source": PROXY_SOURCE, "patterns_ignoring_case": PROXY_PATTERNS, "text": "clean_body of corpus v2.2",
            "annotated_items_whose_clean_body_differs_from_the_model_input_text": data["text_differs_from_model_text"],
            "items_where_the_model_input_text_gives_another_result": int((hit != other).sum()),
            "by_subreddit": out}


# =============================================================================
# subsystem agreement and D28 (rule 5)
# =============================================================================
def subsystem_units(key: pd.DataFrame, long: pd.DataFrame) -> list[list[str]]:
    """Primary subsystem labels of each reliability item: one per rating that is not missing, coded relevant and
    gives a primary subsystem; items in id order."""
    ids = sorted(key.index[key["is_reliability"]])
    if len(ids) != 100:
        stop("each tranche must have 100 reliability items")
    keep = long[(~long["missing"]) & (long["stage1_relevant"] == "Y") & (long["subsystem"] != "")]
    by_id = keep.groupby("id")["subsystem"].apply(list).to_dict()
    return [list(by_id.get(i, [])) for i in ids]


def alpha_forms(units: list[list[str]]) -> dict:
    out = {}
    for name, pick in (("two_or_more_labels", lambda u: len(u) >= 2), ("all_three_annotators", lambda u: len(u) == 3)):
        sel = [u for u in units if pick(u)]
        a = ev.alpha_exact(sel, SUBSYSTEMS)
        out[name] = {"alpha": fl(a, 4), "alpha_exact": fr(a), "units": len(sel),
                     "pairable_values": int(sum(len(u) for u in sel)), "_alpha": a}
    return out


def lower_alpha(forms: dict):
    vals = [v["_alpha"] for v in forms.values() if v["_alpha"] is not None]
    return min(vals) if vals else None


def subsystem_shares(data: dict, mask: np.ndarray) -> dict:
    """pi_s: design-weighted share of the CONCERN items with a gold primary subsystem whose subsystem is s."""
    s = mask & data["has1"]
    era = data["era"][s]
    concern = data["g2"][s] == "CONCERN"
    sub = data["gsub"][s]
    has = concern & (sub != "")
    return {"shares": {k: ratio_estimate(has & (sub == k), has, era, N_FRAME) for k in SUBSYSTEMS},
            "concern_items_with_gold_subsystem": int(has.sum()),
            "concern_items_without_gold_subsystem": int((concern & (sub == "")).sum())}


def shares_for_output(sh: dict) -> dict:
    """pi_s as reported: V2X as a count only (R5)."""
    out = {k: (strip(v) if k != "v2x" else {"numerator_items": v["numerator_items"], "denominator_items":
                                            v["denominator_items"], "note": "reported as a count (R5)"})
           for k, v in sh["shares"].items()}
    return {"shares": out, "concern_items_with_gold_subsystem": sh["concern_items_with_gold_subsystem"],
            "concern_items_without_gold_subsystem": sh["concern_items_without_gold_subsystem"]}


def d28(alpha_lower, shares: dict) -> dict:
    sh = shares["shares"]
    eligible = [k for k in SUBSYSTEMS if k not in ("v2x", "none")]
    order = sorted(eligible, key=lambda k: (-(sh[k]["_r"] if sh[k]["_r"] is not None else Fraction(-1)),
                                            SUBSYSTEMS.index(k)))
    first, second = order[0], order[1]
    lo1, hi2 = sh[first]["_low"], sh[second]["_high"]
    cond2 = None if lo1 is None or hi2 is None else lo1 > hi2
    rule1 = None if alpha_lower is None else alpha_lower < D28_RULE1_BAR
    cond1 = None if alpha_lower is None else alpha_lower >= D28_RULE2_BAR
    met = False if (cond1 is False or cond2 is False) else (None if (cond1 is None or cond2 is None) else True)
    return {"alpha_used": fl(alpha_lower, 4), "alpha_used_exact": fr(alpha_lower),
            "rule1_alpha_below_0_6": rule1, "rule2_condition_i_alpha_at_least_0_7": cond1,
            "largest_eligible": first, "second_largest_eligible": second,
            "lower_limit_of_largest": fl(lo1), "upper_limit_of_second": fl(hi2),
            "rule2_condition_ii_intervals_do_not_overlap": cond2, "rule2_met": met}


def d28_changed(pooled: dict) -> dict:
    """Whether the pooled outcome differs from the tranche 1 outcome; None where it cannot be evaluated (rule 5)."""
    ref = D28_TRANCHE1_OUTCOME
    r1, r2 = pooled["rule1_alpha_below_0_6"], pooled["rule2_met"]
    changed = {"rule1": None if r1 is None else r1 != ref["rule1_fires"],
               "rule2": None if r2 is None else r2 != ref["rule2_met"],
               "rule2_first_place": None if r2 is None else bool(r2 and pooled["largest_eligible"] != ref["first_place"])}
    return {"reference_outcome_on_tranche1": ref, "changed": changed,
            "further_deviation_required": any(v is not False for v in changed.values())}


def secondary_labels(long1: pd.DataFrame, long2: pd.DataFrame) -> dict:
    """Rule 6: counts of primary and secondary subsystem labels, rating by rating."""
    def table(rows: pd.DataFrame) -> dict:
        prim, sec = rows["subsystem"], rows["subsystem_secondary"]
        return {"ratings_with_a_primary": int(len(rows)), "ratings_with_a_secondary": int((sec != "").sum()),
                "by_subsystem": {k: {"as_primary": int((prim == k).sum()), "as_secondary": int((sec == k).sum()),
                                     "as_either": int(((prim == k) | (sec == k)).sum())} for k in SUBSYSTEMS},
                "primary_by_secondary": {p: {q: int(((prim == p) & (sec == q)).sum()) for q in cfg.SUBSYSTEMS}
                                         for p in SUBSYSTEMS}}

    def rated(long: pd.DataFrame) -> pd.DataFrame:
        return long[(~long["missing"]) & (long["stage1_relevant"] == "Y") & (long["subsystem"] != "")]

    parts = {"tranche 1": rated(long1), "tranche 2": rated(long2)}
    parts["both tranches"] = pd.concat([parts["tranche 1"], parts["tranche 2"]], ignore_index=True)
    return {"status": "descriptive (Deviations 7 and 9)",
            **{name: {"all_ratings_with_a_primary": table(rows),
                      "ratings_whose_own_class_is_concern": table(rows[rows["stage2_class"] == "CONCERN"])}
               for name, rows in parts.items()}}


# =============================================================================
# tranche 1 checks of Deviations 3 and 4 (rules 7 and 8)
# =============================================================================
def disagreement_concentration(key1: pd.DataFrame, long1: pd.DataFrame) -> dict:
    _, s2 = ev.reliability_units(key1, long1)
    pairs = Counter()
    for vals in s2:
        for a in range(len(vals)):
            for b in range(a + 1, len(vals)):
                if vals[a] != vals[b]:
                    pairs[tuple(sorted((vals[a], vals[b]), key=CLASSES.index))] += 1
    o = {(a, b): Fraction(0) for a in CLASSES for b in CLASSES}
    for vals in s2:
        if len(vals) < 2:
            continue
        cnt = Counter(vals)
        for a in cnt:
            for b in cnt:
                o[(a, b)] += Fraction(cnt[a] * (cnt[b] - (a == b)), len(vals) - 1)
    n_c = {a: sum(o[(a, b)] for b in CLASSES) for a in CLASSES}
    n = sum(n_c.values())
    rows = {}
    for a, b in (("CONCERN", "ENDORSEMENT"), ("CONCERN", "OTHER"), ("ENDORSEMENT", "OTHER")):
        obs = o[(a, b)] + o[(b, a)]
        exp = 2 * n_c[a] * n_c[b] / (n - 1) if n > 1 else None
        rows[f"{a}/{b}"] = {"disagreeing_pairs": int(pairs[(a, b)]), "observed_coincidences": fl(obs),
                            "expected_coincidences": fl(exp),
                            "observed_over_expected": fl(obs / exp) if exp else None, "_ratio": obs / exp if exp else None}
    co, ce = rows["CONCERN/OTHER"], rows["CONCERN/ENDORSEMENT"]
    by_count = co["disagreeing_pairs"] > ce["disagreeing_pairs"]
    by_ratio = None if co["_ratio"] is None or ce["_ratio"] is None else co["_ratio"] > ce["_ratio"]
    return {"items": len(s2), "pairable_values": int(sum(len(v) for v in s2 if len(v) >= 2)), "class_pairs": rows,
            "concentrates_at_concern_other_by_count": bool(by_count),
            "concentrates_at_concern_other_by_observed_over_expected": by_ratio,
            "the_two_measures_agree": None if by_ratio is None else bool(by_count == by_ratio)}


def encoding_sensitivity(key1: pd.DataFrame, long1: pd.DataFrame) -> dict:
    ids = sorted(key1.index[key1["is_reliability"]])
    affected = set(ENCODING_AFFECTED)
    if len(affected) != 24 or not affected <= set(ids):
        stop("the 24 mis-decoded reliability items recorded on 26 September 2026 are not all tranche 1 reliability items")
    s1, s2 = ev.reliability_units(key1, long1)
    keep = [j for j, i in enumerate(ids) if i not in affected]
    out = {"status": EXPLORATORY, "items": len(keep)}
    for name, units, cats in (("Stage 1", [s1[j] for j in keep], ["N", "Y"]), ("Stage 2", [s2[j] for j in keep], CLASSES)):
        a = ev.alpha_exact(units, cats)
        pairable = [u for u in units if len(u) >= 2]
        out[name] = {"alpha": fl(a, 4), "alpha_exact": fr(a), "units": len(pairable),
                     "pairable_values": int(sum(len(u) for u in pairable))}
    return out


def annotator_sensitivity(key1: pd.DataFrame, long1: pd.DataFrame) -> dict:
    era = key1["era"].str.strip()
    out = {"status": EXPLORATORY}
    for a in cfg.ANNOTATORS:
        r = long1[(long1["annotator"] == a) & (~long1["missing"])]
        eras = r["id"].map(era).tolist()
        n_h = Counter(eras)
        w = {h: Fraction(N_FRAME[h], n_h[h]) for h in n_h}
        ww = [w[h] for h in eras]
        y = (r["stage1_relevant"] == "Y").tolist()
        cls = r["stage2_class"].tolist()
        total = sum(ww, Fraction(0))
        rel_w = sum((x for x, k in zip(ww, y) if k), Fraction(0))
        den = sum((x for x, k, c in zip(ww, y, cls) if k and c in CLASSES), Fraction(0))
        out[a] = {"sheet_items_rated": int(len(r)), "items_by_era": {h: int(n_h[h]) for h in ERA_ORDER},
                  "coded_relevant": int(sum(y)), "coded_relevant_without_class": int(sum(1 for k, c in zip(y, cls) if k and not c)),
                  "relevance_share": fl(rel_w / total) if total else None,
                  "class_shares_among_relevant": {c: fl(sum((x for x, k, cc in zip(ww, y, cls) if k and cc == c),
                                                            Fraction(0)) / den) if den else None for c in CLASSES},
                  "class_counts_among_relevant": {c: int(sum(1 for k, cc in zip(y, cls) if k and cc == c)) for c in CLASSES}}
    return out


# =============================================================================
# Deviation 2 (rule 9) and counts the record requires (Deviations 10 and 11)
# =============================================================================
def adjudicated_items(data: dict) -> list[dict]:
    longs = pd.concat([data["long1"].assign(tranche=1), data["long2"].assign(tranche=2)], ignore_index=True)
    rows = []
    for j in np.nonzero(data["s2adj"] | data["subadj"])[0]:
        i = data["ids"][j]
        r = longs[(longs["id"] == i) & (~longs["missing"])].sort_values("annotator")
        if data["s2adj"][j]:
            rows.append({"id": i, "tranche": int(data["tranche"][j]), "level": "Stage 2", "adjudicated": data["g2"][j],
                         "given": dict(zip(r["annotator"], r["label4"]))})
        if data["subadj"][j]:
            given = {a: s for a, s, y in zip(r["annotator"], r["subsystem"], r["stage1_relevant"]) if y == "Y" and s}
            rows.append({"id": i, "tranche": int(data["tranche"][j]), "level": "primary subsystem",
                         "adjudicated": data["gsub"][j], "given": given,
                         "adjudicated_value_given_by_an_annotator": data["gsub"][j] in given.values()})
    return rows


def raw_majority_set(data: dict, alpha_lower) -> dict:
    """Rule 9: the figures that rest on adjudicated labels, recomputed with the adjudicated labels removed."""
    g2 = np.where(data["s2adj"], "", data["g2"])
    raw = dict(data, g2=g2, prim=np.isin(g2, CLASSES), gsub=np.where(data["subadj"], "", data["gsub"]))
    allm = np.ones(len(data["ids"]), bool)
    prev = prevalence(raw, allm)
    rates = concern_rates(raw, allm)
    sh = subsystem_shares(raw, allm)
    return {"status": "sensitivity (Deviation 2: the raw-majority set)",
            "items_without_a_stage2_class": int(data["s2adj"].sum()),
            "items_without_a_gold_subsystem": int(data["subadj"].sum()),
            "relevance_rate": "unchanged: the Stage 1 majority stands (Deviation 2)",
            "class_shares_among_relevant": strip(prev["class_shares_among_relevant"]),
            "class_shares_tranche2": strip(prevalence(raw, data["tranche"] == 2)["class_shares_among_relevant"]),
            "concern_rates_weighted": strip(rates), "three_class": three_class_matrix(raw),
            "pi_s_pooled": shares_for_output(sh), "d28": d28(alpha_lower, sh)}


def tranche2_single_rated_counts(key2: pd.DataFrame, long2: pd.DataFrame) -> dict:
    own = long2[~long2["is_reliability"]]
    out = {}
    for a in cfg.ANNOTATORS:
        r = own[own["annotator"] == a]
        lab = [("missing" if m else (x if x in cfg.LABEL4 else "relevant without a class")) for m, x in
               zip(r["missing"], r["label4"])]
        c = Counter(lab)
        out[a] = {"items": int(len(r)), **{k: int(c[k]) for k in cfg.LABEL4 + ["relevant without a class", "missing"]}}
    return out


def missing_labels(data: dict) -> dict:
    """Items without a gold label, by era, tranche and annotator (Deviation 11): the annotators named are those
    whose rating is missing, or who coded the item relevant without giving the missing label."""
    longs = pd.concat([data["long1"], data["long2"]], ignore_index=True)

    def listing(mask, lacks):
        rows = []
        for j in np.nonzero(mask)[0]:
            i = data["ids"][j]
            r = longs[longs["id"] == i]
            who = sorted(a for a, m, y, c, sub in zip(r["annotator"], r["missing"], r["stage1_relevant"],
                                                      r["stage2_class"], r["subsystem"]) if m or lacks(y, c, sub))
            rows.append({"id": i, "era": data["era"][j], "tranche": int(data["tranche"][j]),
                         "reliability_item": bool(len(r) > 1), "annotators": who})
        return rows

    return {"without_a_gold_stage1_label": listing(~data["has1"], lambda y, c, sub: False),
            "relevant_without_a_stage2_label": listing(data["rel"] & ~data["prim"], lambda y, c, sub: y == "Y" and not c),
            "relevant_without_a_gold_subsystem": listing(data["rel"] & (data["gsub"] == ""),
                                                         lambda y, c, sub: y == "Y" and not sub)}


# =============================================================================
# error rates (rules 10, 11 and 13)
# =============================================================================
def concern_rates(data: dict, mask: np.ndarray) -> dict:
    """Weighted TPR and FPR for CONCERN against the other two classes on the primary items selected by mask
    (exact), with the unweighted counts and Wilson intervals. A refusal is not a CONCERN prediction."""
    sel = data["prim"] & mask
    pos = data["g2"] == "CONCERN"
    hit = data["s2"] == "CONCERN"
    w = data["w"]
    sp, sn = sum(w[sel & pos], Fraction(0)), sum(w[sel & ~pos], Fraction(0))
    tp, fp = sum(w[sel & pos & hit], Fraction(0)), sum(w[sel & ~pos & hit], Fraction(0))
    tpr = tp / sp if sp else None
    fpr = fp / sn if sn else None
    return {"items": int(sel.sum()), "concern_items": int((sel & pos).sum()), "other_items": int((sel & ~pos).sum()),
            "tpr": fl(tpr), "fpr": fl(fpr), "tpr_exact": fr(tpr), "fpr_exact": fr(fpr),
            "tpr_counts": wilson(int((sel & pos & hit).sum()), int((sel & pos).sum())),
            "fpr_counts": wilson(int((sel & ~pos & hit).sum()), int((sel & ~pos).sum())), "_tpr": tpr, "_fpr": fpr}


def three_class_matrix(data: dict) -> dict:
    sel = data["prim"]
    gold = data["g2"]
    pred = np.where(np.isin(data["s2"], CLASSES), data["s2"], "OTHER")      # a refusal counts as OTHER (rule 13)
    w = data["w"]
    M, exact, counts = {}, {}, {}
    for a in CLASSES:
        ga = sel & (gold == a)
        den = sum(w[ga], Fraction(0))
        M[a] = {b: fl(sum(w[ga & (pred == b)], Fraction(0)) / den) if den else None for b in CLASSES}
        exact[a] = {b: fr(sum(w[ga & (pred == b)], Fraction(0)) / den) if den else None for b in CLASSES}
        counts[a] = {b: int((ga & (pred == b)).sum()) for b in CLASSES}
    return {"weighted_rates_gold_by_classified": M, "weighted_rates_exact": exact,
            "counts_gold_by_classified": counts, "refusals_counted_as_other": int((sel & ~np.isin(data["s2"], CLASSES)).sum()),
            "note": "M[i][j]: the weighted share of the gold class i items that the deployed Stage 2 classifier "
                    "classifies j, on the primary item set, with the pooled design weights"}


def relevance_error(data: dict) -> dict:
    s = data["has1"]
    gy = data["rel"]
    py = data["s1"] == "Y"
    by_era = {}
    for e in ERA_ORDER:
        m = s & (data["era"] == e)
        by_era[e] = {}
        for k, num, den in (("e_in", m & py & ~gy, m & py), ("e_out", m & ~py & gy, m & ~py)):
            by_era[e][k] = {**wilson(int(num.sum()), int(den.sum())),
                            "exact": fr(Fraction(int(num.sum()), int(den.sum()))) if den.sum() else None}
    wrongly_in = s & py & ~gy
    wrongly_out = s & ~py & gy
    return {"by_era": by_era,
            "note": "e_in and e_out are sample proportions within each era; the Wilson intervals are description and "
                    "do not enter the relevance-error series (Deviation 13)",
            "wrongly_included_classified_concern_by_stage2": wilson(int((wrongly_in & (data["s2"] == "CONCERN")).sum()),
                                                                    int(wrongly_in.sum())),
            "wrongly_left_out_gold_concern": wilson(int((wrongly_out & (data["g2"] == "CONCERN")).sum()),
                                                    int(wrongly_out.sum()))}


def three_way(data: dict, rates: dict) -> dict:
    s = data["has1"]
    era = data["era"][s]
    py = (data["s1"] == "Y")[s]
    first = ratio_estimate((data["g2"] == "CONCERN")[s], data["prim"][s], era, N_FRAME)
    second = ratio_estimate(py & (data["s2"] == "CONCERN")[s], py, era, N_FRAME)
    tpr, fpr = rates["_tpr"], rates["_fpr"]
    raw = (second["_r"] - fpr) / (tpr - fpr) if (second["_r"] is not None and None not in (tpr, fpr)
                                                 and tpr != fpr) else None
    clipped = None if raw is None else min(max(raw, Fraction(0)), Fraction(1))
    return {"gold_concern_share_among_gold_relevant": strip(first),
            "classified_concern_share_among_items_classified_relevant": strip(second),
            "that_share_corrected_with_the_rates_of_record": fl(clipped), "corrected_raw": fl(raw),
            "corrected_raw_exact": fr(raw), "corrected_was_clipped": None if raw is None else bool(raw != clipped),
            "note": "The first two carry the intervals of Deviation 3; the third carries none (Deviation 13)."}


# =============================================================================
# the item resamples and the temporal calibration check (rule 14)
# =============================================================================
def primary_strata(data: dict) -> dict:
    """The primary item set by era stratum, each sorted by comment id as strings (code-point order)."""
    return {e: sorted((data["ids"][j] for j in np.nonzero(data["prim"] & (data["era"] == e))[0]), key=str)
            for e in ERA_ORDER}


def item_index_arrays(strata: dict, generator: list = ITEM_GENERATOR) -> tuple[dict, str]:
    rng = np.random.default_rng(generator)
    arrays = {e: rng.integers(0, len(strata[e]), size=(N_RESAMPLES, len(strata[e]))) for e in ERA_ORDER}
    h = hashlib.sha256()
    for e in ERA_ORDER:
        h.update(np.ascontiguousarray(arrays[e], dtype="<i8").tobytes(order="C"))
    return arrays, h.hexdigest()


def resample_counts(arrays: dict, strata: dict) -> dict:
    """How many times each item of a stratum is drawn in each resample: an N_RESAMPLES x n_e matrix."""
    out = {}
    for e in ERA_ORDER:
        n = len(strata[e])
        out[e] = np.bincount((arrays[e] + n * np.arange(N_RESAMPLES)[:, None]).ravel(),
                             minlength=N_RESAMPLES * n).reshape(N_RESAMPLES, n).astype(np.float64)
    return out


def resampled_block_rates(data: dict, strata: dict, counts: dict) -> dict:
    """For every resample: the weighted CONCERN TPR and FPR in each block, on both tranches and on each tranche,
    with the pooled design weights; NaN where the denominator is empty."""
    pos_of = {data["ids"][j]: j for j in range(len(data["ids"]))}
    idx = {e: [pos_of[i] for i in strata[e]] for e in ERA_ORDER}

    def weighted(num_ok, den_ok):
        num = np.zeros(N_RESAMPLES)
        den = np.zeros(N_RESAMPLES)
        for e in ERA_ORDER:
            w = float(Fraction(*ERAS[e]))
            num += w * (counts[e] @ num_ok[idx[e]].astype(np.float64))
            den += w * (counts[e] @ den_ok[idx[e]].astype(np.float64))
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(den > 0, num / den, np.nan)

    pos = data["g2"] == "CONCERN"
    hit = data["s2"] == "CONCERN"
    out = {}
    for scope, tmask in (("both tranches", np.ones(len(pos), bool)), ("tranche 1", data["tranche"] == 1),
                         ("tranche 2", data["tranche"] == 2)):
        for b in ("early", "late"):
            m = data["prim"] & tmask & (data["block"] == b)
            out[(scope, b, "tpr")] = weighted(m & pos & hit, m & pos)
            out[(scope, b, "fpr")] = weighted(m & ~pos & hit, m & ~pos)
    return out


def percentile_interval(values: np.ndarray) -> dict:
    undefined = int(np.isnan(values).sum())
    if undefined > MAX_UNDEFINED:
        return {"low": None, "high": None, "resamples_without_value": undefined}
    low, high = np.nanpercentile(values, [2.5, 97.5])
    return {"low": fl(low), "high": fl(high), "resamples_without_value": undefined}


def temporal_check(data: dict, boot: dict) -> dict:
    out = {}
    for scope, tmask in (("both tranches", np.ones(len(data["ids"]), bool)), ("tranche 1", data["tranche"] == 1),
                         ("tranche 2", data["tranche"] == 2)):
        part = {}
        for b in ("early", "late"):
            r = concern_rates(data, tmask & (data["block"] == b))
            r["tpr_interval95"] = percentile_interval(boot[(scope, b, "tpr")])
            r["fpr_interval95"] = percentile_interval(boot[(scope, b, "fpr")])
            part[b] = r
        diffs = {}
        for k in ("tpr", "fpr"):
            e, l = part["early"][f"_{k}"], part["late"][f"_{k}"]
            d = (l - e) if (e is not None and l is not None) else None
            diffs[f"{k}_late_minus_early"] = {"difference": fl(d), "difference_exact": fr(d),
                                             **percentile_interval(boot[(scope, "late", k)] - boot[(scope, "early", k)])}
        out[scope] = {"early": strip(part["early"]), "late": strip(part["late"]), **diffs}
    return out


def f1_block(data: dict, mask: np.ndarray) -> dict:
    """Macro-F1 and per-class F1 of the deployed Stage 2 classifier, unweighted; a refusal is an error."""
    sel = data["prim"] & mask
    gold = np.array([CLASSES.index(x) for x in data["g2"][sel]], dtype=np.int64)
    pred = np.array([CLASSES.index(x) if x in CLASSES else -1 for x in data["s2"][sel]], dtype=np.int64)
    tp, pp, gg = ev.class_counts(pred, gold, 3)
    f1 = [Fraction(2 * tp[c], pp[c] + gg[c]) if gg[c] else None for c in range(3)]
    if len(gold) and all(gg):
        from sklearn.metrics import f1_score                        # a second implementation, as a check
        check = f1_score(gold, pred, labels=[0, 1, 2], average=None, zero_division=0)
        if np.abs(check - np.array([float(x) for x in f1])).max() > 1e-12:
            stop("the two F1 implementations disagree. Report this message before going further.")
    macro = sum(f1, Fraction(0)) / 3 if all(x is not None for x in f1) else None
    return {"items": int(sel.sum()), "macro_f1": fl(macro), "macro_f1_exact": fr(macro),
            "per_class": {c: {"f1": fl(f1[j]), "tp": tp[j], "predicted": pp[j], "gold": gg[j]} for j, c in enumerate(CLASSES)},
            "refusals": int((pred == -1).sum())}


def stage1_block(data: dict, mask: np.ndarray) -> dict:
    """The deployed Stage 1 classifier's accuracy on each class (Wilson) and balanced accuracy, unweighted, from its
    cross-validated predictions."""
    s = data["has1"] & mask
    py = data["s1"] == "Y"
    acc_y = wilson(int((s & data["rel"] & py).sum()), int((s & data["rel"]).sum()))
    acc_n = wilson(int((s & ~data["rel"] & ~py).sum()), int((s & ~data["rel"]).sum()))
    ba = (Fraction(acc_y["k"], acc_y["n"]) + Fraction(acc_n["k"], acc_n["n"])) / 2 if acc_y["n"] and acc_n["n"] else None
    return {"items": int(s.sum()), "accuracy_relevant": acc_y, "accuracy_not_relevant": acc_n,
            "balanced_accuracy": fl(ba), "balanced_accuracy_exact": fr(ba)}


# =============================================================================
# checks against the record, the preflight's dry run, and the previews (rule 15)
# =============================================================================
def reproduce_record(data: dict) -> dict:
    """Figures of record that rest on these inputs, none by era, year or block: each must be reproduced exactly."""
    res = data["evaluation"]
    rates = concern_rates(data, np.ones(len(data["ids"]), bool))
    if fr(rates["_tpr"] - rates["_fpr"]) != RATES_OF_RECORD["tpr_minus_fpr_exact"] \
            or rates["tpr"] != RATES_OF_RECORD["tpr"] or rates["fpr"] != RATES_OF_RECORD["fpr"]:
        stop("the weighted CONCERN rates recomputed here are not the rates of record. Report this message before going further.")
    unw = res["stage2"]["prevalence_correction_error_rates"]["unweighted"]
    tc, fc = rates["tpr_counts"], rates["fpr_counts"]
    if fr(Fraction(tc["k"], tc["n"]) - Fraction(fc["k"], fc["n"])) != unw["tpr_minus_fpr_exact"] \
            or fl(Fraction(tc["k"], tc["n"])) != unw["tpr"] or fl(Fraction(fc["k"], fc["n"])) != unw["fpr"]:
        stop("the unweighted CONCERN rates recomputed here are not those of the evaluation output")
    conf = res["stage2"]["configurations"][DEPLOYED_STAGE2]["pooled"]["confusion_gold_by_predicted"]
    for a in CLASSES:
        ga = data["prim"] & (data["g2"] == a)
        mine = {b: int((ga & (data["s2"] == b)).sum()) for b in CLASSES} | {"no class": int((ga & ~np.isin(data["s2"], CLASSES)).sum())}
        if mine != conf[a]:
            stop("the deployed Stage 2 classifier's confusion table differs from the evaluation output")
    sets = res["item_sets"]
    mine = {"stage2_primary": {"items": int(data["prim"].sum()), "tranche1": int((data["prim"] & (data["tranche"] == 1)).sum()),
                               "tranche2": int((data["prim"] & (data["tranche"] == 2)).sum()),
                               "by_class": {c: int((data["g2"] == c).sum()) for c in CLASSES}},
            "stage1": {"items": int(data["has1"].sum()), "Y": int(data["rel"].sum()), "N": int((data["g1"] == "N").sum())}}
    if mine != sets:
        stop("the item sets differ from those of the evaluation output")
    for name, key in ((DEPLOYED_STAGE1, "s1"), (TEXT_ONLY, "s1t")):
        rec = res["stage1"]["configurations"][name]["accuracy_by_class"]
        py = data[key] == "Y"
        got = {"Y": (int((data["rel"] & py).sum()), int(data["rel"].sum())),
               "N": (int((data["has1"] & ~data["rel"] & ~py).sum()), int((data["has1"] & ~data["rel"]).sum()))}
        if any(got[c] != (rec[c]["correct"], rec[c]["items"]) for c in ("Y", "N")):
            stop(f"{name}: the Stage 1 accuracy by class differs from the evaluation output")
    return {"weighted_concern_rates": {"tpr": rates["tpr"], "fpr": rates["fpr"],
                                       "tpr_minus_fpr_exact": fr(rates["_tpr"] - rates["_fpr"])},
            "unweighted_concern_rates": {"tpr": f"{tc['k']}/{tc['n']}", "fpr": f"{fc['k']}/{fc['n']}"},
            "confusion_table_item_sets_and_stage1_accuracies": "as in the evaluation output", "_rates": rates}


def shuffled_for_dry_run(data: dict) -> dict:
    """The inputs with each item's era, block and design weight taken from another item by a fixed permutation, so
    that the preflight's dry run of every analysis computes no figure by the real era or block."""
    perm = np.random.default_rng(DRY_RUN_GENERATORS["shuffle"]).permutation(len(data["ids"]))
    return dict(data, era=data["era"][perm], block=data["block"][perm], w=data["w"][perm])


def check_proxy_source() -> None:
    """config.py is the file committed at be001c7 (its SHA-256); CORE_TERMS, read from it without running it, is the
    term list above; and the patterns follow from the terms as Deviation 14 states."""
    src = PROXY_SOURCE
    path = cfg.REPO / src["file"]
    got = ev.text_sha256(path) if path.exists() else None
    if got != src["sha256_lf"]:
        stop(f"{src['file']} (the term list of the lexical proxy) is not the file committed at {src['commit']} "
             f"(SHA-256 {(got or 'none')[:16]}..., recorded {src['sha256_lf'][:16]}...). "
             f"Report this message before going further.")
    terms = None
    for node in ast.parse(path.read_text(encoding="utf-8-sig")).body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == src["term_list"]
                                                for x in node.targets):
            terms = ast.literal_eval(node.value)
    if terms != PROXY_TERMS:
        stop(f"{src['file']}: {src['term_list']} is not the term list recorded for the lexical proxy. "
             f"Report this message before going further.")
    if [proxy_pattern(x) for x in terms] != PROXY_PATTERNS or PROXY_RE.pattern != "|".join(PROXY_PATTERNS) \
            or PROXY_RE.flags != re.IGNORECASE | re.UNICODE:
        stop("the lexical-proxy patterns do not follow from the term list as Deviation 14 states. "
             "Report this message before going further.")


def compare_previews(data: dict) -> dict:
    """The four previews, set against what this script computes (none is by temporal block)."""
    t1 = data["tranche"] == 1
    out = {}
    forms = alpha_forms(subsystem_units(data["key1"], data["long1"]))
    found = {k: (f"{float(v['_alpha']):.3f}" if v["_alpha"] is not None else None, v["units"], v["pairable_values"])
             for k, v in forms.items()}
    out["tranche1_subsystem_alpha_register_30_september"] = {"same": found == PREVIEW_TRANCHE1_SUBSYSTEM_ALPHA,
                                                             "computed": found, "preview": PREVIEW_TRANCHE1_SUBSYSTEM_ALPHA}
    sh = subsystem_shares(data, t1)
    found = {"shares": {k: (pct1(sh["shares"][k]["estimate"]), pct1(sh["shares"][k]["low"]), pct1(sh["shares"][k]["high"]))
                        for k in PREVIEW_TRANCHE1_PI_S["shares"]},
             "items": {k: sh["shares"][k]["numerator_items"] for k in SUBSYSTEMS},
             "concern_items": sh["concern_items_with_gold_subsystem"] + sh["concern_items_without_gold_subsystem"]}
    out["tranche1_pi_s_register_4_october"] = {"same": found == PREVIEW_TRANCHE1_PI_S, "computed": found,
                                               "preview": PREVIEW_TRANCHE1_PI_S}
    s = t1 & data["has1"]
    dec = composition_check(data["rel"][s], data["era"][s], data["sub"][s])["seven_groups"]
    found = {"difference": f"{100 * float(dec['_difference']):+.1f}", "mix": f"{100 * float(dec['_mix']):+.1f}",
             "within": f"{100 * float(dec['_within']):+.1f}"}
    out["tranche1_decomposition_deviation_8"] = {"same": found == PREVIEW_TRANCHE1_DECOMPOSITION, "computed": found,
                                                 "preview": PREVIEW_TRANCHE1_DECOMPOSITION}
    forms = alpha_forms(subsystem_units(data["key1"], data["long1"]) + subsystem_units(data["key2"], data["long2"]))
    found = {k: (f"{float(v['_alpha']):.3f}" if v["_alpha"] is not None else None) for k, v in forms.items()}
    out["pooled_subsystem_alpha_register_10_october"] = {"same": found == PREVIEW_POOLED_SUBSYSTEM_ALPHA,
                                                         "computed": found, "preview": PREVIEW_POOLED_SUBSYSTEM_ALPHA}
    return out


# =============================================================================
# the analyses
# =============================================================================
def analyse(data: dict, record: dict, previews: dict, generator: list = ITEM_GENERATOR) -> dict:
    allm = np.ones(len(data["ids"]), bool)
    t1, t2 = data["tranche"] == 1, data["tranche"] == 2
    s = data["has1"]

    # 1. prevalence
    p_pooled, p1, p2 = prevalence(data, allm), prevalence(data, t1), prevalence(data, t2)
    prev = {"pooled": strip(p_pooled), "tranche 1": strip(p1), "tranche 2": strip(p2),
            "tranche 2 minus tranche 1": tranche_difference(prevalence(data, t1, fpc=False),
                                                            prevalence(data, t2, fpc=False))}

    # 2. RQ4
    rq4 = {"era_difference_pooled": prev["pooled"]["era_difference_2022_2025_minus_2016_2018"],
           "composition_check_pooled": strip(composition_check(data["rel"][s], data["era"][s], data["sub"][s])),
           "composition_check_tranche1_beside_the_preview": strip(composition_check(data["rel"][s & t1], data["era"][s & t1],
                                                                                   data["sub"][s & t1]))}

    # 3. text-only sensitivity
    era = data["era"][s]
    ones = np.ones(int(s.sum()), dtype=np.int64)
    s1t = (data["s1t"] == "Y")[s]
    six = np.isin(data["sub"][s], SIX)
    rel = data["rel"][s]
    if any(int((era == e).sum()) == 0 for e in ERA_ORDER):
        stop("an era has no item with a gold Stage 1 label")
    sizes6 = {e: Fraction(N_FRAME[e] * int((six & (era == e)).sum()), int((era == e).sum())) for e in ERA_ORDER}
    text_only = {
        "status": EXPLORATORY,
        "a_text_only_variant_cross_validated_predictions": {
            "rates": strip(rates_by_era(s1t, ones, era, N_FRAME)),
            "decomposition": strip(decomposition(s1t, era, np.array([SEVEN_GROUPS[x] for x in data["sub"][s]],
                                                                      dtype=object), SEVEN_NAMES))},
        "b_gold_labels_in_the_six_subreddits": {
            "items": int(six.sum()), "rates": strip(rates_by_era(rel & six, six, era, N_FRAME)),
            "decomposition": strip(decomposition(rel[six], era[six], data["sub"][s][six], SIX, sizes6))}}

    # 4. lexical proxy
    proxy = lexical_proxy(data)

    # 5. subsystem agreement and D28
    u1 = subsystem_units(data["key1"], data["long1"])
    u2 = subsystem_units(data["key2"], data["long2"])
    alpha = {"both tranches (200 items)": alpha_forms(u1 + u2), "tranche 1 (100 items)": alpha_forms(u1),
             "tranche 2 (100 items)": alpha_forms(u2)}
    lower_pooled = lower_alpha(alpha["both tranches (200 items)"])
    sh_pooled, sh_t1 = subsystem_shares(data, allm), subsystem_shares(data, t1)
    pooled = d28(lower_pooled, sh_pooled)
    subsystem = {"alpha": strip(alpha), "pi_s_pooled": shares_for_output(sh_pooled),
                 "pi_s_tranche1": shares_for_output(sh_t1), "d28_pooled_of_record": pooled,
                 "d28_tranche1_beside": d28(lower_alpha(alpha["tranche 1 (100 items)"]), sh_t1),
                 "d28_outcome_against_tranche1": d28_changed(pooled),
                 "secondary_labels": secondary_labels(data["long1"], data["long2"])}

    # 6. tranche 1 checks
    rel_rec = data["evaluation"]["reliability"]["tranche 1 (100 items)"]
    t1checks = {"disagreement_concentration": strip(disagreement_concentration(data["key1"], data["long1"])),
                "encoding_sensitivity": encoding_sensitivity(data["key1"], data["long1"]),
                "alpha_on_the_100_items_of_record": {k: rel_rec[k]["alpha"] for k in ("Stage 1", "Stage 2")},
                "annotator_sensitivity": annotator_sensitivity(data["key1"], data["long1"]),
                "bootstrap_alpha_intervals_of_record": {"status": EXPLORATORY,
                                                        **{k: {"alpha": v["alpha"], **v["interval95"]}
                                                           for k, v in rel_rec.items()}}}

    # 7. Deviation 2
    dev2 = {"adjudicated_items": adjudicated_items(data), "raw_majority_set": raw_majority_set(data, lower_pooled)}

    # 8. error rates
    rates = record["_rates"]
    errors = {"rates_of_record_reproduced": record["weighted_concern_rates"],
              "three_class": three_class_matrix(data), "relevance_error": relevance_error(data),
              "three_way_comparison": three_way(data, rates)}

    # 9. temporal calibration check
    strata = primary_strata(data)
    arrays, arrays_sha = item_index_arrays(strata, generator)
    boot = resampled_block_rates(data, strata, resample_counts(arrays, strata))
    blocks = data["block"]
    temporal = {"block_rates": temporal_check(data, boot),
                "stage2_f1_by_block": {b: f1_block(data, blocks == b) for b in ("early", "late")},
                "stage1_accuracy_by_block": {b: stage1_block(data, blocks == b) for b in ("early", "late")},
                "items_by_block": {"primary_item_set": {b: int((data["prim"] & (blocks == b)).sum()) for b in ("early", "late")},
                                   "stage1_items": {b: int((s & (blocks == b)).sum()) for b in ("early", "late")}},
                "item_resamples": {"resamples": N_RESAMPLES, "generator": f"numpy.random.default_rng({generator})",
                                   "strata_sizes": {e: len(strata[e]) for e in ERA_ORDER},
                                   "index_arrays_sha256": arrays_sha,
                                   "hash_rule": "each era's array as little-endian 64-bit integers in row-major order, "
                                                "the three joined in era order"},
                "note": "TPR and FPR for CONCERN against the other two classes, weighted by the pooled design weights; "
                        "intervals: 2.5th and 97.5th percentiles over the 2,000 item resamples, a figure for one tranche "
                        "formed from that tranche's items in each resample; Wilson intervals on the unweighted counts. "
                        "F1 and the Stage 1 accuracies are on both tranches, unweighted and descriptive."}

    # 10. counts the record requires
    counts = {"tranche2_single_rated_items_by_annotator": tranche2_single_rated_counts(data["key2"], data["long2"]),
              "missing_labels": missing_labels(data)}

    return {"prevalence": prev, "rq4": rq4, "text_only_sensitivity": text_only, "lexical_proxy": proxy,
            "subsystem": subsystem, "tranche1_checks": t1checks, "deviation_2": dev2, "error_rates": strip(errors),
            "temporal_calibration_check": temporal, "counts_required_by_the_record": counts,
            "figures_of_record_reproduced": strip(record), "comparison_with_previews": previews}


# =============================================================================
# main
# =============================================================================
def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Sample analyses of record (Deviation 13).")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks; no rate by block shown; writes nothing")
    mode.add_argument("--confirm-committed", action="store_true", help="the run of record (after the commit)")
    args = ap.parse_args()
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit) or --confirm-committed (after the commit: the run of record)")
    print("Sample analyses (Deviation 13): " + ("preflight, before the commit\n" if args.preflight else "the run of record\n"))
    me = ev.text_sha256(Path(__file__).resolve())
    out_dir = run_folder(me)
    print(f"this script: analysis_01_sample.py SHA-256 {me}")
    if (out_dir / "sample_results.json").exists():
        stop(f"this script's sample analyses have already been run: their results are in {out_dir}. They are run once.")
    loaded = load_all()
    data = loaded["data"]
    print("inputs: every input with a recorded SHA-256 matches it (the scripts of record, the folds, the gold label "
          "fingerprints, the model inputs, the twelve prediction files, the files of record, the tranche 2 key and the "
          "evaluation output); the gold labels and subsystems re-formed from the files of record match gold_labels.csv; "
          "corpus v2.2 and the frame match R5 (membership, counts by subreddit and tier, the split at the boundary)")
    record = reproduce_record(data)
    print("record: the rates of record, the confusion table, the item sets and the Stage 1 accuracies of the "
          "evaluation output are reproduced exactly")
    check_proxy_source()
    print(f"lexical proxy: {PROXY_SOURCE['file']} matches the file committed at {PROXY_SOURCE['commit']}; its "
          f"{PROXY_SOURCE['term_list']} and the patterns of Deviation 14 check")
    previews = compare_previews(data)
    for name, v in previews.items():
        print(f"preview {name}: {'same' if v['same'] else 'DIFFERENT: computed ' + json.dumps(v['computed'])}")
    if args.preflight:
        dry = analyse(shuffled_for_dry_run(data), record, previews, generator=DRY_RUN_GENERATORS["resamples"])
        render_report(json.loads(json.dumps(strip(dry), default=json_default)))
        print("dry run: every analysis ran on the real inputs with each item's era, block and design weight taken "
              "from another item, and its report was rendered; the result was discarded and nothing was shown")
        n_diff = sum(not v["same"] for v in previews.values())
        print("\nPREFLIGHT PASSED: every input that has a record matches it and the figures of record are reproduced. "
              "No rate by the real temporal block was computed or shown, no figure by era or block was shown apart "
              "from the preview comparisons, and nothing was written.")
        if n_diff:
            print(f"{n_diff} of {len(previews)} previews differ from what this script computes. Report this output "
                  f"before committing: a difference that follows from a rule of this file is recorded in the register, "
                  f"not removed.")
        return
    results = analyse(data, record, previews)
    results = {"specification": "R1, R5 and Deviations 1 to 14 of docs/analysis_preregistration.md; "
                                "analysis_01_sample.py", **results,
               "inputs_sha256": loaded["shas"], "corpus_checks": loaded["corpus"]}
    write_outputs(results, me, out_dir, loaded)


# =============================================================================
# outputs
# =============================================================================
def json_default(x):
    """NumPy scalars become Python numbers; anything else that JSON cannot hold is an error, not a string."""
    if isinstance(x, np.bool_):
        return bool(x)
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.floating):
        return fl(x)
    raise TypeError(f"a result of type {type(x).__name__} cannot be written: report this message before going further")


def write_outputs(results: dict, me: str, out_dir: Path, loaded: dict) -> None:
    """Written to a fresh work folder, then moved into place with sample_results.json last: a run that fails
    part-way leaves no results file, so it can simply be run again (it gives the same bytes)."""
    clean = json.loads(json.dumps(strip(results), default=json_default))
    report = render_report(clean)
    work = OUT_ROOT / f"in_progress_{os.getpid()}_{time.time_ns()}"
    work.mkdir(parents=True)
    try:
        mc.write_json(work / "sample_results.json", clean)
        with open(work / "sample_report.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
        outputs = {name: mc.sha256_file(work / name) for name in ("sample_results.json", "sample_report.md")}
        created = mc.now_iso()
        mc.write_json(work / "sample_manifest.json", {
            "created": created, "script": {"file": "analysis_01_sample.py", "sha256_lf": me},
            "scripts_of_record_sha256_lf": loaded["scripts"], "lexical_proxy_source": PROXY_SOURCE,
            "inputs_sha256": loaded["shas"], "corpus": loaded["corpus"], "outputs_sha256": outputs,
            "versions": {**mc.versions("numpy", "pandas", "scipy", "sklearn", "pyarrow"), **loaded["versions"]}})
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in ("sample_report.md", "sample_manifest.json", "sample_results.json"):
            mc.replace_patiently(work / name, out_dir / name)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    t = clean["temporal_calibration_check"]["item_resamples"]
    rel = out_dir.relative_to(cfg.REPO).as_posix()
    src = PROXY_SOURCE
    mc.show_register_block(out_dir / "PASTE_sample_block.txt", [
        f"- `analysis_01_sample.py` (SHA-256 `{me}`) run {created} with `--confirm-committed`. Every input with a "
        f"recorded SHA-256 matched it; corpus v2.2 and the frame matched R5.",
        f"- Outputs, in `{rel}/` (not committed): `sample_results.json` SHA-256 `{outputs['sample_results.json']}`; "
        f"`sample_report.md` `{outputs['sample_report.md']}`.",
        f"- Item index arrays (`numpy.random.default_rng([24916660, 3, 1])`, {N_RESAMPLES:,} resamples; strata of "
        f"{', '.join(str(v) for v in t['strata_sizes'].values())} items): SHA-256 `{t['index_arrays_sha256']}`.",
        f"- Lexical proxy: term list `{src['term_list']}` in `{src['file']}` as committed at `{src['commit']}` "
        f"(SHA-256 `{src['sha256_lf']}`); matching rule of Deviation 14.",
        f"- Corpus v2.2 file SHA-256 `{loaded['corpus']['corpus_file_sha256']}`; frame list "
        f"`{loaded['corpus']['frame_file_sha256']}` (both recorded here for the first time; R5 records the memberships).",
    ])
    print(f"\nwritten: {out_dir}")


def render_report(r: dict) -> str:
    def pct(x):
        return "n/a" if x is None else f"{100 * x:.1f}%"

    def pts(x):
        return "n/a" if x is None else f"{100 * x:+.1f} points"

    def ci(v, f=pct):
        return "no interval" if v.get("low") is None else f"{f(v['low'])} to {f(v['high'])}"

    def num(x, d=3):
        return "n/a" if x is None else f"{x:.{d}f}"

    def yes(x):
        return {True: "yes", False: "no", None: "cannot be evaluated"}[x]

    def est(v):
        return f"{pct(v['estimate'])} ({ci(v)})"

    scopes = ("pooled", "tranche 1", "tranche 2")
    L = ["# Sample analyses of record (Deviation 13)", "",
         "The main figures. Every figure, with the counts behind it, is in `sample_results.json`.", ""]
    p = r["prevalence"]
    td = p["tranche 2 minus tranche 1"]
    L += ["## Prevalence (design-weighted; 95% intervals of Deviation 3, and Wald intervals for the tranche difference)", "",
          "| Estimate | Pooled sample | Tranche 1 | Tranche 2 | Tranche 2 minus tranche 1 |", "|---|---|---|---|---|"]
    for k in ["overall"] + ERA_ORDER:
        d = td[f"relevance_rate_{k}"]
        L.append(f"| Relevance rate, {k} | " + " | ".join(est(p[s]["relevance_rate"][k]) for s in scopes) +
                 f" | {pts(d['difference'])} ({ci(d, pts)}) |")
    for c in CLASSES:
        d = td[f"{c}_share_among_relevant"]
        L.append(f"| {c} share among relevant | " + " | ".join(est(p[s]["class_shares_among_relevant"][c]) for s in scopes) +
                 f" | {pts(d['difference'])} ({ci(d, pts)}) |")
    L.append("| Relevance rate, 2022-2025 minus 2016-2018 | " + " | ".join(
        f"{pts(p[s]['era_difference_2022_2025_minus_2016_2018']['difference'])} "
        f"({ci(p[s]['era_difference_2022_2025_minus_2016_2018'], pts)})" for s in scopes) + " | |")
    L += ["", "The tranche difference is description (Deviation 11); it is not used to choose between the tranches.", ""]

    L += ["## RQ4 composition check (Deviation 8; exploratory)", "",
          "| Sample | Groups | Difference | Mix part | Within-group part | Standardised era rates |", "|---|---|---|---|---|---|"]
    flags = []
    for label, block in (("pooled", r["rq4"]["composition_check_pooled"]),
                         ("tranche 1", r["rq4"]["composition_check_tranche1_beside_the_preview"])):
        for g in ("seven_groups", "two_groups"):
            x = block[g]
            st = " / ".join(pct(x["standardised_era_rates_pooled_frame_mix"][e]) for e in ERA_ORDER)
            L.append(f"| {label} | {g.replace('_', ' ')} | {pts(x['difference_2022_2025_minus_2016_2018'])} | "
                     f"{pts(x['mix_part'])} | {pts(x['within_group_part'])} | {st} |")
            flags += [f"{label}, {g.replace('_', ' ')}: {f}" for f in x["flags"]]
    L += ["", "Standardised era rates: 2016-2018 / 2019-2021 / 2022-2025, at the pooled frame mix. Flags: " +
          ("; ".join(flags) if flags else "none") + ".", ""]

    t = r["text_only_sensitivity"]
    a, b = t["a_text_only_variant_cross_validated_predictions"], t["b_gold_labels_in_the_six_subreddits"]
    L += ["## Text-only sensitivity (Deviations 12 and 13; exploratory)", "",
          "| Source | 2016-2018 | 2019-2021 | 2022-2025 | 2022-2025 minus 2016-2018 | Mix part | Within-group part |",
          "|---|---|---|---|---|---|---|",
          "| (a) text-only variant, all items | " + " | ".join(est(a["rates"][e]) for e in ERA_ORDER) +
          f" | {pts(a['decomposition']['difference_2022_2025_minus_2016_2018'])} | "
          f"{pts(a['decomposition']['mix_part'])} | {pts(a['decomposition']['within_group_part'])} |",
          "| (b) gold labels, six subreddits | " + " | ".join(est(b["rates"][e]) for e in ERA_ORDER) +
          f" | {pts(b['decomposition']['difference_2022_2025_minus_2016_2018'])} | {pts(b['decomposition']['mix_part'])} | "
          f"{pts(b['decomposition']['within_group_part'])} |", "",
          "Decomposition of (a) over the seven groups of Deviation 8; of (b) over its six subreddits.", ""]

    px = r["lexical_proxy"]
    L += ["## Lexical proxy against the gold Stage 1 label (items with a gold Stage 1 label)", "",
          "| Subreddit | Items | Proxy and gold | Proxy only | Gold only | Neither | Agreement |", "|---|---|---|---|---|---|---|"]
    for k, v in px["by_subreddit"].items():
        L.append(f"| {k} | {v['items']} | {v['proxy_and_gold_relevant']} | {v['proxy_only']} | {v['gold_only']} | "
                 f"{v['neither']} | {pct(v['agreement']['share'])} |")
    src = px["source"]
    L += ["", f"Term list: `{src['term_list']}` in `{src['file']}` as committed at `{src['commit']}`; matching rule: "
              f"Deviation 14 (whole words, in any letter case). Text: {px['text']}; annotated items "
              f"whose clean_body differs from the text given to the models: "
              f"{px['annotated_items_whose_clean_body_differs_from_the_model_input_text']}, of which the proxy gives "
              f"another result on {px['items_where_the_model_input_text_gives_another_result']}.", ""]

    sb = r["subsystem"]
    L += ["## Subsystem agreement and D28", "", "| Reliability items | Form | Alpha | Units | Pairable values |",
          "|---|---|---|---|---|"]
    for k, forms in sb["alpha"].items():
        for f_, v in forms.items():
            L.append(f"| {k} | {f_.replace('_', ' ')} | {num(v['alpha'], 4)} | {v['units']} | {v['pairable_values']} |")
    L += ["", "| Subsystem | pi_s, pooled sample | Items | pi_s, tranche 1 | Items |", "|---|---|---|---|---|"]
    for k in SUBSYSTEMS:
        x, y = sb["pi_s_pooled"]["shares"][k], sb["pi_s_tranche1"]["shares"][k]
        if k == "v2x":
            L.append(f"| v2x | count only (R5) | {x['numerator_items']} | count only (R5) | {y['numerator_items']} |")
        else:
            L.append(f"| {k} | {est(x)} | {x['numerator_items']} | {est(y)} | {y['numerator_items']} |")
    for label, d in (("pooled sample (of record)", sb["d28_pooled_of_record"]), ("tranche 1 (beside it)", sb["d28_tranche1_beside"])):
        L += ["", f"D28, {label}: lower subsystem alpha {num(d['alpha_used'], 4)}. Rule 1 (alpha below 0.6) fires: "
                  f"{yes(d['rule1_alpha_below_0_6'])}. Rule 2: condition (i), alpha at least 0.7: "
                  f"{yes(d['rule2_condition_i_alpha_at_least_0_7'])}; condition (ii), the intervals of {d['largest_eligible']} "
                  f"and {d['second_largest_eligible']} do not overlap ({pct(d['lower_limit_of_largest'])} against "
                  f"{pct(d['upper_limit_of_second'])}): {yes(d['rule2_condition_ii_intervals_do_not_overlap'])}; "
                  f"met: {yes(d['rule2_met'])}."]
    ch = sb["d28_outcome_against_tranche1"]
    L += ["", f"Against the tranche 1 outcome (Rule 1 did not fire; Rule 2 met with sensing first): Rule 1 changed "
              f"{yes(ch['changed']['rule1'])}; Rule 2 changed {yes(ch['changed']['rule2'])}; first place changed "
              f"{yes(ch['changed']['rule2_first_place'])}. A further deviation is required (Deviations 10 and 11): "
              f"{yes(ch['further_deviation_required'])}.", ""]

    tc = r["tranche1_checks"]
    dc = tc["disagreement_concentration"]
    L += ["## Tranche 1 checks (Deviations 3 and 4)", "",
          "| Class pair | Disagreeing pairs | Observed coincidences | Expected coincidences | Observed / expected |",
          "|---|---|---|---|---|"]
    for k, v in dc["class_pairs"].items():
        L.append(f"| {k} | {v['disagreeing_pairs']} | {num(v['observed_coincidences'])} | "
                 f"{num(v['expected_coincidences'])} | {num(v['observed_over_expected'])} |")
    es, a100 = tc["encoding_sensitivity"], tc["alpha_on_the_100_items_of_record"]
    L += ["", f"Disagreement concentrates at CONCERN/OTHER rather than CONCERN/ENDORSEMENT: by count "
              f"{yes(dc['concentrates_at_concern_other_by_count'])}; by observed over expected coincidences "
              f"{yes(dc['concentrates_at_concern_other_by_observed_over_expected'])}.",
          f"Encoding sensitivity (exploratory; {es['items']} reliability items): Stage 1 alpha {num(es['Stage 1']['alpha'], 4)}, "
          f"Stage 2 alpha {num(es['Stage 2']['alpha'], 4)}; on all 100 items (of record) {num(a100['Stage 1'], 4)} and "
          f"{num(a100['Stage 2'], 4)}.", "",
          "Class distribution by annotator's sheet (exploratory), beside the design-weighted tranche 1 figures:", "",
          "| Source | Relevance share | CONCERN | ENDORSEMENT | OTHER |", "|---|---|---|---|---|"]
    t1p = p["tranche 1"]
    L.append(f"| Tranche 1, design-weighted | {pct(t1p['relevance_rate']['overall']['estimate'])} | " +
             " | ".join(pct(t1p["class_shares_among_relevant"][c]["estimate"]) for c in CLASSES) + " |")
    for k in cfg.ANNOTATORS:
        v = tc["annotator_sensitivity"][k]
        L.append(f"| Annotator {k}'s sheet | {pct(v['relevance_share'])} | " +
                 " | ".join(pct(v["class_shares_among_relevant"][c]) for c in CLASSES) + " |")
    L.append("")

    d2 = r["deviation_2"]
    rm = d2["raw_majority_set"]
    L += ["## Deviation 2: adjudicated items and the raw-majority set", "", "| Item | Tranche | Level | Adjudicated | Given |",
          "|---|---|---|---|---|"]
    for x in d2["adjudicated_items"]:
        L.append(f"| {x['id']} | {x['tranche']} | {x['level']} | {x['adjudicated']} | "
                 f"{', '.join(f'{k} {v}' for k, v in x['given'].items())} |")
    L += ["", "| Figure | Adjudicated gold set (of record) | Raw-majority set |", "|---|---|---|"]
    for c in CLASSES:
        L.append(f"| {c} share among relevant, pooled | {est(p['pooled']['class_shares_among_relevant'][c])} | "
                 f"{est(rm['class_shares_among_relevant'][c])} |")
    e = r["error_rates"]
    L += [f"| Weighted TPR / FPR for CONCERN | {num(e['rates_of_record_reproduced']['tpr'], 6)} / "
          f"{num(e['rates_of_record_reproduced']['fpr'], 6)} | {num(rm['concern_rates_weighted']['tpr'], 6)} / "
          f"{num(rm['concern_rates_weighted']['fpr'], 6)} |",
          f"| D28 condition (ii): first place; met | {sb['d28_pooled_of_record']['largest_eligible']}; "
          f"{yes(sb['d28_pooled_of_record']['rule2_condition_ii_intervals_do_not_overlap'])} | "
          f"{rm['d28']['largest_eligible']}; {yes(rm['d28']['rule2_condition_ii_intervals_do_not_overlap'])} |", ""]

    L += ["## Error rates of the deployed classifiers", "",
          f"Rates of record, recomputed: TPR {e['rates_of_record_reproduced']['tpr']}, FPR "
          f"{e['rates_of_record_reproduced']['fpr']}.", "",
          "Weighted three-class rates M_ij (rows: gold class; columns: classified as):", "",
          "| Gold class | CONCERN | ENDORSEMENT | OTHER |", "|---|---|---|---|"]
    for c in CLASSES:
        row = e["three_class"]["weighted_rates_gold_by_classified"][c]
        L.append(f"| {c} | " + " | ".join(num(row[x], 4) for x in CLASSES) + " |")
    L += ["", "| Era | e_in | e_out |", "|---|---|---|"]
    for k, v in e["relevance_error"]["by_era"].items():
        L.append(f"| {k} | {v['e_in']['k']}/{v['e_in']['n']} ({pct(v['e_in']['share'])}) | "
                 f"{v['e_out']['k']}/{v['e_out']['n']} ({pct(v['e_out']['share'])}) |")
    re_ = e["relevance_error"]
    wi, wo = re_["wrongly_included_classified_concern_by_stage2"], re_["wrongly_left_out_gold_concern"]
    tw = e["three_way_comparison"]
    g1 = tw["gold_concern_share_among_gold_relevant"]
    g2 = tw["classified_concern_share_among_items_classified_relevant"]
    clip = "" if not tw["corrected_was_clipped"] else f" (clipped; raw value {pct(tw['corrected_raw'])})"
    L += ["", f"Items wrongly included that Stage 2 classifies CONCERN: {wi['k']}/{wi['n']} ({pct(wi['share'])}; "
              f"{pct(wi['wilson95_low'])} to {pct(wi['wilson95_high'])}). Items wrongly left out that are gold CONCERN: "
              f"{wo['k']}/{wo['n']} ({pct(wo['share'])}; {pct(wo['wilson95_low'])} to {pct(wo['wilson95_high'])}).",
          f"CONCERN share three ways: gold labels {est(g1)}; classified {est(g2)}; classified and corrected "
          f"{pct(tw['that_share_corrected_with_the_rates_of_record'])}{clip}.", ""]

    tc = r["temporal_calibration_check"]
    L += ["## Temporal calibration check", "",
          "| Scope | Rate | Early | Late | Late minus early |", "|---|---|---|---|---|"]
    for scope, v in tc["block_rates"].items():
        for k in ("tpr", "fpr"):
            ee, ll, dd = v["early"], v["late"], v[f"{k}_late_minus_early"]
            cells = []
            for x in (ee, ll):
                c = x[f"{k}_counts"]
                cells.append(f"{num(x[k])} ({ci(x[k + '_interval95'], num)}; {c['k']}/{c['n']})")
            L.append(f"| {scope} | {k.upper()} | {cells[0]} | {cells[1]} | {num(dd['difference'])} ({ci(dd, num)}) |")
    L += ["", "Weighted by the pooled design weights; intervals: 95% percentile intervals from the 2,000 item resamples; "
              "counts: unweighted (Wilson intervals in the results file).", "",
          "| Block | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | Stage 1 accuracy, relevant | "
          "Stage 1 accuracy, not relevant | Stage 1 balanced accuracy |", "|---|---|---|---|---|---|---|---|"]
    for blk in ("early", "late"):
        f = tc["stage2_f1_by_block"][blk]
        s1 = tc["stage1_accuracy_by_block"][blk]
        L.append(f"| {blk} | {num(f['macro_f1'])} | " + " | ".join(num(f["per_class"][c]["f1"]) for c in CLASSES) +
                 f" | {s1['accuracy_relevant']['k']}/{s1['accuracy_relevant']['n']} | "
                 f"{s1['accuracy_not_relevant']['k']}/{s1['accuracy_not_relevant']['n']} | {num(s1['balanced_accuracy'])} |")
    ir = tc["item_resamples"]
    L += ["", "Both tranches, unweighted, descriptive.", "",
          f"Item index arrays: SHA-256 `{ir['index_arrays_sha256']}` (strata of "
          f"{', '.join(str(v) for v in ir['strata_sizes'].values())} items).", ""]
    pv = r["comparison_with_previews"]
    L += ["## Previews", "", "| Preview | Same as this run |", "|---|---|"]
    for k, v in pv.items():
        L.append(f"| {k.replace('_', ' ')} | {yes(v['same'])} |")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    main()
