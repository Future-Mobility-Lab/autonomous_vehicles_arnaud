"""Model comparison, step 2 (on the PC): Claude Haiku 4.5 and Claude Sonnet 4.6, zero-shot,
under the universal and the domain-specific label schema (four configurations).

Run from the repository folder, with the virtual environment active and the API key set:
    python models_02_claude.py --check-connection     one call per model on a test sentence
    python models_02_claude.py                        all four configurations, every annotated item
The second command refuses to start until the first has passed under the committed settings.

The key is read from the environment variable ANTHROPIC_API_KEY and is never printed or saved.

What it does (Deviation 12; settings in models_config.py):
  - every one of the 1,000 annotated items, once per configuration, comment text only;
  - the prompt is the reference study's shared zero-shot template, word for word, with the
    configuration's three labels; temperature 0, at most 50 output tokens, no system prompt;
  - the answer is read by exact match, then by a single label phrase inside it;
  - an answer that names no class is retried once with the same prompt; a second such answer
    is recorded as a refusal and scored as an error. Connection errors and overload are retried
    by the client and do not count as that retry. Each answered call is logged before the
    retry is sent, so an item cut off part-way resumes from its recorded answers; only a call
    under way at a hard stop (a closed window, a power cut) is lost unanswered, as a connection
    error would be;
  - the run halts for review when the measured spend reaches the ceiling in models_config.py;
  - the API must answer under the identifier asked for (or that identifier plus a date), and
    every call of a configuration must be answered by the same model version, or the run stops;
  - every call is logged (tokens, time, request id) so that the run can resume and the cost
    per 1,000 comments and the access window are measured.

It sets no prediction against a label and prints no count by predicted class.

Writes, in data/models/claude/:
  <config>_log.jsonl          one line per item (both attempts), appended as the run goes
  <config>_predictions.csv    id, pred_class, status, attempts, tokens, raw answers
  <config>_manifest.json      settings, refusal rate, tokens, cost, access window, hashes
"""
from __future__ import annotations

import argparse
import json
import os
import re
import threading
import time
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait

import pandas as pd

import models_common as mc
import models_config as cfg

OUT_DIR = cfg.MODELS_DIR / "claude"
INPUT = cfg.MODELS_DIR / "zero_shot_input.csv"
TEST_SENTENCE = "This is a test sentence used only to check the connection."


# =============================================================================
# prompt and parsing (fixed by models_config.py)
# =============================================================================
def label_block(schema: str) -> str:
    labels = cfg.SCHEMAS[schema]
    return "\n".join(cfg.LABEL_BLOCK_LINE.format(label=labels[c]) for c in cfg.CLASSES)


def build_prompt(schema: str, text: str) -> str:
    return cfg.PROMPT_TEMPLATE.format(label_block=label_block(schema), text=text)


# Characters stripped from both ends of an answer before matching: spaces, quotation marks
# (straight and curly), backticks, asterisks, underscores, full stops, colons, semicolons,
# exclamation marks, hyphens and bullets.
_EDGE = " \t\r\n\"'`*_.:;!-\u2022\u201c\u201d\u2018\u2019"


def normalise(text: str) -> str:
    t = re.sub(r"\s+", " ", str(text)).strip().lower()
    return t.strip(_EDGE).strip()


def parse_answer(text: str, schema: str):
    """The class named by an answer: exact match first, then a single label phrase inside it."""
    labels = {c: normalise(p) for c, p in cfg.SCHEMAS[schema].items()}
    t = normalise(text)
    if not t:
        return None
    for c, p in labels.items():
        if t == p:
            return c
    hits = [c for c, p in labels.items() if p in t]
    return hits[0] if len(hits) == 1 else None


# =============================================================================
# the API
# =============================================================================
def make_client():
    try:
        import anthropic
    except ImportError:
        mc.stop("the anthropic package is not installed in this environment. "
                f"Install the pinned version: pip install anthropic=={cfg.ANTHROPIC_SDK_VERSION}")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        mc.stop("the environment variable ANTHROPIC_API_KEY is not set in this terminal.")
    if anthropic.__version__ != cfg.ANTHROPIC_SDK_VERSION:
        mc.stop(f"anthropic {anthropic.__version__} is installed; this run uses {cfg.ANTHROPIC_SDK_VERSION}. "
                f"Install it: pip install anthropic=={cfg.ANTHROPIC_SDK_VERSION}")
    return anthropic.Anthropic(max_retries=cfg.CLAUDE_TRANSPORT_RETRIES, timeout=cfg.CLAUDE_TIMEOUT_SECONDS)


def request_body(model: str, prompt: str) -> dict:
    """The request as committed: one user message, no system prompt, temperature 0, 50 tokens.
    Version 1 of the Anthropic Python SDK no longer takes temperature as a keyword, so it is
    sent in the request body; the API still accepts it for these two models."""
    return {"model": model, "max_tokens": cfg.CLAUDE_SETTINGS["max_tokens"],
            "messages": [{"role": "user", "content": prompt}],
            "extra_body": {"temperature": cfg.CLAUDE_SETTINGS["temperature"]}}


def same_model(requested: str, returned: str) -> bool:
    """The API must answer with the identifier asked for, or with that identifier plus a date."""
    return re.fullmatch(re.escape(requested) + r"(-\d{8})?", returned or "") is not None


def call(client, model: str, prompt: str) -> dict:
    """One answered call. The caller checks the model identifier the API reports (`model`)."""
    started = mc.now_iso()
    msg = client.messages.create(**request_body(model, prompt))
    text = "".join(getattr(b, "text", "") or "" for b in (msg.content or []) if getattr(b, "type", "") == "text")
    usage = getattr(msg, "usage", None)
    return {"at": started, "message_id": getattr(msg, "id", None),
            "request_id": getattr(msg, "_request_id", None), "model": str(getattr(msg, "model", "") or ""),
            "stop_reason": getattr(msg, "stop_reason", None), "text": text,
            "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
            "output_tokens": int(getattr(usage, "output_tokens", 0) or 0)}


def mismatch(model: str, attempt: dict) -> str:
    return f"MODEL_MISMATCH: asked for {model}, the API answered with {attempt['model'] or 'no model name'}"


def explain(e: Exception) -> str:
    name = type(e).__name__
    later = "Run the same command again later: finished items are kept."
    hints = {"AuthenticationError": "the API key was refused. Check ANTHROPIC_API_KEY.",
             "PermissionDeniedError": "the API key may not use this model. Take this message to Claude.",
             "NotFoundError": "the model identifier was not found. Take this message to Claude; do not change it.",
             "BadRequestError": "the API refused the request. Take this message to Claude; do not change "
                                "anything in the scripts.",
             "UnprocessableEntityError": "the API refused the request. Take this message to Claude.",
             "RequestTooLargeError": "the request was too large. Take this message to Claude.",
             "RateLimitError": "rate limit or spending limit reached after all retries. Wait a few minutes, "
                               "then run the same command again: finished items are kept.",
             "APIConnectionError": "no connection after all retries. " + later,
             "APITimeoutError": "the API timed out after all retries. " + later,
             "DeadlineExceededError": "the API timed out after all retries. " + later,
             "InternalServerError": "the API was unavailable after all retries. " + later,
             "ServiceUnavailableError": "the API was unavailable after all retries. " + later,
             "OverloadedError": "the API was overloaded after all retries. " + later}
    if "temperature" in str(e).lower():
        hint = "the API refused temperature 0 for this model. Take this message to Claude; do not change anything."
    elif "credit balance" in str(e).lower():
        hint = "the account's credit balance is too low. Add credit in the Claude Console, then " + later[0].lower() \
               + later[1:]
    else:
        hint = hints.get(name, "Take this message to Claude.")
    return f"{name}: {e}\n  {hint}"


# =============================================================================
# one configuration
# =============================================================================
def read_log(path) -> tuple[dict, list]:
    """Items finished in an earlier session, and the records of items not finished: a "partial"
    record keeps an answered call before its retry is sent, an "interrupted" one the calls of an
    item cut off by an error. Their calls are billed, so they count towards cost, and an
    unfinished item resumes from the last of them. A torn last line (interrupted write) is ignored."""
    done, cut_off = {}, []
    if not path.exists():
        return done, cut_off
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("status") in ("ok", "refusal") and rec.get("id"):
                done[rec["id"]] = rec
            elif rec.get("status") in ("partial", "interrupted"):
                cut_off.append(rec)
    return done, cut_off


def append_line(path, rec: dict) -> None:
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def call_cost(model: str, attempt: dict) -> float:
    price = cfg.CLAUDE_PRICES_USD_PER_MTOK[model]
    return attempt["input_tokens"] * price["input"] / 1e6 + attempt["output_tokens"] * price["output"] / 1e6


def unique_calls(records) -> list:
    """Every answered call in the records, once. A call carried from a cut-off record into the
    item's final record appears in both, so calls are told apart by the API's message id."""
    seen, calls = set(), []
    for r in records:
        for x in r["attempts"]:
            key = x.get("message_id") or (x["at"], x["text"], x["input_tokens"], x["output_tokens"])
            if key not in seen:
                seen.add(key)
                calls.append(x)
    return calls


def read_connection_checks() -> list:
    path = OUT_DIR / "connection_check.jsonl"
    out = []
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


def spent_so_far() -> float:
    """Measured spend of every call logged so far: all four configurations and the connection checks."""
    total = 0.0
    for config in cfg.CLAUDE_CONFIGS:
        model = cfg.CLAUDE_MODELS[config.split("-")[0]]
        done, cut_off = read_log(OUT_DIR / f"{config}_log.jsonl")
        total += sum(call_cost(model, x) for x in unique_calls([*done.values(), *cut_off]))
    for x in read_connection_checks():
        try:
            total += call_cost(x.get("requested") or cfg.CLAUDE_MODELS[x["family"]], x)
        except KeyError:
            continue
    return total


def run_config(client, config: str, items: pd.DataFrame, input_sha: str, spend: dict) -> dict:
    family, schema = config.split("-")
    model = cfg.CLAUDE_MODELS[family]
    log_path = OUT_DIR / f"{config}_log.jsonl"
    done, cut_off = read_log(log_path)
    fingerprint = mc.text_sha256(json.dumps({"model": model, "schema": schema, "template": cfg.PROMPT_TEMPLATE,
                                             "labels": cfg.SCHEMAS[schema], "settings": cfg.CLAUDE_SETTINGS,
                                             "input": input_sha}, sort_keys=True))
    if any(r.get("fingerprint") != fingerprint for r in [*done.values(), *cut_off]):
        mc.stop(f"{log_path.name} holds items from a different input, model or wording. Take this to Claude.")
    todo = [(i, t) for i, t in zip(items["id"], items["text"]) if i not in done]
    print(f"\n{config}: model {model} | {len(done)} items already done, {len(todo)} to do", flush=True)
    if log_path.exists() and log_path.stat().st_size:           # close a line torn by an interruption
        with open(log_path, "rb") as f:
            f.seek(-1, os.SEEK_END)
            torn = f.read(1) != b"\n"
        if torn:
            with open(log_path, "a", encoding="utf-8", newline="\n") as f:
                f.write("\n")

    lock = threading.Lock()
    counter = {"n": len(done), "refusals": sum(r["status"] == "refusal" for r in done.values())}
    # Every call of a configuration must be answered under the identifier asked for, by one and
    # the same model version.
    answered_by = {x["model"] for x in unique_calls([*done.values(), *cut_off])}
    wrong = sorted(m for m in answered_by if not same_model(model, m))
    if wrong:
        mc.stop(f"MODEL_MISMATCH: {log_path.name} holds answers from {wrong}, not {model}. Take this to Claude.")
    if len(answered_by) > 1:
        mc.stop(f"MODEL_CHANGED: {log_path.name} holds answers from {sorted(answered_by)}. Take this to Claude.")
    # An item cut off part-way resumes where it stopped: its answered calls are kept, so that no
    # item gets more than the one retry of Deviation 12. The last cut-off record of an item holds
    # all its answered calls.
    partial = {r["id"]: r["attempts"] for r in cut_off if r["id"] not in done}
    started = time.time()

    def work(item_id: str, text: str) -> None:
        prompt = build_prompt(schema, text)
        attempts, pred = [dict(a) for a in partial.get(item_id, [])], None
        for a in attempts:
            a["parsed"] = parse_answer(a["text"], schema)
            if a["parsed"] is not None:
                pred = a["parsed"]
                break
        try:
            while pred is None and len(attempts) < 1 + cfg.NO_CLASS_RETRIES:
                a = call(client, model, prompt)
                attempts.append(a)
                with lock:
                    if not same_model(model, a["model"]):
                        raise RuntimeError(mismatch(model, a))
                    answered_by.add(a["model"])
                    if len(answered_by) > 1:
                        raise RuntimeError(f"MODEL_CHANGED: {config} has answers from {sorted(answered_by)}")
                    spend["usd"] += call_cost(model, a)
                    if spend["usd"] >= cfg.CLAUDE_SPEND_CEILING_USD:
                        raise RuntimeError(f"SPEND_CEILING: measured spend US${spend['usd']:.2f} has reached the "
                                           f"ceiling of US${cfg.CLAUDE_SPEND_CEILING_USD:.2f} (O26). Halt and review")
                a["parsed"] = parse_answer(a["text"], schema)
                if a["parsed"] is not None:
                    pred = a["parsed"]
                elif len(attempts) < 1 + cfg.NO_CLASS_RETRIES:      # log the answered call before the retry
                    with lock:
                        append_line(log_path, {"id": item_id, "config": config, "fingerprint": fingerprint,
                                               "status": "partial", "attempts": attempts})
        except Exception:
            if attempts:                 # an answered call is billed: keep it, and resume from it
                with lock:
                    append_line(log_path, {"id": item_id, "config": config, "fingerprint": fingerprint,
                                           "status": "interrupted", "attempts": attempts})
            raise
        rec = {"id": item_id, "config": config, "fingerprint": fingerprint,
               "prompt_sha256": mc.text_sha256(prompt),
               "status": "ok" if pred else "refusal", "pred_class": pred or "", "attempts": attempts}
        with lock:
            append_line(log_path, rec)
            done[item_id] = rec
            counter["n"] += 1
            counter["refusals"] += pred is None
            if counter["n"] % 50 == 0 or counter["n"] == len(items):
                rate = (counter["n"] - (len(items) - len(todo))) / max(time.time() - started, 1e-9)
                left = (len(items) - counter["n"]) / rate / 60 if rate > 0 else float("nan")
                print(f"  {counter['n']:,}/{len(items):,} items | refusals so far {counter['refusals']} | "
                      f"~{left:4.1f} min left", flush=True)

    if todo:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        first_error, interrupted = None, False
        with ThreadPoolExecutor(max_workers=cfg.CLAUDE_CONCURRENCY) as pool:
            futures = [pool.submit(work, i, t) for i, t in todo]
            try:
                while True:                      # short waits, so that Ctrl+C is seen on Windows too
                    finished, pending = wait(futures, timeout=1, return_when=FIRST_EXCEPTION)
                    errors = [f.exception() for f in finished if f.exception() is not None]
                    if errors or not pending:
                        break
            except KeyboardInterrupt:            # Ctrl+C: stop cleanly
                errors, interrupted = [], True
            if errors or interrupted:
                first_error = errors[0] if errors else None
                for f in futures:
                    f.cancel()                   # calls already under way finish before the stop
        if interrupted:
            mc.stop(f"{config} stopped by the user. {counter['n']} of {len(items)} items are finished and kept; "
                    f"run the same command again to continue.")
        if first_error is not None:
            e = first_error
            kept = f"{counter['n']} of {len(items)} items are finished and kept."
            if str(e).startswith(("MODEL_MISMATCH", "MODEL_CHANGED", "SPEND_CEILING")):
                mc.stop(f"{config}: {e}\n  {kept} Take this message to Claude.")
            mc.stop(f"{config} stopped. {kept}\n  " + explain(e))

    # ---- assemble, from the log as written ------------------------------------------------
    done, cut_off = read_log(log_path)
    missing = [i for i in items["id"] if i not in done]
    if missing:
        mc.stop(f"{config}: {len(missing)} items have no result")
    rows = []
    for i in items["id"]:
        r = done[i]
        a = r["attempts"]
        rows.append([i, r["pred_class"], r["status"], len(a), sum(x["input_tokens"] for x in a),
                     sum(x["output_tokens"] for x in a), a[0]["text"], a[1]["text"] if len(a) > 1 else "",
                     ";".join(str(x["request_id"]) for x in a)])
    final_calls = unique_calls([done[i] for i in items["id"]])
    every_call = unique_calls([done[i] for i in items["id"]] + cut_off)   # with billed calls of cut-off items
    extra = every_call[len(final_calls):]
    tokens_in = sum(x["input_tokens"] for x in every_call)
    tokens_out = sum(x["output_tokens"] for x in every_call)
    calls = len(every_call)
    times = [x["at"] for x in every_call]
    answered_by = {x["model"] for x in every_call}
    pred_path = OUT_DIR / f"{config}_predictions.csv"
    pred_sha = mc.write_rows_csv(pred_path, ["id", "pred_class", "status", "attempts", "input_tokens",
                                             "output_tokens", "answer_1", "answer_2", "request_ids"], rows)
    price = cfg.CLAUDE_PRICES_USD_PER_MTOK[model]
    cost = tokens_in * price["input"] / 1e6 + tokens_out * price["output"] / 1e6
    refusals = sum(1 for r in rows if r[2] == "refusal")
    stop_reasons = {}
    for x in every_call:
        stop_reasons[str(x["stop_reason"])] = stop_reasons.get(str(x["stop_reason"]), 0) + 1
    manifest = {
        "created": mc.now_iso(),
        "specification": "Deviation 12, docs/analysis_preregistration.md; models_config.py",
        "config": config, "model": model, "answered_by": sorted(answered_by), "schema": schema,
        "labels": cfg.SCHEMAS[schema],
        "prompt_template": cfg.PROMPT_TEMPLATE, "label_block": label_block(schema),
        "settings": cfg.CLAUDE_SETTINGS, "no_class_retries": cfg.NO_CLASS_RETRIES,
        "concurrency": cfg.CLAUDE_CONCURRENCY, "timeout_seconds": cfg.CLAUDE_TIMEOUT_SECONDS,
        "transport_retries": cfg.CLAUDE_TRANSPORT_RETRIES, "stop_reasons": stop_reasons,
        "items": len(rows), "calls": calls, "calls_on_items_cut_off": len(extra),
        "refusals": refusals, "refusal_rate": refusals / len(rows),
        "retried_items": sum(1 for r in rows if r[3] > 1),
        "tokens": {"input": tokens_in, "output": tokens_out},
        "prices_usd_per_mtok": price, "cost_usd": round(cost, 6),
        "cost_usd_per_1000_comments": round(cost / len(rows) * 1000, 6),
        "access_window": {"first_call": min(times), "last_call": max(times)},
        "input": {"file": "data/models/zero_shot_input.csv", "sha256": input_sha},
        "predictions": {"file": f"data/models/claude/{pred_path.name}", "sha256": pred_sha},
        "log": {"file": f"data/models/claude/{log_path.name}", "sha256": mc.sha256_file(log_path)},
        "versions": mc.versions("anthropic", "pandas"),
    }
    mc.write_json(OUT_DIR / f"{config}_manifest.json", manifest)
    print(f"{config}: done | refusals {refusals} of {len(rows)} | tokens in {tokens_in:,}, out {tokens_out:,} | "
          f"cost US${cost:.4f} (US${cost / len(rows) * 1000:.4f} per 1,000 comments) | "
          f"first call {min(times)}, last call {max(times)}")
    return manifest


def check_connection(client) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Connection check: one call per model on a test sentence (no annotated item is sent), "
          f"with the committed settings (temperature {cfg.CLAUDE_SETTINGS['temperature']}, "
          f"at most {cfg.CLAUDE_SETTINGS['max_tokens']} output tokens, no system prompt).")
    for family, model in cfg.CLAUDE_MODELS.items():
        try:
            a = call(client, model, build_prompt("universal", TEST_SENTENCE))
        except Exception as e:                           # noqa: BLE001 - reported to the user
            mc.stop(f"{model}: " + explain(e))
        a["parsed"] = parse_answer(a["text"], "universal")
        ok = same_model(model, a["model"])
        append_line(OUT_DIR / "connection_check.jsonl",
                    {"family": family, "requested": model, "passed": ok, "settings": cfg.CLAUDE_SETTINGS,
                     "sdk": cfg.ANTHROPIC_SDK_VERSION, **a})
        if not ok:
            mc.stop(mismatch(model, a) + "\n  Take this message to Claude.")
        print(f"  {model}: answered by {a['model']} (stop reason {a['stop_reason']}, "
              f"{a['input_tokens']} input tokens); the answer "
              f"{'names' if a['parsed'] else 'does not name'} one of the three labels")
    print("Connection check passed: the key works, both models accept the settings, and both answer "
          "under the identifiers asked for.")


def connection_checked(models) -> list:
    """Models with no passing connection check under the committed settings and client version."""
    passed = {x.get("requested") for x in read_connection_checks()
              if x.get("passed") is True and x.get("settings") == cfg.CLAUDE_SETTINGS
              and x.get("sdk") == cfg.ANTHROPIC_SDK_VERSION}
    return [m for m in models if m not in passed]


def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Claude zero-shot runs (Deviation 12).")
    ap.add_argument("--check-connection", action="store_true", help="one call per model on a test sentence")
    ap.add_argument("--config", choices=cfg.CLAUDE_CONFIGS + ["all"], default="all")
    args = ap.parse_args()

    client = make_client()
    if args.check_connection:
        check_connection(client)
        return
    if not INPUT.exists():
        mc.stop(f"{INPUT} not found. Run models_01_prepare.py first.")
    items = pd.read_csv(INPUT, dtype=str, keep_default_na=False, encoding="utf-8")
    input_sha = mc.sha256_file(INPUT)
    prep = cfg.MODELS_DIR / "prepare_manifest.json"
    if not prep.exists():
        mc.stop(f"{prep} not found. Run models_01_prepare.py first.")
    if mc.read_json(prep)["inputs"]["zero_shot_input"]["sha256"] != input_sha:
        mc.stop("zero_shot_input.csv is not the file models_01_prepare.py wrote. Run step 1 again.")
    if list(items.columns) != ["id", "text"] or len(items) != 1000 or items["id"].duplicated().any():
        mc.stop("zero_shot_input.csv must hold the 1,000 annotated items with the columns id,text")
    configs = cfg.CLAUDE_CONFIGS if args.config == "all" else [args.config]
    unchecked = connection_checked(sorted({cfg.CLAUDE_MODELS[c.split("-")[0]] for c in configs}))
    if unchecked:
        mc.stop(f"no passing connection check for {', '.join(unchecked)}. Run the check first (it sends no "
                f"annotated item):\n  python models_02_claude.py --check-connection")
    spend = {"usd": spent_so_far()}
    print(f"input: {len(items)} items (SHA-256 {input_sha[:16]}...) | configurations: {', '.join(configs)}")
    print(f"measured spend so far: US${spend['usd']:.4f} of the US${cfg.CLAUDE_SPEND_CEILING_USD:.2f} ceiling")
    if spend["usd"] >= cfg.CLAUDE_SPEND_CEILING_USD:
        mc.stop("the spending ceiling has been reached (O26). Halt and review: take this message to Claude.")
    for config in configs:
        run_config(client, config, items, input_sha, spend)
    print(f"\nAll requested configurations are complete. Measured spend so far: US${spent_so_far():.4f}. "
          "No prediction was set against a label.")


if __name__ == "__main__":
    main()
