"""Exploratory runs of Claude Opus 5.5 and Claude Fable 5.1 (Deviation 15 of docs/analysis_preregistration.md).

Steps, in this order, from the repository folder with the virtual environment active:
    python models_07_frontier.py --preflight
        Before the commit. Checks every module and input file the runs use against the record, builds every
        prompt the runs will send and checks it against the prompt the run of record sent for the same comment,
        then stops. It runs no model, sends nothing and writes nothing.
    python models_07_frontier.py --check-connection
        (API key set.) Six single requests on the test sentence: each model with each of the three prompts.
        No comment is sent.
    python models_07_frontier.py --pilot
        (API key set.) The pilot of Deviation 15: 30 comments, each model, each prompt (180 single requests).
        Prints tokens per call, refusals and answers that name no label, the pilot gate and the plan of the
        stopping rule. No answer is tabulated.
    python models_07_frontier.py --run STEP
        (API key set.) One step of the order of runs, through the Message Batches API, in this order:
        opus-eval, fable-eval, opus-corpus, fable-corpus. A step sends its runs one batch at a time and waits
        for each batch. A step that stops resumes from its log when the same command is given again.
    python models_07_frontier.py --status
        The state of every run and the measured spend. Sends nothing.
    python models_07_frontier.py --stops
        After a run is not started or halts under the stopping rule: the register lines of the stop, of the
        complete runs of its step, and the counts and log hash of a halted run. Sends nothing.
One API step at a time: a lock file stops a second one from starting while another is under way.
The API key is read from the environment variable ANTHROPIC_API_KEY and is never printed or saved.

What the runs print (Deviation 15): progress, the number of comments each run covers, counts of calls, of
refusals (with their categories) and of comments with no label, spend, and file hashes. Nothing from a run is
printed or written by class, subsystem, period, era, subreddit, tier or thread size.

Rules fixed with this file (where Deviation 15 is silent, or to say how it is applied)
  1. Record. Every module this file imports is checked against its SHA-256 with LF line endings (the files in
     the repository at aff4276). The inputs are checked as the scripts of record check them: the gold labels
     and the zero-shot input by models_05_evaluate.py, the corpus input and the Stage 1 predictions by
     models_06_deploy.py, the two Stage 2 evaluation runs of record by models_05_evaluate.py and the SHA-256
     of their logs, and the two corpus-run logs of record by the SHA-256 the register recorded on 15 October.
  2. Prompts. Universal and domain-specific Stage 2 prompts are built by models_02_claude.build_prompt, the
     subsystem prompt by models_06_deploy.subsystem_prompt, from the text the run of record used: the evaluation
     Stage 2 runs from data/models/zero_shot_input.csv, every other run from data/models/deploy/corpus_input.csv.
     Before any run sends a comment, the SHA-256 of each of its prompts must equal the prompt_sha256 that the run
     of record logged for the same comment and prompt, or the step stops. The pilot's universal prompts have no
     run of record and are built by the same function.
  3. Requests. Every request is one user message, max_tokens 4,000, output_config {"effort": "low"} and
     inference_geo "global" (the default, set so that the list prices hold whatever default the workspace has), and
     nothing else: no system prompt, no temperature, top_p, top_k or thinking setting. The answer is the text of
     the response's text blocks. It is read by models_02_claude.parse_answer (Stage 2) or
     models_06_deploy.parse_subsystem (subsystem). An answer that names no label, an empty one included, is
     retried once; a second such answer is a refusal (Stage 2) or unclassified (subsystem). A response with the
     stop reason "refusal" is final, with its category, and is not retried. No fallback is requested. The single
     requests (connection check and pilot) are sent with a timeout of 600 seconds and at most two automatic
     retries; a retry after a lost connection may be billed for an answer that is never received (at most about
     US$0.41 at Claude Fable 5.1's 4,000-token limit), which the US$3.00 held back covers. The region and the service tier that each answer reports (usage.inference_geo, usage.service_tier)
     are logged.
  4. Model version. Every answer must come under the identifier asked for (or that identifier plus a date), and
     every answer from one model, in the connection check, the pilot and every run, by the same model version,
     or the step stops for good and a further deviation decides. Such an answer is logged before the step stops,
     so that its cost is measured, and the pilot and every run first check every answer already logged.
  5. Pilot. The 30 comments are drawn from the Tier 1+2 comments classified relevant at Stage 1, the 1,000
     tranche items left out, with numpy.random.default_rng([24916660, 15]).choice(n, 30, replace=False) over the
     n comments sorted by id as strings in code-point order. Gate: if, for a model, more than 10% of its 90 pilot
     answers are refusals, or more than 10% name no label after the retry, its later runs are not made.
  6. Batches. A run is sent in batches, one batch at a time: at most 100 requests until the run has 50 answered
     calls, so that its own cost per call is measured before larger batches go out, and at most 1,000 after
     that. Each request has the custom id <run code><send number>-<comment id>. A batch is created once, with a
     timeout of 300 seconds and no automatic retry, after its registry entry is written. If the API refuses it
     (an HTTP error from 400 to 499 other than 408, 409 and 429), it was not created. If the outcome is not known
     (a timeout, a lost connection, any other error, or an interruption), the step stops. When a step is given
     again, before anything is sent, the API's list of batches is read: a batch absent from the registry, created
     within 60 minutes of the attempt and holding as many requests is taken as that batch; with more than one, the
     step stops; with none, the batch was not created if the attempt was 15 minutes ago or more, and otherwise the
     step stops and is given again after that time. Results are logged as they are read, and a batch is
     marked processed once all its results are logged. A request that expired or was cancelled, or that errored
     with api_error, overloaded_error, rate_limit_error or timeout_error, is sent again. An invalid_request_error
     is counted against the comment, which is sent again once; a second one makes it a refusal (unclassified in a
     subsystem run). An authentication, permission, not-found or billing error, an error of any other type, any
     error about a spending limit or a credit balance, or errors on more than 5% of a batch's requests stop the
     run without being counted: no error of that batch is logged, and its comments are sent again when the run
     resumes. A comment with five logged sends and no result stops the run for good, and a further deviation
     decides.
  7. Spend. Every logged call of this file (connection check, pilot and runs) is costed from its logged tokens at
     the list prices of 20 October 2026 (PRICES below; half through the Batches API; thinking is billed as
     output). The credit recorded is US$107.73 and the ceiling US$104.73. Before a run starts, its estimate is
     its number of comments times the pilot's calls per comment and mean batch cost per call for that model and
     prompt, plus 20%; it starts only if the estimate added to the measured spend is within the ceiling. Before
     each batch the rest of the run is estimated again from the run's own calls (from the pilot until the run
     has 50 answered calls), plus 20%, and the run halts if the estimate no longer fits. The run's own calls per
     comment count one more call for each comment whose answer named no label and is still to be retried. Every
     estimate is written, with the measured spend and its source, to the batch registry with the size of the batch
     that follows it, or to stops.jsonl when it stops the run; a complete run's manifest repeats its estimates. A run that does not start for cost, or halts, ends the runs of
     Deviation 15: no later run is made. A run that halts is kept as incomplete and enters no figure.
  8. Order. The steps run in the order opus-eval, fable-eval, opus-corpus, fable-corpus; a step starts only after
     every earlier step is complete or was not made under the pilot gate.

Writes, in data/models/frontier/ (data/ is not committed):
  connection_check.jsonl                                  --check-connection
  pilot_log.jsonl, pilot_manifest.json                    --pilot
  batches.jsonl, stops.jsonl                              --run (the batch registry; runs not made or halted)
  <run>_log.jsonl, <run>_predictions.csv, <run>_manifest.json   --run
  PASTE_<step>_block.txt, PASTE_stops_block.txt           the register lines of each step and of a stop (hashes and
                                                          counts only)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import statistics
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
OUT = cfg.MODELS_DIR / "frontier"

# SHA-256 with LF line endings of each committed module this file imports: the files in the repository at aff4276.
MODULES_OF_RECORD = {
    "models_config.py": "69c2ccc97a14eb5061f32f7c29cc1dda668060d6840702ff95c206338193e37a",
    "models_common.py": "65e7cbdef6c7594fabc71cb0b0f8bf22774e64749205fbbba3e7a18de1e57980",
    "models_01_prepare.py": "bb50327400d5e53d2633205bdd380fad9364affb35bdb072e143ed219a6074e0",
    "models_02_claude.py": "dbdddd642e2dc7a7725482693ca71197e92d301fcc56ffef4ea6c23e1d996146",
    "models_05_evaluate.py": "98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734",
    "models_06_deploy.py": "651e7f5edb59835ba706f173233eb9aea5ebad5e6617e2f13f5520a91198ec21",
}
# The corpus runs of record (docs/decision_register.md, 15 October 2026).
DEPLOY_RECORD = {
    "corpus_input.csv": "816bc9dfea5d73c7fed55446e833aae75b9bcd070bcf89e60e2fd0e3305566b4",
    "stage1_corpus_predictions.csv": "087e1e58ff3f9c36efa307e7735ead27e997a918452dbad993b085d119513cdf",
    "stage2_log.jsonl": "7cf2ef8510755843334077d1fbd88700b40d83bc8371e11953c0a3537c25ed49",
    "subsystem_log.jsonl": "daecd753f46b4d2cd2dca1fba883fdb9a1e27ccd221f1e5f884bbee0e52b389e",
}
STAGE2_EVAL_ITEMS = 598                         # gold items with a Stage 2 class (models_05_evaluate.GOLD_ITEMS)
CORPUS_STAGE2_ITEMS = 6503                      # the Tier 1+2 comments classified relevant (15 October 2026)
TRANCHE_ITEMS = 1000

MODELS = {"opus": "claude-opus-5-5", "fable": "claude-fable-5-1"}
NAMES = {"opus": "Claude Opus 5.5", "fable": "Claude Fable 5.1"}
MAX_TOKENS = 4000                               # Deviation 15: covers thinking and answer together
EFFORT = "low"                                  # Deviation 15: fixed for both models and every call
# List prices in US dollars per million tokens, 20 October 2026 (platform.claude.com/docs/en/about-claude/pricing):
# base input, output, 5-minute cache write, cache read. The Batches API charges half of each.
PRICES = {
    "claude-opus-5-5": {"input": 4.00, "output": 20.00, "cache_write": 5.00, "cache_read": 0.20},
    "claude-fable-5-1": {"input": 10.00, "output": 50.00, "cache_write": 12.50, "cache_read": 0.25},
}
BATCH_FACTOR = 0.5
CREDIT_USD = 107.73                             # the Claude Console on 20 October 2026: US$7.73 bought, US$100.00 promotional
RESERVE_USD = 3.00
CEILING_USD = round(CREDIT_USD - RESERVE_USD, 2)   # 104.73
MARGIN = 1.2                                    # Deviation 15: estimates plus 20%
OWN_RATE_AFTER = 50                             # rule 7: the run's own calls once it has this many answered calls
BATCH_SIZE = 1000
FIRST_BATCH_SIZE = 100                          # rule 6: until the run has OWN_RATE_AFTER answered calls
POLL_SECONDS = 30
SINGLE_TIMEOUT_SECONDS = 600                    # rule 3: one single request (connection check, pilot)
SINGLE_RETRIES = 2
CREATE_TIMEOUT_SECONDS = 300                    # rule 6: creating a batch, with no automatic retry
FOUND_WINDOW_MINUTES = 60                       # rule 6: a batch found in the API's list of batches
SETTLE_MINUTES = 15                             # rule 6: only after this is a batch absent from the list not created
INFERENCE_GEO = "global"                        # rule 3: global routing, the default, which PRICES assume
ERROR_SHARE_STOP = 0.05
MAX_SENDS = 5
PILOT_SIZE = 30
PILOT_SEED = [24916660, 15]
PILOT_GATE = 0.10
KINDS = ("universal", "domain", "subsystem")    # the three prompts
CUSTOM_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
ID_CHARS = re.compile(r"^[A-Za-z0-9]+$")

RUNS = {   # run -> model, prompt kind, item set, custom-id code
    "opus-eval-universal": {"model": "opus", "kind": "universal", "items": "eval", "code": "oeu"},
    "opus-eval-domain": {"model": "opus", "kind": "domain", "items": "eval", "code": "oed"},
    "opus-eval-subsystem": {"model": "opus", "kind": "subsystem", "items": "eval", "code": "oes"},
    "fable-eval-universal": {"model": "fable", "kind": "universal", "items": "eval", "code": "feu"},
    "fable-eval-domain": {"model": "fable", "kind": "domain", "items": "eval", "code": "fed"},
    "fable-eval-subsystem": {"model": "fable", "kind": "subsystem", "items": "eval", "code": "fes"},
    "opus-corpus-stage2": {"model": "opus", "kind": "domain", "items": "corpus", "code": "ocd"},
    "opus-corpus-subsystem": {"model": "opus", "kind": "subsystem", "items": "corpus", "code": "ocs"},
    "fable-corpus-stage2": {"model": "fable", "kind": "domain", "items": "corpus", "code": "fcd"},
    "fable-corpus-subsystem": {"model": "fable", "kind": "subsystem", "items": "corpus", "code": "fcs"},
}
STEPS = {
    "opus-eval": ["opus-eval-universal", "opus-eval-domain", "opus-eval-subsystem"],
    "fable-eval": ["fable-eval-universal", "fable-eval-domain", "fable-eval-subsystem"],
    "opus-corpus": ["opus-corpus-stage2", "opus-corpus-subsystem"],
    "fable-corpus": ["fable-corpus-stage2", "fable-corpus-subsystem"],
}
ORDER = ["opus-eval", "fable-eval", "opus-corpus", "fable-corpus"]
STEP_MODEL = {"opus-eval": "opus", "fable-eval": "fable", "opus-corpus": "opus", "fable-corpus": "fable"}
STEP_OF = {run: step for step, runs in STEPS.items() for run in runs}
CODES = {spec["code"]: run for run, spec in RUNS.items()}

TRANSIENT_ERRORS = {"api_error", "overloaded_error", "rate_limit_error", "timeout_error"}   # sent again (rule 6)
COUNTED_ERRORS = {"invalid_request_error"}                                                # counted (rule 6)
SYSTEMIC_ERRORS = {"authentication_error", "permission_error", "not_found_error", "billing_error"}
SYSTEMIC_WORDS = ("usage limit", "credit balance", "spend limit", "spending limit")
REPORT = "Report this message before going further."
STOPS_COMMAND = "python models_07_frontier.py --stops"


# =============================================================================
# small helpers
# =============================================================================
def stop(message: str) -> None:
    mc.stop(message)


def text_file_sha256(path: Path) -> str:
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
            stop(f"{path.name} is not the file in the repository at aff4276 (SHA-256 {got[:16]}..., recorded "
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


def read_jsonl(path: Path) -> list:
    out = []
    if not Path(path).exists():
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:                    # a torn last line
                continue
    return out


def close_torn_line(path: Path) -> None:
    if path.exists() and path.stat().st_size:
        with open(path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            torn = f.read(1) != b"\n"
        if torn:
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write("\n")


def money(x: float) -> str:
    return f"US${x:.4f}"


def show_block(name: str, lines: list[str]) -> None:
    mc.show_register_block(OUT / f"PASTE_{name}_block.txt", lines)


def no_answer(kind: str) -> str:
    return "unclassified" if kind == "subsystem" else "refusal"


# =============================================================================
# the record: inputs, items, prompts
# =============================================================================
def committed_modules():
    import models_01_prepare as prep
    import models_02_claude as mcl
    import models_05_evaluate as ev
    import models_06_deploy as dep
    return {"modules_sha256_lf": check_modules([cfg, mc, prep, mcl, ev, dep])}, mcl, ev, dep


def record_prompt_hashes(path: Path, final: tuple, ids: set, what: str) -> dict:
    """{comment id: prompt_sha256} from the final records of a log of record."""
    out = {}
    for rec in read_jsonl(path):
        if rec.get("status") in final and rec.get("id") in ids and rec.get("prompt_sha256"):
            out[rec["id"]] = rec["prompt_sha256"]
    missing = sorted(ids - set(out))
    if missing:
        stop(f"{what}: {len(missing)} comments have no prompt_sha256 in {path.name}, e.g. {missing[:3]}. {REPORT}")
    return out


def load_record() -> dict:
    """Every check of rule 1 and rule 2, and the items and prompts of every run. Sends nothing, writes nothing."""
    info, mcl, ev, dep = committed_modules()
    import pandas as pd

    # gold labels (models_05_evaluate) and the 598 items with a Stage 2 class
    gold, gold_shas = ev.load_gold()
    eval_ids = sorted(i for i in gold.index if gold.at[i, "gold_stage2"] in cfg.CLASSES)
    if len(eval_ids) != STAGE2_EVAL_ITEMS or len(gold) != TRANCHE_ITEMS:
        stop(f"gold_labels.csv gives {len(eval_ids)} items with a Stage 2 class; the record has {STAGE2_EVAL_ITEMS}")
    zs_path = cfg.MODELS_DIR / "zero_shot_input.csv"
    zs_sha = ev.check_sha(zs_path, ev.INPUTS_SHA256["zero_shot_input.csv"], "zero_shot_input.csv")
    zs = pd.read_csv(zs_path, dtype=str, keep_default_na=False, encoding="utf-8")
    if list(zs.columns) != ["id", "text"] or set(zs["id"]) != set(gold.index):
        stop("zero_shot_input.csv must hold the 1,000 annotated items with the columns id,text")
    zs_text = dict(zip(zs["id"], zs["text"]))

    # the corpus input and the Stage 1 predictions (models_06_deploy), and the 6,503 comments
    data = dep.load_corpus_runs()
    for name, want in (("corpus_input.csv", DEPLOY_RECORD["corpus_input.csv"]),
                       ("stage1_corpus_predictions.csv", DEPLOY_RECORD["stage1_corpus_predictions.csv"])):
        if data["shas"].get(name) != want:
            stop(f"{name}: SHA-256 {str(data['shas'].get(name))[:16]}... is not the one recorded on 15 October. {REPORT}")
    corpus = data["corpus"]
    corpus_items = dep.stage2_items(corpus)
    corpus_text = dict(corpus_items)
    if len(corpus_items) != CORPUS_STAGE2_ITEMS:
        stop(f"the corpus runs of record give {len(corpus_items):,} Tier 1+2 comments classified relevant, not "
             f"{CORPUS_STAGE2_ITEMS:,}. {REPORT}")
    missing = [i for i in eval_ids if i not in corpus.index]
    if missing:
        stop(f"{len(missing)} gold items are not in corpus_input.csv. {REPORT}")
    sub_eval_text = {i: corpus.at[i, "text"] for i in eval_ids}

    # the runs of record whose prompts are compared (rule 2)
    rec_hash = {}
    for schema in ("universal", "domain"):
        name = f"sonnet-{schema}"
        _, man, _ = ev.open_run(name)
        log = cfg.MODELS_DIR / "claude" / f"{name}_log.jsonl"
        check_file_sha(log, (man.get("log") or {}).get("sha256", ""), f"{name}_log.jsonl (the evaluation run of record)")
        rec_hash[("eval", schema)] = record_prompt_hashes(log, ("ok", "refusal"), set(eval_ids), f"{name}_log.jsonl")
    deploy = cfg.MODELS_DIR / "deploy"
    s2_log, sub_log = deploy / "stage2_log.jsonl", deploy / "subsystem_log.jsonl"
    check_file_sha(s2_log, DEPLOY_RECORD["stage2_log.jsonl"], "stage2_log.jsonl (the corpus run of record)")
    check_file_sha(sub_log, DEPLOY_RECORD["subsystem_log.jsonl"], "subsystem_log.jsonl (the corpus run of record)")
    corpus_ids = set(corpus_text)
    rec_hash[("corpus", "domain")] = record_prompt_hashes(s2_log, ("ok", "refusal"), corpus_ids, "stage2_log.jsonl")
    rec_hash[("corpus", "subsystem")] = record_prompt_hashes(sub_log, ("ok", "unclassified"), corpus_ids | set(eval_ids),
                                                             "subsystem_log.jsonl")
    dep.check_subsystem_prompt()

    # every id must be safe in a custom id (rule 6)
    bad = [i for i in set(eval_ids) | corpus_ids if not ID_CHARS.fullmatch(str(i))]
    if bad:
        stop(f"{len(bad)} comment ids hold characters other than letters and digits, e.g. {bad[:3]}. {REPORT}")

    # the pilot (rule 5)
    import numpy as np
    pool = sorted(set(corpus_text) - set(gold.index))
    pick = np.random.default_rng(PILOT_SEED).choice(len(pool), PILOT_SIZE, replace=False)
    pilot_ids = sorted(pool[int(k)] for k in pick)

    def prompt(kind: str, text: str) -> str:
        return dep.subsystem_prompt(text) if kind == "subsystem" else mcl.build_prompt(kind, text)

    items = {}
    for run, spec in RUNS.items():
        kind = spec["kind"]
        if spec["items"] == "eval":
            text = zs_text if kind != "subsystem" else sub_eval_text
            rows = [(i, prompt(kind, text[i])) for i in eval_ids]
            ref = rec_hash[("eval", kind)] if kind != "subsystem" else rec_hash[("corpus", "subsystem")]
        else:
            rows = [(i, prompt(kind, corpus_text[i])) for i in sorted(corpus_text)]
            ref = rec_hash[("corpus", kind)]
        differ = [i for i, p in rows if mc.text_sha256(p) != ref[i]]
        if differ:
            stop(f"{run}: {len(differ)} prompts differ from the prompt of record for the same comment, e.g. "
                 f"{differ[:3]}. {REPORT}")
        items[run] = rows
    pilot = {}
    for kind in KINDS:
        rows = [(i, prompt(kind, corpus_text[i])) for i in pilot_ids]
        if kind != "universal":
            ref = rec_hash[("corpus", kind)]
            differ = [i for i, p in rows if mc.text_sha256(p) != ref[i]]
            if differ:
                stop(f"pilot, {kind} prompt: {len(differ)} prompts differ from the prompt of record. {REPORT}")
        pilot[kind] = rows
    for run, rows in items.items():
        for i, _ in rows:
            cid = f"{RUNS[run]['code']}{MAX_SENDS}-{i}"
            if not CUSTOM_ID.fullmatch(cid):
                stop(f"the custom id {cid} is not valid. {REPORT}")

    info["inputs"] = {**gold_shas, "zero_shot_input.csv": zs_sha, **data["shas"],
                      "stage2_log.jsonl": DEPLOY_RECORD["stage2_log.jsonl"],
                      "subsystem_log.jsonl": DEPLOY_RECORD["subsystem_log.jsonl"]}
    info["pilot_ids_sha256"] = mc.ids_sha256(pilot_ids)
    return {"info": info, "items": items, "pilot": pilot, "pilot_ids": pilot_ids, "mcl": mcl, "dep": dep,
            "test_sentence": mcl.TEST_SENTENCE, "prompt": prompt}


# =============================================================================
# requests, answers, cost
# =============================================================================
def request_params(model: str, prompt: str) -> dict:
    """Deviation 15: one user message, max_tokens 4,000, effort low, global routing; no system prompt, temperature,
    top_p, top_k or thinking setting."""
    return {"model": model, "max_tokens": MAX_TOKENS, "messages": [{"role": "user", "content": prompt}],
            "output_config": {"effort": EFFORT}, "inference_geo": INFERENCE_GEO}


def attempt_from_message(msg, at: str, mode: str, batch_id=None, request_id=None, custom_id=None) -> dict:
    content = getattr(msg, "content", None) or []
    text = "".join(getattr(b, "text", "") or "" for b in content if getattr(b, "type", "") == "text")
    usage = getattr(msg, "usage", None)
    details = getattr(usage, "output_tokens_details", None)
    stop_details = getattr(msg, "stop_details", None)
    return {"at": at, "mode": mode, "message_id": getattr(msg, "id", None), "request_id": request_id,
            "batch_id": batch_id, "custom_id": custom_id, "model": str(getattr(msg, "model", "") or ""),
            "stop_reason": getattr(msg, "stop_reason", None),
            "refusal_category": getattr(stop_details, "category", None) if stop_details is not None else None,
            "text": text,
            "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
            "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
            "thinking_tokens": int(getattr(details, "thinking_tokens", 0) or 0) if details is not None else None,
            "cache_creation_input_tokens": int(getattr(usage, "cache_creation_input_tokens", 0) or 0),
            "cache_read_input_tokens": int(getattr(usage, "cache_read_input_tokens", 0) or 0),
            "inference_geo": getattr(usage, "inference_geo", None),
            "service_tier": getattr(usage, "service_tier", None)}


def single_client(client):
    """Rule 3: the client for single requests."""
    return client.with_options(timeout=SINGLE_TIMEOUT_SECONDS, max_retries=SINGLE_RETRIES)


def call_cost(model: str, a: dict, mode: str | None = None) -> float:
    p = PRICES[model]
    f = BATCH_FACTOR if (mode or a.get("mode")) == "batch" else 1.0
    return f * (a["input_tokens"] * p["input"] + a["output_tokens"] * p["output"]
                + a.get("cache_creation_input_tokens", 0) * p["cache_write"]
                + a.get("cache_read_input_tokens", 0) * p["cache_read"]) / 1e6


def parse(kind: str, text: str, mcl, dep):
    return dep.parse_subsystem(text) if kind == "subsystem" else mcl.parse_answer(text, kind)


def unique_calls(records) -> list:
    """Every answered call in the records, once (by the API's message id)."""
    seen, calls = set(), []
    for r in records:
        for x in r.get("attempts", []):
            key = x.get("message_id") or (x.get("at"), x.get("text"), x.get("input_tokens"), x.get("output_tokens"))
            if key not in seen:
                seen.add(key)
                calls.append(x)
    return calls


def same_version(model: str, answers: set) -> list:
    """Problems with the identifiers that answered (rule 4)."""
    import models_02_claude as mcl
    wrong = sorted(m for m in answers if not mcl.same_model(model, m))
    problems = [f"answers from {wrong}, not {model}"] if wrong else []
    if len(answers) > 1:
        problems.append(f"answers from more than one version: {sorted(answers)}")
    return problems


def logged_attempts(model_key: str) -> list:
    """Every answer of this model logged by this file: connection check, pilot and runs."""
    model = MODELS[model_key]
    out = [x for x in read_jsonl(OUT / "connection_check.jsonl") if x.get("requested") == model]
    for rec in read_jsonl(OUT / "pilot_log.jsonl"):
        if rec.get("model") == model:
            out += rec.get("attempts", [])
    for run, spec in RUNS.items():
        if spec["model"] == model_key:
            for rec in read_jsonl(OUT / f"{run}_log.jsonl"):
                out += rec.get("attempts", [])
    return out


def answered_by(model_key: str) -> set:
    return {a.get("model") for a in logged_attempts(model_key) if a.get("model") is not None}


def logged_problems(model_key: str) -> list:
    """Rule 4 applied to every answer already logged."""
    attempts = logged_attempts(model_key)
    return same_version(MODELS[model_key], {a.get("model") for a in attempts if a.get("model") is not None})


def measured_spend() -> float:
    """Every logged call of this file, at the list prices (rule 7)."""
    total = 0.0
    for x in read_jsonl(OUT / "connection_check.jsonl"):
        if x.get("requested") in PRICES and "input_tokens" in x:
            total += call_cost(x["requested"], x, "single")
    for x in unique_calls(read_jsonl(OUT / "pilot_log.jsonl")):
        total += call_cost(x["requested"], x, "single")
    for run, spec in RUNS.items():
        model = MODELS[spec["model"]]
        for x in unique_calls(read_jsonl(OUT / f"{run}_log.jsonl")):
            total += call_cost(model, x, "batch")
    return total


def explain(e: Exception) -> str:
    name = type(e).__name__
    again = "Give the same command again later: finished work is kept."
    hints = {"AuthenticationError": "the API key was refused. Check ANTHROPIC_API_KEY.",
             "PermissionDeniedError": f"the API key may not use this model. {REPORT}",
             "NotFoundError": f"the model identifier was not found; do not change it. {REPORT}",
             "RateLimitError": "rate limit or spending limit reached after all retries. Wait a few minutes, then "
                               "give the same command again: finished work is kept.",
             "APIConnectionError": "no connection after all retries. " + again,
             "APITimeoutError": "the API timed out after all retries. " + again,
             "InternalServerError": "the API was unavailable after all retries. " + again,
             "ServiceUnavailableError": "the API was unavailable after all retries. " + again,
             "OverloadedError": "the API was overloaded after all retries. " + again,
             "DeadlineExceededError": "the API timed out after all retries. " + again}
    low = str(e).lower()
    if "credit balance" in low:
        hint = f"the account's credit balance is too low. No credit is added for these runs (Deviation 15). {REPORT}"
    elif any(w in low for w in SYSTEMIC_WORDS):
        hint = (f"a spending limit of the account was reached. Check the limit on the Console's Billing page against "
                f"the procedure. {REPORT}")
    else:
        hint = hints.get(name, REPORT)
    return f"{name}: {e}\n  {hint}"


class RunLock:
    """data/models/frontier/api_run.lock, made with O_EXCL: a second API step cannot start while one is under way."""

    def __enter__(self):
        OUT.mkdir(parents=True, exist_ok=True)
        self.path = OUT / "api_run.lock"
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            stop(f"another API step may be under way ({self.path} exists). Give one command at a time. If no other "
                 f"step is running (for example after a power cut), delete that file and give the command again.")
        with os.fdopen(fd, "w") as f:
            f.write(f"{os.getpid()} {mc.now_iso()}\n")
        return self

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        return False


# =============================================================================
# --preflight
# =============================================================================
def preflight() -> None:
    me = own_sha256()
    print(f"Deviation 15: preflight, before the commit\nthis script: models_07_frontier.py SHA-256 {me}")
    rec = load_record()
    print("modules: every module imported is the file in the repository at aff4276")
    for run in RUNS:
        print(f"  {run}: {len(rec['items'][run]):,} comments; every prompt equals the prompt of record")
    print(f"  pilot: {len(rec['pilot_ids'])} comments (membership SHA-256 {rec['info']['pilot_ids_sha256'][:16]}...); "
          f"domain-specific and subsystem prompts equal the prompts of record")
    print(f"settings: max_tokens {MAX_TOKENS}, effort {EFFORT}, inference_geo {INFERENCE_GEO}, no temperature, no system "
          f"prompt; batches of at most "
          f"{FIRST_BATCH_SIZE} then {BATCH_SIZE:,}; credit US${CREDIT_USD:.2f}, ceiling US${CEILING_USD:.2f}")
    print(f"\nPREFLIGHT PASSED: {sum(len(v) for v in rec['items'].values()):,} run requests and "
          f"{PILOT_SIZE * len(KINDS) * len(MODELS)} pilot requests checked. No model was run, nothing was sent and "
          f"nothing was written.")


# =============================================================================
# --check-connection
# =============================================================================
def check_connection() -> None:
    me = own_sha256()
    print(f"Deviation 15: connection check\nthis script: models_07_frontier.py SHA-256 {me}")
    info, mcl, ev, dep = committed_modules()
    client = single_client(mcl.make_client())
    with RunLock():
        close_torn_line(OUT / "connection_check.jsonl")
        check_id = mc.now_iso()
        lines = []
        for key, model in MODELS.items():
            for kind in KINDS:
                prompt = dep.subsystem_prompt(mcl.TEST_SENTENCE) if kind == "subsystem" else \
                    mcl.build_prompt(kind, mcl.TEST_SENTENCE)
                try:
                    started = mc.now_iso()
                    raw = client.messages.with_raw_response.create(**request_params(model, prompt))
                    msg = raw.parse()
                    a = attempt_from_message(msg, started, "single", request_id=raw.request_id)
                except Exception as e:                       # noqa: BLE001 - reported to the user
                    stop(f"{model}: " + explain(e))
                named = a["stop_reason"] != "refusal" and parse(kind, a["text"], mcl, dep) is not None
                same = mcl.same_model(model, a["model"])
                mcl.append_line(OUT / "connection_check.jsonl",
                                {"check_id": check_id, "requested": model, "kind": kind, "passed": same,
                                 "named_a_label": named,
                                 "settings": {"max_tokens": MAX_TOKENS, "effort": EFFORT, "inference_geo": INFERENCE_GEO},
                                 "sdk": cfg.ANTHROPIC_SDK_VERSION, **a})
                if not same:
                    stop(f"MODEL_MISMATCH: asked for {model}, the API answered with {a['model'] or 'no model name'}. "
                         f"{REPORT}")
                print(f"  {model}, {kind} prompt: answered by {a['model']} ({a['input_tokens']} input, "
                      f"{a['output_tokens']} output tokens; stop reason {a['stop_reason']}; region "
                      f"{a['inference_geo'] or 'not reported'}; tier {a['service_tier'] or 'not reported'}); the answer "
                      f"{'names' if named else 'does not name'} a label")
                lines.append(f"{model} {kind}: input {a['input_tokens']}, output {a['output_tokens']}, stop "
                             f"{a['stop_reason']}, region {a['inference_geo'] or 'not reported'}, tier "
                             f"{a['service_tier'] or 'not reported'}, {'names a label' if named else 'names no label'}")
        for key in MODELS:
            problems = logged_problems(key)
            if problems:
                stop(f"MODEL_MISMATCH: {MODELS[key]}: {'; '.join(problems)}. {REPORT}")
    spend = measured_spend()
    v = mc.versions("anthropic")
    print(f"Connection check passed: both models accept the settings and answer under the identifiers asked for. "
          f"Measured spend so far {money(spend)}.")
    show_block("connection", [
        f"- `models_07_frontier.py` (SHA-256 `{me}`) run {check_id} with `--check-connection`: six single requests on "
        f"the test sentence, each answered under the identifier asked for ({', '.join(MODELS.values())}). "
        + "; ".join(lines) + f". Measured spend so far {money(spend)}. `connection_check.jsonl` "
        f"`{mc.sha256_file(OUT / 'connection_check.jsonl')}`. Python {v['python']}, anthropic {v['anthropic']}."])


def passed_connection() -> bool:
    checks = {}
    for x in read_jsonl(OUT / "connection_check.jsonl"):
        if x.get("passed") is True and x.get("settings") == {"max_tokens": MAX_TOKENS, "effort": EFFORT,
                                                               "inference_geo": INFERENCE_GEO} \
                and x.get("sdk") == cfg.ANTHROPIC_SDK_VERSION:
            checks.setdefault(x.get("check_id"), set()).add((x.get("requested"), x.get("kind")))
    want = {(m, k) for m in MODELS.values() for k in KINDS}
    return any(v == want for v in checks.values())


# =============================================================================
# --pilot
# =============================================================================
def pilot_stats(records: list) -> dict:
    """Per model and prompt: comments, calls, mean tokens per call, refusals, answers naming no label, mean batch cost
    per call and calls per comment. Counts only: no answer is tabulated."""
    out = {}
    for model in MODELS.values():
        for kind in KINDS:
            recs = [r for r in records if r["model"] == model and r["kind"] == kind and r["status"] in ("ok", "refusal")]
            calls = [a for r in recs for a in r["attempts"]]
            n = len(recs)
            out[f"{model}|{kind}"] = {
                "comments": n, "calls": len(calls),
                "mean_input_tokens": statistics.fmean(a["input_tokens"] for a in calls) if calls else 0.0,
                "mean_output_tokens": statistics.fmean(a["output_tokens"] for a in calls) if calls else 0.0,
                "mean_thinking_tokens": statistics.fmean(a.get("thinking_tokens") or 0 for a in calls) if calls else 0.0,
                "max_output_tokens": max((a["output_tokens"] for a in calls), default=0),
                "refusals": sum(r.get("reason") == "refusal_stop" for r in recs),
                "refusal_categories": dict(Counter(str(r.get("refusal_category")) for r in recs
                                                   if r.get("reason") == "refusal_stop")),
                "no_label_after_retry": sum(r.get("reason") == "no_label" for r in recs),
                "stop_reasons": dict(Counter(str(a["stop_reason"]) for a in calls)),
                "mean_batch_cost_per_call": statistics.fmean(call_cost(model, a, "batch") for a in calls) if calls else 0.0,
                "calls_per_comment": len(calls) / n if n else 0.0,
                "cost_single": sum(call_cost(model, a, "single") for a in calls),
            }
    return out


def gate(stats: dict) -> dict:
    """Rule 5: a model passes when at most 10% of its 90 pilot answers are refusals and at most 10% name no label."""
    out = {}
    for key, model in MODELS.items():
        rows = [stats[f"{model}|{k}"] for k in KINDS]
        n = sum(r["comments"] for r in rows)
        refusals, no_label = sum(r["refusals"] for r in rows), sum(r["no_label_after_retry"] for r in rows)
        out[key] = {"answers": n, "refusals": refusals, "no_label_after_retry": no_label,
                    "passes": n > 0 and refusals <= PILOT_GATE * n and no_label <= PILOT_GATE * n}
    return out


def run_estimate(run: str, n_comments: int, stats: dict) -> float:
    spec = RUNS[run]
    s = stats[f"{MODELS[spec['model']]}|{spec['kind']}"]
    return n_comments * s["calls_per_comment"] * s["mean_batch_cost_per_call"] * MARGIN


def plan(stats: dict, gates: dict, spend: float, sizes: dict) -> list:
    rows, cum, ended = [], spend, False
    for step in ORDER:
        for run in STEPS[step]:
            est = run_estimate(run, sizes[run], stats)
            if not gates[RUNS[run]["model"]]["passes"]:
                rows.append({"run": run, "estimate": est, "outcome": "not made (pilot gate)"})
                continue
            if ended or cum + est > CEILING_USD:
                ended = True
                rows.append({"run": run, "estimate": est, "outcome": "would not start (stopping rule)"})
                continue
            cum += est
            rows.append({"run": run, "estimate": est, "cumulative": cum, "outcome": "fits"})
    return rows


def run_pilot() -> None:
    me = own_sha256()
    print(f"Deviation 15: pilot\nthis script: models_07_frontier.py SHA-256 {me}")
    rec = load_record()
    mcl, dep = rec["mcl"], rec["dep"]
    if not passed_connection():
        stop("no passing connection check under the committed settings. Run the check first (it sends no comment):\n"
             "  python models_07_frontier.py --check-connection")
    for key in MODELS:                                      # rules 3 and 4: every answer already logged
        problems = logged_problems(key)
        if problems:
            stop(f"MODEL_MISMATCH: {MODELS[key]}: {'; '.join(problems)}. A further deviation decides (rule 4). {REPORT}")
    client = single_client(mcl.make_client())
    path = OUT / "pilot_log.jsonl"
    with RunLock():
        close_torn_line(path)
        done = {(r["model"], r["kind"], r["id"]): r for r in read_jsonl(path) if r.get("status") in ("ok", "refusal")}
        partial = {}
        for r in read_jsonl(path):
            if r.get("status") == "partial":
                partial[(r["model"], r["kind"], r["id"])] = r["attempts"]
        todo = [(model, kind, i, p) for model in MODELS.values() for kind in KINDS for i, p in rec["pilot"][kind]
                if (model, kind, i) not in done]
        total = len(MODELS) * len(KINDS) * PILOT_SIZE
        spend = {"usd": measured_spend()}
        print(f"pilot: {total} comment-prompts ({len(done)} already done, {len(todo)} to do); measured spend so far "
              f"{money(spend['usd'])} of the US${CEILING_USD:.2f} ceiling", flush=True)
        lock = threading.Lock()
        counter = {"n": len(done)}
        started = time.time()

        def work(model: str, kind: str, item_id: str, prompt: str) -> None:
            attempts, label = [dict(a) for a in partial.get((model, kind, item_id), [])], None
            refused = None
            for a in attempts:
                if a["stop_reason"] == "refusal":
                    refused = a
                    break
                label = parse(kind, a["text"], mcl, dep)
                if label is not None:
                    break
            while refused is None and label is None and len(attempts) < 1 + cfg.NO_CLASS_RETRIES:
                at = mc.now_iso()
                raw = client.messages.with_raw_response.create(**request_params(model, prompt))
                a = attempt_from_message(raw.parse(), at, "single", request_id=raw.request_id)
                a["requested"] = model
                attempts.append(a)
                problem = None
                if not mcl.same_model(model, a["model"]):
                    problem = f"MODEL_MISMATCH: asked for {model}, the API answered with {a['model']}"
                with lock:
                    spend["usd"] += call_cost(model, a, "single")
                    if problem is None and spend["usd"] >= CEILING_USD:
                        problem = f"SPEND_CEILING: measured spend {money(spend['usd'])} reached the ceiling"
                    if problem is not None:                 # logged first, so that its cost is measured (rule 4)
                        mcl.append_line(path, {"model": model, "kind": kind, "id": item_id, "status": "partial",
                                               "attempts": attempts, "stopped": problem})
                if problem is not None:
                    raise RuntimeError(problem)
                if a["stop_reason"] == "refusal":
                    refused = a
                else:
                    label = parse(kind, a["text"], mcl, dep)
                if label is None and refused is None and len(attempts) < 1 + cfg.NO_CLASS_RETRIES:
                    with lock:
                        mcl.append_line(path, {"model": model, "kind": kind, "id": item_id, "status": "partial",
                                               "attempts": attempts})
            if refused is not None:
                status, reason = "refusal", "refusal_stop"
            elif label is None:
                status, reason = "refusal", "no_label"
            else:
                status, reason = "ok", ""
            out = {"model": model, "kind": kind, "id": item_id, "prompt_sha256": mc.text_sha256(prompt),
                   "status": status, "reason": reason,
                   "refusal_category": refused.get("refusal_category") if refused else None,
                   "attempts": attempts}               # the label itself is not written (rule 5: never tabulated)
            with lock:
                mcl.append_line(path, out)
                counter["n"] += 1
                if counter["n"] % 30 == 0 or counter["n"] == total:
                    rate = (counter["n"] - (total - len(todo))) / max(time.time() - started, 1e-9)
                    left = (total - counter["n"]) / rate / 60 if rate > 0 else float("nan")
                    print(f"  {counter['n']}/{total} | spend {money(spend['usd'])} | ~{left:4.1f} min left", flush=True)

        if todo:
            OUT.mkdir(parents=True, exist_ok=True)
            first_error, interrupted = None, False
            with ThreadPoolExecutor(max_workers=cfg.CLAUDE_CONCURRENCY) as pool:
                futures = [pool.submit(work, *t) for t in todo]
                try:
                    while True:
                        finished, pending = wait(futures, timeout=1, return_when=FIRST_EXCEPTION)
                        errors = [f.exception() for f in finished if f.exception() is not None]
                        if errors or not pending:
                            break
                except KeyboardInterrupt:
                    errors, interrupted = [], True
                if errors or interrupted:
                    first_error = errors[0] if errors else None
                    for f in futures:
                        f.cancel()
            if interrupted:
                stop("the pilot was stopped by the user; give the same command again to continue.")
            if first_error is not None:
                e = first_error
                if str(e).startswith(("MODEL_MISMATCH", "SPEND_CEILING")):
                    stop(f"pilot: {e}. {REPORT}")
                stop("pilot stopped. Finished requests are kept.\n  " + explain(e))

    records = [r for r in read_jsonl(path) if r.get("status") in ("ok", "refusal")]
    if len(records) != total:
        stop(f"pilot: {len(records)} of {total} comment-prompts have a result. {REPORT}")
    for key in MODELS:
        problems = logged_problems(key)
        if problems:
            stop(f"MODEL_MISMATCH: {MODELS[key]}: {'; '.join(problems)}. {REPORT}")
    man_path, log_sha = OUT / "pilot_manifest.json", mc.sha256_file(path)
    old = mc.read_json(man_path) if man_path.exists() else {}
    if (old.get("script") or {}).get("sha256_lf") == me and (old.get("log") or {}).get("sha256") == log_sha:
        manifest = old                                      # the pilot given again: its summary is not rewritten
        print("\nThe pilot was already complete; its summary is shown again unchanged.")
    else:
        stats = pilot_stats(records)
        gates = gate(stats)
        spend_now = measured_spend()
        sizes = {run: len(rows) for run, rows in rec["items"].items()}
        manifest = {"created": mc.now_iso(), "specification": "Deviation 15, docs/analysis_preregistration.md",
                    "script": {"file": "models_07_frontier.py", "sha256_lf": me},
                    "pilot_ids_sha256": rec["info"]["pilot_ids_sha256"], "stats": stats, "gate": gates,
                    "plan": plan(stats, gates, spend_now, sizes), "measured_spend_usd": round(spend_now, 6),
                    "ceiling_usd": CEILING_USD, "log": {"file": "data/models/frontier/pilot_log.jsonl", "sha256": log_sha},
                    "versions": mc.versions("anthropic", "numpy", "pandas")}
        mc.write_json(man_path, manifest)
    stats, gates, rows = manifest["stats"], manifest["gate"], manifest["plan"]
    spend_now = manifest["measured_spend_usd"]
    print("\nPilot, per model and prompt (counts only; no answer is tabulated):")
    for model in MODELS.values():
        for kind in KINDS:
            s = stats[f"{model}|{kind}"]
            print(f"  {model}, {kind}: {s['comments']} comments, {s['calls']} calls; mean tokens per call in "
                  f"{s['mean_input_tokens']:.0f}, out {s['mean_output_tokens']:.0f} (thinking {s['mean_thinking_tokens']:.0f}, "
                  f"largest out {s['max_output_tokens']}); refusals {s['refusals']}; no label after the retry "
                  f"{s['no_label_after_retry']}")
    for key, g in gates.items():
        print(f"  gate, {NAMES[key]}: refusals {g['refusals']} and no label {g['no_label_after_retry']} of {g['answers']} "
              f"answers: {'passes' if g['passes'] else 'FAILS: its later runs are not made'}")
    print(f"\nPlan of the stopping rule (estimates from the pilot at batch prices, plus 20%; measured spend now "
          f"{money(spend_now)}; ceiling US${CEILING_USD:.2f}):")
    for r in rows:
        cum = f", cumulative {money(r['cumulative'])}" if "cumulative" in r else ""
        print(f"  {r['run']}: estimate {money(r['estimate'])}{cum}: {r['outcome']}")
    v = manifest["versions"]
    geo = Counter(str(x.get("inference_geo") or "not reported") for x in unique_calls(read_jsonl(path)))
    lines = [f"- `models_07_frontier.py` (SHA-256 `{me}`) run {manifest['created']} with `--pilot`: 30 comments "
             f"(membership SHA-256 `{rec['info']['pilot_ids_sha256']}`), each model, each prompt; inference region reported by "
             f"the calls: {', '.join(f'{k} {n}' for k, n in sorted(geo.items()))}; "
             f"`pilot_log.jsonl` `{manifest['log']['sha256']}`; `pilot_manifest.json` `{mc.sha256_file(OUT / 'pilot_manifest.json')}`."]
    for model in MODELS.values():
        parts = []
        for kind in KINDS:
            s = stats[f"{model}|{kind}"]
            cats = ", ".join(f"{k} {n}" for k, n in sorted(s["refusal_categories"].items())) or "none"
            parts.append(f"{kind}: {s['calls']} calls, mean tokens in {s['mean_input_tokens']:.1f}, out "
                         f"{s['mean_output_tokens']:.1f} (thinking {s['mean_thinking_tokens']:.1f}); refusals "
                         f"{s['refusals']} ({cats}); no label after the retry {s['no_label_after_retry']}")
        lines.append(f"- `{model}`: " + "; ".join(parts) + ".")
    lines.append("- Gate (rule 5): " + "; ".join(
        f"{NAMES[k]} {'passes' if g['passes'] else 'fails'} (refusals {g['refusals']}, no label after the retry "
        f"{g['no_label_after_retry']}, of {g['answers']} answers)" for k, g in gates.items()) + ".")
    lines.append("- Plan (estimates at batch prices plus 20%): " + "; ".join(
        f"{r['run']} {money(r['estimate'])} {r['outcome']}" for r in rows)
        + f". Measured spend {money(spend_now)}; ceiling US${CEILING_USD:.2f}. Python {v['python']}, anthropic "
          f"{v['anthropic']}, NumPy {v['numpy']}, pandas {v['pandas']}.")
    show_block("pilot", lines)


def load_pilot() -> dict:
    path = OUT / "pilot_manifest.json"
    if not path.exists():
        stop("the pilot has not been run: python models_07_frontier.py --pilot")
    man = mc.read_json(path)
    if (man.get("script") or {}).get("sha256_lf") != own_sha256():
        stop(f"pilot_manifest.json was written by another version of this file. {REPORT}")
    if (man.get("log") or {}).get("sha256") != mc.sha256_file(OUT / "pilot_log.jsonl"):
        stop(f"pilot_log.jsonl has changed since the pilot was summarised. {REPORT}")
    return man


# =============================================================================
# --run: the batch runs
# =============================================================================
def read_stops() -> list:
    return read_jsonl(OUT / "stops.jsonl")


def ended_by_rule() -> dict | None:
    for s in read_stops():
        if s.get("event") in ("not_started", "halted"):
            return s
    return None


def minutes_since(iso: str) -> float:
    from datetime import datetime, timezone
    try:
        then = datetime.fromisoformat(iso)
    except ValueError:
        return 0.0
    return max((datetime.now(timezone.utc) - then).total_seconds() / 60, 0.0)


def append_record(path: Path, rec: dict) -> None:
    """One line, flushed to disk, after closing a torn last line."""
    OUT.mkdir(parents=True, exist_ok=True)
    close_torn_line(path)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def record_stop(event: str, run: str, reason: str, **extra) -> None:
    append_record(OUT / "stops.jsonl", {"event": event, "run": run, "reason": reason, "at": mc.now_iso(), **extra})


def read_run_log(run: str) -> tuple[dict, dict, set]:
    """Final records by id; the last unfinished record by id (its answered attempts and counted errors); and the
    custom ids already logged."""
    done, last, seen = {}, {}, set()
    for rec in read_jsonl(OUT / f"{run}_log.jsonl"):
        if rec.get("custom_id"):
            seen.add(rec["custom_id"])
        i = rec.get("id")
        if not i:
            continue
        if rec.get("status") in ("ok", "refusal", "unclassified"):
            done[i] = rec
        elif rec.get("status") in ("partial", "errored", "resend"):
            last[i] = rec
    return done, last, seen


def registry() -> list:
    return read_jsonl(OUT / "batches.jsonl")


def write_registry(rec: dict) -> None:
    append_record(OUT / "batches.jsonl", rec)


def open_submissions(run: str | None = None) -> list:
    """Batches whose creation was attempted and neither confirmed nor refused (rule 6)."""
    opened, closed = {}, set()
    for r in registry():
        if run is not None and r.get("run") != run:
            continue
        if r.get("event") == "submitting":
            opened[r["token"]] = r
        elif r.get("event") in ("submitted", "not_created") and r.get("token"):
            closed.add(r["token"])
    return [r for t, r in opened.items() if t not in closed]


def outstanding_batches(run: str) -> list:
    submitted, processed = {}, set()
    for r in registry():
        if r.get("run") != run:
            continue
        if r.get("event") == "submitted":
            submitted[r["batch_id"]] = r
        elif r.get("event") == "processed":
            processed.add(r["batch_id"])
    return [b for k, b in submitted.items() if k not in processed]


def outstanding(run: str) -> dict | None:
    left = outstanding_batches(run)
    if len(left) > 1:
        stop(f"{run}: more than one batch is outstanding. {REPORT}")
    return left[0] if left else None


def batch_size_of(b) -> int:
    rc = b.request_counts
    return int(rc.processing + rc.succeeded + rc.errored + rc.canceled + rc.expired)


def resolve_submissions(client) -> None:
    """Rule 6: before anything is sent, a batch whose creation was neither confirmed nor refused is looked for in the
    API's list of batches."""
    from datetime import datetime, timedelta
    pending = open_submissions()
    if not pending:
        return
    try:
        listed = list(client.messages.batches.list(limit=100).data)
    except Exception as e:                                  # noqa: BLE001 - reported to the user
        stop("the API's list of batches could not be read, and nothing was sent. Give the same command again.\n  "
             + explain(e))
    known = {r["batch_id"] for r in registry() if r.get("event") == "submitted"}
    window = timedelta(minutes=FOUND_WINDOW_MINUTES)
    for s in pending:
        at = datetime.fromisoformat(s["at"])
        found = [b for b in listed if b.id not in known and batch_size_of(b) == s["size"]
                 and abs(b.created_at - at) <= window]
        if len(found) > 1:
            stop(f"{s['run']}: {len(found)} batches in the API's list could be the batch whose creation was not "
                 f"confirmed (registry token {s['token']}): {', '.join(b.id for b in found)}. {REPORT}")
        if found:
            b = found[0]
            write_registry({"event": "submitted", "run": s["run"], "token": s["token"], "batch_id": b.id, "at": s["at"],
                            "requests": s["requests"], "found_in_the_list_of_batches": mc.now_iso()})
            known.add(b.id)
            print(f"{s['run']}: the batch whose creation was not confirmed is in the API's list of batches ({b.id}) "
                  f"and is taken as created.", flush=True)
        elif minutes_since(s["at"]) < SETTLE_MINUTES:
            when = (at + timedelta(minutes=SETTLE_MINUTES + 1)).astimezone().strftime("%H:%M")
            stop(f"{s['run']}: the batch whose creation was not confirmed is not in the API's list of batches yet. It "
                 f"may still appear there, so nothing was sent. Give the same command again after {when}.")
        else:
            write_registry({"event": "not_created", "run": s["run"], "token": s["token"], "at": mc.now_iso(),
                            "error": f"not in the API's list of batches {SETTLE_MINUTES} minutes or more after the "
                                     f"attempt"})
            print(f"{s['run']}: the batch whose creation was not confirmed is not in the API's list of batches "
                  f"{SETTLE_MINUTES} minutes after the attempt, so it was not created.", flush=True)


def sends_by_id(run: str) -> tuple[Counter, Counter]:
    """Per comment: the sends whose outcome was logged (they count towards the five of rule 6), and the highest send
    number used in any batch, so that every custom id of a comment is new."""
    logged = {}
    for rec in read_jsonl(OUT / f"{run}_log.jsonl"):
        if rec.get("id") and rec.get("custom_id"):
            logged.setdefault(rec["id"], set()).add(rec["custom_id"])
    highest = Counter()
    for r in registry():
        if r.get("run") == run and r.get("event") in ("submitting", "submitted"):
            for cid, i, n in r.get("requests", []):
                highest[i] = max(highest[i], int(n))
    return Counter({i: len(c) for i, c in logged.items()}), highest


def run_rates(run: str, stats: dict) -> tuple[float, float, str]:
    """Calls per comment and mean batch cost per call: the run's own once it has OWN_RATE_AFTER answered calls,
    the pilot's before (rule 7). A comment answered without a result yet needs one more call."""
    spec = RUNS[run]
    model = MODELS[spec["model"]]
    done, last, _ = read_run_log(run)
    calls = unique_calls([*done.values(), *last.values()])
    if len(calls) >= OWN_RATE_AFTER and done:
        cost = statistics.fmean(call_cost(model, a, "batch") for a in calls)
        waiting = sum(1 for i, r in last.items() if i not in done and any(a.get("message_id") for a in r.get("attempts", [])))
        return (len(calls) + waiting) / (len(done) + waiting), cost, "the run's own calls"
    s = stats[f"{model}|{spec['kind']}"]
    return s["calls_per_comment"], s["mean_batch_cost_per_call"], "the pilot"


def explain_result_error(err) -> tuple[str, str]:
    inner = getattr(err, "error", None)
    etype = str(getattr(inner, "type", "") or "")
    message = str(getattr(inner, "message", "") or "")
    return etype, message


def process_batch(run: str, batch, rec_items: dict, client, mcl, dep, version_seen: set) -> dict:
    """Log every result of an ended batch (rule 6). Returns counts; stops the run on a systemic error and, after
    logging the batch, on an answer from another model or version (rule 4)."""
    spec = RUNS[run]
    model, kind = MODELS[spec["model"]], spec["kind"]
    path = OUT / f"{run}_log.jsonl"
    close_torn_line(path)
    done, last, seen = read_run_log(run)
    reg = {cid: (i, n) for cid, i, n in batch["requests"]}
    results = list(client.messages.batches.results(batch["batch_id"]))
    counts = Counter()
    errored, systemic = [], []
    for res in results:
        cid = res.custom_id
        if cid not in reg:
            stop(f"{run}: the batch returned a custom id it was not sent ({cid}). {REPORT}")
        r = res.result
        rtype = getattr(r, "type", "")
        counts[rtype] += 1
        if rtype == "errored":
            etype, message = explain_result_error(r.error)
            errored.append((cid, etype, message))
            if etype in SYSTEMIC_ERRORS or etype not in TRANSIENT_ERRORS | COUNTED_ERRORS \
                    or any(w in message.lower() for w in SYSTEMIC_WORDS):
                systemic.append((cid, etype, message))
    if len(results) != len(reg):
        stop(f"{run}: the batch returned {len(results)} results for {len(reg)} requests. {REPORT}")
    halt_errors = bool(systemic) or len(errored) > ERROR_SHARE_STOP * len(reg)
    at = mc.now_iso()
    problems = []
    for res in results:
        cid = res.custom_id
        if cid in seen:
            continue                                        # logged before an interruption
        item_id, n = reg[cid]
        if item_id in done:
            continue
        r = res.result
        rtype = getattr(r, "type", "")
        prev = last.get(item_id, {})
        attempts = [dict(a) for a in prev.get("attempts", [])]
        counted = int(prev.get("counted_errors", 0))
        base = {"id": item_id, "custom_id": cid, "batch_id": batch["batch_id"], "send": n}
        if rtype == "succeeded":
            a = attempt_from_message(r.message, at, "batch", batch_id=batch["batch_id"], custom_id=cid)
            attempts.append(a)
            problem = None
            if not mcl.same_model(model, a["model"]):
                problem = f"MODEL_MISMATCH: asked for {model}, the API answered with {a['model']}"
            else:
                version_seen.add(a["model"])
                if len(version_seen) > 1:
                    problem = f"MODEL_CHANGED: answers from {sorted(version_seen)}"
            if problem is not None:                         # logged, so that its cost is measured (rule 4)
                problems.append(problem)
                out = {**base, "status": "partial", "attempts": attempts, "counted_errors": counted, "stopped": problem}
            elif a["stop_reason"] == "refusal":
                out = {**base, "status": no_answer(kind), "reason": "refusal_stop",
                       "refusal_category": a.get("refusal_category"), "label": "", "attempts": attempts,
                       "counted_errors": counted}
            else:
                label = parse(kind, a["text"], mcl, dep)
                answered = sum(1 for x in attempts if x.get("message_id"))
                if label is not None:
                    out = {**base, "status": "ok", "reason": "", "label": label, "attempts": attempts,
                           "counted_errors": counted}
                elif answered < 1 + cfg.NO_CLASS_RETRIES:
                    out = {**base, "status": "partial", "attempts": attempts, "counted_errors": counted}
                else:
                    out = {**base, "status": no_answer(kind), "reason": "no_label", "label": "", "attempts": attempts,
                           "counted_errors": counted}
            out["prompt_sha256"] = mc.text_sha256(rec_items[item_id])
        elif rtype == "errored":
            if halt_errors:
                continue                                    # not counted: the comment is sent again on resume
            etype, message = explain_result_error(r.error)
            if etype in COUNTED_ERRORS:
                counted += 1
                if counted >= 2:
                    out = {**base, "status": no_answer(kind), "reason": "api_error", "label": "",
                           "error": {"type": etype, "message": message[:500]}, "attempts": attempts,
                           "counted_errors": counted, "prompt_sha256": mc.text_sha256(rec_items[item_id])}
                else:
                    out = {**base, "status": "errored", "error": {"type": etype, "message": message[:500]},
                           "attempts": attempts, "counted_errors": counted}
            else:                                           # one of TRANSIENT_ERRORS: sent again
                out = {**base, "status": "resend", "error": {"type": etype, "message": message[:500]},
                       "attempts": attempts, "counted_errors": counted}
        else:                                               # expired or canceled: not processed, sent again
            out = {**base, "status": "resend", "result_type": rtype, "attempts": attempts, "counted_errors": counted}
        mcl.append_line(path, {"run": run, **out})
        if out["status"] in ("ok", "refusal", "unclassified"):
            done[item_id] = out
        else:
            last[item_id] = out
    minutes = round(minutes_since(batch["at"]), 2)
    if halt_errors:
        sample = (systemic or errored)[0]
        write_registry({"event": "processed", "run": run, "batch_id": batch["batch_id"], "at": mc.now_iso(),
                        "counts": dict(counts), "errors_not_counted": len(errored), "minutes": minutes})
        why = "an error that is not about the request" if systemic else \
            f"errors on {len(errored)} of {len(reg)} requests (more than 5%)"
        stop(f"{run} stopped: {why} (first: {sample[1]}: {sample[2][:200]}). The answered requests are kept; the "
             f"others are sent again when the same command is given again.\n  "
             + (explain(RuntimeError(sample[2])) if systemic else REPORT))
    write_registry({"event": "processed", "run": run, "batch_id": batch["batch_id"], "at": mc.now_iso(),
                    "counts": dict(counts), "minutes": minutes})
    if problems:
        stop(f"{run}: {problems[0]}" + (f" (and {len(problems) - 1} more answers)" if len(problems) > 1 else "")
             + f". The batch's results are logged, so that their cost is measured. A further deviation decides "
               f"(rule 4). {REPORT}")
    return dict(counts)


def wait_for(client, batch: dict, run: str, k: int, k_total: int, durations: list) -> None:
    started = time.time()
    while True:
        try:
            b = client.messages.batches.retrieve(batch["batch_id"])
        except Exception as e:                              # noqa: BLE001 - reported to the user
            stop(f"{run}: the batch could not be checked. It keeps running on the API side; give the same command "
                 f"again to resume.\n  " + explain(e))
        rc = b.request_counts
        if b.processing_status == "ended":
            return
        mean = statistics.fmean(durations) if durations else None
        left = f"; about {mean * (k_total - k + 1) / 60:.0f} min left for this run" if mean else ""
        print(f"  batch {k} of about {k_total}: {rc.processing} processing, {rc.succeeded} done, {rc.errored} errored "
              f"| waiting {(time.time() - started) / 60:.1f} min{left}", flush=True)
        try:
            time.sleep(POLL_SECONDS)
        except KeyboardInterrupt:
            stop(f"{run}: stopped by the user while waiting. The batch keeps running on the API side; give the same "
                 f"command again to resume.")


ESTIMATE_KEYS = ("at", "size", "estimate_rest_usd", "spend_usd", "ceiling_usd", "source", "calls_per_comment",
                 "cost_per_call_usd", "comments_without_a_result")


def assemble(run: str, rec_items: dict, me: str, inputs: dict) -> dict:
    spec = RUNS[run]
    model, kind = MODELS[spec["model"]], spec["kind"]
    pred_path, man_path, log_path = OUT / f"{run}_predictions.csv", OUT / f"{run}_manifest.json", OUT / f"{run}_log.jsonl"
    if man_path.exists() and pred_path.exists():
        old = mc.read_json(man_path)
        if (old.get("script") or {}).get("sha256_lf") == me and (old.get("log") or {}).get("sha256") == mc.sha256_file(log_path) \
                and (old.get("predictions") or {}).get("sha256") == mc.sha256_file(pred_path):
            old["manifest_sha256"] = mc.sha256_file(man_path)
            return old
    done, last, _ = read_run_log(run)
    ids = list(rec_items)
    missing = [i for i in ids if i not in done]
    if missing:
        stop(f"{run}: {len(missing)} comments have no result")
    header = ["id", "label", "status", "reason", "refusal_category", "attempts", "input_tokens", "output_tokens",
              "thinking_tokens", "answer_1", "answer_2", "message_ids", "batch_ids", "counted_errors"]
    rows = []
    for i in ids:
        r = done[i]
        a = r.get("attempts", [])
        rows.append([i, r.get("label", ""), r["status"], r.get("reason", ""), r.get("refusal_category") or "", len(a),
                     sum(x["input_tokens"] for x in a), sum(x["output_tokens"] for x in a),
                     sum(x.get("thinking_tokens") or 0 for x in a), a[0]["text"] if a else "",
                     a[1]["text"] if len(a) > 1 else "", ";".join(str(x.get("message_id")) for x in a),
                     ";".join(sorted({str(x.get("batch_id")) for x in a})), r.get("counted_errors", 0)])
    every = unique_calls([*done.values(), *last.values()])
    pred_sha = mc.write_rows_csv(pred_path, header, rows)
    entries = [r for r in registry() if r.get("run") == run]
    batches = sorted({b["batch_id"] for b in entries if b.get("event") == "submitted"})
    finals = Counter(r[2] for r in rows)
    reasons = Counter(r[3] for r in rows if r[2] != "ok")
    cats = Counter(r[4] or "none" for r in rows if r[3] == "refusal_stop")
    cost = sum(call_cost(model, x, "batch") for x in every)
    times = sorted(x["at"] for x in every)
    manifest = {
        "created": mc.now_iso(), "specification": "Deviation 15, docs/analysis_preregistration.md",
        "script": {"file": "models_07_frontier.py", "sha256_lf": me}, "run": run, "model": model,
        "answered_by": sorted({x["model"] for x in every}), "prompt": kind, "items": spec["items"],
        "request": {"max_tokens": MAX_TOKENS, "effort": EFFORT, "inference_geo": INFERENCE_GEO,
                    "temperature": "not sent", "system_prompt": None, "interface": "Message Batches API"},
        "no_class_retries": cfg.NO_CLASS_RETRIES, "comments": len(rows), "calls": len(every),
        "final_status": dict(finals), "no_answer_reasons": dict(reasons), "refusal_categories": dict(cats),
        "tokens": {"input": sum(x["input_tokens"] for x in every), "output": sum(x["output_tokens"] for x in every),
                   "thinking": sum(x.get("thinking_tokens") or 0 for x in every)},
        "inference_geo": dict(Counter(str(x.get("inference_geo") or "not reported") for x in every)),
        "service_tier": dict(Counter(str(x.get("service_tier") or "not reported") for x in every)),
        "prices_usd_per_mtok": PRICES[model], "batch_factor": BATCH_FACTOR, "cost_usd": round(cost, 6),
        "cost_usd_per_1000_comments": round(cost / len(rows) * 1000, 6),
        "cost_usd_per_1000_comments_standard": round(cost / BATCH_FACTOR / len(rows) * 1000, 6),
        "stopping_rule": {"ceiling_usd": CEILING_USD, "margin": MARGIN,
                          "at_the_start": [{k: e.get(k) for k in ("at", "comments", "estimate_usd", "spend_usd", "source")}
                                           for e in entries if e.get("event") == "started"],
                          "before_each_batch": [{k: e.get(k) for k in ESTIMATE_KEYS}
                                                for e in entries if e.get("event") == "submitting"]},
        "batches": batches, "access_window": {"first_result": times[0] if times else None,
                                              "last_result": times[-1] if times else None},
        "inputs": inputs, "predictions": {"file": f"data/models/frontier/{pred_path.name}", "sha256": pred_sha},
        "log": {"file": f"data/models/frontier/{log_path.name}", "sha256": mc.sha256_file(log_path)},
        "versions": mc.versions("anthropic", "pandas"),
    }
    mc.write_json(man_path, manifest)
    manifest["manifest_sha256"] = mc.sha256_file(man_path)
    return manifest


def run_complete(run: str, me: str) -> bool:
    man_path, log_path = OUT / f"{run}_manifest.json", OUT / f"{run}_log.jsonl"
    if not man_path.exists() or not log_path.exists():
        return False
    man = mc.read_json(man_path)
    return (man.get("script") or {}).get("sha256_lf") == me and \
        (man.get("log") or {}).get("sha256") == mc.sha256_file(OUT / f"{run}_log.jsonl")


def check_answers(model_key: str) -> None:
    problems = logged_problems(model_key)
    if problems:
        stop(f"MODEL_MISMATCH: {MODELS[model_key]}: {'; '.join(problems)}. A further deviation decides (rule 4). "
             f"{REPORT}")


def create_batch(client, run: str, model: str, reqs: list, rec_items: dict, token: str):
    """Rule 6: one attempt, no automatic retry. Returns the batch, or stops."""
    try:
        return client.with_options(timeout=CREATE_TIMEOUT_SECONDS, max_retries=0).messages.batches.create(
            requests=[{"custom_id": cid, "params": request_params(model, rec_items[i])} for cid, i, n in reqs])
    except Exception as e:                                  # noqa: BLE001 - reported to the user
        code = getattr(e, "status_code", None)
        if isinstance(code, int) and 400 <= code < 500 and code not in (408, 409, 429):
            write_registry({"event": "not_created", "run": run, "token": token, "at": mc.now_iso(),
                            "error": f"{type(e).__name__}: {str(e)[:300]}"})
            stop(f"{run}: the API refused the batch, so it was not created.\n  " + explain(e))
        stop(f"{run}: it is not known whether the batch was created, and nothing more was sent. Give the same command "
             f"again: the API's list of batches is checked first, and if the batch is not there yet the step waits "
             f"until {SETTLE_MINUTES} minutes after the attempt.\n  " + explain(e))


def run_one(run: str, rec: dict, pilot: dict, client, me: str) -> dict:
    spec = RUNS[run]
    model, kind = MODELS[spec["model"]], spec["kind"]
    mcl, dep = rec["mcl"], rec["dep"]
    rec_items = dict(rec["items"][run])
    stats = pilot["stats"]
    if outstanding(run) is None:
        check_answers(spec["model"])
    version_seen = answered_by(spec["model"])
    if open_submissions(run):
        stop(f"{run}: a batch whose creation was not confirmed is still open. {REPORT}")
    done, last, _ = read_run_log(run)
    first = not done and not last and outstanding(run) is None
    spend = measured_spend()
    if first:
        est = run_estimate(run, len(rec_items), stats)
        print(f"\n{run}: {len(rec_items):,} comments; estimate {money(est)} (the pilot, plus 20%); measured spend "
              f"{money(spend)}; ceiling US${CEILING_USD:.2f}", flush=True)
        if spend + est > CEILING_USD:
            record_stop("not_started", run, "the estimate added to the measured spend is above the ceiling",
                        estimate_usd=round(est, 6), spend_usd=round(spend, 6), ceiling_usd=CEILING_USD, source="the pilot")
            stop(f"{run} is not started: estimate {money(est)} + spend {money(spend)} is above the ceiling of "
                 f"US${CEILING_USD:.2f}. Under the stopping rule of Deviation 15 no later run is made. For the register "
                 f"lines of the stop, give:\n  {STOPS_COMMAND}")
        write_registry({"event": "started", "run": run, "at": mc.now_iso(), "comments": len(rec_items),
                        "estimate_usd": round(est, 6), "spend_usd": round(spend, 6), "ceiling_usd": CEILING_USD,
                        "source": "the pilot"})
    else:
        print(f"\n{run}: {len(rec_items):,} comments; {len(done):,} finished; resuming; measured spend {money(spend)}",
              flush=True)
    durations = [b["minutes"] * 60 for b in registry() if b.get("event") == "processed" and b.get("minutes")]
    while True:
        b = outstanding(run)
        if b is not None:
            k = sum(1 for r in registry() if r.get("run") == run and r.get("event") == "submitted")
            k_total = k + math.ceil(max(len(rec_items) - len(read_run_log(run)[0]) - len(b["requests"]), 0) / BATCH_SIZE)
            wait_for(client, b, run, k, k_total, durations)
            counts = process_batch(run, b, rec_items, client, mcl, dep, version_seen)
            durations.append(minutes_since(b["at"]) * 60)
            spend = measured_spend()
            done_now = len(read_run_log(run)[0])
            print(f"  batch {k} logged: {sum(counts.values())} results | {done_now:,}/{len(rec_items):,} comments "
                  f"finished | measured spend {money(spend)}", flush=True)
            if done_now < len(rec_items) and spend >= CEILING_USD:
                record_stop("halted", run, "the measured spend reached the ceiling", spend_usd=round(spend, 6),
                            ceiling_usd=CEILING_USD)
                stop(f"{run} halted: the measured spend {money(spend)} reached the ceiling. Under the stopping rule no "
                     f"later run is made; this run is incomplete and enters no figure. For the register lines of the "
                     f"stop, give:\n  {STOPS_COMMAND}")
            continue
        done, last, _ = read_run_log(run)
        logged, highest = sends_by_id(run)
        pending = [i for i in rec_items if i not in done]
        if not pending:
            break
        stuck = [i for i in pending if logged[i] >= MAX_SENDS]
        if stuck:
            stop(f"{run}: {len(stuck)} comments have {MAX_SENDS} logged sends without a result, e.g. {stuck[:3]}. A "
                 f"further deviation decides (rule 6). {REPORT}")
        cpc, cost_call, source = run_rates(run, stats)
        rest = len(pending) * cpc * cost_call * MARGIN
        spend = measured_spend()
        if spend + rest > CEILING_USD:
            record_stop("halted", run, "the estimate of the rest of the run no longer fits", estimate_usd=round(rest, 6),
                        spend_usd=round(spend, 6), ceiling_usd=CEILING_USD, source=source)
            stop(f"{run} halted before its next batch: the rest of the run is estimated at {money(rest)} (from {source}, "
                 f"plus 20%), and with the spend of {money(spend)} that is above the ceiling of US${CEILING_USD:.2f}. "
                 f"Under the stopping rule no later run is made; this run is incomplete and enters no figure. For the "
                 f"register lines of the stop, give:\n  {STOPS_COMMAND}")
        check_answers(spec["model"])                     # rule 4, before anything more is sent
        answered_so_far = len(unique_calls([*done.values(), *last.values()]))
        size = BATCH_SIZE if answered_so_far >= OWN_RATE_AFTER else min(FIRST_BATCH_SIZE, BATCH_SIZE)
        reqs = [[f"{spec['code']}{highest[i] + 1}-{i}", i, highest[i] + 1] for i in pending[:size]]
        token = f"{run}-{len(registry())}-{int(time.time())}"
        write_registry({"event": "submitting", "run": run, "token": token, "at": mc.now_iso(), "size": len(reqs),
                        "requests": reqs, "estimate_rest_usd": round(rest, 6), "spend_usd": round(spend, 6),
                        "ceiling_usd": CEILING_USD, "source": source, "calls_per_comment": round(cpc, 6),
                        "cost_per_call_usd": round(cost_call, 8), "comments_without_a_result": len(pending)})
        created = create_batch(client, run, model, reqs, rec_items, token)
        write_registry({"event": "submitted", "run": run, "token": token, "batch_id": created.id, "at": mc.now_iso(),
                        "requests": reqs})
        print(f"  batch submitted: {len(reqs):,} requests ({created.id}); {len(pending):,} comments still without a "
              f"result; estimate of the rest {money(rest)} (from {source})", flush=True)
    inputs = rec["info"]["inputs"]
    man = assemble(run, rec_items, me, inputs)
    print(f"{run}: done | {man['comments']:,} comments | calls {man['calls']:,} | refusals "
          f"{man['final_status'].get('refusal', 0)} | unclassified {man['final_status'].get('unclassified', 0)} | cost "
          f"{money(man['cost_usd'])} | measured spend {money(measured_spend())}", flush=True)
    return man


def outstanding_any() -> list:
    """Runs with a submitted batch that is not yet processed."""
    return [run for run in RUNS if outstanding_batches(run)]


def run_lines(run: str, man: dict) -> str:
    st = man["final_status"]
    cats = ", ".join(f"{k} {n}" for k, n in sorted(man["refusal_categories"].items())) or "none"
    reasons = ", ".join(f"{k} {n}" for k, n in sorted(man["no_answer_reasons"].items())) or "none"
    geo = ", ".join(f"{k} {n:,}" for k, n in sorted((man.get("inference_geo") or {}).items())) or "not recorded"
    return (f"- `{run}` (`{man['model']}`, {man['prompt']} prompt, answered by `{', '.join(man['answered_by'])}`): "
            f"{man['comments']:,} comments; calls {man['calls']:,}; with a label {st.get('ok', 0):,}; refusals "
            f"{st.get('refusal', 0)}; unclassified {st.get('unclassified', 0)} (reasons: {reasons}; refusal "
            f"categories: {cats}); tokens in {man['tokens']['input']:,}, out {man['tokens']['output']:,} (thinking "
            f"{man['tokens']['thinking']:,}); inference region reported by the calls: {geo}; cost {money(man['cost_usd'])} "
            f"({money(man['cost_usd_per_1000_comments'])} per 1,000 comments at batch prices); "
            f"{len(man['batches'])} batches, first result {man['access_window']['first_result']}, last "
            f"{man['access_window']['last_result']}. `{run}_predictions.csv` `{man['predictions']['sha256']}`; "
            f"`{run}_log.jsonl` `{man['log']['sha256']}`; `{run}_manifest.json` `{man['manifest_sha256']}`.")


def file_hashes(names: tuple) -> str:
    found = [f"`{n}` `{mc.sha256_file(OUT / n)}`" for n in names if (OUT / n).exists()]
    return "; ".join(found) if found else "none"


def run_step(step: str) -> None:
    me = own_sha256()
    print(f"Deviation 15: step {step}\nthis script: models_07_frontier.py SHA-256 {me}")
    rec = load_record()
    pilot = load_pilot()
    if not passed_connection():
        stop("no passing connection check under the committed settings. Run --check-connection first.")
    gates = pilot["gate"]
    position = ORDER.index(step)
    for earlier in ORDER[:position]:
        if gates[STEP_MODEL[earlier]]["passes"] and not all(run_complete(r, me) for r in STEPS[earlier]):
            stop(f"{step} cannot start before {earlier} is complete (rule 8).")
    if not gates[STEP_MODEL[step]]["passes"]:
        stop(f"{step}: {NAMES[STEP_MODEL[step]]} failed the pilot gate, so its runs are not made (rule 5).")
    mcl = rec["mcl"]
    client = mcl.make_client()
    lines = []
    with RunLock():
        resolve_submissions(client)
        ended = ended_by_rule()
        if ended is not None:
            stop(f"the runs of Deviation 15 ended under the stopping rule at {ended['run']} "
                 f"({ended['event'].replace('_', ' ')}): no later run is made.")
        others = [r for r in outstanding_any() if r not in STEPS[step]]
        if others:
            stop(f"a batch of {others[0]} is outstanding; finish that step first.")
        for run in STEPS[step]:
            if run_complete(run, me):
                man = mc.read_json(OUT / f"{run}_manifest.json")
                man["manifest_sha256"] = mc.sha256_file(OUT / f"{run}_manifest.json")
                print(f"\n{run}: already complete")
            else:
                man = run_one(run, rec, pilot, client, me)
            lines.append(run_lines(run, man))
    spend = measured_spend()
    v = mc.versions("anthropic", "pandas")
    lines.insert(0, f"- `models_07_frontier.py` (SHA-256 `{me}`) with `--run {step}`: measured spend of Deviation 15 "
                    f"after the step {money(spend)} (ceiling US${CEILING_USD:.2f}). Python {v['python']}, anthropic "
                    f"{v['anthropic']}, pandas {v['pandas']}.")
    lines.append(f"- Batch registry after the step: {file_hashes(('batches.jsonl',))}.")
    print(f"\nstep {step}: done | measured spend {money(spend)} of the US${CEILING_USD:.2f} ceiling")
    show_block(step, lines)


# =============================================================================
# --status and --stops
# =============================================================================
def status() -> None:
    me = own_sha256()
    print(f"Deviation 15: status\nthis script: models_07_frontier.py SHA-256 {me}")
    print(f"connection check passed: {'yes' if passed_connection() else 'no'}")
    pm = OUT / "pilot_manifest.json"
    print(f"pilot: {'done' if pm.exists() else 'not run'}")
    for run in RUNS:
        done, last, _ = read_run_log(run)
        state = "complete" if run_complete(run, me) else (f"{len(done):,} comments finished" if done or last else "not started")
        if outstanding_batches(run):
            state += "; a batch is outstanding"
        if open_submissions(run):
            state += "; a batch whose creation was not confirmed (checked when the step is given again)"
        print(f"  {run}: {state}")
    for s in read_stops():
        print(f"  stop: {s['event'].replace('_', ' ')} at {s['run']}: {s['reason']}")
    print(f"measured spend {money(measured_spend())} of the US${CEILING_USD:.2f} ceiling")


def halted_line(run: str) -> str:
    spec = RUNS[run]
    model = MODELS[spec["model"]]
    path = OUT / f"{run}_log.jsonl"
    done, last, _ = read_run_log(run)
    every = unique_calls(read_jsonl(path))
    finals = Counter(r["status"] for r in done.values())
    n = STAGE2_EVAL_ITEMS if spec["items"] == "eval" else CORPUS_STAGE2_ITEMS
    cost = sum(call_cost(model, x, "batch") for x in every)
    return (f"- `{run}` (`{model}`, {spec['kind']} prompt), halted and incomplete: {len(done):,} of {n:,} comments with a "
            f"result (with a label {finals.get('ok', 0):,}; refusals {finals.get('refusal', 0)}; unclassified "
            f"{finals.get('unclassified', 0)}); calls {len(every):,}; tokens in {sum(x['input_tokens'] for x in every):,}, "
            f"out {sum(x['output_tokens'] for x in every):,} (thinking "
            f"{sum(x.get('thinking_tokens') or 0 for x in every):,}); cost {money(cost)} at batch prices. "
            f"`{run}_log.jsonl` `{mc.sha256_file(path) if path.exists() else 'no log'}`. It has no predictions file "
            f"and enters no figure.")


def stops_block() -> None:
    me = own_sha256()
    rows = read_stops()
    if not rows:
        print("No run was not made or halted under the stopping rule.")
        return
    lines = [f"- `models_07_frontier.py` (SHA-256 `{me}`) with `--stops`: measured spend of Deviation 15 "
             f"{money(measured_spend())} (ceiling US${CEILING_USD:.2f})."]
    for s in rows:
        detail = [f"{k} {money(s[key])}" for k, key in (("estimate", "estimate_usd"), ("spend", "spend_usd"))
                  if key in s]
        if "ceiling_usd" in s:
            detail.append(f"ceiling US${s['ceiling_usd']:.2f}")
        if "source" in s:
            detail.append(f"from {s['source']}")
        lines.append(f"- {s['run']} {s['event'].replace('_', ' ')} at {s['at']}: {s['reason']}"
                     + (f" ({', '.join(detail)})" if detail else "") + ".")
    steps = []
    for s in rows:
        if STEP_OF.get(s["run"]) and STEP_OF[s["run"]] not in steps:
            steps.append(STEP_OF[s["run"]])
    for step in steps:
        for run in STEPS[step]:
            if run_complete(run, me):
                man = mc.read_json(OUT / f"{run}_manifest.json")
                man["manifest_sha256"] = mc.sha256_file(OUT / f"{run}_manifest.json")
                lines.append(run_lines(run, man))
            elif any(s["run"] == run and s["event"] == "halted" for s in rows):
                lines.append(halted_line(run))
    lines.append(f"- {file_hashes(('batches.jsonl', 'stops.jsonl'))}.")
    show_block("stops", lines)


# =============================================================================
# main
# =============================================================================
def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Exploratory runs of Claude Opus 5.5 and Claude Fable 5.1 (Deviation 15).")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true", help="before the commit: checks only; sends and writes nothing")
    mode.add_argument("--check-connection", action="store_true", help="six requests on the test sentence")
    mode.add_argument("--pilot", action="store_true", help="the pilot of Deviation 15")
    mode.add_argument("--run", choices=ORDER, help="one step of the order of runs")
    mode.add_argument("--status", action="store_true", help="the state of every run; sends nothing")
    mode.add_argument("--stops", action="store_true", help="the register lines of runs not made or halted")
    args = ap.parse_args()
    if args.preflight:
        preflight()
    elif args.check_connection:
        check_connection()
    elif args.pilot:
        run_pilot()
    elif args.run:
        run_step(args.run)
    elif args.status:
        status()
    else:
        stops_block()


if __name__ == "__main__":
    main()
