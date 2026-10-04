"""Tranche 2, step 2: BART-MNLI pre-filter scores for every frame item.

Standalone on purpose: it imports nothing from the repository, so it can run on
any machine with a GPU (for example a Colab T4) given only prefilter_input.csv.

    python tranche2_02_score_prefilter.py --input prefilter_input.csv --output prefilter_scores.csv

What it does (Deviation 10):
  - premise = the comment text alone (no subreddit), truncated to the model's
    maximum input length;
  - four hypotheses: one for Stage 1 relevance, one for each Stage 2 class;
  - relevance probability = the entailment share of a softmax over the entailment
    and contradiction logits of the relevance hypothesis; predicted relevant at >= 0.5;
  - predicted class = the class hypothesis with the highest entailment logit
    (a tie goes to the first of CONCERN, ENDORSEMENT, OTHER);
  - predicted label = N when not predicted relevant, otherwise the predicted class.

All twelve raw logits are kept for every item, rounded to six decimal places,
and every derived column is computed from the rounded values, so the output
file can be re-derived from itself.

A comment that contains a literal control string of the tokenizer (for example
"</s>") has that string spaced out for the model input only; the ids are logged
in the manifest.

The output file, once written, is the frozen record. A second run on other
hardware can differ in the last decimal place and is not a substitute for it.

The wording below is part of the pre-commitment. Do not change it after
Deviation 10 is committed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

# torch and transformers are imported inside main(), so that step 3 can import
# derive() and the specification from this file on a machine without them.

# ---- pre-committed pre-filter specification (Deviation 10) ---------------------
MODEL_ID = "facebook/bart-large-mnli"
MODEL_REVISION = "main"          # resolved to a commit hash at the start of the run
RELEVANCE_THRESHOLD = 0.5
CLASSES = ["CONCERN", "ENDORSEMENT", "OTHER"]
HYPOTHESES = {
    "relevance": "This comment is about self-driving or connected vehicles, driver-assistance systems such as "
                 "Autopilot, robotaxis, or the sensors, software or data of such vehicles.",
    "CONCERN": "This comment expresses worry, doubt or criticism about self-driving or connected vehicle technology.",
    "ENDORSEMENT": "This comment expresses support, approval or optimism about self-driving or connected "
                   "vehicle technology.",
    "OTHER": "This comment is neutral or factual and takes no position on self-driving or connected "
             "vehicle technology.",
}
# -------------------------------------------------------------------------------

HYP_NAMES = list(HYPOTHESES)                      # relevance, CONCERN, ENDORSEMENT, OTHER
NLI = ["contra", "neutral", "entail"]
LOGIT_COLS = [f"lg_{h}_{n}" for h in HYP_NAMES for n in NLI]
_LOGIT_TEXT = re.compile(r"^-?\d+\.\d{6}$")


def derive(df: pd.DataFrame, threshold: float = RELEVANCE_THRESHOLD) -> pd.DataFrame:
    """Derived columns from the (rounded) logits. Step 3 repeats this to verify the file."""
    out = df.copy()
    ent = out["lg_relevance_entail"].to_numpy(dtype=np.float64)
    con = out["lg_relevance_contra"].to_numpy(dtype=np.float64)
    p_rel = 1.0 / (1.0 + np.exp(-(ent - con)))
    cls = np.stack([out[f"lg_{k}_entail"].to_numpy(dtype=np.float64) for k in CLASSES], axis=1)
    z = cls - cls.max(axis=1, keepdims=True)
    p_cls = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
    pred_class = np.array(CLASSES)[cls.argmax(axis=1)]          # ties -> first in CLASSES order
    pred_rel = p_rel >= threshold
    out["p_relevant"] = p_rel
    for j, k in enumerate(CLASSES):
        out[f"p_{k}"] = p_cls[:, j]
    out["pred_relevant"] = np.where(pred_rel, "Y", "N")
    out["pred_class"] = pred_class
    out["pred_label"] = np.where(pred_rel, pred_class, "N")
    out["confidence"] = p_cls.max(axis=1)
    return out


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def stop(message: str) -> None:
    print("\nSTOPPED: " + message)
    sys.exit(1)


def spec_fingerprint(model_name: str, commit, input_sha: str, max_len: int, precision: str) -> str:
    payload = json.dumps({"model": model_name, "commit": commit, "hypotheses": HYPOTHESES, "input": input_sha,
                          "max_len": max_len, "precision": precision}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def resolve_commit(model_name: str, revision: str):
    """The commit hash of the model files on the Hugging Face hub, or None for a local folder."""
    if Path(model_name).exists():
        return None, "local folder"
    try:
        from huggingface_hub import HfApi
        sha = HfApi().model_info(model_name, revision=revision).sha
        if sha:
            return str(sha), "huggingface_hub.HfApi.model_info"
        return None, "the hub returned no commit hash"
    except Exception as e:                              # noqa: BLE001 - reported to the user below
        return None, repr(e)


def read_partial(path: Path, valid_ids: set) -> dict:
    """Rows already scored. Only complete, well-formed rows are trusted: an interrupted write
    can leave a torn last line, which is dropped and scored again."""
    done: dict[str, list[float]] = {}
    with open(path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows or rows[0] != ["id"] + LOGIT_COLS:
        stop(f"{path.name} has an unexpected header. Delete it and its .json file, then run again.")
    body = rows[1:]
    for n, r in enumerate(body):
        good = (len(r) == 1 + len(LOGIT_COLS) and r[0] in valid_ids and r[0] not in done
                and all(_LOGIT_TEXT.match(x) for x in r[1:]))
        if good:
            done[r[0]] = [float(x) for x in r[1:]]
        elif n == len(body) - 1:
            print(f"  note: the last line of {path.name} was incomplete and is scored again")
        else:
            stop(f"{path.name} is damaged at line {n + 2}. Delete it and its .json file, then run again.")
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id"] + LOGIT_COLS)
        for i, vals in done.items():
            w.writerow([i] + [f"{v:.6f}" for v in vals])
    os.replace(tmp, path)
    return done


def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(description="BART-MNLI pre-filter scores for the tranche 2 draw frame.")
    ap.add_argument("--input", default="prefilter_input.csv")
    ap.add_argument("--output", default="prefilter_scores.csv")
    ap.add_argument("--model", default=MODEL_ID, help="leave at the default for the run of record")
    ap.add_argument("--revision", default=MODEL_REVISION)
    ap.add_argument("--device", default=None, help="cuda / mps / cpu (default: best available)")
    ap.add_argument("--token-budget", type=int, default=None,
                    help="tokens per forward pass (default 24000 on GPU, 6000 on CPU)")
    ap.add_argument("--fp16", action="store_true", help="half precision on GPU (off for the run of record)")
    ap.add_argument("--limit", type=int, default=None,
                    help="smoke test: score only the first N ids; writes <output>.smoke.csv and no manifest")
    ap.add_argument("--allow-unknown-commit", action="store_true",
                    help="go on even if the model commit cannot be read from the hub (record why)")
    args = ap.parse_args()

    import torch
    import transformers
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    in_path, out_path = Path(args.input), Path(args.output)
    if not in_path.exists():
        stop(f"input file not found: {in_path}")
    data = pd.read_csv(in_path, dtype=str, keep_default_na=False, encoding="utf-8")
    if list(data.columns) != ["id", "text"]:
        stop(f"expected columns id,text in {in_path}; found {list(data.columns)}")
    if data["id"].duplicated().any() or (data["text"].str.strip() == "").any():
        stop("the input has duplicate ids or empty text")
    data = data.sort_values("id").reset_index(drop=True)
    input_sha = sha256_file(in_path)
    if args.limit:
        data = data.head(args.limit).copy()
        out_path = out_path.with_suffix(".smoke.csv")
    else:
        # a finished scores file is the frozen record: it is never scored again
        done_manifest = out_path.with_name(out_path.stem + "_manifest.json")
        if out_path.exists() and done_manifest.exists():
            with open(done_manifest, encoding="utf-8") as f:
                old_manifest = json.load(f)
            if (old_manifest.get("output_sha256") == sha256_file(out_path)
                    and old_manifest.get("input_sha256") == input_sha):
                print(f"{out_path.name} is already complete and matches its manifest. It is the frozen record and is "
                      f"not scored again.")
                print(f"scores SHA-256 {old_manifest['output_sha256']}")
                return
            stop(f"{out_path.name} and {done_manifest.name} are here but do not match each other or this input file.")
    print(f"input: {len(data):,} items from {in_path.name} (SHA-256 {input_sha[:16]}...)")

    device = args.device or ("cuda" if torch.cuda.is_available()
                             else "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
                             else "cpu")
    budget = args.token_budget or (24000 if device == "cuda" else 6000)
    precision = "fp16" if (args.fp16 and device == "cuda") else "fp32"
    print(f"device: {device} ({precision}) | torch {torch.__version__} | transformers {transformers.__version__}")
    if device == "cpu":
        print("NOTE: on a CPU this takes hours. A GPU run takes minutes.")

    # --- the model, pinned to a commit ----------------------------------------------
    local = Path(args.model).exists()
    commit, how = resolve_commit(args.model, args.revision)
    if commit is None and not local and not args.allow_unknown_commit:
        stop(f"could not read the model commit from the Hugging Face hub ({how}).\n"
             f"  Deviation 10 requires it in the manifest. Check the connection and run again, or pass\n"
             f"  --allow-unknown-commit and record why.")
    load_kwargs = {} if local else {"revision": commit or args.revision}
    tok = AutoTokenizer.from_pretrained(args.model, **load_kwargs)
    model = AutoModelForSequenceClassification.from_pretrained(args.model, **load_kwargs)
    model.eval().to(device)
    if precision == "fp16":
        model.half()
    seen = getattr(model.config, "_commit_hash", None)
    if commit and seen and seen != commit:
        stop(f"the loaded model reports commit {seen}, not the resolved {commit}")

    label2id = {str(k).lower(): int(v) for k, v in model.config.label2id.items()}

    def label_index(prefix: str) -> int:
        hits = [v for k, v in label2id.items() if k.startswith(prefix)]
        if len(hits) != 1:
            stop(f"cannot identify the `{prefix}` label in the model config: {model.config.label2id}")
        return hits[0]

    idx = {"contra": label_index("contra"), "neutral": label_index("neutral"), "entail": label_index("entail")}
    print(f"model: {args.model} at commit {commit} | NLI label indices {idx}")

    max_len = int(min(tok.model_max_length, getattr(model.config, "max_position_embeddings", 1024)))
    hyp_len = max(len(tok(h, add_special_tokens=False, verbose=False)["input_ids"]) for h in HYPOTHESES.values())
    overhead = hyp_len + 4                               # <s> premise </s></s> hypothesis </s>

    # --- literal control strings inside a comment (e.g. "</s>") would be read as control
    #     tokens; they are spaced out for the model input only, and logged.
    specials = [t for t in tok.all_special_tokens if t]
    texts = data["text"].tolist()
    sanitised_ids = []
    for j, t in enumerate(texts):
        if any(s in t for s in specials):
            for s in specials:
                t = t.replace(s, s[0] + " " + s[1:])
            texts[j] = t
            sanitised_ids.append(data["id"].iloc[j])
    special_ids = set(tok.all_special_ids)
    premise_tokens = []
    for start in range(0, len(texts), 1000):
        enc = tok(texts[start:start + 1000], add_special_tokens=False, verbose=False)["input_ids"]
        for k, ids in enumerate(enc):
            if special_ids.intersection(ids):
                stop(f"comment {data['id'].iloc[start + k]} still tokenises to a control token after sanitising")
            premise_tokens.append(len(ids))
    data["n_tokens"] = premise_tokens
    data["truncated"] = np.where(data["n_tokens"] + overhead > max_len, "Y", "N")
    print(f"tokens per comment: median {int(np.median(premise_tokens))}, max {max(premise_tokens)} | "
          f"truncated at {max_len}: {int((data['truncated'] == 'Y').sum())} | "
          f"control strings spaced out: {len(sanitised_ids)}")

    # --- resume support -----------------------------------------------------------
    partial = out_path.with_suffix(".partial.csv")
    meta = out_path.with_suffix(".partial.json")
    fingerprint = spec_fingerprint(args.model, commit, input_sha, max_len, precision)
    done: dict[str, list[float]] = {}
    if partial.exists():
        old = json.load(open(meta, encoding="utf-8")) if meta.exists() else {}
        if old.get("fingerprint") != fingerprint:
            stop(f"{partial.name} was produced with a different input, model, wording or precision. "
                 f"Delete {partial.name} and {meta.name}, then run again.")
        done = read_partial(partial, set(data["id"]))
        info = {"fingerprint": fingerprint, "sessions": int(old.get("sessions", 1)) + 1,
                "first_started": old.get("first_started")}
        print(f"resuming: {len(done):,} items already scored (session {info['sessions']})")
    else:
        with open(partial, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(["id"] + LOGIT_COLS)
        info = {"fingerprint": fingerprint, "sessions": 1, "first_started": now_iso()}
    with open(meta, "w", encoding="utf-8") as f:
        json.dump(info, f)

    order = [int(j) for j in np.argsort(-data["n_tokens"].to_numpy(), kind="stable") if data["id"].iloc[j] not in done]
    hyps = [HYPOTHESES[h] for h in HYP_NAMES]

    def forward(rows: list[int]):
        """Logits (len(rows), 4, 3) ordered contra, neutral, entail; None if the GPU ran out of memory."""
        prem = [texts[j] for j in rows]
        enc = tok([p for _ in hyps for p in prem], [h for h in hyps for _ in prem],
                  truncation="only_first", max_length=max_len, padding=True, return_tensors="pt")
        if tok.eos_token_id is not None:               # BART pools on the last </s>; counts must agree
            eos = (enc["input_ids"] == tok.eos_token_id).sum(dim=1)
            if int(eos.min()) != int(eos.max()):
                stop("unequal numbers of end-of-sequence tokens in a batch; please report this")
        try:
            with torch.inference_mode():
                logits = model(**{k: v.to(device) for k, v in enc.items()}).logits.float().cpu().numpy()
        except RuntimeError as e:
            if "out of memory" not in str(e).lower():
                raise
            return None
        logits = logits.reshape(len(hyps), len(rows), -1).transpose(1, 0, 2)
        return logits[:, :, [idx["contra"], idx["neutral"], idx["entail"]]]

    def score(rows: list[int]) -> np.ndarray:
        out = forward(rows)
        if out is not None:
            return out
        if len(rows) == 1:
            stop("out of memory on a single comment. Run again with a smaller --token-budget.")
        if device == "cuda":
            torch.cuda.empty_cache()
        half = len(rows) // 2
        return np.concatenate([score(rows[:half]), score(rows[half:])], axis=0)

    started = time.time()
    n_total, n_done_start = len(order), len(done)
    pos = 0
    batch_no = 0
    with open(partial, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        while pos < n_total:
            longest = min(int(data["n_tokens"].iloc[order[pos]]) + overhead, max_len)
            n_items = max(1, budget // (len(hyps) * longest))
            rows = order[pos:pos + n_items]
            lg = score(rows)
            for j, vals in zip(rows, lg.reshape(len(rows), -1)):
                vals = [round(float(v), 6) for v in vals]
                if not all(np.isfinite(vals)):
                    stop(f"non-finite logits for id {data['id'].iloc[j]}")
                writer.writerow([data["id"].iloc[j]] + [f"{v:.6f}" for v in vals])
                done[data["id"].iloc[j]] = vals
            f.flush()
            os.fsync(f.fileno())
            pos += len(rows)
            batch_no += 1
            if batch_no % 10 == 0 or pos == n_total:
                elapsed = time.time() - started
                rate = pos / elapsed if elapsed > 0 else 0.0
                eta = (n_total - pos) / rate if rate > 0 else float("nan")
                print(f"  {n_done_start + pos:,}/{len(data):,} items | {rate:5.1f} items/s | "
                      f"elapsed {elapsed / 60:5.1f} min | remaining ~{eta / 60:5.1f} min", flush=True)

    # --- assemble, derive, write --------------------------------------------------
    missing = [i for i in data["id"] if i not in done]
    if missing:
        stop(f"{len(missing)} items have no scores")
    logits = pd.DataFrame([done[i] for i in data["id"]], columns=LOGIT_COLS).astype(float).round(6)
    table = pd.concat([data[["id", "n_tokens", "truncated"]].reset_index(drop=True), logits], axis=1)
    table = derive(table)
    table.to_csv(out_path, index=False, encoding="utf-8", lineterminator="\n", float_format="%.6f")
    counts = {k: int((table["pred_label"] == k).sum()) for k in ["N"] + CLASSES}
    n_rel = len(table) - counts["N"]
    # No count is displayed. Counts by predicted label go to the manifest only: the annotators,
    # the author included, stay blind to them (Deviation 10). Only a pass/fail check is shown.
    print(f"\nwrote {out_path} ({len(table):,} rows)")
    if not args.limit:
        if n_rel < 1000:
            print("WARNING: very few items are predicted relevant. Check that the model is the committed one.")
        else:
            print("check passed: at least 1,000 items are predicted relevant (the number is not displayed)")

    if args.limit:
        print("smoke test only: no manifest written, and the partial files are removed.")
        partial.unlink(missing_ok=True)
        meta.unlink(missing_ok=True)
        return

    manifest = {
        "created": now_iso(),
        "specification": "Deviation 10, docs/analysis_preregistration.md",
        "model": args.model,
        "revision_requested": args.revision,
        "model_commit_hash": commit,
        "model_commit_resolved_by": how,
        "nli_label_indices": idx,
        "hypotheses": HYPOTHESES,
        "relevance_threshold": RELEVANCE_THRESHOLD,
        "premise": "comment text only; truncation='only_first'",
        "max_length_tokens": max_len,
        "truncated_items": int((table["truncated"] == "Y").sum()),
        "control_strings_spaced_out_ids": sanitised_ids,
        "input_file": in_path.name,
        "input_sha256": input_sha,
        "rows": int(len(table)),
        "output_file": out_path.name,
        "output_sha256": sha256_file(out_path),
        "predicted_label_counts_all_frame_items": counts,
        "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "precision": precision,
        "token_budget_last_session": budget,
        "sessions": info["sessions"],
        "first_started": info["first_started"],
        "runtime_minutes_last_session": round((time.time() - started) / 60, 2),
        "versions": {"python": platform.python_version(), "torch": torch.__version__,
                     "transformers": transformers.__version__, "numpy": np.__version__,
                     "pandas": pd.__version__},
    }
    man_path = out_path.with_name(out_path.stem + "_manifest.json")
    with open(man_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    partial.unlink(missing_ok=True)
    meta.unlink(missing_ok=True)
    print(f"wrote {man_path}")
    print(f"scores SHA-256 {manifest['output_sha256']}")
    print("\nNext: copy both files into data/tranche2/ and run  python tranche2_03_allocate.py")
    print("Do not open either file: they hold every item's predicted label (sealed under Deviation 10).")


if __name__ == "__main__":
    main()
