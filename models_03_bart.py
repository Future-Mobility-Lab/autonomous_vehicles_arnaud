"""Model comparison, step 3: BART-MNLI zero-shot, under the two label schemas (Deviation 12).

  python models_03_bart.py --schema universal
      Scores the three universal hypotheses for the 1,000 annotated items. Use a GPU (for example
      Colab: upload models_config.py, models_common.py, this file and zero_shot_input.csv); a CPU
      works but is slow. The method is the pre-filter's (tranche2_02_score_prefilter.py at 64a64a8):
      premise = comment text, truncated to the model's maximum length; predicted class = the class
      hypothesis with the highest entailment logit, a tie going to CONCERN, ENDORSEMENT, OTHER in
      that order; logits rounded to six decimal places; fp32; model pinned to a commit.

  python models_03_bart.py --schema domain --confirm-unsealed
      The domain-specific schema is the three class hypotheses of Deviation 10. Its predictions are
      taken from the frozen pre-filter scores and not re-run. This reads prefilter_scores.csv,
      which stays sealed until the model scripts are committed: run it only after that commit.

It sets no prediction against a label and prints no count by predicted class.
Writes, in data/models/bart/ (or --out-dir): bart_<schema>_predictions.csv and a manifest.
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

import models_common as mc
import models_config as cfg

# The Deviation 10 class hypotheses, word for word (tranche2_02_score_prefilter.py at 64a64a8).
# The domain-specific schema must reproduce them exactly.
DEVIATION10_CLASS_HYPOTHESES = {
    "CONCERN": "This comment expresses worry, doubt or criticism about self-driving or connected vehicle technology.",
    "ENDORSEMENT": "This comment expresses support, approval or optimism about self-driving or connected "
                   "vehicle technology.",
    "OTHER": "This comment is neutral or factual and takes no position on self-driving or connected "
             "vehicle technology.",
}
NLI = ["contra", "neutral", "entail"]


def hypotheses(schema: str) -> dict:
    return {c: cfg.BART_HYPOTHESIS.format(label=cfg.SCHEMAS[schema][c]) for c in cfg.CLASSES}


def predicted_class(df: pd.DataFrame) -> np.ndarray:
    ent = np.stack([df[f"lg_{c}_entail"].to_numpy(dtype=np.float64) for c in cfg.CLASSES], axis=1)
    return np.array(cfg.CLASSES)[ent.argmax(axis=1)]                # ties -> first in CLASSES order


def read_items(path: Path) -> pd.DataFrame:
    if not path.exists():
        mc.stop(f"{path} not found. Run models_01_prepare.py first, or pass --input.")
    items = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    if list(items.columns) != ["id", "text"] or len(items) != 1000 or items["id"].duplicated().any():
        mc.stop(f"{path.name} must hold the 1,000 annotated items with the columns id,text")
    return items.sort_values("id").reset_index(drop=True)


# =============================================================================
# domain-specific schema: from the frozen pre-filter scores
# =============================================================================
def run_domain(items: pd.DataFrame, input_sha: str, out_dir: Path) -> None:
    if hypotheses("domain") != DEVIATION10_CLASS_HYPOTHESES:
        mc.stop("the domain-specific schema does not reproduce the Deviation 10 class hypotheses")
    if not cfg.PREFILTER_SCORES.exists():
        mc.stop(f"{cfg.PREFILTER_SCORES} not found")
    scores_sha = mc.sha256_file(cfg.PREFILTER_SCORES)
    if scores_sha != cfg.PREFILTER_SCORES_SHA256:          # the authoritative check: recorded at 01f3d8a
        mc.stop(f"prefilter_scores.csv has SHA-256 {scores_sha[:8]}..., not the {cfg.PREFILTER_SCORES_SHA256[:8]}... "
                f"recorded at 01f3d8a. Take this message to Claude.")
    print(f"frozen scores: prefilter_scores.csv matches the SHA-256 recorded at 01f3d8a ({scores_sha[:16]}...)")
    # The manifest, where present, must agree with the record (the scores file is the reference).
    man = mc.read_json(cfg.PREFILTER_SCORES_MANIFEST) if cfg.PREFILTER_SCORES_MANIFEST.exists() else {}
    if man.get("output_sha256") not in (None, scores_sha):
        mc.stop("prefilter_scores_manifest.json gives a different SHA-256 for the scores. Take this to Claude.")
    hyps = man.get("hypotheses") or {}
    if any(k in hyps and hyps[k] != DEVIATION10_CLASS_HYPOTHESES[k] for k in cfg.CLASSES):
        mc.stop("the manifest's class hypotheses are not those of Deviation 10. Take this to Claude.")
    commit = man.get("model_commit_hash") or cfg.PREFILTER_MODEL_COMMIT
    if commit != cfg.PREFILTER_MODEL_COMMIT or commit != cfg.CHECKPOINTS["bart_mnli"]["commit"]:
        mc.stop(f"the frozen scores' model commit {commit} is not the recorded and pinned "
                f"{cfg.PREFILTER_MODEL_COMMIT}. Take this to Claude.")
    same = True
    scores = pd.read_csv(cfg.PREFILTER_SCORES, dtype={"id": str}, keep_default_na=False, encoding="utf-8")
    need = [f"lg_{c}_entail" for c in cfg.CLASSES]
    if "id" not in scores.columns or any(c not in scores.columns for c in need):
        mc.stop(f"prefilter_scores.csv lacks the columns id and {need}; it has {list(scores.columns)[:30]}. "
                f"Take this to Claude.")
    scores = scores.set_index("id")
    missing = [i for i in items["id"] if i not in scores.index]
    if missing:
        mc.stop(f"{len(missing)} annotated items are not in the frozen scores, e.g. {missing[:5]}")
    sub = scores.loc[items["id"]].reset_index()
    recomputed = predicted_class(sub)
    if "pred_class" in sub.columns:                        # where it holds a class, it must agree
        held = sub["pred_class"].astype(str).to_numpy()
        named = np.isin(held, cfg.CLASSES)
        if not (held[named] == recomputed[named]).all():
            mc.stop("the pred_class column of the frozen scores disagrees with its own logits")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "bart_domain_predictions.csv"
    cols = [f"lg_{c}_entail" for c in cfg.CLASSES]
    sha = mc.write_rows_csv(path, ["id", "pred_class"] + cols,
                            [[i, p] + [f"{float(v):.6f}" for v in vals]
                             for i, p, vals in zip(sub["id"], recomputed, sub[cols].to_numpy())])
    mc.write_json(out_dir / "bart_domain_manifest.json", {
        "created": mc.now_iso(),
        "specification": "Deviation 12: domain-specific schema = Deviation 10 class hypotheses, from the frozen "
                         "pre-filter scores, not re-run",
        "hypotheses": DEVIATION10_CLASS_HYPOTHESES,
        "frozen_scores": {"file": "data/tranche2/prefilter_scores.csv", "sha256": scores_sha},
        "frozen_model_commit": commit, "same_commit_as_pinned_for_universal": same,
        "items": len(sub), "input_sha256": input_sha,
        "predictions": {"file": f"{path.name}", "sha256": sha},
    })
    print(f"domain-specific schema: {len(sub)} items taken from the frozen scores; model commit {commit}, "
          f"the same as the commit pinned for the universal run")
    print(f"wrote {path} (SHA-256 {sha[:16]}...)")


# =============================================================================
# universal schema: a new run, same method as the pre-filter
# =============================================================================
def run_universal(items: pd.DataFrame, input_sha: str, out_dir: Path, device_arg, token_budget, test_model_dir):
    import torch
    import transformers
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    mc.check_run_libraries(["transformers"])
    if cfg.CHECKPOINTS["bart_mnli"]["commit"] != cfg.PREFILTER_MODEL_COMMIT:
        mc.stop("the pinned BART-MNLI commit is not the commit of the frozen pre-filter scores")
    hyps = hypotheses("universal")
    names = list(cfg.CLASSES)
    device = device_arg or ("cuda" if torch.cuda.is_available()
                            else "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
                            else "cpu")
    budget = token_budget or (24000 if device == "cuda" else 6000)
    print(f"device: {device} (fp32) | torch {torch.__version__} | transformers {transformers.__version__}")
    if test_model_dir:
        repo, commit, load = test_model_dir, None, {}
        print("TEST MODEL: not the run of record")
    else:
        repo, commit = cfg.CHECKPOINTS["bart_mnli"]["repo"], cfg.CHECKPOINTS["bart_mnli"]["commit"]
        load = {"revision": commit}
    tok = AutoTokenizer.from_pretrained(repo, **load)
    model = AutoModelForSequenceClassification.from_pretrained(repo, dtype=torch.float32, **load)
    model.eval().to(device)
    seen = getattr(model.config, "_commit_hash", None)
    if commit and seen and seen != commit:
        mc.stop(f"the loaded model reports commit {seen}, not the pinned {commit}")
    label2id = {str(k).lower(): int(v) for k, v in model.config.label2id.items()}

    def label_index(prefix: str) -> int:
        hits = [v for k, v in label2id.items() if k.startswith(prefix)]
        if len(hits) != 1:
            mc.stop(f"cannot identify the `{prefix}` label in the model config: {model.config.label2id}")
        return hits[0]

    idx = {n: label_index(n) for n in NLI}
    max_len = int(min(tok.model_max_length, getattr(model.config, "max_position_embeddings", 1024)))
    hyp_len = max(len(tok(h, add_special_tokens=False, verbose=False)["input_ids"]) for h in hyps.values())
    overhead = hyp_len + 4
    specials = [t for t in tok.all_special_tokens if t]
    texts = items["text"].tolist()
    sanitised = []
    for j, t in enumerate(texts):
        if any(s in t for s in specials):
            for s in specials:
                t = t.replace(s, s[0] + " " + s[1:])
            texts[j] = t
            sanitised.append(items["id"].iloc[j])
    special_ids = set(tok.all_special_ids)
    n_tokens = []
    for start in range(0, len(texts), 1000):
        enc = tok(texts[start:start + 1000], add_special_tokens=False, verbose=False)["input_ids"]
        for k, ids in enumerate(enc):
            if special_ids.intersection(ids):
                mc.stop(f"comment {items['id'].iloc[start + k]} still tokenises to a control token")
            n_tokens.append(len(ids))
    items = items.assign(n_tokens=n_tokens)
    items["truncated"] = np.where(items["n_tokens"] + overhead > max_len, "Y", "N")
    order = [int(j) for j in np.argsort(-items["n_tokens"].to_numpy(), kind="stable")]
    hyp_list = [hyps[n] for n in names]

    def forward(rows):
        prem = [texts[j] for j in rows]
        enc = tok([p for _ in hyp_list for p in prem], [h for h in hyp_list for _ in prem],
                  truncation="only_first", max_length=max_len, padding=True, return_tensors="pt")
        if tok.eos_token_id is not None:
            eos = (enc["input_ids"] == tok.eos_token_id).sum(dim=1)
            if int(eos.min()) != int(eos.max()):
                mc.stop("unequal numbers of end-of-sequence tokens in a batch; take this to Claude")
        try:
            with torch.inference_mode():
                logits = model(**{k: v.to(device) for k, v in enc.items()}).logits.float().cpu().numpy()
        except RuntimeError as e:
            if "out of memory" not in str(e).lower():
                raise
            return None
        logits = logits.reshape(len(hyp_list), len(rows), -1).transpose(1, 0, 2)
        return logits[:, :, [idx["contra"], idx["neutral"], idx["entail"]]]

    def score(rows):
        out = forward(rows)
        if out is not None:
            return out
        if len(rows) == 1:
            mc.stop("out of memory on a single comment; run again with a smaller --token-budget")
        if device == "cuda":
            torch.cuda.empty_cache()
        half = len(rows) // 2
        return np.concatenate([score(rows[:half]), score(rows[half:])], axis=0)

    started = time.time()
    done = {}
    pos = 0
    while pos < len(order):
        longest = min(int(items["n_tokens"].iloc[order[pos]]) + overhead, max_len)
        n = max(1, budget // (len(hyp_list) * longest))
        rows = order[pos:pos + n]
        lg = score(rows)
        for j, vals in zip(rows, lg.reshape(len(rows), -1)):
            vals = [round(float(v), 6) for v in vals]
            if not all(np.isfinite(vals)):
                mc.stop(f"non-finite logits for id {items['id'].iloc[j]}")
            done[items["id"].iloc[j]] = vals
        pos += len(rows)
    cols = [f"lg_{h}_{n}" for h in names for n in NLI]
    table = pd.concat([items[["id", "n_tokens", "truncated"]].reset_index(drop=True),
                       pd.DataFrame([done[i] for i in items["id"]], columns=cols).astype(float).round(6)], axis=1)
    table["pred_class"] = predicted_class(table)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "bart_universal_predictions.csv"
    table.to_csv(path, index=False, encoding="utf-8", lineterminator="\n", float_format="%.6f")
    sha = mc.sha256_file(path)
    mc.write_json(out_dir / "bart_universal_manifest.json", {
        "created": mc.now_iso(),
        "specification": "Deviation 12: universal schema; method of tranche2_02_score_prefilter.py at 64a64a8",
        "model": repo, "model_commit_pinned": commit, "model_commit_loaded": seen, "test_model": bool(test_model_dir),
        "hypotheses": hyps, "nli_label_indices": idx, "premise": "comment text only; truncation='only_first'",
        "max_length_tokens": max_len, "truncated_items": int((table["truncated"] == "Y").sum()),
        "control_strings_spaced_out_ids": sanitised, "items": len(table), "input_sha256": input_sha,
        "predictions": {"file": path.name, "sha256": sha}, "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None, "precision": "fp32",
        "runtime_minutes": round((time.time() - started) / 60, 2),
        "versions": {**mc.versions("numpy", "pandas"), "torch": torch.__version__,
                     "transformers": transformers.__version__},
    })
    print(f"universal schema: {len(table)} items scored in {(time.time() - started) / 60:.1f} min | "
          f"truncated {int((table['truncated'] == 'Y').sum())} | wrote {path} (SHA-256 {sha[:16]}...)")


def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="BART-MNLI zero-shot (Deviation 12).")
    ap.add_argument("--schema", choices=["universal", "domain"], required=True)
    ap.add_argument("--input", default=str(cfg.MODELS_DIR / "zero_shot_input.csv"))
    ap.add_argument("--out-dir", default=str(cfg.MODELS_DIR / "bart"))
    ap.add_argument("--device", default=None)
    ap.add_argument("--token-budget", type=int, default=None)
    ap.add_argument("--confirm-unsealed", action="store_true",
                    help="required for --schema domain: the model scripts are committed, so the scores are unsealed")
    ap.add_argument("--test-model-dir", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    items = read_items(Path(args.input))
    input_sha = mc.sha256_file(Path(args.input))
    if args.schema == "domain":
        if not args.confirm_unsealed:
            mc.stop("the domain-specific predictions come from prefilter_scores.csv, which is sealed until the model "
                    "scripts are committed. After that commit, run again with --confirm-unsealed.")
        run_domain(items, input_sha, Path(args.out_dir))
    else:
        run_universal(items, input_sha, Path(args.out_dir), args.device, args.token_budget, args.test_model_dir)
    print("No prediction was set against a label.")


if __name__ == "__main__":
    main()
