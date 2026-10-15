"""Corpus runs of the deployed classifiers (Deviation 13 of docs/analysis_preregistration.md).

Steps, in this order, from the repository folder with the virtual environment active:
    python models_06_deploy.py --preflight
        Before the commit (PC). Checks every module and input file the runs use against the record, and the
        comment text the runs will be given, then stops. It runs no model, sends nothing and writes nothing.
    python models_06_deploy.py --prepare
        After the commit (PC). Writes data/models/deploy/corpus_input.csv: every comment of corpus v2.2 with its
        tier, subreddit and text, the text prepared as Deviation 10 prepared it for the pre-filter.
    python models_06_deploy.py --stage1 --train-input F --corpus-input F --input-manifest F --out-dir D
        On a GPU (for example Colab). Retrains the deployed Stage 1 classifier once on the 1,000 tranche items and
        runs it once over all 12,776 comments of corpus v2.2. Upload this file, models_config.py, models_common.py,
        models_04_finetune_cv.py, data/models/finetune_input.csv, data/models/deploy/corpus_input.csv and
        corpus_input_manifest.json; install transformers 5.19.0 and scikit-learn 1.9.0; put --out-dir on Google Drive.
        Its two output files are written only when it finishes; if the session ends before, the step is given
        again from the start. Copy the two files to data/models/deploy/ on the PC.
    python models_06_deploy.py --check-connection
        (PC, API key set.) Two calls on the test sentence: one with the Stage 2 prompt, one with the subsystem
        prompt. No comment is sent.
    python models_06_deploy.py --stage2
        (PC, API key set.) The deployed Stage 2 classifier over every Tier 1+2 comment classified relevant.
    python models_06_deploy.py --subsystem
        (PC, API key set.) After the Stage 2 run: the subsystem classifier over the same comments and over the
        tranche items that are relevant in the gold set and not among them (validation only).
A run that stops resumes from its log when the same command is given again; finished comments are kept. One
API step at a time: a lock file stops a second one from starting while another is under way.
The API key is read from the environment variable ANTHROPIC_API_KEY and is never printed or saved.

What the runs print (Deviation 13): progress, the number of comments each run covers, the counts of refusals,
of unclassified comments and of comments set aside (totals, at the end of a run), spend, and file hashes. Nothing
from a classifier run is printed or written by class, subsystem, period, era, subreddit, tier or thread size.

Rules fixed with this file (where Deviation 13 is silent, or to say how a committed rule is applied)
  1. Record. Every module this file imports is checked against its SHA-256 with LF line endings (the files in the
     repository at 8d9c0d1), and every input file against its recorded SHA-256 or against the manifest of the
     step that wrote it. A step accepts an earlier step's output only if this same file made it (its SHA-256 is
     in that step's manifest).
  2. Text (Deviations 10 and 13). The text of every run is clean_body of corpus v2.2 with the characters removed
     that tranche2_common.shown_text removes, the function that prepared the pre-filter input, used unchanged.
     It must equal the pre-filter input of record for each of the 12,166 frame comments, and the text of
     finetune_input.csv for each of the 1,000 tranche items, or the step stops.
  3. Subreddit (Deviations 1 and 13). The Stage 1 input is the pair ("r/" + subreddit, comment). The subreddit is
     the corpus value with any leading "r/" removed; for the eight subreddits of Tiers 1 and 2 it is written in
     the letter case of the training input (finetune_input.csv), so that the model reads the strings it was
     trained on. The 1,000 tranche items must have the same subreddit in both, ignoring letter case.
  4. Stage 1 (Deviation 13; FINAL_RETRAINING in models_config.py). The items, input pair, special-string rule and
     settings of models_04_finetune_cv.py, used unchanged, with no held-out split, no evaluation and no
     checkpoint during training. The learning-rate schedule is set for the 10 epochs of the cross-validation runs
     and training stops at the end of epoch 5; the epochs, steps and learning rate are checked after training.
     Seed 24916660. A comment is classified relevant when its probability of Y is greater than that of N (the
     arg-max of the cross-validation runs; an exact tie is N). Probabilities are written to six decimals. That
     RoBERTa is the deployed Stage 1 model (evaluation of record) and that 5 is the median of its folds' best
     epochs are both checked.
  5. Prompts (Deviation 13). Stage 2: the domain-specific prompt, request, settings, answer reading, retry rule and
     logging of models_02_claude.py, imported unchanged. Subsystem: the prompt of Deviation 13 word for word,
     checked against the committed pre-registration whenever an API step starts, and its answer reading as
     Deviation 13 states it, after the cleaning of the evaluation runs.
  6. Model version. Every call must be answered under claude-sonnet-4-6 (or that identifier plus a date) and by
     the model version that answered the evaluation run of record (sonnet-domain), or the step stops. A run that
     stops for this cannot resume: a further deviation then decides what is done.
  7. Comments. Stage 2: the Tier 1+2 comments classified relevant at Stage 1. Subsystem run: the same comments,
     and the tranche items that are relevant in the gold set and not among them (validation only). Each run
     takes its comments in order of id.
  8. Errors (Deviation 13). After the client's retries, a connection error, a timeout (status 408 included),
     status 409 or 429 (which the client also retries) or a status of 500 or above stops the run, which resumes
     from its log. Any other error from the API stops the run, and the
     comment is recorded as rejected. At the next start each rejected comment is sent first, alone; if it is
     rejected again it is set aside and the run goes on. When the next 20 comments (all the comments left, if
     fewer than 20 remain) have been answered with no API error, each comment set aside is recorded as a refusal
     (Stage 2) or as unclassified (subsystem run) and listed. If the run stops first, the comment is sent first
     again at the next start. If no comment is left to answer after a comment is set aside, the run stops for
     review, and a further deviation decides how the comment is recorded.
  9. Spend (Deviation 13). Every logged call of the two runs and of this file's connection checks, at the list
     prices of models_config.py. The ceiling is US$23 unless --ceiling sets another, which is recorded in the
     register with its reason before the run. A run halts when the measured spend reaches the ceiling. Before the
     first call of the subsystem run the estimate of Deviation 13 is computed from every call logged by the Stage
     2 run and from the connection check, and the run does not start if the estimate added to the spend so far is
     above the ceiling.

Writes, in data/models/deploy/ (data/ is not committed):
  corpus_input.csv, corpus_input_manifest.json                 --prepare
  stage1_corpus_predictions.csv, stage1_corpus_manifest.json   --stage1 (in --out-dir; copy them here)
  connection_check.jsonl                                       --check-connection
  stage2_log.jsonl, stage2_predictions.csv, stage2_manifest.json            --stage2
  subsystem_log.jsonl, subsystem_predictions.csv, subsystem_manifest.json   --subsystem
  PASTE_<step>_block.txt                                       the register lines of each step (hashes only)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
import tempfile
import threading
import time
from collections import Counter
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
from pathlib import Path

import models_common as mc
import models_config as cfg

# =============================================================================
# THE RECORD
# =============================================================================
DEPLOY_DIR = cfg.MODELS_DIR / "deploy"
CORPUS_INPUT = DEPLOY_DIR / "corpus_input.csv"
CORPUS_INPUT_MANIFEST = DEPLOY_DIR / "corpus_input_manifest.json"
STAGE1_PREDICTIONS_NAME = "stage1_corpus_predictions.csv"
STAGE1_MANIFEST_NAME = "stage1_corpus_manifest.json"
CONNECTION_LOG = DEPLOY_DIR / "connection_check.jsonl"

# SHA-256 with LF line endings of each module this file imports: the files in the repository at 8d9c0d1.
MODULES_OF_RECORD = {
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
    "models_02_claude.py": "dbdddd642e2dc7a7725482693ca71197e92d301fcc56ffef4ea6c23e1d996146",
    "models_04_finetune_cv.py": "2f64b2ae903d755e25b019a6604d2b7b74ff038b10a39bd32abba3192e2c908b",
    "models_05_evaluate.py": "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734",
    "analysis_01_sample.py": "95f7a48c7509c58eca11330814be32fef0a8c1e430447790fdccfa5da6fdd952",
    "tranche2_common.py": "631df7b37fe9381ca7293fd07b70d6150e56eb269b9ae444fc7a2168efc74ac6",
}

CORPUS_ROWS = 12776                             # R5
FRAME_ROWS = 12166                              # R5
TIERS_ANALYSED = ("Tier 1", "Tier 2")           # R5: Tier 3 receives Stage 1 only (Deviation 13)

STAGE1_MODEL = "roberta"                        # the deployed Stage 1 model (evaluation of record, Deviation 12)
STAGE1_RUN_OF_RECORD = "stage1-roberta"
STAGE1_LABELS = ["N", "Y"]                      # as in models_04_finetune_cv.py
STAGE1_TRAINING_ITEMS = 1000                    # every item with a gold Stage 1 label (bb3fbfe)
FINAL_EPOCHS = 5                                # Deviation 13: the median of the best epochs 5, 5, 5, 2 and 2
# TrainingArguments fields that differ from those of the cross-validation runs, and nothing else may differ:
# the final retraining has no held-out split, so no evaluation, no checkpoint and no best model to restore.
FINAL_TRAINING_DIFFERENCES = {"eval_strategy", "do_eval", "save_strategy", "load_best_model_at_end",
                              "metric_for_best_model", "greater_is_better", "save_only_model", "save_total_limit"}
ACCEPT_TEST_MODEL = False                       # True only in the synthetic tests of this file

MODEL = cfg.CLAUDE_MODELS["sonnet"]             # claude-sonnet-4-6 (Deviation 13)
EVALUATION_RUN = "sonnet-domain"                # the evaluation run of the deployed Stage 2 classifier
CEILING_USD = 23.00                             # Deviation 13: both API runs and their connection checks
WINDOW = 20                                     # Deviation 13: comments answered before a set-aside is recorded
ESTIMATE_PRICES = (3.00, 15.00)                 # Deviation 13: US$ per million input and output tokens

# The subsystem prompt of Deviation 13, word for word ("{comment text}" there is "{text}" here).
SUBSYSTEM_PROMPT = (
    'You are a careful annotator.\n'
    'Choose exactly ONE label for the comment.\n'
    '\n'
    'Candidate labels:\n'
    "- sensing: the vehicle's perception of the world outside it. Cameras, lidar, radar, ultrasonics, sensor fusion, what the car can and cannot see, sensor failure or degradation, camera-only versus lidar arguments.\n"
    '- in_vehicle_networks: data moving inside the vehicle. CAN bus, ECUs, domain controllers, infotainment (IVI) as a networked component, over-the-air software updates to vehicle systems, onboard compute.\n'
    '- v2x: the vehicle talking to something outside itself. V2V, V2I, vehicle-to-cloud, fleet telemetry uplink, connected infrastructure, traffic signal communication, remote operation or teleoperation links.\n'
    '- cybersecurity: attack, defence, or vulnerability. Hacking, remote takeover, spoofing a sensor or GPS, ransomware, key or access control, security of updates.\n'
    '- privacy: what is collected about people and who can see it. Cabin cameras, location history, driver monitoring, footage handed to police or insurers, surveillance framing, whether owners can opt out.\n'
    '- data_governance: the rules and ownership around data rather than the data path itself. Who owns the recorded data, regulation and compliance, disclosure obligations, data retention, consent regimes, standards bodies, liability framed around data or evidence.\n'
    '- none: the comment is CAV-relevant but engages no identifiable subsystem. This is a real and common answer. Use it for comments about autonomy in general, company or market commentary, timelines, safety statistics with no mechanism, and jokes. When genuinely torn between a subsystem and none, choose none.\n'
    '\n'
    'Comment:\n'
    '{text}\n'
    '\n'
    'Return ONLY the label name.'
)
SUBSYSTEM_BLOCK_SHA256 = "63d1e9b6b566290730469c52c9ac543c309fa11a26b966b4baed1a86e581bef0"   # the committed block
SUBSYSTEM_NAMES = list(cfg.PRIMARY_SUBSYSTEMS)  # the seven primary values, in the order of the prompt

RUNS = {    # the two API runs
    "stage2": {"label_key": "pred_class", "no_answer": "refusal", "final": ("ok", "refusal"), "count": "refusals"},
    "subsystem": {"label_key": "subsystem", "no_answer": "unclassified", "final": ("ok", "unclassified"),
                  "count": "unclassified"},
}
REPORT = "Report this message before going further."


# =============================================================================
# small helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


def text_file_sha256(path: Path) -> str:
    """SHA-256 of a text file with LF line endings, as the register records script hashes."""
    return mc.text_sha256(Path(path).read_bytes().decode("utf-8").replace("\r\n", "\n"))


def own_sha256() -> str:
    return text_file_sha256(Path(__file__).resolve())


def check_modules(modules) -> dict:
    out = {}
    for module in modules:
        path = Path(module.__file__).resolve()
        want = MODULES_OF_RECORD.get(path.name)
        got = text_file_sha256(path)
        if got != want:
            stop(f"{path.name} is not the file in the repository at 8d9c0d1 (SHA-256 {got[:16]}..., recorded "
                 f"{(want or 'none')[:16]}...). {REPORT}")
        out[path.name] = got
    return out


def check_file_sha(path: Path, want: str, what: str) -> str:
    if not Path(path).exists():
        stop(f"{what}: not found at {path}")
    got = mc.sha256_file(Path(path))
    if got != want:
        stop(f"{what}: SHA-256 {got[:16]}... is not the {want[:16]}... recorded for it ({path}). {REPORT}")
    return got


def read_csv(path: Path):
    import pandas as pd
    return pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")


def subreddit_name(value) -> str:
    return re.sub(r"^/?r/", "", str(value).strip())


def show_block(name: str, lines: list[str], out_dir: Path = DEPLOY_DIR) -> None:
    mc.show_register_block(Path(out_dir) / f"PASTE_{name}_block.txt", lines)


# =============================================================================
# the subsystem prompt and its answer
# =============================================================================
def committed_subsystem_block() -> str:
    """The prompt of Deviation 13 as committed in docs/analysis_preregistration.md."""
    path = cfg.REPO / "docs" / "analysis_preregistration.md"
    if not path.exists():
        stop(f"{path} not found: the subsystem prompt is checked against the committed pre-registration")
    text = path.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")
    start = text.find("### Deviation 13 — ")
    anchor = text.find("The prompt reads as follows, each label on one line:", max(start, 0))
    a = text.find("```\n", anchor)
    b = text.find("\n```", a + 4)
    if start < 0 or anchor < 0 or a < 0 or b < 0:
        stop(f"the subsystem prompt of Deviation 13 was not found in {path.name}. {REPORT}")
    return text[a + 4:b]


def check_subsystem_prompt() -> str:
    block = committed_subsystem_block()
    if mc.text_sha256(block) != SUBSYSTEM_BLOCK_SHA256 or block.replace("{comment text}", "{text}") != SUBSYSTEM_PROMPT:
        stop(f"the subsystem prompt in this file is not the prompt of Deviation 13 as committed. {REPORT}")
    return SUBSYSTEM_BLOCK_SHA256


def subsystem_prompt(text: str) -> str:
    return SUBSYSTEM_PROMPT.replace("{text}", text)


def parse_subsystem(answer: str):
    """Deviation 13: the cleaned answer if it is one of the seven names; otherwise the one name matched as a whole
    word (an underscore matched by an underscore, one space or one hyphen), once or more; otherwise none."""
    import models_02_claude as mcl
    t = mcl.normalise(answer)
    if not t:
        return None
    if t in SUBSYSTEM_NAMES:
        return t
    hits = [n for n in SUBSYSTEM_NAMES
            if re.search("(?<![a-z0-9_])" + n.replace("_", "[ _-]") + "(?![a-z0-9_])", t)]
    return hits[0] if len(hits) == 1 else None


def build_prompt(kind: str, text: str) -> str:
    import models_02_claude as mcl
    return mcl.build_prompt("domain", text) if kind == "stage2" else subsystem_prompt(text)


def parse(kind: str, answer: str):
    import models_02_claude as mcl
    return mcl.parse_answer(answer, "domain") if kind == "stage2" else parse_subsystem(answer)


# =============================================================================
# the corpus input (--preflight, --prepare)
# =============================================================================
def corpus_input_rows() -> tuple[list, dict]:
    """Every check of rules 1 to 4 that can be made on the PC, and the rows of corpus_input.csv."""
    import pandas as pd
    import analysis_01_sample as sample
    import models_01_prepare as prep
    import models_02_claude as mcl
    import models_04_finetune_cv as ft
    import models_05_evaluate as ev
    import tranche2_common as t2

    info = {"modules_sha256_lf": check_modules([cfg, mc, prep, mcl, ft, ev, sample, t2])}
    print("modules: every module imported is the file in the repository at 8d9c0d1")

    # the evaluation of record: the deployed classifiers, the folds' best epochs, the version that answered
    _, info["evaluation_results_sha256"] = sample.load_evaluation_results()
    if (sample.DEPLOYED_STAGE1, sample.DEPLOYED_STAGE2) != (STAGE1_RUN_OF_RECORD, EVALUATION_RUN):
        stop(f"the evaluation of record does not deploy {STAGE1_RUN_OF_RECORD} and {EVALUATION_RUN}. {REPORT}")
    _, cv, cv_sha = ev.open_run(STAGE1_RUN_OF_RECORD)
    best = [float(x) for x in cv.get("best_epochs") or []]
    if len(best) != cfg.N_FOLDS or statistics.median(best) != FINAL_EPOCHS:
        stop(f"the best epochs of the {STAGE1_RUN_OF_RECORD} folds are {best}; their median is not the "
             f"{FINAL_EPOCHS} of Deviation 13. {REPORT}")
    _, s2, _ = ev.open_run(EVALUATION_RUN)
    answered = s2.get("answered_by") or []
    if len(answered) != 1 or not mcl.same_model(MODEL, answered[0]):
        stop(f"the evaluation run {EVALUATION_RUN} does not name one model version answering under {MODEL}. {REPORT}")
    info["stage1_cross_validation"] = {"predictions_sha256": cv_sha, "best_epochs": best, "median": FINAL_EPOCHS}
    info["evaluation_model_version"] = answered[0]
    info["subsystem_prompt_block_sha256"] = check_subsystem_prompt()
    print(f"record: deployed {STAGE1_RUN_OF_RECORD} and {EVALUATION_RUN}; best epochs {best}, median "
          f"{FINAL_EPOCHS}; evaluation answered by {answered[0]}; the subsystem prompt is Deviation 13's")

    # corpus v2.2 and the frame (R5)
    if not sample.CORPUS.exists():
        stop(f"corpus v2.2 not found at {sample.CORPUS}")
    try:
        corpus = pd.read_parquet(sample.CORPUS, columns=["id", "subreddit", "tier", "clean_body"])
    except Exception as e:                                  # noqa: BLE001 - reported, not handled
        stop(f"corpus v2.2 could not be read with the columns id, subreddit, tier, clean_body ({e})")
    corpus["id"] = corpus["id"].astype(str)
    if len(corpus) != CORPUS_ROWS or corpus["id"].duplicated().any() \
            or mc.ids_sha256(corpus["id"]) != sample.CORPUS_MEMBERSHIP_SHA256:
        stop(f"corpus v2.2: the membership does not match R5 (SHA-256 of the sorted ids). {REPORT}")
    subs = corpus["subreddit"].map(subreddit_name)
    if dict(Counter(subs.str.lower())) != sample.R5_SUBREDDIT_COUNTS \
            or dict(Counter(corpus["tier"].astype(str))) != sample.R5_TIER_COUNTS:
        stop(f"corpus v2.2: the counts by subreddit or by tier differ from R5. {REPORT}")
    if corpus["clean_body"].isna().any() or (corpus["clean_body"].astype(str).str.strip() == "").any():
        stop("corpus v2.2: a comment has no text")
    frame = [x for x in sample.FRAME_IDS.read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n") if x] \
        if sample.FRAME_IDS.exists() else []
    if len(frame) != FRAME_ROWS or len(set(frame)) != FRAME_ROWS or mc.ids_sha256(frame) != sample.FRAME_MEMBERSHIP_SHA256:
        stop(f"draw_frame_ids.txt: the membership does not match R5. {REPORT}")
    info["corpus"] = {"file_sha256": mc.sha256_file(sample.CORPUS), "membership_sha256": sample.CORPUS_MEMBERSHIP_SHA256,
                      "rows": CORPUS_ROWS, "frame_membership_sha256": sample.FRAME_MEMBERSHIP_SHA256}

    # the text (rule 2): the pre-filter preparation, checked against the pre-filter input of record
    text = corpus["clean_body"].astype(str).map(t2.shown_text)
    corpus = corpus.assign(subreddit=subs, text=text).set_index("id")
    pin_sha = check_file_sha(cfg.PREFILTER_INPUT, cfg.PREFILTER_INPUT_SHA256, "prefilter_input.csv (the pre-filter input)")
    pin = read_csv(cfg.PREFILTER_INPUT)
    if list(pin.columns) != ["id", "text"] or sorted(pin["id"]) != sorted(frame) or pin["id"].duplicated().any():
        stop("prefilter_input.csv must hold the 12,166 frame comments with the columns id,text")
    differ = [i for i, t in zip(pin["id"], pin["text"]) if corpus.at[i, "text"] != t]
    if differ:
        stop(f"the text prepared here differs from the pre-filter input of record for {len(differ)} frame comments, "
             f"e.g. {differ[:5]}. {REPORT}")
    info["prefilter_input"] = {"file_sha256": pin_sha, "frame_comments_equal": len(pin)}
    info["comments_with_characters_removed"] = int((corpus["text"] != corpus["clean_body"].astype(str)).sum())

    # the training input (rule 3): text and subreddit of the tranche items, and the letter case of each subreddit
    ft_path = cfg.MODELS_DIR / "finetune_input.csv"
    ft_sha = check_file_sha(ft_path, ev.INPUTS_SHA256["finetune_input.csv"], "finetune_input.csv")
    train = ft.load_items(ft_path, 1)
    if len(train) != STAGE1_TRAINING_ITEMS or not set(train["id"]) <= set(corpus.index):
        stop(f"finetune_input.csv must hold the {STAGE1_TRAINING_ITEMS:,} tranche items with a gold Stage 1 label")
    bad_text = [i for i, t in zip(train["id"], train["text"]) if corpus.at[i, "text"] != t]
    bad_sub = [i for i, s in zip(train["id"], train["subreddit"]) if corpus.at[i, "subreddit"].lower() != s.lower()]
    if bad_text or bad_sub:
        stop(f"finetune_input.csv and the corpus disagree on the text of {len(bad_text)} and the subreddit of "
             f"{len(bad_sub)} tranche items, e.g. {(bad_text + bad_sub)[:5]}. {REPORT}")
    case = {}
    for s in train["subreddit"]:
        case.setdefault(s.lower(), set()).add(s)
    if any(len(v) != 1 for v in case.values()):
        stop(f"finetune_input.csv writes a subreddit in more than one letter case: {case}. {REPORT}")
    case = {k: next(iter(v)) for k, v in case.items()}
    tier12 = corpus["tier"].isin(TIERS_ANALYSED)
    lower = corpus["subreddit"].str.lower()
    if not set(lower[tier12]) <= set(case):
        stop(f"a Tier 1 or Tier 2 subreddit is not in the training input. {REPORT}")
    written = corpus["subreddit"].where(~tier12, lower.map(case))
    info["finetune_input"] = {"file_sha256": ft_sha, "tranche_items_equal": len(train)}
    info["subreddit_letter_case"] = {"training_input": dict(sorted(case.items())),
                                     "corpus_agrees": bool((written == corpus["subreddit"]).all())}
    rows = [[i, corpus.at[i, "tier"], written[i], corpus.at[i, "text"]] for i in sorted(corpus.index)]
    print(f"text: the prepared text equals the pre-filter input for all {len(pin):,} frame comments and "
          f"finetune_input.csv for all {len(train):,} tranche items; subreddit letter case as in the training input "
          f"({'the same as' if info['subreddit_letter_case']['corpus_agrees'] else 'not the same as'} the corpus)")
    return rows, info


def preflight() -> None:
    me = own_sha256()
    print(f"Corpus runs (Deviation 13): preflight, before the commit\nthis script: models_06_deploy.py SHA-256 {me}")
    rows, _ = corpus_input_rows()
    print(f"\nPREFLIGHT PASSED: {len(rows):,} comments would be written to the corpus input. No model was run, "
          f"nothing was sent and nothing was written.")


def prepare() -> None:
    me = own_sha256()
    print(f"Corpus runs (Deviation 13): the corpus input\nthis script: models_06_deploy.py SHA-256 {me}")
    rows, info = corpus_input_rows()
    header = ["id", "tier", "subreddit", "text"]
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DEPLOY_DIR / "corpus_input.csv.new"
    sha = mc.write_rows_csv(tmp, header, rows)
    back = read_csv(tmp)
    if list(back.columns) != header or back.values.tolist() != rows:
        tmp.unlink()
        stop(f"corpus_input.csv does not read back as written. Nothing was kept. {REPORT}")
    if CORPUS_INPUT.exists():
        if mc.sha256_file(CORPUS_INPUT) != sha:
            tmp.unlink()
            stop(f"{CORPUS_INPUT} exists and differs from the file this step writes now. {REPORT}")
        tmp.unlink()
        print("corpus_input.csv was already written; it is unchanged")
    else:
        mc.replace_patiently(tmp, CORPUS_INPUT)
    manifest = {"created": mc.now_iso(), "specification": "Deviation 13, docs/analysis_preregistration.md",
                "script": {"file": "models_06_deploy.py", "sha256_lf": me}, **info, "rows": len(rows),
                "output": {"file": "data/models/deploy/corpus_input.csv", "sha256": sha},
                "versions": mc.versions("pandas", "numpy", "pyarrow")}
    old = mc.read_json(CORPUS_INPUT_MANIFEST) if CORPUS_INPUT_MANIFEST.exists() else {}
    if (old.get("script") or {}).get("sha256_lf") == me and (old.get("output") or {}).get("sha256") == sha:
        manifest = old                                      # the manifest of the first run is kept as written
    else:
        mc.write_json(CORPUS_INPUT_MANIFEST, manifest)
    man_sha = mc.sha256_file(CORPUS_INPUT_MANIFEST)
    print(f"\nwritten: {CORPUS_INPUT} ({len(rows):,} comments, SHA-256 {sha})")
    show_block("prepare", [
        f"- `models_06_deploy.py` (SHA-256 `{me}`) run {manifest['created']} with `--prepare`: corpus v2.2 and "
        f"the frame matched R5; the prepared text equals the pre-filter input of record for all "
        f"{info['prefilter_input']['frame_comments_equal']:,} frame comments and `finetune_input.csv` for all "
        f"{info['finetune_input']['tranche_items_equal']:,} tranche items.",
        f"- `data/models/deploy/corpus_input.csv` ({len(rows):,} comments) SHA-256 `{sha}`; "
        f"`corpus_input_manifest.json` `{man_sha}`. The corpus writes every Tier 1 and 2 subreddit "
        + ("in the letter case of the training input." if info["subreddit_letter_case"]["corpus_agrees"] else
           "not always in the letter case of the training input, which the Stage 1 input uses (rule 3).")
        + f" Python {manifest['versions']['python']}, pandas {manifest['versions']['pandas']}, NumPy "
          f"{manifest['versions']['numpy']}, PyArrow {manifest['versions']['pyarrow']}.",
    ])


# =============================================================================
# Stage 1: final retraining and the corpus run (--stage1, on a GPU)
# =============================================================================
def final_training_args(output_dir: str, seed: int):
    """The TrainingArguments of the cross-validation runs, with no evaluation and no checkpoint."""
    from transformers import TrainingArguments
    f = cfg.FINETUNE
    return TrainingArguments(
        output_dir=output_dir, eval_strategy="no", save_strategy="no", load_best_model_at_end=False,
        learning_rate=f["learning_rate"], per_device_train_batch_size=f["batch_size"],
        per_device_eval_batch_size=f["eval_batch_size"], num_train_epochs=f["max_epochs"],
        weight_decay=f["weight_decay"], adam_beta1=f["adam_betas"][0], adam_beta2=f["adam_betas"][1],
        adam_epsilon=f["adam_epsilon"], max_grad_norm=f["max_grad_norm"], optim="adamw_torch",
        warmup_steps=0, lr_scheduler_type="linear", logging_steps=10, report_to="none",
        seed=seed, fp16=False, bf16=False, disable_tqdm=True)


def check_training_args(mine, reference) -> None:
    a, b = mine.to_dict(), reference.to_dict()
    differ = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    extra = [k for k in differ if k not in FINAL_TRAINING_DIFFERENCES]
    if extra:
        stop(f"the final retraining's settings differ from those of the cross-validation runs in {extra}. {REPORT}")


def stop_after_epochs(epochs: int):
    from transformers import TrainerCallback

    class StopAfterEpochs(TrainerCallback):
        def on_epoch_end(self, args, state, control, **kwargs):
            if state.epoch is not None and state.epoch >= epochs - 1e-9:
                control.should_training_stop = True
            return control

    return StopAfterEpochs()


def stage1(args) -> None:
    mc.check_run_libraries(["transformers", "scikit-learn"])
    import numpy as np
    import torch
    import transformers
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, set_seed
    from transformers.trainer_callback import PrinterCallback, ProgressCallback
    import models_04_finetune_cv as ft

    me = own_sha256()
    print(f"Corpus runs (Deviation 13): Stage 1, final retraining and the corpus run\n"
          f"this script: models_06_deploy.py SHA-256 {me}")
    modules = check_modules([cfg, mc, ft])
    man_path, train_path, corpus_path = Path(args.input_manifest), Path(args.train_input), Path(args.corpus_input)
    if not man_path.exists():
        stop(f"{man_path} not found (the --prepare step writes corpus_input_manifest.json)")
    man = mc.read_json(man_path)
    if (man.get("script") or {}).get("sha256_lf") != me:
        stop(f"{man_path.name} was written by another version of this file. {REPORT}")
    man_sha = mc.sha256_file(man_path)
    train_sha = check_file_sha(train_path, man["finetune_input"]["file_sha256"], "finetune_input.csv")
    corpus_sha = check_file_sha(corpus_path, man["output"]["sha256"], "corpus_input.csv")
    out_dir = Path(args.out_dir)
    pred_path, out_man_path = out_dir / STAGE1_PREDICTIONS_NAME, out_dir / STAGE1_MANIFEST_NAME
    if out_man_path.exists():
        stop(f"{out_man_path} exists: the Stage 1 corpus run has been made. It is made once.")
    if pred_path.exists():
        stop(f"{pred_path} exists without its manifest: a run stopped while its outputs were being moved into place. "
             f"Delete {pred_path.name} from {out_dir} and give the command again. {REPORT}")
    train = ft.load_items(train_path, 1)
    corpus = read_csv(corpus_path)
    if len(train) != STAGE1_TRAINING_ITEMS:
        stop(f"the training input holds {len(train)} items with a gold Stage 1 label, not {STAGE1_TRAINING_ITEMS}")
    if list(corpus.columns) != ["id", "tier", "subreddit", "text"] or len(corpus) != CORPUS_ROWS \
            or corpus["id"].duplicated().any():
        stop(f"corpus_input.csv must hold the {CORPUS_ROWS:,} comments with the columns id,tier,subreddit,text")
    if args.test_model_dir:
        repo, revision = args.test_model_dir, None
        print("TEST MODEL: not the run of record")
    else:
        repo, revision = cfg.CHECKPOINTS[STAGE1_MODEL]["repo"], cfg.CHECKPOINTS[STAGE1_MODEL]["commit"]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"training items {len(train):,} | corpus comments {len(corpus):,} | model {repo} @ {revision} | device "
          f"{device} | torch {torch.__version__}, transformers {transformers.__version__}")
    if device == "cpu":
        print("NOTE: no GPU found. This works on a CPU but takes much longer.")

    load = {"revision": revision} if revision else {}
    tok = AutoTokenizer.from_pretrained(repo, **load)
    train, spaced_train = ft.space_out_special_strings(tok, train)
    corpus, spaced_corpus = ft.space_out_special_strings(tok, corpus)
    lab2id = {label: j for j, label in enumerate(STAGE1_LABELS)}
    set_seed(cfg.SEED)
    model = AutoModelForSequenceClassification.from_pretrained(
        repo, num_labels=len(STAGE1_LABELS), id2label=dict(enumerate(STAGE1_LABELS)), label2id=lab2id,
        dtype=torch.float32, **load)
    seen = getattr(model.config, "_commit_hash", None)
    if revision and seen and seen != revision:
        stop(f"the loaded model reports commit {seen}, not the pinned {revision}")
    work = Path(args.work_dir)
    work.mkdir(parents=True, exist_ok=True)
    targs = final_training_args(str(work / "final"), cfg.SEED)
    check_training_args(targs, ft.training_args(str(work / "final"), cfg.SEED))
    trainer = Trainer(model=model, args=targs,
                      train_dataset=ft.EncodedDataset(ft.encode(tok, train, 1, False), [lab2id[x] for x in train["label"]]),
                      processing_class=tok, callbacks=[stop_after_epochs(FINAL_EPOCHS)])
    trainer.remove_callback(PrinterCallback)              # no loss is printed
    trainer.remove_callback(ProgressCallback)
    t0 = time.time()
    trainer.train()
    steps_per_epoch = math.ceil(len(train) / cfg.FINETUNE["batch_size"])
    lr = float(trainer.lr_scheduler.get_last_lr()[0])
    lr_expected = cfg.FINETUNE["learning_rate"] * (1 - FINAL_EPOCHS / cfg.FINETUNE["max_epochs"])
    if trainer.state.global_step != FINAL_EPOCHS * steps_per_epoch or abs((trainer.state.epoch or 0) - FINAL_EPOCHS) > 1e-6 \
            or abs(lr - lr_expected) > 1e-12:
        stop(f"training did not stop at the end of epoch {FINAL_EPOCHS} of a {cfg.FINETUNE['max_epochs']}-epoch "
             f"schedule (steps {trainer.state.global_step}, epoch {trainer.state.epoch}, learning rate {lr}). {REPORT}")
    minutes_training = round((time.time() - t0) / 60, 2)
    print(f"trained: {FINAL_EPOCHS} epochs, {trainer.state.global_step} steps, {minutes_training} min; now the corpus run")
    logits = trainer.predict(ft.EncodedDataset(ft.encode(tok, corpus, 1, False))).predictions
    z = logits - logits.max(axis=1, keepdims=True)
    prob = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
    pred = np.array(STAGE1_LABELS)[prob.argmax(axis=1)]
    rows = [[i, p] + [f"{v:.6f}" for v in pr] for i, p, pr in zip(corpus["id"], pred, prob)]
    out_dir.mkdir(parents=True, exist_ok=True)
    part = out_dir / (STAGE1_PREDICTIONS_NAME + ".part")
    sha = mc.write_rows_csv(part, ["id", "pred"] + [f"p_{label}" for label in STAGE1_LABELS], rows)
    versions = {**mc.versions("numpy", "sklearn", "accelerate"), "torch": torch.__version__,
                "transformers": transformers.__version__}
    manifest = {
        "created": mc.now_iso(),
        "specification": "Deviation 13; FINAL_RETRAINING in models_config.py; models_04_finetune_cv.py",
        "script": {"file": "models_06_deploy.py", "sha256_lf": me}, "modules_sha256_lf": modules,
        "model": repo, "model_commit_pinned": revision, "model_commit_loaded": seen,
        "test_model": bool(args.test_model_dir), "labels": STAGE1_LABELS,
        "input_format": f"pair ({cfg.STAGE1_SUBREDDIT_SEGMENT!r}, comment), only the comment truncated",
        "settings": cfg.FINETUNE, "seed": cfg.SEED, "epochs_trained": FINAL_EPOCHS,
        "schedule_epochs": cfg.FINETUNE["max_epochs"], "training_items": len(train),
        "steps": trainer.state.global_step, "learning_rate_after_last_step": lr,
        "decision_rule": "arg-max of the two probabilities, as in the cross-validation runs (an exact tie is N)",
        "special_strings_spaced_out_ids": {"training": spaced_train, "corpus": spaced_corpus},
        "inputs": {"finetune_input.csv": train_sha, "corpus_input.csv": corpus_sha, "corpus_input_manifest.json": man_sha},
        "predictions": {"file": STAGE1_PREDICTIONS_NAME, "sha256": sha, "comments": len(rows)},
        "device": device, "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "minutes": round((time.time() - t0) / 60, 2), "versions": versions,
    }
    man_part = out_dir / (STAGE1_MANIFEST_NAME + ".part")
    mc.write_json(man_part, manifest)
    mc.replace_patiently(part, pred_path)                   # the predictions first, the manifest last
    mc.replace_patiently(man_part, out_man_path)
    msha = mc.sha256_file(out_man_path)
    print(f"\nwritten: {pred_path} ({len(rows):,} comments, SHA-256 {sha}) and {out_man_path.name}")
    show_block("stage1", [
        f"- `models_06_deploy.py` (SHA-256 `{me}`) run {manifest['created']} with `--stage1` on "
        f"{manifest['gpu'] or device}: `{repo}` at `{revision}` retrained on {len(train):,} items for {FINAL_EPOCHS} "
        f"epochs of a {cfg.FINETUNE['max_epochs']}-epoch schedule ({trainer.state.global_step} steps; learning rate "
        f"{lr:.3g} after the last step), seed {cfg.SEED}; Python {versions['python']}, torch {torch.__version__}, "
        f"transformers {transformers.__version__}, scikit-learn {versions.get('sklearn')}, accelerate "
        f"{versions.get('accelerate')}, NumPy {versions.get('numpy')}.",
        f"- Inputs: `finetune_input.csv` SHA-256 `{train_sha}`; `corpus_input.csv` `{corpus_sha}`.",
        f"- Output: `{STAGE1_PREDICTIONS_NAME}` ({len(rows):,} comments) SHA-256 `{sha}`; `{STAGE1_MANIFEST_NAME}` "
        f"`{msha}`. Comments with a special-token string spaced out: {len(spaced_corpus)} "
        f"({len(spaced_train)} training items).",
    ], out_dir)


# =============================================================================
# the API runs: inputs (--check-connection, --stage2, --subsystem)
# =============================================================================
def api_modules():
    import models_01_prepare as prep
    import models_02_claude as mcl
    import models_05_evaluate as ev
    check_modules([cfg, mc, prep, mcl, ev])
    return mcl, ev


def evaluation_version(ev) -> str:
    _, man, _ = ev.open_run(EVALUATION_RUN)
    answered = man.get("answered_by") or []
    if len(answered) != 1:
        stop(f"the evaluation run {EVALUATION_RUN} does not name one model version. {REPORT}")
    return answered[0]


def load_corpus_runs() -> dict:
    """corpus_input.csv and the Stage 1 predictions, each checked against the manifest of the step that wrote it."""
    me = own_sha256()
    if not CORPUS_INPUT_MANIFEST.exists():
        stop(f"{CORPUS_INPUT_MANIFEST} not found: run --prepare first")
    man = mc.read_json(CORPUS_INPUT_MANIFEST)
    if (man.get("script") or {}).get("sha256_lf") != me:
        stop(f"{CORPUS_INPUT_MANIFEST.name} was written by another version of this file. {REPORT}")
    corpus_sha = check_file_sha(CORPUS_INPUT, man["output"]["sha256"], "corpus_input.csv")
    corpus = read_csv(CORPUS_INPUT)
    s1_man_path, s1_path = DEPLOY_DIR / STAGE1_MANIFEST_NAME, DEPLOY_DIR / STAGE1_PREDICTIONS_NAME
    if not s1_man_path.exists() or not s1_path.exists():
        stop(f"the Stage 1 corpus run's files were not found in {DEPLOY_DIR} ({STAGE1_PREDICTIONS_NAME}, "
             f"{STAGE1_MANIFEST_NAME}): copy them there from the --stage1 output folder")
    s1 = mc.read_json(s1_man_path)
    if (s1.get("script") or {}).get("sha256_lf") != me:
        stop(f"{STAGE1_MANIFEST_NAME} was written by another version of this file. {REPORT}")
    if s1.get("test_model") and not ACCEPT_TEST_MODEL:
        stop(f"{STAGE1_MANIFEST_NAME} records a test model, not the run of record. {REPORT}")
    if (s1.get("inputs") or {}).get("corpus_input.csv") != corpus_sha \
            or (s1.get("inputs") or {}).get("finetune_input.csv") != man["finetune_input"]["file_sha256"]:
        stop(f"the Stage 1 corpus run was made on other inputs than these. {REPORT}")
    s1_sha = check_file_sha(s1_path, s1["predictions"]["sha256"], STAGE1_PREDICTIONS_NAME)
    pred = read_csv(s1_path)
    if list(pred.columns) != ["id", "pred", "p_N", "p_Y"] or pred["id"].tolist() != corpus["id"].tolist() \
            or not set(pred["pred"]) <= set(STAGE1_LABELS):
        stop(f"{STAGE1_PREDICTIONS_NAME} must give N or Y for each comment of corpus_input.csv, in its order")
    corpus = corpus.assign(stage1=pred["pred"].to_numpy()).set_index("id")
    return {"corpus": corpus, "shas": {"corpus_input.csv": corpus_sha, STAGE1_PREDICTIONS_NAME: s1_sha},
            "finetune_input_sha256": man["finetune_input"]["file_sha256"]}


def stage2_items(corpus) -> list:
    sel = corpus[corpus["tier"].isin(TIERS_ANALYSED) & (corpus["stage1"] == "Y")]
    return [(i, sel.at[i, "text"]) for i in sorted(sel.index)]


# =============================================================================
# the API runs: errors, logs and spend
# =============================================================================
def is_transport(e: Exception) -> bool:
    """A connection error, a timeout (408), status 409 or 429, or a status of 500 or above (Deviation 13; the client
    retries all of these)."""
    try:
        import anthropic
    except ImportError:
        return False
    if isinstance(e, anthropic.APIConnectionError):         # includes APITimeoutError
        return True
    code = getattr(e, "status_code", None) if isinstance(e, anthropic.APIStatusError) else None
    return code is not None and (code in (408, 409, 429) or code >= 500)


def is_rejection(e: Exception) -> bool:
    """Any other error from the API (Deviation 13)."""
    try:
        import anthropic
    except ImportError:
        return False
    return isinstance(e, anthropic.APIStatusError) and not is_transport(e)


def explain(e: Exception) -> str:
    name = type(e).__name__
    again = "Give the same command again later: finished comments are kept."
    hints = {"AuthenticationError": "the API key was refused. Check ANTHROPIC_API_KEY.",
             "PermissionDeniedError": f"the API key may not use this model. {REPORT}",
             "NotFoundError": f"the model identifier was not found; do not change it. {REPORT}",
             "RateLimitError": "rate limit or spending limit reached after all retries. Wait a few minutes, then "
                               "give the same command again: finished comments are kept.",
             "APIConnectionError": "no connection after all retries. " + again,
             "APITimeoutError": "the API timed out after all retries. " + again,
             "InternalServerError": "the API was unavailable after all retries. " + again,
             "ServiceUnavailableError": "the API was unavailable after all retries. " + again,
             "OverloadedError": "the API was overloaded after all retries. " + again,
             "DeadlineExceededError": "the API timed out after all retries. " + again}
    if "credit balance" in str(e).lower():
        hint = "the account's credit balance is too low. Add credit in the Anthropic Console, then g" + again[1:]
    elif "temperature" in str(e).lower():
        hint = f"the API refused temperature 0; do not change anything. {REPORT}"
    else:
        hint = hints.get(name, REPORT)
    return f"{name}: {e}\n  {hint}"


def log_path(kind: str) -> Path:
    return DEPLOY_DIR / f"{kind}_log.jsonl"


def read_log(kind: str) -> tuple[dict, list, list]:
    """The finished comments; the other records in log order (partial, interrupted, rejected, set aside), each
    holding every answered call of its comment so far; and the estimate records of the subsystem run. A torn last
    line is ignored."""
    done, others, estimates = {}, [], []
    path = log_path(kind)
    if not path.exists():
        return done, others, estimates
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            status = rec.get("status")
            if status in RUNS[kind]["final"] and rec.get("id"):
                done[rec["id"]] = rec
            elif status in ("partial", "interrupted", "rejected", "set_aside") and rec.get("id"):
                others.append(rec)
            elif status == "estimate":
                estimates.append(rec)
    return done, others, estimates


def read_connection_log() -> list:
    out = []
    if CONNECTION_LOG.exists():
        with open(CONNECTION_LOG, encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def deployment_spend(mcl) -> float:
    """Measured spend: every logged call of both runs and of this file's connection checks (Deviation 13)."""
    total = 0.0
    for kind in RUNS:
        done, others, _ = read_log(kind)
        total += sum(mcl.call_cost(MODEL, x) for x in mcl.unique_calls([*done.values(), *others]))
    for x in read_connection_log():
        total += mcl.call_cost(MODEL, x)
    return total


def passing_check(version: str) -> dict | None:
    """The latest connection check in which both prompts passed under the committed settings and client."""
    last = None
    checks = {}
    for x in read_connection_log():
        if x.get("passed") is True and x.get("settings") == cfg.CLAUDE_SETTINGS and x.get("requested") == MODEL \
                and x.get("sdk") == cfg.ANTHROPIC_SDK_VERSION and x.get("model") == version:
            checks.setdefault(x.get("check_id"), {})[x.get("purpose")] = x
    for check_id, both in checks.items():
        if set(both) == set(RUNS):
            last = both
    return last


# =============================================================================
# the API runs: one run
# =============================================================================
class RunLock:
    """data/models/deploy/api_run.lock, made with O_EXCL: a second API step cannot start while one is under way."""
    path = DEPLOY_DIR / "api_run.lock"

    def __enter__(self):
        RunLock.path = DEPLOY_DIR / "api_run.lock"
        DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
        try:
            fd = os.open(RunLock.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            stop(f"another API step may be under way ({RunLock.path} exists). Give one command at a time. If no other "
                 f"step is running (for example after a power cut), delete that file and give the command again.")
        with os.fdopen(fd, "w") as f:
            f.write(f"{os.getpid()} {mc.now_iso()}\n")
        return self

    def __exit__(self, *exc):
        try:
            RunLock.path.unlink()
        except FileNotFoundError:
            pass
        return False


def run_fingerprint(kind: str, inputs: dict) -> str:
    return mc.text_sha256(json.dumps({
        "kind": kind, "model": MODEL, "settings": cfg.CLAUDE_SETTINGS, "retries": cfg.NO_CLASS_RETRIES,
        "template": cfg.PROMPT_TEMPLATE if kind == "stage2" else SUBSYSTEM_PROMPT,
        "labels": cfg.DOMAIN_LABELS if kind == "stage2" else SUBSYSTEM_NAMES, "inputs": inputs}, sort_keys=True))


def api_run(kind: str, mcl, client, items: list, inputs: dict, spend: dict, ceiling: float, version: str) -> None:
    """Every comment of the run, resumed from the log; returns when each has a final record."""
    spec = RUNS[kind]
    path = log_path(kind)
    fingerprint = run_fingerprint(kind, inputs)
    done, others, _ = read_log(kind)
    if any(r.get("fingerprint") != fingerprint for r in [*done.values(), *others]):
        stop(f"{path.name} holds comments from a different input, model or wording. {REPORT}")
    text = dict(items)
    if not set(done) | {r["id"] for r in others} <= set(text):
        stop(f"{path.name} holds comments that are not in this run. {REPORT}")
    answered = {x["model"] for x in mcl.unique_calls([*done.values(), *others])}
    if answered - {version}:
        stop(f"MODEL_MISMATCH: {path.name} holds answers from {sorted(answered)}, not {version}. {REPORT}")
    last_attempts, rejected, history = {}, [], {}
    for r in others:                                        # in log order: the last record holds every call
        last_attempts[r["id"]] = r.get("attempts", [])
        if r["status"] in ("rejected", "set_aside"):
            history.setdefault(r["id"], []).append(r)
            if r["id"] not in rejected:
                rejected.append(r["id"])
    pending = [i for i in rejected if i not in done]
    todo = [i for i, _ in items if i not in done and i not in pending]
    print(f"\n{kind}: model {MODEL} | {len(items):,} comments | {len(done):,} already done, {len(pending)} rejected "
          f"at the last start, {len(todo):,} to do", flush=True)
    if path.exists() and path.stat().st_size:               # close a line torn by an interruption
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            torn = f.read(1) != b"\n"
        if torn:
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write("\n")
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    lock = threading.Lock()
    counter = {"n": len(done), "no_answer": sum(r["status"] == spec["no_answer"] for r in done.values())}
    window = {"set_aside": [], "needed": 0, "count": 0, "stopping": False}
    started, total = time.time(), len(items)

    def append(rec: dict) -> None:
        mcl.append_line(path, {"id": rec.pop("id"), "kind": kind, "fingerprint": fingerprint, **rec})

    def record_set_aside() -> None:                         # under the lock
        for j in window["set_aside"]:
            rec = {"id": j, "kind": kind, "fingerprint": fingerprint, "status": spec["no_answer"],
                   spec["label_key"]: "", "attempts": last_attempts.get(j, []),
                   "reason": f"set aside after a second API rejection; the next {window['needed']} comments were "
                             f"answered with no API error (Deviation 13)",
                   "rejections": [{k: r.get(k) for k in ("status", "at", "error", "status_code")} for r in history.get(j, [])]}
            mcl.append_line(path, rec)
            done[j] = rec
            counter["n"] += 1
            counter["no_answer"] += 1
        window["set_aside"] = []

    def work(item_id: str, sent_first: bool = False) -> str:
        prompt = build_prompt(kind, text[item_id])
        attempts, label = [dict(a) for a in last_attempts.get(item_id, [])], None
        for a in attempts:
            a["parsed"] = parse(kind, a["text"])
            if a["parsed"] is not None:
                label = a["parsed"]
                break
        try:
            while label is None and len(attempts) < 1 + cfg.NO_CLASS_RETRIES:
                a = mcl.call(client, MODEL, prompt)
                attempts.append(a)
                with lock:
                    if not mcl.same_model(MODEL, a["model"]) or a["model"] != version:
                        raise RuntimeError(f"MODEL_MISMATCH: asked for {MODEL}, the API answered with "
                                           f"{a['model'] or 'no model name'}; the evaluation run was answered by {version}")
                    spend["usd"] += mcl.call_cost(MODEL, a)
                    if spend["usd"] >= ceiling:
                        raise RuntimeError(f"SPEND_CEILING: the measured spend of both runs, US${spend['usd']:.4f}, has "
                                           f"reached the ceiling of US${ceiling:.2f}: the run halts (Deviation 13)")
                a["parsed"] = parse(kind, a["text"])
                if a["parsed"] is not None:
                    label = a["parsed"]
                elif len(attempts) < 1 + cfg.NO_CLASS_RETRIES:      # log the answered call before the retry
                    with lock:
                        append({"id": item_id, "status": "partial", "attempts": attempts})
        except Exception as e:
            rejection = is_rejection(e)
            with lock:
                if not (sent_first and rejection):
                    window["stopping"] = True
                if rejection:
                    rec = {"id": item_id, "status": "set_aside" if sent_first else "rejected", "at": mc.now_iso(),
                           "error": type(e).__name__, "status_code": getattr(e, "status_code", None),
                           "message": str(e)[:500], "attempts": attempts}
                    history.setdefault(item_id, []).append(dict(rec))
                    last_attempts[item_id] = attempts
                    append(rec)
                elif attempts:
                    last_attempts[item_id] = attempts
                    append({"id": item_id, "status": "interrupted", "attempts": attempts})
            if sent_first and rejection:
                return "set_aside"
            raise
        rec = {"id": item_id, "kind": kind, "fingerprint": fingerprint, "prompt_sha256": mc.text_sha256(prompt),
               "status": "ok" if label else spec["no_answer"], spec["label_key"]: label or "", "attempts": attempts}
        with lock:
            mcl.append_line(path, rec)
            done[item_id] = rec
            counter["n"] += 1
            counter["no_answer"] += label is None
            if not sent_first and window["set_aside"] and not window["stopping"]:
                window["count"] += 1
                if window["count"] >= window["needed"]:
                    record_set_aside()
            if counter["n"] % 250 == 0 or counter["n"] == total:
                rate = (counter["n"] - (total - len(todo) - len(pending))) / max(time.time() - started, 1e-9)
                left = (total - counter["n"]) / rate / 60 if rate > 0 else float("nan")
                print(f"  {counter['n']:,}/{total:,} comments | spend US${spend['usd']:.2f} | ~{left:4.1f} min left",
                      flush=True)
        return "done"

    def halt(e: Exception) -> None:
        kept = f"{counter['n']:,} of {total:,} comments are finished and kept."
        if str(e).startswith("MODEL_MISMATCH"):
            stop(f"{kind}: {e}\n  {kept} {REPORT}")
        if str(e).startswith("SPEND_CEILING"):
            stop(f"{kind}: {e}\n  {kept} Only the ceiling may change: record a new ceiling and the reason in the "
                 f"register, then give the same command with --ceiling <new ceiling>. {REPORT}")
        if is_rejection(e):
            systemic = type(e).__name__ in ("AuthenticationError", "PermissionDeniedError", "NotFoundError") \
                or "credit balance" in str(e).lower()
            stop(f"{kind} stopped: the API rejected a comment.\n  "
                 + (explain(e) if systemic else f"{type(e).__name__}: {e}")
                 + f"\n  {kept} The comment is recorded as rejected. When the same command is given again it is sent "
                   f"first, alone; if it is rejected again it is set aside (Deviation 13)."
                 + (" Fix the cause above first." if systemic else ""))
        stop(f"{kind} stopped. {kept}\n  " + explain(e))

    try:                                                    # rejected comments are sent first, one at a time
        for item_id in pending:
            if work(item_id, sent_first=True) == "set_aside":
                window["set_aside"].append(item_id)
    except KeyboardInterrupt:
        stop(f"{kind} stopped by the user. {counter['n']:,} of {total:,} comments are finished and kept.")
    except Exception as e:                                  # noqa: BLE001 - reported to the user
        halt(e)
    if window["set_aside"]:
        window["needed"] = min(WINDOW, len(todo))
        if window["needed"] == 0:
            stop(f"{kind}: {', '.join(window['set_aside'])} rejected again and set aside, and no comment is left to "
                 f"answer, so the rule of Deviation 13 cannot be applied. {REPORT}")
        print(f"  set aside after a second rejection: {', '.join(window['set_aside'])}; recorded as "
              f"{spec['no_answer']} once the next {window['needed']} comments are answered with no API error", flush=True)
    if todo:
        first_error, interrupted = None, False
        with ThreadPoolExecutor(max_workers=cfg.CLAUDE_CONCURRENCY) as pool:
            futures = [pool.submit(work, i) for i in todo]
            try:
                while True:                                 # short waits, so that Ctrl+C is seen on Windows too
                    finished, pending_f = wait(futures, timeout=1, return_when=FIRST_EXCEPTION)
                    errors = [f.exception() for f in finished if f.exception() is not None]
                    if errors or not pending_f:
                        break
            except KeyboardInterrupt:
                errors, interrupted = [], True
            if errors or interrupted:
                with lock:
                    window["stopping"] = True
                first_error = errors[0] if errors else None
                for f in futures:
                    f.cancel()                              # calls under way finish before the stop
        if interrupted:
            stop(f"{kind} stopped by the user. {counter['n']:,} of {total:,} comments are finished and kept; give "
                 f"the same command again to continue.")
        if first_error is not None:
            halt(first_error)
    if window["set_aside"]:
        stop(f"{kind}: comments set aside were not recorded. {REPORT}")


def assemble(kind: str, mcl, items: list, inputs: dict, ceiling: float, version: str, me: str,
             validation_only: set = frozenset()) -> dict:
    """The predictions file and the manifest, from the log as written. Given again after the run is complete, it
    returns the manifest already written (the log is unchanged), so that the hashes recorded stay the same."""
    spec = RUNS[kind]
    pred_path, man_path = DEPLOY_DIR / f"{kind}_predictions.csv", DEPLOY_DIR / f"{kind}_manifest.json"
    if man_path.exists() and pred_path.exists():
        old = mc.read_json(man_path)
        if (old.get("script") or {}).get("sha256_lf") == me \
                and (old.get("log") or {}).get("sha256") == mc.sha256_file(log_path(kind)) \
                and (old.get("predictions") or {}).get("sha256") == mc.sha256_file(pred_path):
            old["manifest_sha256"] = mc.sha256_file(man_path)
            return old
    done, others, estimates = read_log(kind)
    ids = [i for i, _ in items]
    missing = [i for i in ids if i not in done]
    if missing:
        stop(f"{kind}: {len(missing)} comments have no result")
    rejections = {}
    for r in others:
        if r["status"] in ("rejected", "set_aside"):
            rejections[r["id"]] = rejections.get(r["id"], 0) + 1
    header = ["id", spec["label_key"], "status", "attempts", "input_tokens", "output_tokens", "answer_1", "answer_2",
              "request_ids", "api_rejections"] + (["validation_only"] if kind == "subsystem" else [])
    rows = []
    for i in ids:
        r = done[i]
        a = r["attempts"]
        rows.append([i, r[spec["label_key"]], r["status"], len(a), sum(x["input_tokens"] for x in a),
                     sum(x["output_tokens"] for x in a), a[0]["text"] if a else "", a[1]["text"] if len(a) > 1 else "",
                     ";".join(str(x["request_id"]) for x in a), rejections.get(i, 0)]
                    + (["yes" if i in validation_only else ""] if kind == "subsystem" else []))
    every_call = mcl.unique_calls([done[i] for i in ids] + others)
    tokens_in = sum(x["input_tokens"] for x in every_call)
    tokens_out = sum(x["output_tokens"] for x in every_call)
    times = sorted(x["at"] for x in every_call)
    answered = sorted({x["model"] for x in every_call})
    cost = sum(mcl.call_cost(MODEL, x) for x in every_call)
    set_aside = [i for i in ids if done[i].get("reason")]
    pred_sha = mc.write_rows_csv(pred_path, header, rows)
    stop_reasons = {}
    for x in every_call:
        stop_reasons[str(x["stop_reason"])] = stop_reasons.get(str(x["stop_reason"]), 0) + 1
    manifest = {
        "created": mc.now_iso(), "specification": "Deviation 13, docs/analysis_preregistration.md",
        "script": {"file": "models_06_deploy.py", "sha256_lf": me}, "run": kind, "model": MODEL,
        "answered_by": answered, "evaluation_run_answered_by": version,
        "prompt_template": cfg.PROMPT_TEMPLATE if kind == "stage2" else SUBSYSTEM_PROMPT,
        "labels": cfg.DOMAIN_LABELS if kind == "stage2" else SUBSYSTEM_NAMES,
        "settings": cfg.CLAUDE_SETTINGS, "no_class_retries": cfg.NO_CLASS_RETRIES,
        "concurrency": cfg.CLAUDE_CONCURRENCY, "timeout_seconds": cfg.CLAUDE_TIMEOUT_SECONDS,
        "transport_retries": cfg.CLAUDE_TRANSPORT_RETRIES, "stop_reasons": stop_reasons,
        "comments": len(rows), "validation_only": len(validation_only), "calls": len(every_call),
        spec["no_answer"]: sum(1 for r in rows if r[2] == spec["no_answer"]),
        "set_aside_after_two_rejections": set_aside,
        "comments_with_api_rejections": sorted(rejections), "tokens": {"input": tokens_in, "output": tokens_out},
        "prices_usd_per_mtok": cfg.CLAUDE_PRICES_USD_PER_MTOK[MODEL], "cost_usd": round(cost, 6),
        "spend_both_runs_usd": round(deployment_spend(mcl), 6), "ceiling_usd": ceiling,
        "estimate_before_run": estimates[0] if estimates else None,
        "access_window": {"first_call": times[0] if times else None, "last_call": times[-1] if times else None},
        "inputs": inputs,
        "predictions": {"file": f"data/models/deploy/{pred_path.name}", "sha256": pred_sha},
        "log": {"file": f"data/models/deploy/{log_path(kind).name}", "sha256": mc.sha256_file(log_path(kind))},
        "versions": mc.versions("anthropic", "pandas"),
    }
    mc.write_json(man_path, manifest)
    manifest["manifest_sha256"] = mc.sha256_file(man_path)
    return manifest


# =============================================================================
# the API steps
# =============================================================================
def check_connection() -> None:
    mcl, ev = api_modules()
    check_subsystem_prompt()
    version = evaluation_version(ev)
    client = mcl.make_client()
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    with RunLock():
        connection_calls(mcl, client, version)


def connection_calls(mcl, client, version: str) -> None:
    check_id = mc.now_iso()
    print(f"Connection check: two calls to {MODEL} on the test sentence (no comment is sent), with the committed "
          f"settings (temperature {cfg.CLAUDE_SETTINGS['temperature']}, at most {cfg.CLAUDE_SETTINGS['max_tokens']} "
          f"output tokens, no system prompt).")
    tokens = {}
    for purpose in RUNS:
        try:
            a = mcl.call(client, MODEL, build_prompt(purpose, mcl.TEST_SENTENCE))
        except Exception as e:                              # noqa: BLE001 - reported to the user
            stop(f"{MODEL}: " + explain(e))
        ok = mcl.same_model(MODEL, a["model"]) and a["model"] == version
        mcl.append_line(CONNECTION_LOG, {"check_id": check_id, "purpose": purpose, "requested": MODEL, "passed": ok,
                                         "evaluation_version": version, "settings": cfg.CLAUDE_SETTINGS,
                                         "sdk": cfg.ANTHROPIC_SDK_VERSION, **a})
        if not ok:
            stop(f"MODEL_MISMATCH: asked for {MODEL}, the API answered with {a['model'] or 'no model name'}; the "
                 f"evaluation run was answered by {version}. {REPORT}")
        tokens[purpose] = a["input_tokens"]
        print(f"  {purpose} prompt: answered by {a['model']} ({a['input_tokens']} input tokens; stop reason "
              f"{a['stop_reason']})")
    d = tokens["subsystem"] - tokens["stage2"]
    print(f"Connection check passed: both prompts answered by {version}, the version that answered the evaluation "
          f"run. D = {tokens['subsystem']} - {tokens['stage2']} = {d} input tokens.")
    v = mc.versions("anthropic")
    show_block("connection", [
        f"- `models_06_deploy.py` (SHA-256 `{own_sha256()}`) run {check_id} with `--check-connection`: both prompts "
        f"answered by `{version}`, the version that answered the evaluation run; input tokens on the test sentence: "
        f"Stage 2 prompt {tokens['stage2']}, subsystem prompt {tokens['subsystem']}; D = {d}. Python {v['python']}, "
        f"anthropic {v['anthropic']}."])


def api_start(ceiling: float):
    """The checks every API run makes before its first call."""
    mcl, ev = api_modules()
    check_subsystem_prompt()
    version = evaluation_version(ev)
    if passing_check(version) is None:
        stop("no passing connection check under the committed settings. Run the check first (it sends no comment):\n"
             "  python models_06_deploy.py --check-connection")
    if ceiling != CEILING_USD:
        print(f"ceiling: US${ceiling:.2f}, not the US${CEILING_USD:.2f} of Deviation 13. A new ceiling is recorded in "
              f"the register with its reason before the run.")
    spend = {"usd": deployment_spend(mcl)}
    print(f"measured spend of both runs so far: US${spend['usd']:.4f} of the US${ceiling:.2f} ceiling")
    if spend["usd"] >= ceiling:
        stop(f"the measured spend has reached the ceiling. Only the ceiling may change (Deviation 13). {REPORT}")
    return mcl, ev, version, spend


def run_stage2(ceiling: float) -> None:
    me = own_sha256()
    print(f"Corpus runs (Deviation 13): Stage 2\nthis script: models_06_deploy.py SHA-256 {me}")
    with RunLock():
        stage2_steps(ceiling, me)


def stage2_steps(ceiling: float, me: str) -> None:
    mcl, ev, version, spend = api_start(ceiling)
    data = load_corpus_runs()
    items = stage2_items(data["corpus"])
    print(f"input: {len(items):,} comments (the Tier 1+2 comments classified relevant at Stage 1)")
    client = mcl.make_client()
    api_run("stage2", mcl, client, items, data["shas"], spend, ceiling, version)
    man = assemble("stage2", mcl, items, data["shas"], ceiling, version, me)
    sa = man["set_aside_after_two_rejections"]
    print(f"\nstage2: done | {man['comments']:,} comments | refusals {man['refusal']} | calls {man['calls']:,} | "
          f"cost US${man['cost_usd']:.4f} | spend of both runs US${man['spend_both_runs_usd']:.4f}")
    show_block("stage2", [
        f"- `models_06_deploy.py` (SHA-256 `{me}`) with `--stage2`, first call {man['access_window']['first_call']}, "
        f"last call {man['access_window']['last_call']}: {man['comments']:,} comments (the Tier 1+2 comments "
        f"classified relevant at Stage 1), answered by `{version}`. Refusals: {man['refusal']}"
        + (f", of which {len(sa)} set aside after two API rejections ({', '.join(sa)})" if sa else "")
        + f". Calls {man['calls']:,}; tokens in {man['tokens']['input']:,}, out {man['tokens']['output']:,}; cost "
        f"US${man['cost_usd']:.4f}; measured spend of both runs so far US${man['spend_both_runs_usd']:.4f} (ceiling "
        f"US${ceiling:.2f}).",
        f"- Inputs: `corpus_input.csv` SHA-256 `{data['shas']['corpus_input.csv']}`; `{STAGE1_PREDICTIONS_NAME}` "
        f"`{data['shas'][STAGE1_PREDICTIONS_NAME]}`.",
        f"- Outputs, in `data/models/deploy/` (not committed): `stage2_predictions.csv` SHA-256 "
        f"`{man['predictions']['sha256']}`; `stage2_log.jsonl` `{man['log']['sha256']}`; `stage2_manifest.json` "
        f"`{man['manifest_sha256']}`. Python {man['versions']['python']}, anthropic {man['versions']['anthropic']}, "
        f"pandas {man['versions']['pandas']}."])


def run_subsystem(ceiling: float) -> None:
    me = own_sha256()
    print(f"Corpus runs (Deviation 13): the subsystem classifier\nthis script: models_06_deploy.py SHA-256 {me}")
    with RunLock():
        subsystem_steps(ceiling, me)


def subsystem_steps(ceiling: float, me: str) -> None:
    mcl, ev, version, spend = api_start(ceiling)
    data = load_corpus_runs()
    s2_items = stage2_items(data["corpus"])
    s2_done, _, _ = read_log("stage2")
    s2_man_path = DEPLOY_DIR / "stage2_manifest.json"
    if not s2_man_path.exists() or any(i not in s2_done for i, _ in s2_items):
        stop("the Stage 2 run is not complete: the subsystem run is made after it (Deviation 13)")
    s2_man = mc.read_json(s2_man_path)
    if (s2_man.get("script") or {}).get("sha256_lf") != me or s2_man.get("comments") != len(s2_items):
        stop(f"stage2_manifest.json does not record this file's complete Stage 2 run. {REPORT}")
    check_file_sha(DEPLOY_DIR / "stage2_predictions.csv", s2_man["predictions"]["sha256"], "stage2_predictions.csv")
    gold, gold_shas = ev.load_gold()
    relevant = set(i for i, _ in s2_items)
    extra = sorted(i for i in gold.index if gold.at[i, "gold_stage1"] == "Y" and i not in relevant)
    corpus = data["corpus"]
    items = sorted(s2_items + [(i, corpus.at[i, "text"]) for i in extra])
    inputs = {**data["shas"], "gold_labels.csv": gold_shas["gold_labels.csv"]}
    print(f"input: {len(items):,} comments: {len(s2_items):,} Tier 1+2 comments classified relevant and {len(extra)} "
          f"tranche items relevant in the gold set and not among them (validation only)")
    done, others, estimates = read_log("subsystem")
    if not done and not others:                             # before the first call: the estimate of Deviation 13
        s2_done, s2_others, _ = read_log("stage2")
        calls = mcl.unique_calls([*s2_done.values(), *s2_others])
        tin, tout, n = sum(x["input_tokens"] for x in calls), sum(x["output_tokens"] for x in calls), len(calls)
        check = passing_check(version)
        d = check["subsystem"]["input_tokens"] - check["stage2"]["input_tokens"]
        price = cfg.CLAUDE_PRICES_USD_PER_MTOK[MODEL]
        if (price["input"], price["output"]) != ESTIMATE_PRICES:
            stop(f"the list prices of models_config.py are not those of the estimate in Deviation 13. {REPORT}")
        estimate = ((tin + n * d) * ESTIMATE_PRICES[0] + tout * ESTIMATE_PRICES[1]) / 1e6
        print(f"estimate (Deviation 13): (({tin:,} + {n:,} x {d}) x 3 + {tout:,} x 15) / 1,000,000 = US${estimate:.4f}; "
              f"with the spend so far, US${spend['usd'] + estimate:.4f} against the ceiling of US${ceiling:.2f}")
        if spend["usd"] + estimate > ceiling:
            stop(f"the subsystem run is not started: the estimate added to the spend so far is above the ceiling "
                 f"(Deviation 13). Only the ceiling may change: record a new ceiling and the reason in the register, "
                 f"then give the same command with --ceiling <new ceiling>. {REPORT}")
        DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
        mcl.append_line(log_path("subsystem"), {
            "status": "estimate", "kind": "subsystem", "at": mc.now_iso(), "input_tokens_stage2": tin,
            "output_tokens_stage2": tout, "calls_stage2": n, "d": d, "estimate_usd": round(estimate, 6),
            "spend_usd": round(spend["usd"], 6), "ceiling_usd": ceiling})
    client = mcl.make_client()
    api_run("subsystem", mcl, client, items, inputs, spend, ceiling, version)
    man = assemble("subsystem", mcl, items, inputs, ceiling, version, me, validation_only=set(extra))
    sa = man["set_aside_after_two_rejections"]
    est = man["estimate_before_run"] or {}
    print(f"\nsubsystem: done | {man['comments']:,} comments | unclassified {man['unclassified']} | calls "
          f"{man['calls']:,} | cost US${man['cost_usd']:.4f} | spend of both runs US${man['spend_both_runs_usd']:.4f}")
    show_block("subsystem", [
        f"- Before the first call of the subsystem run, the estimate of Deviation 13: US${est.get('estimate_usd', 0):.4f} "
        f"(Stage 2 run: {est.get('input_tokens_stage2', 0):,} input and {est.get('output_tokens_stage2', 0):,} output "
        f"tokens in {est.get('calls_stage2', 0):,} calls; D = {est.get('d')}); measured spend then US$"
        f"{est.get('spend_usd', 0):.4f}; ceiling US${est.get('ceiling_usd', ceiling):.2f}.",
        f"- `models_06_deploy.py` (SHA-256 `{me}`) with `--subsystem`, first call "
        f"{man['access_window']['first_call']}, last call {man['access_window']['last_call']}: {man['comments']:,} "
        f"comments ({len(s2_items):,} Tier 1+2 comments classified relevant; {len(extra)} tranche items relevant in "
        f"the gold set and not among them, for validation only), answered by `{version}`. Unclassified: "
        f"{man['unclassified']}"
        + (f", of which {len(sa)} set aside after two API rejections ({', '.join(sa)})" if sa else "")
        + f". Calls {man['calls']:,}; tokens in {man['tokens']['input']:,}, out {man['tokens']['output']:,}; cost "
        f"US${man['cost_usd']:.4f}; measured spend of both runs US${man['spend_both_runs_usd']:.4f} (ceiling "
        f"US${ceiling:.2f}).",
        f"- Inputs: `corpus_input.csv` SHA-256 `{inputs['corpus_input.csv']}`; `{STAGE1_PREDICTIONS_NAME}` "
        f"`{inputs[STAGE1_PREDICTIONS_NAME]}`; `gold_labels.csv` `{inputs['gold_labels.csv']}`.",
        f"- Outputs, in `data/models/deploy/` (not committed): `subsystem_predictions.csv` SHA-256 "
        f"`{man['predictions']['sha256']}`; `subsystem_log.jsonl` `{man['log']['sha256']}`; "
        f"`subsystem_manifest.json` `{man['manifest_sha256']}`. Python {man['versions']['python']}, anthropic "
        f"{man['versions']['anthropic']}, pandas {man['versions']['pandas']}."])


# =============================================================================
# main
# =============================================================================
def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Corpus runs of the deployed classifiers (Deviation 13).")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks only; writes nothing")
    mode.add_argument("--prepare", action="store_true", help="the corpus input (PC)")
    mode.add_argument("--stage1", action="store_true", help="final retraining and the Stage 1 corpus run (GPU)")
    mode.add_argument("--check-connection", action="store_true", help="two calls on the test sentence")
    mode.add_argument("--stage2", action="store_true", help="the Stage 2 corpus run")
    mode.add_argument("--subsystem", action="store_true", help="the subsystem run, after the Stage 2 run")
    ap.add_argument("--train-input", default=str(cfg.MODELS_DIR / "finetune_input.csv"))
    ap.add_argument("--corpus-input", default=str(CORPUS_INPUT))
    ap.add_argument("--input-manifest", default=str(CORPUS_INPUT_MANIFEST))
    ap.add_argument("--out-dir", default=str(DEPLOY_DIR))
    ap.add_argument("--work-dir", default=str(Path(tempfile.gettempdir()) / "models_06_work"))
    ap.add_argument("--ceiling", type=float, default=CEILING_USD, help="US$; only with a register entry (Deviation 13)")
    ap.add_argument("--test-model-dir", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.preflight:
        preflight()
    elif args.prepare:
        prepare()
    elif args.stage1:
        stage1(args)
    elif args.check_connection:
        check_connection()
    elif args.stage2:
        run_stage2(args.ceiling)
    else:
        run_subsystem(args.ceiling)


if __name__ == "__main__":
    main()
