"""Exploratory analyses of the runs of Claude Opus 5.5 and Claude Fable 5.1 (on the PC): the figures that Deviation 15
of docs/analysis_preregistration.md lists under "What is computed", each beside the figure of record it parallels.

From the repository folder, with the virtual environment active (no GPU, no internet):
    python analysis_06_frontier.py --preflight
        Before the commit. Checks every input against the record; runs the code path on the labels and rates of
        record and checks that it reproduces the figures of record (rule 13); checks the files of any run of
        Deviation 15 that is already in data/models/frontier/ (rule 2), computing nothing from them; then runs every
        analysis once as a dry run on the real data structure with the labels of all ten runs replaced by labels
        drawn at random from fixed made-up distributions (rule 15), so that no output of a run of Deviation 15
        enters it. The result, its report and its values are discarded unseen. It writes no output (Python may
        refresh its caches), and it can be run before any run of Deviation 15 exists.
    python analysis_06_frontier.py --confirm-committed
        After this file is committed and its SHA-256 recorded, and after the runs of Deviation 15 have ended. The run
        of record. It runs once: it refuses to start if this file's results already exist (the SHA-256 is that of
        the file with LF line endings, as the register records script hashes).

Inputs, each checked against the record (rule 1): the inputs of the sample analyses of record, read and checked by
analysis_01_sample.load_all; the predictions of the evaluation of record, read by models_05_evaluate.verify; corpus
v2.2, the three prediction files of the corpus runs of record, thread_sizes.csv and the frame, read and checked by
the loaders of analysis_03_series.py; results/series_results.json and results/sample_results.json; the manifests
of the two corpus runs of record (data/models/deploy/stage2_manifest.json, subsystem_manifest.json); and what
models_07_frontier.py wrote in data/models/frontier/: for each run <run>_manifest.json, <run>_predictions.csv and
<run>_log.jsonl, with stops.jsonl and pilot_manifest.json (and pilot_log.jsonl, by its SHA-256 only). It runs no
model and sends nothing.

What it computes. Every figure is exploratory: the rules that give it were fixed after every result of record had
been seen (Deviation 15), so none can confirm a result. Each is reported beside the figure of record it parallels.
  0. The ten runs: complete, halted or not made, with the reason; counts of comments, calls, refusals (by category)
     and comments with no label.
  A. From each complete evaluation run, on the 598 items with a gold Stage 2 class: macro-F1, per-class F1, the
     weighted and unweighted CONCERN true- and false-positive rates and M_ij, for each schema; for the subsystem
     prompt, agreement with the gold primary subsystem on the 596 items that have one, per value, with Wilson 95%
     intervals. The permutation tests on macro-F1 of Deviation 15, one family of their own, Holm within it.
  B. For each model whose two corpus runs are complete: the agreement of its corpus and evaluation runs on the
     tranche items both cover; the primary, block-specific, companion, pooled, tier-level, three-class (CONCERN),
     word-floor-25, Tier 1 and Tier 2 series with their intervals, Sen's slopes, Gilbert intervals and Mann-Kendall
     p-values, from its own labels and its own rates; RQ2: pi_s, C_s and E_s for sensing and none, the counts of the
     other values, and the test of sensing if the sparsity rule gives it a series.
  C. Cost per 1,000 comments of each complete run, at batch and at standard prices, the thinking tokens apart.

Rules fixed with this file (where Deviation 15 is silent, or to say how it is applied)
  1. Inputs. Every module this file imports is checked against its SHA-256 with LF line endings (the files in the
     repository at aff4276), and models_07_frontier.py, if it is in the repository folder, against
     FRONTIER_SCRIPT_SHA256, the committed file that made the runs. The inputs of the analyses of record are read
     and checked by the functions of record named above. The two results files of record are checked against the
     SHA-256 the register records (LF line endings), and the two corpus-run manifests of record against theirs (the
     files as they stand). Any difference stops the script.
  2. A run of Deviation 15 is complete when its manifest is in data/models/frontier/ and: it names the committed
     models_07_frontier.py, the run, its model, prompt and items, max_tokens 4,000, effort low and (where it records
     one) inference_geo global, and answers from one version of the model asked for; the predictions file and the
     log have the SHA-256 it records; the
     predictions file has the columns models_07_frontier.py writes and one row for each comment of the run, in id
     order and none twice (the 598 items with a gold Stage 2 class, or the 6,503 Tier 1+2 comments classified
     relevant at Stage 1 in the corpus run of record), each with a label and the status ok, or with no label, the
     status refusal (Stage 2) or unclassified (subsystem) and its reason; the final records of the log give every
     comment the same status and label; and the calls, tokens, counts, cost and (where it records them) regions and
     service tiers that the manifest records are those recounted from the log and the file. Any departure stops
     the script.
  3. A run without a manifest is not complete and enters no figure. It is halted when stops.jsonl records it so,
     and not made when stops.jsonl records that it was not started, when its model failed the pilot gate
     (pilot_manifest.json, which must name the committed models_07_frontier.py and match pilot_log.jsonl), or when
     an earlier run ended the runs under the stopping rule; the reason is reported with it. A run that left a log
     is reported with its counts (comments with a final result by status, refusal categories, answered calls). The
     run of record stops if a run is in none of these states (a log, or no file yet, without a recorded reason),
     because the runs have then not ended, or have ended in a way that Deviation 15 leaves to a further deviation;
     the preflight reports such a run and passes.
  4. Codes. On the 598 items a refusal is a prediction of no class: an error in F1, not CONCERN in the CONCERN rates
     and OTHER in M_ij, as models_05_evaluate.py and analysis_01_sample.py count it. On the corpus a refusal is not
     CONCERN in every share and OTHER in the three-class correction (Deviation 13), and an unclassified comment is
     the eighth value of the subsystem measures. In the table of two runs' labels a refusal is a fourth value at
     Stage 2, and unclassified an eighth value for the subsystem.
  5. Stage 2 figures (A). For each complete evaluation run with a Stage 2 prompt, on the 598 items:
     models_05_evaluate.encode, stage2_metrics (checked against scikit-learn's F1, as the evaluation of record
     checks it) and concern_rates, weighted by the pooled design weights and unweighted; and
     analysis_01_sample.three_class_matrix. Beside them, the figures of Claude Sonnet 4.6 under the same schema in
     evaluation_results.json, and for the domain-specific schema the M_ij of record (results/sample_results.json);
     the sample analyses give M_ij for the deployed configuration only, so the universal schema has none of record.
  6. Subsystem agreement (A). For each complete evaluation run with the subsystem prompt,
     analysis_03_series.subsystem_validation on its labels (rule 11 of that file: both tranches and each, with and
     without the three adjudicated items; an unclassified item is a column and a disagreement), beside the tables
     of the classifier of record in results/series_results.json.
  7. Comparisons (A). Universal schema: Claude Opus 5.5 against Claude Sonnet 4.6, Claude Fable 5.1 against Claude
     Sonnet 4.6, each against RoBERTa, and Claude Opus 5.5 against Claude Fable 5.1; domain-specific schema: each
     against Claude Sonnet 4.6, and Claude Opus 5.5 against Claude Fable 5.1, in this order. The first named is a
     in models_05_evaluate.permutation_test on macro-F1, with its coins (10,000 permutations, seed 24916660, the
     items in id order). A test is in the family only if both its runs are complete. Holm-Bonferroni within the
     family (models_05_evaluate.holm), a test being significant when its adjusted p is below 0.05. Beside the tests
     against RoBERTa, the comparison of record of RoBERTa with Claude Sonnet 4.6 under the same schema (Family B,
     universal; Family C, domain-specific).
  8. Agreement of a model's corpus and evaluation runs (B), on the tranche items that both cover (classified
     relevant at Stage 1 in the corpus run of record, and with a gold Stage 2 class): the table of the evaluation
     run's label against the corpus run's, and the number and share with the same label, for the domain-specific
     schema and for the subsystem. Beside the first, the table of record; the subsystem classifier of record was
     run once, so the second has none.
  9. A model's error rates (B), from its domain-specific evaluation run, by the computation of
     analysis_03_series.item_side: the weighted CONCERN TPR and FPR, the early- and late-block rates of both
     tranches and M_ij, each with its 2,000 item resamples of record (their SHA-256 checked), without that
     function's check against the rates of record. This computation must reproduce item_side exactly on the
     predictions of record before any label of a run of Deviation 15 is used.
 10. Series (B). For each model whose two corpus runs, and the evaluation runs they need, are complete: its corpus
     labels and its rates take the place of those of record, and analysis_03_series computes the series
     (reweighting, comment_features, aggregates with the generator of record, quarterly_series, series_block): the
     primary, block-specific, companion, pooled, tier-level, three-class (CONCERN component), word-floor-25, Tier 1
     and Tier 2 series, each by quarter with its bootstrap intervals, and with Sen's slope, the Gilbert interval
     and the Mann-Kendall p-value over 2016 Q1 to 2024 Q4 (rule 5 of that file). The reweighting, the comment
     resamples and the tier shares rest on Stage 1 of record and are those of record; the SHA-256 of the comment
     index arrays must equal the one recorded. Not computed: Hamed-Rao, R3's criteria, changepoints, STL, the GLM,
     R4, the half-year and year series, the seasonality analyses and the relevance-error series.
 11. RQ2 (B). The sparsity rule on the model's subsystem labels (analysis_03_series.sparsity); pi_s, C_s and E_s,
     corrected and as classified, with their intervals, for sensing and none, as analysis_03_series.rq2 computes
     them (so only at a resolution the rule gives: a value the rule reports as counts only has its counts), with the
     concern share C they rest on; the counts that rq2
     gives for the other five values and for the unclassified comments; and, if the rule gives sensing a series,
     its test as Family A computes it, in a family of one (the Holm-adjusted p-value is the p-value). No other value
     is tested.
 12. Cost (C). For each complete run, from its log: every answered call once (by its message identifier), with its
     input, output and thinking tokens; its cost at the list prices of Deviation 15, thinking billed as output, at
     standard prices and at batch prices (half); tokens written to or read from a cache, for which Deviation 15
     gives no price, at the prices the run's manifest records (none are expected); per 1,000 comments of the run;
     the thinking tokens and their part of the cost apart (an answer that reports no thinking-token count adds
     none, and such answers are counted); the inference regions the answers report, since the list prices hold
     for global routing. Beside: the cost per 1,000 comments of Claude Sonnet 4.6
     in the evaluation of record (evaluation_results.json) and in the corpus runs of record (their manifests), all
     sent as single requests at list prices; the evaluation runs with the subsystem prompt have none of record.
 13. Reproduction. Before any label of a run of Deviation 15 is used, the code path of rules 5 to 11 is run on the
     labels and rates of record, and every figure it computes that a file of record holds must equal it (a value
     written to six decimals to within one unit of the sixth decimal, an unrounded value of rule 16 of
     analysis_03_series.py within a relative 1e-9): the Stage 2 figures of Claude Sonnet 4.6 under both schemas
     and the test of record of RoBERTa against Claude Sonnet 4.6 (universal) in evaluation_results.json; M_ij in
     sample_results.json; the Stage 2 table of the two runs of record, the nine series, the comment index arrays
     and the RQ2 figures of rule 11 in series_results.json; and item_side (rule 9). A figure that is not
     reproduced stops the script.
 14. Outputs. Figures are written as analysis_03_series.py writes them (its rule 16: six decimals, the p-values,
     Sen's slopes and Gilbert limits unrounded), each beside its figure of record, and the report formats every
     figure from its unrounded value. Every series name in frontier_values.csv carries the label "exploratory
     (Deviation 15)". No comment text, comment identifier or answer text is written.
 15. The preflight's dry run. Every attribute of the comments and items is real. The labels of the ten runs are
     drawn with numpy.random.default_rng([24916660, 15, 96]), run by run in the order of Deviation 15: on the 598
     items a Stage 2 label is the gold class with probability 0.7 and otherwise CONCERN, ENDORSEMENT, OTHER or a
     refusal with probabilities 0.45, 0.25, 0.295 and 0.005, and a subsystem label is the gold value with
     probability 0.6 (where the item has one) and otherwise one of the eight values with the probabilities of the
     series analyses' dry run (rule 17 of analysis_03_series.py); on the corpus each label is drawn from those
     distributions alone. Every comment has one call of 150 input and 60 output tokens, 40 of them thinking.

Writes, in data/analysis/frontier/run_<first 12 hex digits of this file's SHA-256>/ (data/ is not committed):
  frontier_results.json       every figure, each beside its figure of record (no timestamp: a rerun on the same
                              inputs gives the same bytes)
  frontier_report.md          the main figures, as tables
  frontier_values.csv         every period value of every series of every model, in the columns of
                              series_values.csv, the model's identifier leading the series name (for the figures)
  frontier_manifest.json      time, versions, and the SHA-256 of every input file and of the files above
  PASTE_frontier_block.txt    the register lines (hashes only)
After the run, frontier_results.json, frontier_report.md and frontier_values.csv are copied to results/ and
committed with the register lines, so that every figure is in a results file committed to the repository.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import time
from collections import Counter
from fractions import Fraction
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path

import numpy as np
import pandas as pd

import analysis_01_sample as sample
import analysis_03_series as series
import models_01_prepare as prep
import models_05_evaluate as ev
import models_common as mc
import models_config as cfg

# =============================================================================
# THE RECORD
# =============================================================================
SCRIPT = "analysis_06_frontier.py"
REPORT = "Report this message before going further."
MODULES_OF_RECORD = {                             # SHA-256 with LF line endings: the files in the repository at aff4276
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
    "models_05_evaluate.py": "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734",
    "analysis_01_sample.py": "95f7a48c7509c58eca11330814be32fef0a8c1e430447790fdccfa5da6fdd952",
    "analysis_03_series.py": "8ebbf3d2e66cd15f6620461577643b154bb87dc5a58bf7e686c68794f8cad13e",
}
FRONTIER_SCRIPT = "models_07_frontier.py"
NOT_FILLED = "<to be filled>"
# the committed models_07_frontier.py, SHA-256 with LF line endings (register, 20 October 2026)
FRONTIER_SCRIPT_SHA256 = "fa9906d43d6b4a4151f07980e3198e1598861d6e67591e04effd9d1dbe118009"
LIBRARIES = {"scipy": "1.18.0", "pymannkendall": "1.4.3"}   # the libraries of the series analyses that this file uses
RESULTS_OF_RECORD = {                             # SHA-256 with LF line endings (register, 14 and 17 October 2026)
    "series_results.json": (cfg.REPO / "results" / "series_results.json",
                            "d955027383c7c1e55800a629c5a67f1c850389e25bea7fa483c97fb6a9465de8"),
    "sample_results.json": (cfg.REPO / "results" / "sample_results.json",
                            "be9db9a168e6d432d5f7b6190a7a204a624e1aa4992cd399cbb90288a383c5d7"),
}
CORPUS_RUN_MANIFESTS = {                          # the corpus runs of record, the files as they stand (15 October 2026)
    "stage2": (series.DEPLOY_DIR / "stage2_manifest.json",
               "eafaefada3c07b02ebe14b5afa9c0e075585e7b86640184fe30e28f9d72462ef"),
    "subsystem": (series.DEPLOY_DIR / "subsystem_manifest.json",
                  "deda5363f2ee2d969492d390848e9879f256ae279335e8b8af350ad972f74e3e"),
}
RECORD_MODEL = "claude-sonnet-4-6"                # the Claude model of record (Deviations 12 and 13)
RUN_DIR = cfg.MODELS_DIR / "frontier"             # where models_07_frontier.py writes
OUT_ROOT = cfg.REPO / "data" / "analysis" / "frontier"

MODELS = {"opus": "claude-opus-5-5", "fable": "claude-fable-5-1"}
NAMES = {"opus": "Claude Opus 5.5", "fable": "Claude Fable 5.1"}
KIND_NAMES = {"universal": "universal", "domain": "domain-specific", "subsystem": "subsystem"}
RUNS = {   # in the order of the runs of Deviation 15: run -> (model, prompt, items)
    "opus-eval-universal": ("opus", "universal", "eval"),
    "opus-eval-domain": ("opus", "domain", "eval"),
    "opus-eval-subsystem": ("opus", "subsystem", "eval"),
    "fable-eval-universal": ("fable", "universal", "eval"),
    "fable-eval-domain": ("fable", "domain", "eval"),
    "fable-eval-subsystem": ("fable", "subsystem", "eval"),
    "opus-corpus-stage2": ("opus", "domain", "corpus"),
    "opus-corpus-subsystem": ("opus", "subsystem", "corpus"),
    "fable-corpus-stage2": ("fable", "domain", "corpus"),
    "fable-corpus-subsystem": ("fable", "subsystem", "corpus"),
}
ORDER = list(RUNS)
EVAL_ITEMS, CORPUS_ITEMS = 598, 6503              # Deviation 15
MAX_TOKENS, EFFORT, ROUTING = 4000, "low", "global"   # Deviation 15: max_tokens, effort and inference_geo
PRICES = {   # Deviation 15: US dollars per million input and output tokens, 20 October 2026, single requests
    "claude-opus-5-5": {"input": Fraction(4), "output": Fraction(20)},
    "claude-fable-5-1": {"input": Fraction(10), "output": Fraction(50)},
}
BATCH_FACTOR = Fraction(1, 2)                     # Deviation 15: half those prices through the Batches API
PREDICTION_COLUMNS = ["id", "label", "status", "reason", "refusal_category", "attempts", "input_tokens", "output_tokens",
                      "thinking_tokens", "answer_1", "answer_2", "message_ids", "batch_ids", "counted_errors"]
REASONS = {"refusal_stop", "no_label", "api_error"}   # models_07_frontier.py: why a comment has no label
FINAL = ("ok", "refusal", "unclassified")
STOP_EVENTS = ("not_started", "halted")
CLASSES = list(sample.CLASSES)
SUBSYSTEMS = list(sample.SUBSYSTEMS)
UNCLASSIFIED = series.UNCLASSIFIED
VALUES8 = list(series.VALUES8)
MEASURED = ["sensing", "none"]                    # Deviation 15: pi_s, C_s and E_s for these two values only
RECORD_STAGE2 = {"universal": "sonnet-universal", "domain": "sonnet-domain"}
FAMILY = [("universal", "opus", "sonnet-universal"), ("universal", "fable", "sonnet-universal"),
          ("universal", "opus", "roberta"), ("universal", "fable", "roberta"), ("universal", "opus", "fable"),
          ("domain", "opus", "sonnet-domain"), ("domain", "fable", "sonnet-domain"), ("domain", "opus", "fable")]
RECORD_COMPARISON = {   # the comparison of record of RoBERTa with Claude Sonnet 4.6 under each schema
    "universal": ("family_b", "both tranches, universal schema", "roberta", "sonnet-universal"),
    "domain": ("family_c", "both tranches, domain-specific schema", "roberta", "sonnet-domain"),
}
SERIES = [   # name in analysis_03_series.quarterly_series, name in series_values.csv, place in series_results.json
    ("primary", "primary (quarter)", ("rq1", "primary_series")),
    ("block_specific", "block-specific (quarter)", ("rq1", "block_specific_series")),
    ("companion", "companion (quarter)", ("rq1", "companion_series")),
    ("pooled", "pooled (quarter)", ("rq1", "pooled_series")),
    ("tier_level", "tier-level (quarter)", ("rq1", "tier_level_series")),
    ("three_class_concern", "three-class CONCERN component (quarter)", ("rq1", "three_class_correction")),
    ("word_floor_25", "word floor 25 (quarter)", ("sensitivities", "word_floor_25")),
    ("tier1", "Tier 1 (quarter)", ("sensitivities", "tier_strata", "tier1")),
    ("tier2", "Tier 2 (quarter)", ("sensitivities", "tier_strata", "tier2")),
]
SERIES_TITLES = {"primary": "Primary", "block_specific": "Block-specific (the model's block rates)",
                 "companion": "Companion", "pooled": "Pooled", "tier_level": "Tier-level",
                 "three_class_concern": "Three-class correction, CONCERN", "word_floor_25": "Word floor 25",
                 "tier1": "Tier 1", "tier2": "Tier 2"}
NOT_COMPUTED = ("changepoints, STL, the GLM, R4 (thread size), the half-year and year series, the seasonality "
                "analyses, the relevance-error series, Hamed-Rao and R3's criteria are not computed for these "
                "models (Deviation 15)")
EXPLORATORY = "exploratory (Deviation 15)"
STATEMENT = ("Every figure here is exploratory: these rules were fixed after every result of record had been seen "
             "(Deviation 15), so no figure here can confirm a result. Each is reported beside the figure of record it "
             "parallels, whatever its value.")
TOLERANCE_UNROUNDED = 1e-9                        # rule 13
TOLERANCE_ROUNDED = 1.000001e-6
DRY_RUN = {   # rule 15: made-up label distributions for the preflight's dry run
    "stage2": (CLASSES + ["refusal"], [0.45, 0.25, 0.295, 0.005]),
    "subsystem": series.DRY_RUN["subsystem"],
    "keep_gold_stage2": 0.7, "keep_gold_subsystem": 0.6,
    "tokens": {"input": 150, "output": 60, "thinking": 40},
}
DRY_RUN_GENERATOR = [cfg.SEED, 15, 96]


# =============================================================================
# helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


def own_sha256() -> str:
    return ev.text_sha256(Path(__file__).resolve())


def run_folder(me: str) -> Path:
    return OUT_ROOT / f"run_{me[:12]}"


def num(x):
    return series.num(x)


def fl(x):
    return sample.fl(x)


def fr(x):
    return sample.fr(x)


def no_answer(kind: str) -> str:
    return UNCLASSIFIED if kind == "subsystem" else "refusal"


def dig(tree: dict, path: tuple, what: str):
    """A value of a results file of record, or a stop if the file does not hold it."""
    x = tree
    for k in path:
        if not isinstance(x, dict) or k not in x:
            stop(f"{what} has no entry {' > '.join(str(p) for p in path)}: it is not the file this script was written "
                 f"for. {REPORT}")
        x = x[k]
    return x


def filled() -> bool:
    return re.fullmatch(r"[0-9a-f]{64}", FRONTIER_SCRIPT_SHA256 or "") is not None


def cap(text: str) -> str:
    return text[:1].upper() + text[1:]


# =============================================================================
# inputs (rule 1)
# =============================================================================
def check_modules() -> dict:
    out = {}
    for module in (cfg, mc, prep, ev, sample, series):
        path = Path(module.__file__).resolve()
        want = MODULES_OF_RECORD.get(path.name)
        got = ev.text_sha256(path)
        if got != want:
            stop(f"{path.name} is not the file in the repository at aff4276 (SHA-256 {got[:16]}..., recorded "
                 f"{(want or 'none')[:16]}...). {REPORT}")
        out[path.name] = got
    return out


def check_frontier_script() -> dict:
    """models_07_frontier.py in the repository folder must be the committed file that FRONTIER_SCRIPT_SHA256 names."""
    path = cfg.REPO / FRONTIER_SCRIPT
    got = ev.text_sha256(path) if path.exists() else None
    if FRONTIER_SCRIPT_SHA256 != NOT_FILLED and not filled():
        stop(f"FRONTIER_SCRIPT_SHA256 must be 64 hexadecimal digits in lower case, or {NOT_FILLED!r}. {REPORT}")
    if filled() and got is not None and got != FRONTIER_SCRIPT_SHA256:
        stop(f"{FRONTIER_SCRIPT} is not the committed file that made the runs (SHA-256 {got[:16]}..., recorded "
             f"{FRONTIER_SCRIPT_SHA256[:16]}...). {REPORT}")
    return {"filled": filled(), "file_present": got is not None, "file_sha256_lf": got}


def check_libraries() -> dict:
    found = {}
    for name in LIBRARIES:
        try:
            found[name] = package_version(name)
        except PackageNotFoundError:
            found[name] = "not installed"
    if found != LIBRARIES:
        pins = " ".join(f"{n}=={v}" for n, v in LIBRARIES.items())
        stop(f"these analyses use {', '.join(f'{n} {v}' for n, v in LIBRARIES.items())}; found "
             f"{', '.join(f'{n} {v}' for n, v in found.items())}.\n  Install them with:  python -m pip install {pins}")
    return found


def load_record_files() -> tuple[dict, dict]:
    """The two results files of record (LF text) and the two corpus-run manifests of record (files as they stand)."""
    out, shas = {}, {}
    for name, (path, want) in RESULTS_OF_RECORD.items():
        if not path.exists():
            stop(f"{name} not found at {path}")
        got = ev.text_sha256(path)
        if got != want:
            stop(f"{name} is not the results file of record (SHA-256 {got[:16]}..., recorded {want[:16]}...). {REPORT}")
        out[name] = json.loads(path.read_bytes().decode("utf-8"))
        shas[f"results/{name}"] = got
    for run, (path, want) in CORPUS_RUN_MANIFESTS.items():
        shas[path.name] = series.check_file(path, want, path.name)
        man = mc.read_json(path)
        if man.get("run") != run or man.get("model") != RECORD_MODEL or not isinstance(man.get("comments"), int) \
                or man["comments"] <= 0 or not isinstance(man.get("cost_usd"), (int, float)):
            stop(f"{path.name} is not the manifest of the {run} corpus run of record. {REPORT}")
        out[path.name] = man
    return out, shas


# =============================================================================
# the runs of Deviation 15 (rules 2, 3 and 12)
# =============================================================================
def read_jsonl(path: Path) -> tuple[list, int]:
    """The records of a log, as models_07_frontier.py reads them (a line that is not JSON, a torn line, is skipped),
    and the number of lines skipped."""
    out, torn = [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                torn += 1
    return out, torn


def answered_calls(records: list) -> list:
    """Every answered call in the records, once: by the API's message identifier (rule 12)."""
    seen, calls = set(), []
    for r in records:
        for a in r.get("attempts") or []:
            key = a.get("message_id") or (a.get("at"), a.get("text"), a.get("input_tokens"), a.get("output_tokens"))
            if key not in seen:
                seen.add(key)
                calls.append(a)
    return calls


def token_totals(calls: list) -> dict:
    return {"calls": len(calls), "input": sum(int(a.get("input_tokens") or 0) for a in calls),
            "output": sum(int(a.get("output_tokens") or 0) for a in calls),
            "thinking": sum(int(a.get("thinking_tokens") or 0) for a in calls),
            "calls_without_a_thinking_count": sum(1 for a in calls if a.get("thinking_tokens") is None),
            "cache_creation_input": sum(int(a.get("cache_creation_input_tokens") or 0) for a in calls),
            "cache_read_input": sum(int(a.get("cache_read_input_tokens") or 0) for a in calls)}


def price_of(x, what: str) -> Fraction:
    try:
        return Fraction(str(x))
    except (TypeError, ValueError, ZeroDivisionError):
        stop(f"{what} is not a price. {REPORT}")


def run_cost(model: str, tokens: dict, cache_prices: dict) -> dict:
    """Rule 12: exact, in US dollars."""
    p = PRICES[model]
    standard = (tokens["input"] * p["input"] + tokens["output"] * p["output"]
                + tokens["cache_creation_input"] * cache_prices["cache_write"]
                + tokens["cache_read_input"] * cache_prices["cache_read"]) / 1_000_000
    thinking = tokens["thinking"] * p["output"] / 1_000_000
    return {"standard": standard, "batch": standard * BATCH_FACTOR, "thinking_standard": thinking,
            "thinking_batch": thinking * BATCH_FACTOR}


def final_records(records: list, where: str) -> dict:
    """id -> (status, label, reason, refusal category) of each comment's final record."""
    out = {}
    for r in records:
        if r.get("status") in FINAL and r.get("id"):
            cur = (r["status"], r.get("label") or "", r.get("reason") or "", r.get("refusal_category") or "")
            if r["id"] in out and out[r["id"]] != cur:
                stop(f"{where}: a comment has two different final records. {REPORT}")
            out[r["id"]] = cur
    return out


def read_complete_run(run: str, expected: list) -> dict:
    """Rule 2: a run with a manifest, every file checked; its labels and counts."""
    key, kind, items = RUNS[run]
    model = MODELS[key]
    man_path, pred_path, log_path = (RUN_DIR / f"{run}_manifest.json", RUN_DIR / f"{run}_predictions.csv",
                                     RUN_DIR / f"{run}_log.jsonl")
    try:
        man = mc.read_json(man_path)
    except (OSError, ValueError) as e:
        stop(f"{man_path.name} could not be read ({e}). {REPORT}")
    script = (man.get("script") or {}).get("sha256_lf")
    if script != FRONTIER_SCRIPT_SHA256:
        stop(f"{man_path.name} was written by another version of {FRONTIER_SCRIPT} (SHA-256 {str(script)[:16]}..., "
             f"the committed file {FRONTIER_SCRIPT_SHA256[:16]}...). {REPORT}")
    if (man.get("run"), man.get("model"), man.get("prompt"), man.get("items")) != (run, model, kind, items):
        stop(f"{man_path.name} does not describe the run {run} ({model}, {kind} prompt, {items} items). {REPORT}")
    answered = man.get("answered_by")
    if not isinstance(answered, list) or len(answered) != 1 or not ev.same_model(model, str(answered[0])):
        stop(f"{man_path.name}: the run was not answered by one version of {model} ({answered}). {REPORT}")
    request = man.get("request") or {}
    if request.get("max_tokens") != MAX_TOKENS or request.get("effort") != EFFORT \
            or request.get("inference_geo", ROUTING) != ROUTING:
        stop(f"{man_path.name}: the requests were not those of Deviation 15 (max_tokens {MAX_TOKENS}, effort "
             f"{EFFORT}, inference_geo {ROUTING}). {REPORT}")
    shas = {man_path.name: mc.sha256_file(man_path)}
    for path, field in ((pred_path, "predictions"), (log_path, "log")):
        if not path.exists():
            stop(f"{path.name} is missing, although {man_path.name} records it. {REPORT}")
        got = mc.sha256_file(path)
        want = (man.get(field) or {}).get("sha256")
        if got != want:
            stop(f"{path.name} is not the file its manifest records (SHA-256 {got[:16]}..., recorded "
                 f"{str(want)[:16]}...): it was changed after the run was summarised. {REPORT}")
        shas[path.name] = got
    df = ev.read_csv(pred_path)
    if list(df.columns) != PREDICTION_COLUMNS:
        stop(f"{pred_path.name} must have the columns {PREDICTION_COLUMNS} ({FRONTIER_SCRIPT} writes them). {REPORT}")
    ids = df["id"].tolist()
    twice = sorted(i for i, n in Counter(ids).items() if n > 1)
    if twice:
        stop(f"{pred_path.name}: {len(twice)} comment id(s) appear more than once. {REPORT}")
    if ids != expected:
        what = ("items with a gold Stage 2 class" if items == "eval" else
                "Tier 1+2 comments classified relevant at Stage 1 in the corpus run of record")
        stop(f"{pred_path.name} does not hold exactly the {len(expected):,} {what}, in id order: it has {len(ids):,} "
             f"rows, {len(set(ids) - set(expected))} of them not of the run, and lacks {len(set(expected) - set(ids))}. "
             f"{REPORT}")
    allowed = SUBSYSTEMS if kind == "subsystem" else CLASSES
    empty = no_answer(kind)
    ok = (df["status"] == "ok") & df["label"].isin(allowed) & (df["reason"] == "") & (df["refusal_category"] == "")
    none = (df["status"] == empty) & (df["label"] == "") & df["reason"].isin(REASONS) \
        & ((df["reason"] == "refusal_stop") | (df["refusal_category"] == ""))
    if not (ok | none).all():
        stop(f"{pred_path.name}: a row has neither a label with the status ok nor no label with the status {empty} "
             f"and its reason. {REPORT}")
    records, torn = read_jsonl(log_path)
    finals = final_records(records, log_path.name)
    rows = {i: (s, lab, r, c) for i, s, lab, r, c in zip(df["id"], df["status"], df["label"], df["reason"],
                                                          df["refusal_category"])}
    if set(finals) != set(expected) or any(finals[i] != rows[i] for i in expected):
        stop(f"{log_path.name} and {pred_path.name} do not give every comment the same final status and label. "
             f"{REPORT}")
    calls = answered_calls(records)
    tokens = token_totals(calls)
    counts = {"comments": len(df), "final_status": dict(Counter(df["status"])),
              "no_answer_reasons": dict(Counter(df.loc[df["status"] != "ok", "reason"])),
              "refusal_categories": dict(Counter((c or "none") for c, r in zip(df["refusal_category"], df["reason"])
                                                 if r == "refusal_stop"))}
    recorded = {"comments": man.get("comments"), "final_status": man.get("final_status"),
                "no_answer_reasons": man.get("no_answer_reasons"), "refusal_categories": man.get("refusal_categories")}
    if recorded != counts or man.get("calls") != tokens["calls"] \
            or man.get("tokens") != {k: tokens[k] for k in ("input", "output", "thinking")}:
        stop(f"{man_path.name}: the counts, calls or tokens it records are not those of {pred_path.name} and "
             f"{log_path.name}. {REPORT}")
    for field in ("inference_geo", "service_tier"):          # as the answers report them (rule 12)
        reported = dict(Counter(str(a.get(field) or "not reported") for a in calls))
        if field in man and man[field] != reported:
            stop(f"{man_path.name}: the {field} it records is not that of the answers in {log_path.name}. {REPORT}")
        counts[f"{field}_reported_by_the_answers"] = reported
    prices = man.get("prices_usd_per_mtok") or {}
    if price_of(prices.get("input"), "the manifest's input price") != PRICES[model]["input"] \
            or price_of(prices.get("output"), "the manifest's output price") != PRICES[model]["output"] \
            or price_of(man.get("batch_factor"), "the manifest's batch factor") != BATCH_FACTOR:
        stop(f"{man_path.name}: the run was not costed at the prices of Deviation 15. {REPORT}")
    cache = {"cache_write": price_of(prices.get("cache_write"), "the manifest's cache-write price"),
             "cache_read": price_of(prices.get("cache_read"), "the manifest's cache-read price")}
    cost = run_cost(model, tokens, cache)
    if not isinstance(man.get("cost_usd"), (int, float)) \
            or abs(float(cost["batch"]) - man["cost_usd"]) > TOLERANCE_ROUNDED:
        stop(f"{man_path.name}: the cost it records is not the cost of the calls in {log_path.name}. {REPORT}")
    labels = dict(zip(df["id"], df["label"]))
    return {"status": "complete", "reason": None, "labels": labels, "counts": counts, "tokens": tokens,
            "cache_prices": cache, "cost": cost, "log_lines_not_read": torn, "files_sha256": shas}


def read_unfinished_run(run: str) -> dict:
    """Rule 3: the counts of a run that left a log and no manifest. Its labels are not read."""
    log_path = RUN_DIR / f"{run}_log.jsonl"
    records, torn = read_jsonl(log_path)
    finals = final_records(records, log_path.name)
    status = Counter(s for s, _, _, _ in finals.values())
    cats = Counter((c or "none") for s, _, r, c in finals.values() if r == "refusal_stop")
    reasons = Counter(r for s, _, r, _ in finals.values() if s != "ok")
    return {"counts": {"comments_with_a_final_result": len(finals), "final_status": dict(status),
                       "no_answer_reasons": dict(reasons), "refusal_categories": dict(cats),
                       "answered_calls": len(answered_calls(records))},
            "log_lines_not_read": torn, "files_sha256": {log_path.name: mc.sha256_file(log_path)}}


def read_pilot() -> tuple[dict | None, dict]:
    path, log = RUN_DIR / "pilot_manifest.json", RUN_DIR / "pilot_log.jsonl"
    if not path.exists():
        return None, {}
    man = mc.read_json(path)
    if (man.get("script") or {}).get("sha256_lf") != FRONTIER_SCRIPT_SHA256:
        stop(f"pilot_manifest.json was written by another version of {FRONTIER_SCRIPT}. {REPORT}")
    if not log.exists() or (man.get("log") or {}).get("sha256") != mc.sha256_file(log):
        stop(f"pilot_log.jsonl is missing or has changed since the pilot was summarised. {REPORT}")
    gate = man.get("gate") or {}
    if set(gate) != set(MODELS) or not all(isinstance((gate[k] or {}).get("passes"), bool) for k in MODELS):
        stop(f"pilot_manifest.json does not give the pilot gate of both models. {REPORT}")
    return man, {"pilot_manifest.json": mc.sha256_file(path), "pilot_log.jsonl": mc.sha256_file(log)}


def read_stops() -> tuple[list, dict]:
    path = RUN_DIR / "stops.jsonl"
    if not path.exists():
        return [], {}
    rows, torn = read_jsonl(path)
    if torn or not all(r.get("event") in STOP_EVENTS and r.get("run") in RUNS for r in rows):
        stop(f"stops.jsonl holds a line that is not a stop of a run of Deviation 15. {REPORT}")
    return rows, {"stops.jsonl": mc.sha256_file(path)}


def stop_text(s: dict) -> str:
    extra = ""
    if "estimate_usd" in s:
        extra = (f" (estimate US${s['estimate_usd']:.4f}, measured spend US${s.get('spend_usd', 0):.4f}, ceiling "
                 f"US${s.get('ceiling_usd', 0):.2f})")
    elif "spend_usd" in s:
        extra = f" (measured spend US${s['spend_usd']:.4f})"
    return f"{s['reason']}{extra}"


def read_frontier(expected: dict) -> dict:
    """Rules 2 and 3: the state of every run, with the files of every complete run checked."""
    pilot, pshas = read_pilot()
    stops, sshas = read_stops()
    first = stops[0] if stops else None
    ended = ORDER.index(first["run"]) if first else None
    runs = {}
    for k, run in enumerate(ORDER):
        key, kind, items = RUNS[run]
        man, log = RUN_DIR / f"{run}_manifest.json", RUN_DIR / f"{run}_log.jsonl"
        own = next((s for s in stops if s["run"] == run), None)
        gate_failed = pilot is not None and not pilot["gate"][key]["passes"]
        after_end = ended is not None and k > ended
        base = {"model_key": key, "model": MODELS[key], "kind": kind, "items": items}
        if man.exists():
            why = ("pilot_manifest.json is missing" if pilot is None else
                   f"pilot_manifest.json says that {NAMES[key]} failed the pilot gate" if gate_failed else
                   f"stops.jsonl records that the runs ended at {first['run']} ({first['event']}) before it was "
                   f"complete" if (own is not None or after_end) else None)
            if why:
                stop(f"{man.name} exists, but {why}. {REPORT}")
            runs[run] = {**base, **read_complete_run(run, expected[items])}
            continue
        not_made = (own is not None and own["event"] == "not_started") or gate_failed or after_end
        if not_made and log.exists():
            stop(f"{log.name} exists, but the run was not made: "
                 + ("stops.jsonl records that it was not started" if own is not None and own["event"] == "not_started"
                    else f"{NAMES[key]} failed the pilot gate" if gate_failed else
                    f"the runs ended at {first['run']} ({first['event']})") + f". {REPORT}")
        state = {**base, "status": None, "reason": None, "settled": True, "counts": None, "files_sha256": {}}
        if own is not None and own["event"] == "halted":
            state.update(status="halted", reason=f"under the stopping rule, {stop_text(own)}")
        elif own is not None:
            state.update(status="not made", reason=f"not started under the stopping rule, {stop_text(own)}")
        elif gate_failed:
            state.update(status="not made", reason=f"{NAMES[key]} failed the pilot gate (pilot_manifest.json)")
        elif after_end:
            state.update(status="not made", reason=f"the runs of Deviation 15 ended under the stopping rule at "
                                                   f"{first['run']} ({first['event'].replace('_', ' ')})")
        elif log.exists():
            state.update(status="incomplete", reason="no manifest, and no stop is recorded for it", settled=False)
        else:
            state.update(status="not yet made", reason="no file of the run and no recorded reason: not started, or "
                                                       "its first batch is still outstanding", settled=False)
        if log.exists():
            state.update(read_unfinished_run(run))
        elif state["status"] == "halted":
            state["counts"] = {"comments_with_a_final_result": 0, "answered_calls": 0}
        runs[run] = state
    return {"runs": runs, "pilot_gate": None if pilot is None else
            {k: bool(pilot["gate"][k]["passes"]) for k in MODELS}, "stops": stops,
            "files_sha256": {**pshas, **sshas}, "dry": False}


def dry_run_frontier(data: dict, expected: dict) -> dict:
    """Rule 15: the ten runs, complete, with made-up labels and tokens."""
    rng = np.random.default_rng(DRY_RUN_GENERATOR)
    gold2 = {data["ids"][j]: data["g2"][j] for j in range(len(data["ids"]))}
    goldsub = {data["ids"][j]: data["gsub"][j] for j in range(len(data["ids"]))}
    runs = {}
    for run in ORDER:
        key, kind, items = RUNS[run]
        ids = expected[items]
        names, p = DRY_RUN["subsystem"] if kind == "subsystem" else DRY_RUN["stage2"]
        draw = rng.choice(np.array(names, dtype=object), size=len(ids), p=p)
        if items == "eval":
            keep = rng.random(len(ids)) < (DRY_RUN["keep_gold_subsystem"] if kind == "subsystem" else
                                           DRY_RUN["keep_gold_stage2"])
            gold = goldsub if kind == "subsystem" else gold2
            draw = np.array([gold[i] if (k and gold[i] in (SUBSYSTEMS if kind == "subsystem" else CLASSES)) else d
                             for i, k, d in zip(ids, keep, draw)], dtype=object)
        empty = no_answer(kind)
        labels = {i: ("" if d in ("refusal", UNCLASSIFIED) else str(d)) for i, d in zip(ids, draw)}
        status = Counter(("ok" if lab else empty) for lab in labels.values())
        reasons = Counter("no_label" for lab in labels.values() if not lab)
        t = DRY_RUN["tokens"]
        tokens = {"calls": len(ids), "input": t["input"] * len(ids), "output": t["output"] * len(ids),
                  "thinking": t["thinking"] * len(ids), "calls_without_a_thinking_count": 0,
                  "cache_creation_input": 0, "cache_read_input": 0}
        cache = {"cache_write": Fraction(0), "cache_read": Fraction(0)}
        runs[run] = {"model_key": key, "model": MODELS[key], "kind": kind, "items": items, "status": "complete",
                     "reason": None, "labels": labels,
                     "counts": {"comments": len(ids), "final_status": dict(status), "no_answer_reasons": dict(reasons),
                                "refusal_categories": {}},
                     "tokens": tokens, "cache_prices": cache, "cost": run_cost(MODELS[key], tokens, cache),
                     "log_lines_not_read": 0, "files_sha256": {}}
    return {"runs": runs, "pilot_gate": {k: True for k in MODELS}, "stops": [], "files_sha256": {}, "dry": True}


# =============================================================================
# A: the evaluation runs (rules 5 to 7)
# =============================================================================
def stage2_figures(p: np.ndarray, g2: np.ndarray, w2: list, data: dict, labels: dict) -> dict:
    """Rule 5: the Stage 2 figures of the evaluation of record, with the functions of record."""
    from sklearn.metrics import f1_score                      # a second implementation, as a check
    m = ev.stage2_metrics(p, g2)
    check = f1_score(g2, p, labels=[0, 1, 2], average=None, zero_division=0)
    if np.abs(check - np.array([float(x) for x in m["_f1"]])).max() > 1e-12:
        stop(f"the two F1 implementations disagree. {REPORT}")
    s2 = np.array([labels.get(i, "") for i in data["ids"]], dtype=object)
    return {"metrics": ev.strip_private(m), "concern_rates_weighted": ev.strip_private(ev.concern_rates(p, g2, w2)),
            "concern_rates_unweighted": ev.strip_private(ev.concern_rates(p, g2, None)),
            "three_class_rates_M": sample.three_class_matrix(dict(data, s2=s2))}


def record_stage2(rec: dict, schema: str) -> dict:
    name = RECORD_STAGE2[schema]
    c = dig(rec["evaluation"], ("stage2", "configurations", name), "evaluation_results.json")
    return {"configuration": name, "name": ev.NAMES[name],
            "metrics": dig(c, ("pooled",), "evaluation_results.json"),
            "concern_rates_weighted": dig(c, ("concern_rates_weighted",), "evaluation_results.json"),
            "concern_rates_unweighted": dig(c, ("concern_rates_unweighted",), "evaluation_results.json"),
            "three_class_rates_M": (dig(rec["sample"], ("error_rates", "three_class"), "sample_results.json")
                                    if schema == "domain" else None),
            "note": None if schema == "domain" else
            "no M_ij of record: the sample analyses give M_ij for the deployed configuration only"}


def subsystem_labels_array(data: dict, labels: dict) -> np.ndarray:
    return np.array([((labels[i] or UNCLASSIFIED) if i in labels else "") for i in data["ids"]], dtype=object)


def subsystem_agreement(data: dict, labels: dict) -> dict:
    """Rule 6: analysis_03_series.subsystem_validation on the labels of an evaluation run."""
    tranche = {"subsys": subsystem_labels_array(data, labels), "position": {i: k for k, i in enumerate(data["ids"])}}
    return series.subsystem_validation(tranche, data, False)


def comparison_family(enc: dict, g2: np.ndarray, available: set, rec: dict) -> dict:
    """Rule 7: the permutation tests of Deviation 15 on macro-F1, one family, Holm within it."""
    tests, dropped = [], []
    for schema, a, b in FAMILY:
        need = [f"{a}-eval-{schema}"] + ([f"{b}-eval-{schema}"] if b in MODELS else [])
        missing = [r for r in need if r not in available]
        name_b = NAMES[b] if b in MODELS else ev.NAMES[b]
        entry = {"schema": schema, "a": MODELS[a], "a_name": NAMES[a], "b": MODELS.get(b, b), "b_name": name_b}
        if missing:
            dropped.append({**entry, "reason": f"dropped: {', '.join(missing)} not complete"})
            continue
        pb = enc[(b, schema)] if b in MODELS else enc[b]
        t = ev.permutation_test(enc[(a, schema)], pb, g2, [0, 1, 2])
        tests.append({**entry, "statistic": "macro-F1", **t})
    adjusted = ev.holm([t["_p"] for t in tests]) if tests else []
    for t, adj in zip(tests, adjusted):
        t["holm_adjusted_p"] = float(adj)
        t["holm_adjusted_p_exact"] = fr(adj)
        t["significant_after_holm"] = bool(adj < ev.LEVEL)
        t["result"] = "significant" if adj < ev.LEVEL else "not demonstrably significant"
    record = {}
    for schema, (family, scope, a, b) in RECORD_COMPARISON.items():
        rows = [r for r in dig(rec["evaluation"], ("stage2", family), "evaluation_results.json")
                if r.get("scope") == scope and r.get("a") == a and r.get("b") == b]
        if len(rows) != 1:
            stop(f"evaluation_results.json does not hold one comparison of {a} with {b} ({scope}). {REPORT}")
        record[schema] = rows[0]
    return {"label": EXPLORATORY, "tests": ev.strip_private(tests), "size": len(tests), "dropped": dropped,
            "level": 0.05, "permutations": ev.N_PERM, "seed": cfg.SEED,
            "comparisons_of_record_with_roberta": record,
            "note": "one family of its own, outside every family of R5 and Deviation 12; Holm-Bonferroni within it at "
                    "0.05; a is the first configuration named, and the difference is a minus b (Deviation 15)"}


# =============================================================================
# B: the corpus runs (rules 8 to 11)
# =============================================================================
def runs_compared(evaluation: dict, corpus: dict, values: list) -> dict:
    """Rule 8: the labels of two runs on the comments both cover; ids sorted as strings."""
    both = sorted(set(evaluation) & set(corpus))
    pairs = Counter((evaluation[i], corpus[i]) for i in both)
    unknown = {v for pair in pairs for v in pair} - set(values)
    if unknown:
        stop(f"a label outside {values} was found ({sorted(unknown)}). {REPORT}")
    same = sum(n for (a, b), n in pairs.items() if a == b)
    return {"items_both_runs_cover": len(both),
            "evaluation_by_corpus_run": {a: {b: int(pairs[(a, b)]) for b in values} for a in values},
            "same_label": series.count_share(same, len(both))}


def stage2_codes(labels: dict) -> dict:
    return {i: (lab if lab in CLASSES else "refusal") for i, lab in labels.items()}


def subsystem_codes(labels: dict) -> dict:
    return {i: (lab if lab in SUBSYSTEMS else UNCLASSIFIED) for i, lab in labels.items()}


def item_rates(data: dict) -> dict:
    """Rule 9: the computation of analysis_03_series.item_side without its check against the rates of record."""
    every = np.ones(len(data["ids"]), bool)
    overall = sample.concern_rates(data, every)
    blocks = {b: sample.concern_rates(data, data["block"] == b) for b in ("early", "late")}
    M = series.exact_matrix(data)
    if any(x is None for row in M for x in row):
        stop(f"a gold class has no item on the primary item set: the three-class rates are not defined. {REPORT}")
    strata = sample.primary_strata(data)
    arrays, sha = sample.item_index_arrays(strata)
    if sha != series.ITEM_ARRAYS_SHA256:
        stop(f"the item index arrays are not those of record (SHA-256 {sha[:16]}..., recorded "
             f"{series.ITEM_ARRAYS_SHA256[:16]}...). {REPORT}")
    counts = sample.resample_counts(arrays, strata)
    pos = data["g2"] == "CONCERN"
    hit = data["s2"] == "CONCERN"
    prim = data["prim"]

    def row(exact, boot):
        return np.concatenate([[float(exact) if exact is not None else np.nan], boot])

    rates = {"tpr": row(overall["_tpr"], series.resampled_rate(data, strata, counts, prim & pos & hit, prim & pos)),
             "fpr": row(overall["_fpr"], series.resampled_rate(data, strata, counts, prim & ~pos & hit, prim & ~pos))}
    boot_blocks = sample.resampled_block_rates(data, strata, counts)
    for b in ("early", "late"):
        rates[f"tpr_{b}"] = row(blocks[b]["_tpr"], boot_blocks[("both tranches", b, "tpr")])
        rates[f"fpr_{b}"] = row(blocks[b]["_fpr"], boot_blocks[("both tranches", b, "fpr")])
    pred = np.where(np.isin(data["s2"], CLASSES), data["s2"], "OTHER")
    Mr = np.zeros((series.R, 3, 3))
    for i, a in enumerate(CLASSES):
        ga = prim & (data["g2"] == a)
        for j, b in enumerate(CLASSES):
            Mr[:, i, j] = row(M[i][j], series.resampled_rate(data, strata, counts, ga & (pred == b), ga))
    return {"rates": rates, "M": Mr, "M_exact": M, "overall": overall, "blocks": blocks, "index_arrays_sha256": sha}


def rates_used(item: dict) -> dict:
    r = item["rates"]
    return {"tpr": float(r["tpr"][0]), "fpr": float(r["fpr"][0]), "tpr_exact": fr(item["overall"]["_tpr"]),
            "fpr_exact": fr(item["overall"]["_fpr"]), "tpr_minus_fpr": float(r["tpr"][0] - r["fpr"][0]),
            "block_rates_both_tranches": {b: {"tpr": num(r[f"tpr_{b}"][0]), "fpr": num(r[f"fpr_{b}"][0]),
                                              "tpr_exact": fr(item["blocks"][b]["_tpr"]),
                                              "fpr_exact": fr(item["blocks"][b]["_fpr"])} for b in ("early", "late")},
            "three_class_rates_M": {a: {b: float(item["M_exact"][i][j]) for j, b in enumerate(CLASSES)}
                                    for i, a in enumerate(CLASSES)},
            "three_class_rates_M_exact": {a: {b: fr(item["M_exact"][i][j]) for j, b in enumerate(CLASSES)}
                                          for i, a in enumerate(CLASSES)}}


def model_corpus(D: dict, stage2: dict, subsystem: dict) -> dict:
    """The comments of record with a model's corpus labels (rule 4); validation-only items carry no label."""
    ids, pop = D["ids"], D["pop"]
    s2 = np.full(len(ids), "", dtype=object)
    s2[pop] = [(stage2[i] if stage2[i] in CLASSES else "refusal") for i in ids[pop]]
    subsys = np.full(len(ids), "", dtype=object)
    subsys[pop] = [(subsystem[i] if subsystem[i] in SUBSYSTEMS else UNCLASSIFIED) for i in ids[pop]]
    return {**D, "s2": s2, "subsys": subsys, "validation_only": set()}


def rq2_subset(A: np.ndarray, rates: dict, D: dict) -> dict:
    """Rule 11: the RQ2 figures of Deviation 15, as analysis_03_series.rq2 computes them, for sensing and none, with
    the counts of every other value; the test of sensing alone, in a family of one."""
    sp = series.sparsity(D)
    pop = D["pop"]
    span = series.rq2_measures(A, rates, [list(range(series.TREND_Q))])
    quarters = series.rq2_measures(A, rates, [[qi] for qi in range(len(series.QUARTERS))])
    years = series.rq2_measures(A, rates, [series.YEAR_Q_ALL[y] for y in series.YEARS])
    year_labels = [str(y) for y in series.TREND_YEARS] + ["2025 (January-April, descriptive)"]
    out = {}
    for s in VALUES8:
        entry = {"sparsity": sp[s],
                 "counts": {"classified_relevant_by_quarter": {series.QLABELS[qi]: int((pop & (D["qidx"] == qi)
                                                                                        & (D["subsys"] == s)).sum())
                                                               for qi in range(len(series.QUARTERS))},
                            "classified_concern_by_quarter": {series.QLABELS[qi]: int((pop & (D["qidx"] == qi)
                                                                                       & (D["subsys"] == s)
                                                                                       & (D["s2"] == "CONCERN")).sum())
                                                              for qi in range(len(series.QUARTERS))},
                            "classified_relevant_by_year": {str(y): int((pop & (D["year"] == y)
                                                                         & (D["subsys"] == s)).sum())
                                                            for y in series.YEARS},
                            "classified_concern_by_year": {str(y): int((pop & (D["year"] == y) & (D["subsys"] == s)
                                                                        & (D["s2"] == "CONCERN")).sum())
                                                           for y in series.YEARS},
                            "weighted_N_2016_2024": num(span["N"][s][0, 0]),
                            "weighted_K_2016_2024": num(span["K"][s][0, 0]),
                            "A_2016_2024": num(span["A"][s][0, 0])}}
        shares = s in MEASURED and s not in series.COUNTS_ONLY and sp[s]["resolution_by_the_rule"] != "counts only"
        if shares:
            entry["over_2016_2024"] = {
                "pi_s": series.rows(span["pi"][s], ["2016-2024"])[0],
                "C_s": series.rows(span["Cs"][s], ["2016-2024"])[0],
                "E_s": series.rows(span["E"][s], ["2016-2024"], share=False)[0],
                "as_classified": {"pi_s": series.rows(span["pi_classified"][s], ["2016-2024"])[0],
                                  "C_s": series.rows(span["Cs_classified"][s], ["2016-2024"])[0],
                                  "E_s": series.rows(span["E_classified"][s], ["2016-2024"], share=False)[0]}}
            if sp[s]["resolution_by_the_rule"] == "quarterly":
                src, labels, pos, n_trend, per_year = (quarters, series.QLABELS, list(series.QPOS[:series.TREND_Q]),
                                                       series.TREND_Q, 4.0)
            else:
                src, labels, pos, n_trend, per_year = years, year_labels, list(series.YPOS), len(series.TREND_YEARS), 1.0
            entry["series"] = {"resolution": sp[s]["resolution_by_the_rule"], "pi_s": series.rows(src["pi"][s], labels),
                               "C_s": series.rows(src["Cs"][s], labels),
                               "pi_s_as_classified": series.rows(src["pi_classified"][s], labels),
                               "C_s_as_classified": series.rows(src["Cs_classified"][s], labels)}
            if s == "sensing":
                t = series.trend(series.values(src["pi"][s], n_trend), pos, per_year)
                if t.get("sen_slope") is not None:
                    t["holm_adjusted_p"] = t["p"]
                    t["significant_after_holm"] = bool(t["p"] < series.ALPHA)
                entry["family_A_test"] = t
        out[s] = entry
    test = out["sensing"].get("family_A_test") or {}
    tested = "sensing" if test.get("sen_slope") is not None else None
    return {"values": out,
            "sensing_test": {"tests": [tested] if tested else [], "size": 1 if tested else 0,
                             "note": "the test of sensing as Family A computes it, in a family of one; no other value "
                                     "is tested (Deviation 15)"},
            "concern_share_C_2016_2024": series.rows(span["C"], ["2016-2024"])[0],
            "concern_share_C_2016_2024_as_classified": series.rows(span["C_classified"], ["2016-2024"])[0],
            "note": "corrected for Stage 2 error with the model's own rates, assuming equal rates in every subsystem; "
                    "not corrected for the subsystem classifier's error; 2025 is descriptive"}


def corpus_series(Dm: dict, item: dict) -> dict:
    """Rule 10: the series of Deviation 15 by the functions of analysis_03_series, and RQ2 (rule 11)."""
    rates, M = item["rates"], item["M"]
    RW = series.reweighting(Dm)
    X = series.comment_features(Dm, RW)
    A, info = series.aggregates(Dm, X, series.COMMENT_GENERATOR)
    in_span = Dm["pop"] & (Dm["year"] <= 2024)
    v1 = float((in_span & (Dm["tier"] == "Tier 1")).sum() / in_span.sum())
    S = series.quarterly_series(A, rates, M, v1)
    return {"series": {name: series.series_block(S[name]) for name, _, _ in SERIES},
            "classified_share": series.values(S["classified"]), "rq2": rq2_subset(A, rates, Dm),
            "comment_index_arrays_sha256": info["index_arrays_sha256"], "tier_shares_v_2016_2024": v1}


def record_series(rec: dict) -> dict:
    out = {}
    for name, _, path in SERIES:
        block = dig(rec["series"], path, "series_results.json")
        out[name] = {"rows": dig(block, ("rows",), "series_results.json"),
                     "trend": dig(block, ("trend",), "series_results.json")}
    return out


def record_rq2(rec: dict) -> dict:
    q = dig(rec["series"], ("rq2",), "series_results.json")
    values = dig(q, ("values",), "series_results.json")
    return {"values": {s: dig(values, (s,), "series_results.json") for s in VALUES8},
            "family_A": dig(q, ("family_A",), "series_results.json"),
            "concern_share_C_2016_2024": dig(q, ("concern_share_C_2016_2024",), "series_results.json"),
            "concern_share_C_2016_2024_as_classified": dig(q, ("concern_share_C_2016_2024_as_classified",),
                                                           "series_results.json")}


def record_rates(rec: dict) -> dict:
    e = dig(rec["series"], ("error_rates",), "series_results.json")
    b = dig(e, ("block_rates_both_tranches",), "series_results.json")
    rr = dig(e, ("rates_of_record",), "series_results.json")
    return {"tpr": rr["tpr"], "fpr": rr["fpr"], "tpr_exact": rr.get("tpr_exact"), "fpr_exact": rr.get("fpr_exact"),
            "tpr_minus_fpr": rr.get("tpr_minus_fpr"),
            "block_rates_both_tranches": {k: {"tpr": b[k]["tpr"], "fpr": b[k]["fpr"], "tpr_exact": b[k].get("tpr_exact"),
                                              "fpr_exact": b[k].get("fpr_exact")} for k in ("early", "late")},
            "three_class_rates_M": dig(e, ("three_class_rates_M",), "series_results.json")}


def corpus_analysis(key: str, runs: dict, data: dict, D: dict, rec: dict) -> dict:
    need = [f"{key}-corpus-stage2", f"{key}-corpus-subsystem", f"{key}-eval-domain", f"{key}-eval-subsystem"]
    missing = [r for r in need if runs[r]["status"] != "complete"]
    if missing:
        return {"computed": False, "label": EXPLORATORY,
                "reason": "not computed: " + ", ".join(f"{r} is {runs[r]['status']}" for r in missing)}
    c2, cs = runs[f"{key}-corpus-stage2"]["labels"], runs[f"{key}-corpus-subsystem"]["labels"]
    e2, es = runs[f"{key}-eval-domain"]["labels"], runs[f"{key}-eval-subsystem"]["labels"]
    record_table = dig(rec["series"], ("stage2_runs_compared_on_the_tranche_items",), "series_results.json")
    agreement = {
        "stage2": {**runs_compared(stage2_codes(e2), stage2_codes(c2), CLASSES + ["refusal"]),
                   "note": "rows: the evaluation run (domain-specific schema); columns: the corpus run; a refusal is a "
                           "fourth value; on the tranche items both runs cover"},
        "stage2_of_record": record_table,
        "subsystem": {**runs_compared(subsystem_codes(es), subsystem_codes(cs), VALUES8),
                      "note": "rows: the evaluation run; columns: the corpus run; unclassified is an eighth value; on "
                              "the tranche items both runs cover"},
        "subsystem_of_record": None,
        "subsystem_of_record_note": "none: the subsystem classifier of record was run once"}
    s2_eval = np.array([(e2.get(i) or "") for i in data["ids"]], dtype=object)
    item = item_rates(dict(data, s2=s2_eval))
    Dm = model_corpus(D, c2, cs)
    comp = corpus_series(Dm, item)
    if comp["comment_index_arrays_sha256"] != rec["comment_index_arrays_sha256"]:
        stop(f"the comment resamples are not those of record. {REPORT}")
    return {"computed": True, "label": EXPLORATORY, "agreement_with_the_evaluation_run": agreement,
            "rates_used": rates_used(item), "rates_of_record": record_rates(rec),
            "series": comp["series"], "series_of_record": record_series(rec),
            "classified_share": comp["classified_share"], "rq2": comp["rq2"], "rq2_of_record": record_rq2(rec),
            "tier_shares_v_2016_2024": comp["tier_shares_v_2016_2024"],
            "comment_index_arrays_sha256": comp["comment_index_arrays_sha256"],
            "not_computed": NOT_COMPUTED,
            "notes": ["The reweighting, the comment resamples and the tier shares rest on the Stage 1 run of record "
                      "and are those of the series of record.",
                      "The same 598 items supply the model's error rates and judge it, so its rates are somewhat "
                      "optimistic (Deviation 15).",
                      "The values are clipped to [0, 1] for display only; every statistic uses them before clipping."]}


# =============================================================================
# C: cost (rule 12)
# =============================================================================
def cost_section(runs: dict, rec: dict) -> dict:
    out = {}
    record_eval = {k: dig(rec["evaluation"], ("stage2", "configurations", n, "cost_usd_per_1000_comments"),
                          "evaluation_results.json") for k, n in RECORD_STAGE2.items()}
    for run in ORDER:
        x = runs[run]
        key, kind, items = RUNS[run]
        if items == "eval":
            beside = ({"cost_usd_per_1000_comments": record_eval[kind], "source": "evaluation_results.json",
                       "configuration": RECORD_STAGE2[kind]} if kind in record_eval else None)
        else:
            man = rec["corpus_run_manifests"]["stage2" if kind == "domain" else "subsystem"]
            beside = {"cost_usd_per_1000_comments": float(Fraction(str(man["cost_usd"])) / man["comments"] * 1000),
                      "cost_usd": man["cost_usd"], "comments": man["comments"],
                      "source": "stage2_manifest.json" if kind == "domain" else "subsystem_manifest.json"}
        if beside is not None:
            beside["prices"] = "single requests at list prices (no batch)"
        if x["status"] != "complete":
            out[run] = {"computed": False, "reason": f"not computed: the run is {x['status']}",
                        "of_record": beside}
            continue
        t, c, n = x["tokens"], x["cost"], x["counts"]["comments"]
        out[run] = {
            "computed": True, "label": EXPLORATORY, "model": x["model"], "comments": n, "calls": t["calls"],
            "tokens": {"input": t["input"], "output": t["output"], "of_which_thinking": t["thinking"],
                       "cache_creation_input": t["cache_creation_input"], "cache_read_input": t["cache_read_input"]},
            "cost_usd_batch": float(c["batch"]), "cost_usd_batch_exact": fr(c["batch"]),
            "cost_usd_standard": float(c["standard"]), "cost_usd_standard_exact": fr(c["standard"]),
            "cost_usd_per_1000_comments_batch": float(c["batch"] / n * 1000),
            "cost_usd_per_1000_comments_standard": float(c["standard"] / n * 1000),
            "thinking": {"tokens": t["thinking"],
                         "calls_that_report_no_thinking_count": t["calls_without_a_thinking_count"],
                         "share_of_output_tokens": (t["thinking"] / t["output"]) if t["output"] else None,
                         "cost_usd_batch": float(c["thinking_batch"]),
                         "cost_usd_per_1000_comments_batch": float(c["thinking_batch"] / n * 1000),
                         "cost_usd_per_1000_comments_standard": float(c["thinking_standard"] / n * 1000),
                         "share_of_cost": float(c["thinking_standard"] / c["standard"]) if c["standard"] else None},
            "prices_usd_per_mtok": {"input": float(PRICES[x["model"]]["input"]),
                                    "output": float(PRICES[x["model"]]["output"]),
                                    "cache_write": float(x["cache_prices"]["cache_write"]),
                                    "cache_read": float(x["cache_prices"]["cache_read"])},
            "of_record": beside}
    return {"label": EXPLORATORY, "runs": out,
            "note": "from the logged tokens of every answered call; batch prices are half the list prices (the runs "
                    "of Deviation 15 were sent through the Message Batches API); thinking is billed as output and is "
                    "part of the output tokens; standard prices are the list prices of single requests; the list "
                    "prices of Deviation 15 hold for global routing, and the regions the answers report are given "
                    "with each run"}


# =============================================================================
# the analyses
# =============================================================================
def runs_section(frontier: dict) -> dict:
    out = {}
    for run in ORDER:
        x = frontier["runs"][run]
        key, kind, items = RUNS[run]
        out[run] = {"model": MODELS[key], "model_name": NAMES[key], "prompt": KIND_NAMES[kind],
                    "items": "the 598 evaluation items" if items == "eval" else "the 6,503 corpus comments",
                    "status": x["status"], "reason": x["reason"], "counts": x.get("counts"),
                    "log_lines_that_are_not_json": x.get("log_lines_not_read", 0),
                    "files_sha256": x.get("files_sha256", {})}
    return {"runs": out, "pilot_gate": frontier["pilot_gate"],
            "stops": [{k: v for k, v in s.items()} for s in frontier["stops"]],
            "note": "a run that is not complete enters no figure; its counts are those of its log (Deviation 15)"}


def analyse(data: dict, D: dict, rec: dict, frontier: dict) -> dict:
    runs = frontier["runs"]
    complete = {r for r in ORDER if runs[r]["status"] == "complete"}
    prim = np.nonzero(data["prim"])[0]
    prim_ids = [data["ids"][j] for j in prim]
    g2 = np.array([CLASSES.index(data["g2"][j]) for j in prim], dtype=np.int64)
    w2 = [data["w"][j] for j in prim]
    enc = {n: ev.encode(rec["predictions"][n], prim_ids, CLASSES) for n in ("roberta", "sonnet-universal",
                                                                            "sonnet-domain")}
    stage2 = {}
    for schema in ("universal", "domain"):
        part = {"of_record": record_stage2(rec, schema)}
        for key in MODELS:
            run = f"{key}-eval-{schema}"
            if run in complete:
                labels = runs[run]["labels"]
                enc[(key, schema)] = ev.encode(pd.Series(labels), prim_ids, CLASSES)
                part[key] = {"computed": True, "model": MODELS[key],
                             **stage2_figures(enc[(key, schema)], g2, w2, data, labels)}
                part[key]["three_class_rates_M"]["note"] = (
                    f"M[i][j]: the weighted share of the gold class i items that {NAMES[key]} classifies j under the "
                    f"{KIND_NAMES[schema]} schema, on the primary item set, with the pooled design weights")
            else:
                part[key] = {"computed": False, "reason": f"not computed: {run} is {runs[run]['status']}"}
        stage2[schema] = part
    subsystem = {"of_record": dig(rec["series"], ("subsystem_classifier_validation",), "series_results.json")}
    for key in MODELS:
        run = f"{key}-eval-subsystem"
        subsystem[key] = ({"computed": True, "model": MODELS[key], **subsystem_agreement(data, runs[run]["labels"])}
                          if run in complete else
                          {"computed": False, "reason": f"not computed: {run} is {runs[run]['status']}"})
    results = {
        "specification": "Deviation 15 of docs/analysis_preregistration.md; analysis_06_frontier.py",
        "label": EXPLORATORY, "statement": STATEMENT,
        "runs": runs_section(frontier),
        "evaluation": {"label": EXPLORATORY, "items": len(prim_ids), "stage2": stage2,
                       "subsystem_agreement": subsystem, "comparisons": comparison_family(enc, g2, complete, rec)},
        "corpus": {key: corpus_analysis(key, runs, data, D, rec) for key in MODELS},
        "cost": cost_section(runs, rec),
    }
    return results


# =============================================================================
# the figures of record reproduced (rule 13)
# =============================================================================
def same(mine, record, path: str, problems: list, key: str = "") -> None:
    """Figures as written (analysis_03_series.rounded) against a file of record; differences are collected."""
    if isinstance(mine, dict):
        if not isinstance(record, dict):
            problems.append(path)
            return
        for k, v in mine.items():
            if k not in record:
                problems.append(f"{path}/{k}")
            else:
                same(v, record[k], f"{path}/{k}", problems, str(k))
    elif isinstance(mine, list):
        if not isinstance(record, list) or len(mine) != len(record):
            problems.append(path)
            return
        for k, (a, b) in enumerate(zip(mine, record)):
            same(a, b, f"{path}[{k}]", problems, key)
    elif isinstance(mine, bool) or isinstance(record, bool) or mine is None or record is None \
            or isinstance(mine, str) or isinstance(record, str):
        if mine != record:
            problems.append(path)
    elif isinstance(mine, (int, float)) and isinstance(record, (int, float)):
        tol = TOLERANCE_UNROUNDED * max(1.0, abs(float(record))) if key in series.UNROUNDED else TOLERANCE_ROUNDED
        if not abs(float(mine) - float(record)) <= tol:
            problems.append(path)
    elif mine != record:
        problems.append(path)


def reproduce_record(data: dict, D: dict, rec: dict) -> dict:
    """Rule 13: the code path of rules 5 to 11 on the labels and rates of record."""
    problems = []
    prim = np.nonzero(data["prim"])[0]
    prim_ids = [data["ids"][j] for j in prim]
    g2 = np.array([CLASSES.index(data["g2"][j]) for j in prim], dtype=np.int64)
    w2 = [data["w"][j] for j in prim]
    enc = {n: ev.encode(rec["predictions"][n], prim_ids, CLASSES) for n in ("roberta", "sonnet-universal",
                                                                            "sonnet-domain")}
    for schema, name in RECORD_STAGE2.items():
        labels = dict(rec["predictions"][name])
        mine = stage2_figures(enc[name], g2, w2, data, labels)
        c = dig(rec["evaluation"], ("stage2", "configurations", name), "evaluation_results.json")
        for k, rk in (("metrics", "pooled"), ("concern_rates_weighted", "concern_rates_weighted"),
                      ("concern_rates_unweighted", "concern_rates_unweighted")):
            same(series.rounded(mine[k]), c.get(rk), f"evaluation_results.json/{name}/{rk}", problems)
        if schema == "domain":
            same(series.rounded(mine["three_class_rates_M"]), dig(rec["sample"], ("error_rates", "three_class"),
                                                                  "sample_results.json"),
                 "sample_results.json/error_rates/three_class", problems)
    family, scope, a, b = RECORD_COMPARISON["universal"]
    row = [r for r in dig(rec["evaluation"], ("stage2", family), "evaluation_results.json")
           if r.get("scope") == scope and r.get("a") == a and r.get("b") == b]
    t = ev.strip_private(ev.permutation_test(enc[a], enc[b], g2, [0, 1, 2]))
    same(series.rounded(t), row[0] if len(row) == 1 else None, f"evaluation_results.json/{family}/{a}-{b}", problems)
    item = item_rates(data)
    of_record = series.item_side(data)
    same_rates = set(item["rates"]) == set(of_record["rates"]) and all(
        np.array_equal(item["rates"][k], of_record["rates"][k], equal_nan=True) for k in of_record["rates"])
    if not (same_rates and np.array_equal(item["M"], of_record["M"], equal_nan=True)
            and item["M_exact"] == of_record["M_exact"]):
        problems.append("analysis_03_series.item_side")
    corpus2 = {i: D["s2"][k] for k, i in enumerate(D["ids"]) if D["pop"][k]}
    eval2 = {data["ids"][j]: data["s2"][j] for j in prim}
    mine = runs_compared(stage2_codes(eval2), stage2_codes(corpus2), CLASSES + ["refusal"])
    same(series.rounded(mine), dig(rec["series"], ("stage2_runs_compared_on_the_tranche_items",), "series_results.json"),
         "series_results.json/stage2_runs_compared_on_the_tranche_items", problems)
    comp = corpus_series(D, item)
    rec_sha = dig(rec["series"], ("comment_resamples", "index_arrays_sha256"), "series_results.json")
    if comp["comment_index_arrays_sha256"] != rec_sha:
        problems.append("series_results.json/comment_resamples/index_arrays_sha256")
    for name, _, path in SERIES:
        block = dig(rec["series"], path, "series_results.json")
        same(series.rounded(comp["series"][name]), block, f"series_results.json/{'/'.join(path)}", problems)
    rq = record_rq2(rec)
    for s, entry in comp["rq2"]["values"].items():
        mine = series.rounded(entry)
        if "family_A_test" in mine:
            mine["family_A_test"] = {k: v for k, v in mine["family_A_test"].items()
                                     if k not in ("holm_adjusted_p", "significant_after_holm")}
        same(mine, rq["values"][s], f"series_results.json/rq2/values/{s}", problems)
    for k in ("concern_share_C_2016_2024", "concern_share_C_2016_2024_as_classified"):
        same(series.rounded(comp["rq2"][k]), rq[k], f"series_results.json/rq2/{k}", problems)
    if problems:
        stop(f"the code path does not reproduce {len(problems)} figure(s) of record, e.g. {problems[:3]}. {REPORT}")
    return {"comment_index_arrays_sha256": rec_sha, "item_index_arrays_sha256": item["index_arrays_sha256"]}


# =============================================================================
# the values file (for the figures)
# =============================================================================
def value_rows(results: dict) -> list:
    out = []

    def add(name, rws):
        for r in rws:
            iv = r.get("interval95") or {}
            out.append([name, r["period"], r.get("value"), r.get("value_displayed"), iv.get("low"), iv.get("high"),
                        iv.get("low_displayed"), iv.get("high_displayed"), iv.get("resamples_without_value")])

    for key in MODELS:
        c = results["corpus"][key]
        if not c.get("computed"):
            continue
        model = f"{MODELS[key]} ({EXPLORATORY})"
        for name, label, _ in SERIES:
            add(f"{model}: {label}", c["series"][name]["rows"])
        add(f"{model}: primary, classified share (quarter)",
            [{"period": p, "value": v} for p, v in zip(series.QLABELS, c["classified_share"])])
        for s in MEASURED:
            e = c["rq2"]["values"][s]
            if "series" in e:
                res = e["series"]["resolution"]
                add(f"{model}: pi_s {s} ({res})", e["series"]["pi_s"])
                add(f"{model}: C_s {s} ({res})", e["series"]["C_s"])
                add(f"{model}: pi_s {s}, as classified ({res})", e["series"]["pi_s_as_classified"])
                add(f"{model}: C_s {s}, as classified ({res})", e["series"]["C_s_as_classified"])
    return [[(fl(v) if isinstance(v, float) else ("" if v is None else v)) for v in r] for r in out]


# =============================================================================
# the report (every figure formatted from its unrounded value)
# =============================================================================
def render_report(r: dict) -> str:
    def pc(x, d=1):
        return "n/a" if x is None else f"{100 * float(x):.{d}f}%"

    def pp(x, d=2):
        return "n/a" if x is None else f"{100 * float(x):+.{d}f}"

    def p4(x):
        return "n/a" if x is None else f"{float(x):.4f}"

    def pv(x):
        if x is None:
            return "n/a"
        return f"{float(x):.8g}" if f"{float(x):.4f}" == "0.0500" else f"{float(x):.4f}"

    def money(x, d=4):
        return "n/a" if x is None else f"{float(x):.{d}f}"

    def shown(row):
        if not row or row.get("value") is None:
            return "n/a"
        return pc(row["value_displayed"]) + (f" (raw {pc(row['value'])})" if row.get("clipped") else "")

    def iv(i):
        if not i or i.get("low") is None:
            return "n/a"
        lo, hi = (i["low_displayed"], i["high_displayed"]) if "low_displayed" in i else (i["low"], i["high"])
        return f"{pc(lo)} to {pc(hi)}"

    def yes(b):
        return "n/a" if b is None else ("yes" if b else "no")

    def trend_cells(t):
        if not t or t.get("sen_slope") is None:
            return ["n/a"] * 4
        return [pp(t["sen_slope_per_year"]), f"{pp(t['gilbert95_low_per_year'])} to {pp(t['gilbert95_high_per_year'])}",
                pv(t["p"]), yes(t["significant"])]

    def ks(x):
        return f"{x['k']}/{x['n']} ({pc(x['share'])})" if x and x.get("n") else "n/a"

    def wil(x):
        return (f"{x['k']}/{x['n']} ({pc(x['share'])}; Wilson {pc(x['wilson95_low'])} to {pc(x['wilson95_high'])})"
                if x and x.get("n") else "n/a")

    L = ["# Exploratory runs of Claude Opus 5.5 and Claude Fable 5.1", "",
         "Deviation 15 of `docs/analysis_preregistration.md`; `analysis_06_frontier.py`. " + STATEMENT + " Shares are "
         "corrected by adjusted classify-and-count with each model's own rates and clipped to [0, 1] for display; "
         "slopes are in percentage points per year, on the values before clipping.", ""]
    ru = r["runs"]
    L += [f"## 1. The runs; {EXPLORATORY}", "",
          "| Run | Model | Prompt | Status | Comments | Calls | With a label | Refusals or unclassified (reasons) | "
          "Refusal categories |", "|---|---|---|---|---|---|---|---|---|"]
    for run, x in ru["runs"].items():
        c = x.get("counts") or {}
        fs = c.get("final_status") or {}
        n = c.get("comments", c.get("comments_with_a_final_result"))
        calls = (r["cost"]["runs"][run].get("calls") if r["cost"]["runs"][run].get("computed") else
                 c.get("answered_calls"))
        labelled = f"{fs.get('ok', 0):,}" if c else "n/a"
        lacking = f"{sum(v for k, v in fs.items() if k != 'ok'):,}" if c else "n/a"
        reasons = ", ".join(f"{k} {v}" for k, v in sorted((c.get("no_answer_reasons") or {}).items()))
        cats = (", ".join(f"{k} {v}" for k, v in sorted((c.get("refusal_categories") or {}).items())) or "none") \
            if c else "n/a"
        comments = "n/a" if n is None else f"{n:,}"
        calls = "n/a" if calls is None else f"{calls:,}"
        L.append(f"| {run} | {x['model_name']} | {x['prompt']} | {x['status']} | {comments} | {calls} | {labelled} | "
                 f"{lacking}{f' ({reasons})' if reasons else ''} | {cats} |")
    L.append("")
    for run, x in ru["runs"].items():
        if x["status"] != "complete":
            L.append(f"- {run}: {x['status']}: {x['reason']}. It enters no figure.")
    regions = Counter()
    for x in ru["runs"].values():
        for k, v in ((x.get("counts") or {}).get("inference_geo_reported_by_the_answers") or {}).items():
            regions[k] += v
    if regions:
        L.append("- Inference regions reported by the answers of the complete runs: "
                 + ", ".join(f"{k} {v:,}" for k, v in sorted(regions.items()))
                 + " (the prices of Deviation 15 hold for global routing).")
    L.append("")
    ev_ = r["evaluation"]
    L += [f"## 2. Stage 2 on the {ev_['items']} evaluation items; {EXPLORATORY}", ""]
    for schema in ("universal", "domain"):
        part = ev_["stage2"][schema]
        L += [f"### {KIND_NAMES[schema].capitalize()} schema", "",
              "| Classifier | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | No class | TPR (weighted) | "
              "FPR (weighted) | TPR - FPR (weighted) | TPR (unweighted) | FPR (unweighted) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        rows = [(f"{part['of_record']['name']}, of record", part["of_record"])] + \
               [(NAMES[k], part[k]) for k in MODELS if part[k].get("computed")]
        for name, x in rows:
            m, w, u = x["metrics"], x["concern_rates_weighted"], x["concern_rates_unweighted"]
            L.append(f"| {name} | {p4(m['macro_f1'])} | " + " | ".join(p4(m["per_class"][c]["f1"]) for c in CLASSES) +
                     f" | {m['refusals']} | {p4(w['tpr'])} | {p4(w['fpr'])} | {p4(w['tpr_minus_fpr'])} | "
                     f"{p4(u['tpr'])} | {p4(u['fpr'])} |")
        L += [""] + [f"- {NAMES[k]}: {part[k]['reason']}." for k in MODELS if not part[k].get("computed")] + [""]
        L += [f"Three-class rates M_ij, {KIND_NAMES[schema]} schema (weighted; rows: gold class; columns: "
              f"classified, a refusal counted as OTHER):", "",
              "| Classifier | Gold | CONCERN | ENDORSEMENT | OTHER |", "|---|---|---|---|---|"]
        rows = ([(f"{part['of_record']['name']}, of record", part["of_record"]["three_class_rates_M"])]
                if part["of_record"]["three_class_rates_M"] else []) + \
               [(NAMES[k], part[k]["three_class_rates_M"]) for k in MODELS if part[k].get("computed")]
        for name, M in rows:
            for a in CLASSES:
                L.append(f"| {name} | {a} | " + " | ".join(p4(M["weighted_rates_gold_by_classified"][a][b])
                                                            for b in CLASSES) + " |")
        if not part["of_record"]["three_class_rates_M"]:
            L.append(f"\n{cap(part['of_record']['note'])}.")
        L.append("")
    sa = ev_["subsystem_agreement"]
    L += [f"## 3. Subsystem classifier against the gold primary subsystems; {EXPLORATORY}", "",
          "| Classifier | Items | Overall agreement, both tranches | Without the adjudicated items |", "|---|---|---|---|"]
    rows = [("Claude Sonnet 4.6, of record", sa["of_record"])] + [(NAMES[k], sa[k]) for k in MODELS
                                                                  if sa[k].get("computed")]
    for name, x in rows:
        b, nb = x["both tranches, all items"], x["both tranches, without the adjudicated items"]
        L.append(f"| {name} | {b['items']} | {wil(b['overall_agreement'])} | {wil(nb['overall_agreement'])} |")
    L += [""] + [f"- {NAMES[k]}: {sa[k]['reason']}." for k in MODELS if not sa[k].get("computed")]
    L += ["", "Per value, both tranches (of the items with a gold value, the share given it; of the items given a value, "
              "the share whose gold value it is):", "",
          "| Value | " + " | ".join(f"{n}: given its gold value | {n}: right when given" for n, _ in rows) + " |",
          "|---|" + "---|---|" * len(rows)]
    for s in SUBSYSTEMS:
        L.append(f"| {s} | " + " | ".join(f"{ks(x['both tranches, all items']['by_value'][s]['recall'])} | "
                                          f"{ks(x['both tranches, all items']['by_value'][s]['precision'])}"
                                          for _, x in rows) + " |")
    cm = ev_["comparisons"]
    L += ["", f"## 4. Comparisons on macro-F1; {EXPLORATORY}: one family of their own, Holm-Bonferroni at 0.05", "",
          "| Schema | a | b | Difference (a - b) | p | Holm-adjusted p | Result |", "|---|---|---|---|---|---|---|"]
    for t in cm["tests"]:
        L.append(f"| {KIND_NAMES[t['schema']]} | {t['a_name']} | {t['b_name']} | {p4(t['difference'])} | {pv(t['p'])} | "
                 f"{pv(t['holm_adjusted_p'])} | {t['result']} |")
    L += [""] + [f"- Dropped from the family ({KIND_NAMES[d['schema']]} schema): {d['a_name']} against "
                 f"{d['b_name']}; {d['reason']}." for d in cm["dropped"]]
    for schema, x in cm["comparisons_of_record_with_roberta"].items():
        L.append(f"- Comparison of record, {KIND_NAMES[schema]} schema (Family {'B' if schema == 'universal' else 'C'}): "
                 f"RoBERTa against {ev.NAMES[x['b']]}, difference {p4(x['difference'])}, p = {pv(x['p'])}"
                 + (f", Holm-adjusted p = {pv(x['p_holm'])} ({x['result']})" if "p_holm" in x else "") + ".")
    L.append("")
    for key in MODELS:
        c = r["corpus"][key]
        L += [f"## 5{'ab'[list(MODELS).index(key)]}. Corpus runs of {NAMES[key]}; {EXPLORATORY}", ""]
        if not c.get("computed"):
            L += [cap(c["reason"]) + ".", ""]
            continue
        ag = c["agreement_with_the_evaluation_run"]
        s2, rs2, ss = ag["stage2"], ag["stage2_of_record"], ag["subsystem"]
        L += [f"Agreement with the evaluation run on the tranche items both cover: Stage 2 (domain-specific schema) "
              f"{ks(s2['same_label'])} the same label (of record, Claude Sonnet 4.6: {ks(rs2['same_label'])}); "
              f"subsystem {ks(ss['same_label'])} (no figure of record).", "",
              "| Evaluation run \\ corpus run | " + " | ".join(CLASSES + ["refusal"]) + " |", "|---|" + "---|" * 4]
        for a in CLASSES + ["refusal"]:
            L.append(f"| {a} | " + " | ".join(str(s2["evaluation_by_corpus_run"][a][b]) for b in CLASSES + ["refusal"])
                     + " |")
        ru_, rr = c["rates_used"], c["rates_of_record"]
        L += ["", "Error rates (the model's, from its domain-specific evaluation run; beside them those of record):", "",
              "| Rate | Model | Of record |", "|---|---|---|",
              f"| TPR | {p4(ru_['tpr'])} | {p4(rr['tpr'])} |", f"| FPR | {p4(ru_['fpr'])} | {p4(rr['fpr'])} |",
              f"| TPR - FPR | {p4(ru_['tpr_minus_fpr'])} | {p4(rr['tpr_minus_fpr'])} |"]
        for b in ("early", "late"):
            for k in ("tpr", "fpr"):
                L.append(f"| {k.upper()}, {b} block | {p4(ru_['block_rates_both_tranches'][b][k])} | "
                         f"{p4(rr['block_rates_both_tranches'][b][k])} |")
        L += ["", "| Series | Sen's slope | Gilbert 95% interval | MK p | Significant | Of record: Sen's slope | "
                  "Gilbert 95% interval | MK p | Significant |", "|---|---|---|---|---|---|---|---|---|"]
        for name, _, _ in SERIES:
            L.append(f"| {SERIES_TITLES[name]} | " + " | ".join(trend_cells(c["series"][name]["trend"])) + " | "
                     + " | ".join(trend_cells(c["series_of_record"][name]["trend"])) + " |")
        L += ["", "Primary series by quarter:", "",
              "| Quarter | Classified | Corrected | 95% interval | Of record: corrected | 95% interval |",
              "|---|---|---|---|---|---|"]
        rec_rows = c["series_of_record"]["primary"]["rows"]
        for qi, row in enumerate(c["series"]["primary"]["rows"][:series.TREND_Q]):
            L.append(f"| {row['period']} | {pc(c['classified_share'][qi])} | {shown(row)} | {iv(row['interval95'])} | "
                     f"{shown(rec_rows[qi])} | {iv(rec_rows[qi].get('interval95'))} |")
        q2, rq2 = c["rq2"], c["rq2_of_record"]
        L += ["", f"RQ2: concern share C over 2016-2024 (corrected) {shown(q2['concern_share_C_2016_2024'])}; of record "
                  f"{shown(rq2['concern_share_C_2016_2024'])}.", "",
              "| Value | Reported as | pi_s 2016-2024 | C_s | E_s | Of record: reported as | pi_s | C_s | E_s |",
              "|---|---|---|---|---|---|---|---|---|"]
        for s in MEASURED:
            mine, recd = q2["values"][s], rq2["values"][s]

            def cells(e):
                o = e.get("over_2016_2024")
                return ([shown(o["pi_s"]), shown(o["C_s"]), p4(o["E_s"]["value"])] if o else ["counts", "counts", "counts"])

            L.append(f"| {s} | {mine['sparsity']['reported_as']} | " + " | ".join(cells(mine)) + f" | "
                     f"{recd['sparsity']['reported_as']} | " + " | ".join(cells(recd)) + " |")
        t = q2["values"]["sensing"].get("family_A_test")
        rt = rq2["values"]["sensing"].get("family_A_test")
        L += ["", "Test of sensing (Family A's test, a family of one): "
              + (f"Sen's slope {pp(t['sen_slope_per_year'])} points per year (Gilbert {pp(t['gilbert95_low_per_year'])} "
                 f"to {pp(t['gilbert95_high_per_year'])}), p = {pv(t['p'])}" if t and t.get("sen_slope") is not None
                 else "not computed: the sparsity rule gives sensing no series")
              + "; of record: " + (f"Sen's slope {pp(rt['sen_slope_per_year'])}, p = {pv(rt['p'])}, Holm-adjusted "
                                   f"{pv(rt.get('holm_adjusted_p'))}" if rt and rt.get("sen_slope") is not None
                                   else "none") + ".", "",
              "| Value | Classified relevant, 2016-2024 | Median quarterly | Median annual | Of record: classified "
              "relevant | Median quarterly | Median annual |", "|---|---|---|---|---|---|---|"]
        for s in VALUES8:
            mine, recd = q2["values"][s], rq2["values"][s]
            tot = sum(v for k, v in mine["counts"]["classified_relevant_by_year"].items() if int(k) <= 2024)
            rtot = sum(v for k, v in recd["counts"]["classified_relevant_by_year"].items() if int(k) <= 2024)
            L.append(f"| {s} | {tot:,} | {mine['sparsity']['median_quarterly_count']:g} | "
                     f"{mine['sparsity']['median_annual_count']:g} | {rtot:,} | "
                     f"{recd['sparsity']['median_quarterly_count']:g} | {recd['sparsity']['median_annual_count']:g} |")
        L += ["", f"Not computed: {c['not_computed']}.", ""]
    co = r["cost"]["runs"]
    L += [f"## 6. Cost per 1,000 comments; {EXPLORATORY}", "",
          "| Run | Comments | Calls | Tokens in | Tokens out | Of which thinking | Cost (US$, batch prices) | "
          "Per 1,000, batch | Per 1,000, standard | Thinking, per 1,000 (batch) | Of record, per 1,000 (single "
          "requests) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for run, x in co.items():
        rec_ = x.get("of_record")
        beside = money(rec_["cost_usd_per_1000_comments"]) if rec_ else "none"
        if not x.get("computed"):
            L.append(f"| {run} | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | {beside} |")
            continue
        t = x["tokens"]
        L.append(f"| {run} | {x['comments']:,} | {x['calls']:,} | {t['input']:,} | {t['output']:,} | "
                 f"{t['of_which_thinking']:,} | {money(x['cost_usd_batch'])} | "
                 f"{money(x['cost_usd_per_1000_comments_batch'])} | {money(x['cost_usd_per_1000_comments_standard'])} | "
                 f"{money(x['thinking']['cost_usd_per_1000_comments_batch'])} | {beside} |")
    unreported = {run: x["thinking"]["calls_that_report_no_thinking_count"] for run, x in co.items()
                  if x.get("computed") and x["thinking"]["calls_that_report_no_thinking_count"]}
    L += [""] + (["Calls whose answer reported no thinking-token count (counted as none): "
                  + ", ".join(f"{run} {n:,}" for run, n in unreported.items()) + "."] if unreported else []) \
        + ["", cap(r["cost"]["note"]) + ".", ""]
    return "\n".join(L) + "\n"


# =============================================================================
# outputs
# =============================================================================
def library_versions() -> dict:
    v = mc.versions("numpy", "pandas", "scipy", "sklearn")
    v.update({n: package_version(n) for n in LIBRARIES})
    return v


def write_outputs(results: dict, me: str, out_dir: Path, inputs: dict, scripts: dict, frontier: dict) -> None:
    """Written to a fresh work folder, then moved into place with frontier_results.json last: a run that fails
    part-way leaves no results file, so it can simply be run again (it gives the same bytes)."""
    clean = series.rounded(results)
    report = render_report(results)
    work = OUT_ROOT / f"in_progress_{os.getpid()}_{time.time_ns()}"
    work.mkdir(parents=True)
    try:
        mc.write_json(work / "frontier_results.json", clean)
        with open(work / "frontier_report.md", "w", encoding="utf-8", newline="\n") as f:
            f.write(report)
        outputs = {"frontier_results.json": mc.sha256_file(work / "frontier_results.json"),
                   "frontier_report.md": mc.sha256_file(work / "frontier_report.md"),
                   "frontier_values.csv": mc.write_rows_csv(work / "frontier_values.csv", series.VALUE_COLUMNS,
                                                            value_rows(results))}
        created = mc.now_iso()
        versions = library_versions()
        mc.write_json(work / "frontier_manifest.json", {
            "created": created, "script": {"file": SCRIPT, "sha256_lf": me}, "scripts_of_record_sha256_lf": scripts,
            "frontier_script": {"file": FRONTIER_SCRIPT, "sha256_lf": FRONTIER_SCRIPT_SHA256},
            "inputs_sha256": inputs, "outputs_sha256": outputs, "versions": versions})
        out_dir.mkdir(parents=True, exist_ok=True)
        for name in ("frontier_values.csv", "frontier_report.md", "frontier_manifest.json", "frontier_results.json"):
            mc.replace_patiently(work / name, out_dir / name)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    rel = out_dir.relative_to(cfg.REPO).as_posix()
    man_sha = mc.sha256_file(out_dir / "frontier_manifest.json")
    v = versions
    states = []
    for run in ORDER:
        x = frontier["runs"][run]
        files = "; ".join(f"`{k}` `{s}`" for k, s in sorted(x.get("files_sha256", {}).items()))
        states.append(f"`{run}` {x['status']}" + (f" ({files})" if files else ""))
    other = "; ".join(f"`{k}` `{s}`" for k, s in sorted(frontier["files_sha256"].items()))
    mc.show_register_block(out_dir / "PASTE_frontier_block.txt", [
        f"- `{SCRIPT}` (SHA-256 `{me}`) run {created} with `--confirm-committed`: every input matched its SHA-256 of "
        f"record (the inputs of the sample analyses, checked by `analysis_01_sample.py`; corpus v2.2, the three "
        f"prediction files of the corpus runs and `thread_sizes.csv`, checked by `analysis_03_series.py`; "
        f"`results/series_results.json`, `results/sample_results.json`, `stage2_manifest.json` and "
        f"`subsystem_manifest.json`); the code path reproduced the figures of record it recomputes; the item and "
        f"comment index arrays matched the register.",
        f"- The runs of Deviation 15 (`{FRONTIER_SCRIPT}` SHA-256 `{FRONTIER_SCRIPT_SHA256}`): " + "; ".join(states)
        + (f". Also read: {other}." if other else "."),
        f"- Outputs, in `{rel}/` (not committed): `frontier_results.json` SHA-256 `{outputs['frontier_results.json']}`; "
        f"`frontier_report.md` `{outputs['frontier_report.md']}`; `frontier_values.csv` "
        f"`{outputs['frontier_values.csv']}`; `frontier_manifest.json` `{man_sha}`. Python {v['python']}, NumPy "
        f"{v['numpy']}, pandas {v['pandas']}, SciPy {v['scipy']}, scikit-learn {v['sklearn']}, pymannkendall "
        f"{v['pymannkendall']}.",
    ])
    print(f"\nwritten: {out_dir}")


# =============================================================================
# main
# =============================================================================
def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Exploratory analyses of the runs of Deviation 15.")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks and a dry run; writes nothing")
    mode.add_argument("--confirm-committed", action="store_true", help="the run of record (after the commit)")
    args = ap.parse_args()
    if not (args.preflight or args.confirm_committed):
        stop("choose one: --preflight (before the commit) or --confirm-committed (after the commit: the run of record)")
    started = time.time()
    print("Exploratory runs of Deviation 15: " + ("preflight, before the commit\n" if args.preflight else
                                                 "the run of record\n"))
    me = own_sha256()
    out_dir = run_folder(me)
    print(f"this script: {SCRIPT} SHA-256 {me}")
    if (out_dir / "frontier_results.json").exists():
        stop(f"this script's analyses have already been run: their results are in {out_dir}. They are run once.")
    scripts = check_modules()
    front = check_frontier_script()
    if args.confirm_committed and not front["filled"]:
        stop(f"FRONTIER_SCRIPT_SHA256 is not filled in: put in it the SHA-256 (LF line endings) of the committed "
             f"{FRONTIER_SCRIPT}, commit, and run the preflight again. {REPORT}")
    libs = check_libraries()
    print(f"modules: the six imported modules are the files in the repository at aff4276; libraries: "
          f"{', '.join(f'{n} {v}' for n, v in libs.items())}; {FRONTIER_SCRIPT}: "
          + ("not in the folder" if not front["file_present"] else
             ("the committed file" if front["filled"] else "present (FRONTIER_SCRIPT_SHA256 not yet filled in)")))
    loaded = sample.load_all()
    data = loaded["data"]
    print("inputs of the sample analyses: every input with a recorded SHA-256 matches it (checked by "
          "analysis_01_sample.py)")
    gold, _ = ev.load_gold()
    record_runs, _ = ev.verify(gold)
    corpus, cinfo = series.load_corpus()
    runs_of_record = series.load_runs(corpus, data)
    sizes, sizes_sha = series.load_thread_sizes(corpus)
    frame = series.load_frame_ids()
    D = series.assemble(corpus, runs_of_record, sizes, frame, data)
    files, file_shas = load_record_files()
    rec = {"evaluation": data["evaluation"], "series": files["series_results.json"],
           "sample": files["sample_results.json"],
           "corpus_run_manifests": {"stage2": files["stage2_manifest.json"],
                                    "subsystem": files["subsystem_manifest.json"]},
           "predictions": {n: record_runs[n]["pred"] for n in ("roberta", "sonnet-universal", "sonnet-domain")}}
    inputs = {**{f"{k} (checked by analysis_01_sample.py)": v for k, v in loaded["shas"].items()},
              "corpus.parquet": cinfo["file_sha256"], **runs_of_record["shas"], "thread_sizes.csv": sizes_sha,
              **file_shas}
    print(f"corpus runs of record and results of record: every file matches its SHA-256 of record "
          f"({int(D['pop'].sum()):,} Tier 1+2 comments classified relevant)")
    reproduced = reproduce_record(data, D, rec)
    rec["comment_index_arrays_sha256"] = reproduced["comment_index_arrays_sha256"]
    print("record: the code path reproduces every figure of record it recomputes (rule 13); the item and comment "
          "index arrays are those of record")
    prim_ids = [data["ids"][j] for j in np.nonzero(data["prim"])[0]]
    corpus_ids = sorted(str(i) for i in D["ids"][D["pop"]])
    if len(prim_ids) != EVAL_ITEMS or len(corpus_ids) != CORPUS_ITEMS:
        stop(f"the record gives {len(prim_ids):,} items with a gold Stage 2 class and {len(corpus_ids):,} Tier 1+2 "
             f"comments classified relevant; Deviation 15 has {EVAL_ITEMS:,} and {CORPUS_ITEMS:,}. {REPORT}")
    expected = {"eval": prim_ids, "corpus": corpus_ids}
    if args.preflight:
        if front["filled"]:
            present = read_frontier(expected)
            print("runs of Deviation 15: " + "; ".join(f"{run} {x['status']}" for run, x in present["runs"].items())
                  + " (the files of every complete run checked; nothing computed from them)")
        else:
            print("runs of Deviation 15: not checked, because FRONTIER_SCRIPT_SHA256 is not yet filled in")
        dry = dry_run_frontier(data, expected)
        res = analyse(data, D, rec, dry)
        series.rounded(res)
        render_report(res)
        value_rows(res)
        print(f"dry run: every analysis ran on the real data structure with the labels of the ten runs replaced by "
              f"made-up labels (rule 15); its report and values were rendered in memory; the result was discarded and "
              f"nothing was shown ({time.time() - started:.0f} seconds)")
        if not front["filled"]:
            stop(f"PREFLIGHT NOT PASSED: every other check and the dry run passed, but FRONTIER_SCRIPT_SHA256 is not "
                 f"filled in. Put in it the SHA-256 (LF line endings) of the committed {FRONTIER_SCRIPT} and run the "
                 f"preflight again before the commit.")
        print("\nPREFLIGHT PASSED: every input matches the record, the code path reproduces the figures of record, and "
              "every analysis can be computed. No output of a run of Deviation 15 entered any figure, and no output "
              "was written.")
        return
    frontier = read_frontier(expected)
    unsettled = [run for run, x in frontier["runs"].items() if not x.get("settled", True)]
    if unsettled:
        stop(f"the runs of Deviation 15 have not ended: {', '.join(unsettled)} "
             f"{'is' if len(unsettled) == 1 else 'are'} neither complete nor halted nor not made for a recorded "
             f"reason (python models_07_frontier.py --status). The run of record is made once, after the runs end. "
             f"{REPORT}")
    inputs.update(frontier["files_sha256"])
    for run in ORDER:
        inputs.update({f"{k} ({run})": s for k, s in frontier["runs"][run].get("files_sha256", {}).items()})
    print("runs of Deviation 15: " + "; ".join(f"{run} {x['status']}" for run, x in frontier["runs"].items()))
    res = analyse(data, D, rec, frontier)
    results = {**res, "inputs_sha256": inputs, "scripts_of_record_sha256_lf": scripts,
               "frontier_script_sha256_lf": FRONTIER_SCRIPT_SHA256,
               "index_arrays_sha256": {"items": reproduced["item_index_arrays_sha256"],
                                       "comments": reproduced["comment_index_arrays_sha256"]}}
    write_outputs(results, me, out_dir, inputs, scripts, frontier)
    print(f"({time.time() - started:.0f} seconds)")


if __name__ == "__main__":
    main()
