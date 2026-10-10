"""Model comparison, step 4 (GPU, for example Colab): DistilBERT and RoBERTa, fine-tuned, five folds.

    python models_04_finetune_cv.py --stage 2 --model distilbert
    python models_04_finetune_cv.py --stage 2 --model roberta
    python models_04_finetune_cv.py --stage 1 --model distilbert
    python models_04_finetune_cv.py --stage 1 --model roberta
    python models_04_finetune_cv.py --stage 1 --model <deployed> --text-only     (sensitivity, later)

Upload models_config.py, models_common.py, this file and data/models/finetune_input.csv.
On Colab, put --out-dir on Google Drive so that finished folds survive a disconnection; the
training checkpoints go to --work-dir, a local folder, and are deleted after each fold.

What it does (Deviation 12; settings in models_config.py, the reference study's settings):
  - folds from the committed fold files (column `fold` of finetune_input.csv);
  - Stage 2: the items with a gold Stage 2 class, labels CONCERN, ENDORSEMENT, OTHER (indices 0-2);
    the comment text alone;
  - Stage 1: every item with a gold Stage 1 label, labels N, Y; input = the pair
    ("r/<subreddit>", comment), only the comment truncated; --text-only drops the subreddit;
  - for fold k: train on the other four folds of both tranches, with a stratified 15% of them held
    out for early stopping (random_state = SEED, as in the reference code); predict fold k
    without its labels, so that no score is computed on it;
  - Hugging Face Trainer as in the reference code (run_finetune_cv_all.py): AdamW, learning rate
    2e-5, weight decay 0.01, batch 8, up to 10 epochs, evaluation each epoch, early stopping with
    patience 2 on validation macro-F1, best checkpoint restored, 256 tokens, fp32, seed SEED + k;
  - a special-token string of the tokenizer inside a comment (such as "</s>") is spaced out for
    the model input and its id is logged (the rule of Deviation 10);
  - checkpoints pinned to the commits in models_config.py; transformers and scikit-learn at the
    versions fixed there.

It sets no prediction of a held-out fold against a label and prints no score. Each finished
fold is saved at once, so an interrupted session resumes at the next fold.
Writes, in data/models/finetune/ (or --out-dir): <run>_predictions.csv, <run>_manifest.json.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd

import models_common as mc
import models_config as cfg

STAGE_LABELS = {2: list(cfg.CLASSES), 1: ["N", "Y"]}


def load_items(path: Path, stage: int) -> pd.DataFrame:
    if not path.exists():
        mc.stop(f"{path} not found (upload data/models/finetune_input.csv, or pass --input)")
    df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8")
    need = ["id", "tranche", "subreddit", "text", "gold_stage1", "gold_stage2", "label4", "fold"]
    if list(df.columns) != need or df["id"].duplicated().any():
        mc.stop(f"{path.name} must have the columns {need} and one row per id")
    if stage == 2:
        df = df[df["gold_stage2"].isin(cfg.CLASSES)].copy()
        df["label"] = df["gold_stage2"]
    else:
        df = df[df["gold_stage1"].isin(["N", "Y"])].copy()
        df["label"] = df["gold_stage1"]
    df["fold"] = df["fold"].astype(int)
    if sorted(df["fold"].unique()) != list(range(1, cfg.N_FOLDS + 1)):
        mc.stop("the fold column must hold folds 1 to 5")
    return df.sort_values("id").reset_index(drop=True)


def training_args(output_dir: str, seed: int):
    """TrainingArguments as in the reference code, with the optimizer and precision fixed."""
    from transformers import TrainingArguments
    f = cfg.FINETUNE
    return TrainingArguments(
        output_dir=output_dir, eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True,
        metric_for_best_model="macro_f1", greater_is_better=True, save_only_model=True, save_total_limit=1,
        learning_rate=f["learning_rate"], per_device_train_batch_size=f["batch_size"],
        per_device_eval_batch_size=f["eval_batch_size"], num_train_epochs=f["max_epochs"],
        weight_decay=f["weight_decay"], adam_beta1=f["adam_betas"][0], adam_beta2=f["adam_betas"][1],
        adam_epsilon=f["adam_epsilon"], max_grad_norm=f["max_grad_norm"], optim="adamw_torch",
        warmup_steps=0, lr_scheduler_type="linear", logging_steps=10, report_to="none",
        seed=seed, fp16=False, bf16=False, disable_tqdm=True)


class EncodedDataset:
    """Encoded items; without labels for the held-out fold, so that no score is computed on it."""
    def __init__(self, encodings, labels=None):
        self.enc, self.labels = encodings, labels
        self.n = len(next(iter(encodings.values())))

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        import torch
        item = {k: torch.tensor(v[i]) for k, v in self.enc.items()}
        if self.labels is not None:
            item["labels"] = torch.tensor(self.labels[i])
        return item


def space_out_special_strings(tok, df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """The rule of Deviation 10: a special-token string in a comment is spaced out, and logged."""
    specials = [t for t in tok.all_special_tokens if t]
    texts, spaced = df["text"].tolist(), []
    for j, (i, t) in enumerate(zip(df["id"], texts)):
        if any(s in t for s in specials):
            for s in specials:
                t = t.replace(s, s[0] + " " + s[1:])
            texts[j] = t
            spaced.append(i)
    special_ids = set(tok.all_special_ids) - {tok.unk_token_id}   # unknown characters (emoji) map to [UNK]
    for i, ids in zip(df["id"], tok(texts, add_special_tokens=False, verbose=False)["input_ids"]):
        if special_ids.intersection(ids):
            mc.stop(f"comment {i} still tokenises to a special token; take this message to Claude")
    return df.assign(text=texts), spaced


def encode(tok, df: pd.DataFrame, stage: int, text_only: bool):
    texts = df["text"].tolist()
    max_len = cfg.FINETUNE["max_length"]
    if stage == 1 and not text_only:
        first = [cfg.STAGE1_SUBREDDIT_SEGMENT.format(subreddit=s) for s in df["subreddit"]]
        return dict(tok(first, texts, truncation="only_second", padding=True, max_length=max_len))
    return dict(tok(texts, truncation=True, padding=True, max_length=max_len))


def run_fold(k: int, df: pd.DataFrame, stage: int, text_only: bool, work_dir: Path,
             repo: str, revision, labels: list[str]) -> tuple[list, dict]:
    import torch
    from sklearn.metrics import f1_score
    from sklearn.model_selection import train_test_split
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer, EarlyStoppingCallback, Trainer,
                              set_seed)
    from transformers.trainer_callback import PrinterCallback, ProgressCallback

    lab2id = {l: j for j, l in enumerate(labels)}
    load = {"revision": revision} if revision else {}
    tok = AutoTokenizer.from_pretrained(repo, **load)
    df, spaced = space_out_special_strings(tok, df)
    test = df[df["fold"] == k]
    train_all = df[df["fold"] != k]
    train, val = train_test_split(train_all, test_size=cfg.FINETUNE["validation_fraction"], random_state=cfg.SEED,
                                  stratify=train_all["label"])
    seed = cfg.SEED + k
    set_seed(seed)
    model = AutoModelForSequenceClassification.from_pretrained(
        repo, num_labels=len(labels), id2label=dict(enumerate(labels)), label2id=lab2id, dtype=torch.float32, **load)
    seen = getattr(model.config, "_commit_hash", None)
    if revision and seen and seen != revision:
        mc.stop(f"the loaded model reports commit {seen}, not the pinned {revision}")

    def labelled(part):
        return EncodedDataset(encode(tok, part, stage, text_only), [lab2id[x] for x in part["label"]])

    def metrics(p):
        pred = np.argmax(p.predictions, axis=-1)
        return {"macro_f1": f1_score(p.label_ids, pred, average="macro", labels=list(range(len(labels))),
                                     zero_division=0)}

    out = work_dir / f"fold{k}"
    shutil.rmtree(out, ignore_errors=True)
    trainer = Trainer(model=model, args=training_args(str(out), seed), train_dataset=labelled(train),
                      eval_dataset=labelled(val), compute_metrics=metrics, processing_class=tok,
                      callbacks=[EarlyStoppingCallback(early_stopping_patience=cfg.FINETUNE["early_stopping_patience"])])
    trainer.remove_callback(PrinterCallback)              # no loss or validation score is printed
    trainer.remove_callback(ProgressCallback)
    t0 = time.time()
    trainer.train()
    evals = [e for e in trainer.state.log_history if "eval_macro_f1" in e]
    best = max(evals, key=lambda e: e["eval_macro_f1"]) if evals else {}
    logits = trainer.predict(EncodedDataset(encode(tok, test, stage, text_only))).predictions   # no labels
    z = logits - logits.max(axis=1, keepdims=True)
    prob = np.exp(z) / np.exp(z).sum(axis=1, keepdims=True)
    pred = np.array(labels)[prob.argmax(axis=1)]
    rows = [[i, k, p] + [f"{v:.6f}" for v in pr] for i, p, pr in zip(test["id"], pred, prob)]
    info = {"fold": k, "seed": seed, "train_items": len(train), "validation_items": len(val), "test_items": len(test),
            "epochs_run": float(trainer.state.epoch or 0), "best_epoch": best.get("epoch"),
            "best_validation_macro_f1": best.get("eval_macro_f1"), "minutes": round((time.time() - t0) / 60, 2),
            "model_commit_loaded": seen, "special_strings_spaced_out_ids": spaced,
            "optimizer": trainer.args.optim.value if hasattr(trainer.args.optim, "value") else str(trainer.args.optim)}
    shutil.rmtree(out, ignore_errors=True)
    del trainer, model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return rows, info


def main() -> None:
    mc.setup_console()
    ap = argparse.ArgumentParser(description="Fine-tuned DistilBERT / RoBERTa, five folds (Deviation 12).")
    ap.add_argument("--stage", type=int, choices=[1, 2], required=True)
    ap.add_argument("--model", choices=sorted(set(cfg.STAGE2_FINETUNED) | set(cfg.STAGE1_CANDIDATES)), required=True)
    ap.add_argument("--text-only", action="store_true", help="Stage 1 sensitivity: the comment without the subreddit")
    ap.add_argument("--input", default=str(cfg.MODELS_DIR / "finetune_input.csv"))
    ap.add_argument("--out-dir", default=str(cfg.MODELS_DIR / "finetune"))
    ap.add_argument("--work-dir", default=str(Path(tempfile.gettempdir()) / "models_04_checkpoints"),
                    help="local folder for training checkpoints (deleted after each fold)")
    ap.add_argument("--test-model-dir", default=None, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if args.text_only and args.stage != 1:
        mc.stop("--text-only applies to Stage 1 only")
    mc.check_run_libraries(["transformers", "scikit-learn"])

    import torch
    import transformers
    run = f"stage{args.stage}_{args.model}" + ("_textonly" if args.text_only else "")
    labels = STAGE_LABELS[args.stage]
    df = load_items(Path(args.input), args.stage)
    input_sha = mc.sha256_file(Path(args.input))
    if args.test_model_dir:
        repo, revision = args.test_model_dir, None
        print("TEST MODEL: not the run of record")
    else:
        repo, revision = cfg.CHECKPOINTS[args.model]["repo"], cfg.CHECKPOINTS[args.model]["commit"]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"{run}: {len(df)} items, labels {labels} | model {repo} @ {revision} | device {device} | "
          f"torch {torch.__version__}, transformers {transformers.__version__}")
    if device == "cpu":
        print("NOTE: no GPU found. This works on a CPU but takes much longer.")

    out_dir = Path(args.out_dir)
    keep = out_dir / run                                   # finished folds (put on Drive on Colab)
    keep.mkdir(parents=True, exist_ok=True)
    work = Path(args.work_dir) / run                       # checkpoints (local disk)
    work.mkdir(parents=True, exist_ok=True)
    versions = {**mc.versions("numpy", "sklearn", "accelerate"), "torch": torch.__version__,
                "transformers": transformers.__version__}
    fingerprint = mc.text_sha256(json.dumps({"run": run, "repo": repo, "revision": revision, "input": input_sha,
                                             "settings": cfg.FINETUNE, "seed": cfg.SEED,
                                             "segment": cfg.STAGE1_SUBREDDIT_SEGMENT,
                                             "versions": {k: v for k, v in versions.items() if k != "python"}},
                                            sort_keys=True, default=str))
    all_rows, infos = [], []
    for k in range(1, cfg.N_FOLDS + 1):
        pred_path, info_path = keep / f"fold{k}_predictions.json", keep / f"fold{k}_info.json"
        if pred_path.exists() and info_path.exists():
            info = mc.read_json(info_path)
            if info.get("fingerprint") == fingerprint:
                all_rows += mc.read_json(pred_path)["rows"]
                infos.append(info)
                print(f"  fold {k}: already done (kept)")
                continue
            mc.stop(f"the finished folds in {keep} were made with a different input, model, setting or library "
                    f"version (a Colab update can change torch). All five folds of a run must come from one "
                    f"setup: to start this run again from fold 1, delete the folder {keep} and run the same "
                    f"command. If the input or the model changed, take this message to Claude first.")
        rows, info = run_fold(k, df, args.stage, args.text_only, work, repo, revision, labels)
        info["fingerprint"] = fingerprint
        mc.write_json(pred_path, {"rows": rows})
        mc.write_json(info_path, info)
        all_rows += rows
        infos.append(info)
        print(f"  fold {k}: trained on {info['train_items']} (+{info['validation_items']} for early stopping), "
              f"predicted {info['test_items']}, {info['epochs_run']:.0f} epochs, {info['minutes']} min")

    ids = [r[0] for r in all_rows]
    if sorted(ids) != sorted(df["id"]) or len(set(ids)) != len(ids):
        mc.stop("the folds do not cover every item exactly once")
    all_rows.sort(key=lambda r: r[0])
    path = out_dir / f"{run}_predictions.csv"
    sha = mc.write_rows_csv(path, ["id", "fold", "pred"] + [f"p_{l}" for l in labels], all_rows)
    spaced = sorted({i for info in infos for i in info.get("special_strings_spaced_out_ids", [])})
    mc.write_json(out_dir / f"{run}_manifest.json", {
        "created": mc.now_iso(),
        "specification": "Deviation 12; settings in models_config.py (the reference study's run_finetune_cv_all.py)",
        "run": run, "stage": args.stage, "model": repo, "model_commit_pinned": revision,
        "test_model": bool(args.test_model_dir), "labels": labels, "text_only": args.text_only,
        "input_format": ("comment text" if args.stage == 2 or args.text_only
                         else f"pair ({cfg.STAGE1_SUBREDDIT_SEGMENT!r}, comment), only the comment truncated"),
        "settings": cfg.FINETUNE, "seed": cfg.SEED, "folds": infos, "items": len(all_rows),
        "special_strings_spaced_out_ids": spaced,
        "best_epochs": [i.get("best_epoch") for i in infos],
        "input": {"file": Path(args.input).name, "sha256": input_sha},
        "predictions": {"file": path.name, "sha256": sha}, "device": device,
        "gpu": torch.cuda.get_device_name(0) if device == "cuda" else None,
        "minutes": round(sum(i["minutes"] for i in infos), 2), "versions": versions,
    })
    print(f"{run}: wrote {path} ({len(all_rows)} items, SHA-256 {sha[:16]}...). No score was computed on a "
          f"held-out fold.")


if __name__ == "__main__":
    main()
