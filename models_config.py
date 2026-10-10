"""Model comparison: the frozen configuration (Deviation 12, docs/analysis_preregistration.md).

Committed word for word, with the model scripts, before any model is run on an annotated
item and before the Deviation 10 sealed files are opened. Only the CONFIGURATION block
(file locations) may be edited; everything below it is the pre-commitment.

Scripts that use this file:
    models_01_prepare.py      (PC)    gold labels, fold files, model inputs
    models_02_claude.py       (PC)    Claude Haiku 4.5 and Sonnet 4.6, both schemas
    models_03_bart.py         (GPU)   BART-MNLI, universal schema; domain schema from the frozen scores
    models_04_finetune_cv.py  (GPU)   DistilBERT and RoBERTa, Stage 2 and Stage 1, five folds
"""
from __future__ import annotations

from pathlib import Path


def _find_repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for folder in (here, *here.parents):
        if (folder / "docs" / "analysis_preregistration.md").exists():
            return folder
    return here


REPO = _find_repo_root()

# =============================================================================
# CONFIGURATION - file locations only (edit this block only)
# =============================================================================
TRANCHE1_SHEETS = {
    "A": REPO / "data" / "annotation" / "tranche1_annotator_A.xlsx",
    "B": REPO / "data" / "annotation" / "tranche1_annotator_B.xlsx",
    "C": REPO / "data" / "annotation" / "tranche1_annotator_C.xlsx",
}
TRANCHE1_KEY = REPO / "data" / "annotation" / "tranche1_master_key.csv"
TRANCHE1_SUBSYSTEM_SHEETS = {
    "A": REPO / "data" / "annotation" / "tranche1_subsystem_A_filled.xlsx",
    "B": REPO / "data" / "annotation" / "tranche1_subsystem_B_filled.xlsx",
    "C": REPO / "data" / "annotation" / "tranche1_subsystem_C_filled.xlsx",
}
TRANCHE2_SHEETS = {
    "A": REPO / "data" / "tranche2" / "returned" / "tranche2_annotator_A.xlsx",
    "B": REPO / "data" / "tranche2" / "returned" / "tranche2_annotator_B.xlsx",
    "C": REPO / "data" / "tranche2" / "returned" / "tranche2_annotator_C.xlsx",
}
TRANCHE2_KEY = REPO / "data" / "tranche2" / "tranche2_master_key.csv"
PREFILTER_INPUT = REPO / "data" / "tranche2" / "prefilter_input.csv"
PREFILTER_INPUT_MANIFEST = REPO / "data" / "tranche2" / "prefilter_input_manifest.json"
# Sealed under Deviation 10 until this file and the model scripts are committed:
PREFILTER_SCORES = REPO / "data" / "tranche2" / "prefilter_scores.csv"
PREFILTER_SCORES_MANIFEST = REPO / "data" / "tranche2" / "prefilter_scores_manifest.json"
# Outputs. data/ is never committed; splits/ holds the fold files, which are committed.
MODELS_DIR = REPO / "data" / "models"
SPLITS_DIR = REPO / "splits"
# =============================================================================

# ---- files of record (docs/decision_register.md, 26 and 30 September, 10 October 2026) --------
RECORDED_SHA256 = {
    "tranche1_annotator_A": "2fe9b29ff2fb3298c4581e2bb79de711b4713abc40cdd065f2070ca0be39e50e",
    "tranche1_annotator_B": "e80439ae671a21c69ffe5307cdebcf96b16bb33599015361304bff3dc71b4c04",
    "tranche1_annotator_C": "4ec6a12a215edb3c4a0c2ac86d92c7871de0fa88ea84fc50d25cdf2f239ba6f6",
    "tranche1_master_key": "ce50173525fd7ac74a3d720bf5f1a395b131066383f5c121002eb7dfc357755f",
    "tranche1_subsystem_A": "bec8eec480569df8d957df2fb048fc887095a477a732fbf9f6c811d2699c6f6b",
    "tranche1_subsystem_B": "b14d11bb09ae4a47af95d5c8513313c391324c9787af718a5a79a1667742ba8c",
    "tranche1_subsystem_C": "f466866e741e605503b449a812768e049a753e95eaec9b9ac1609fd946bb19ff",
    "tranche2_annotator_A": "bbf4f4f62a72b58db73bb5239798a91e577dc0fce23b1ffc732171a1a0fa406d",
    "tranche2_annotator_B": "6dd5d25735b1214d74b28bbee6947f9e6778945950610b6c04675158a993b504",
    "tranche2_annotator_C": "ad73b59b1126f7813dfa295dfcca0a51d240359d7b8ee5c23b95efe0f9ecc33a",
}
# The comment text of every model input: the pre-filter's input file (clean_body of corpus v2.2),
# as written by tranche2_01_export_prefilter_input.py on 4 October 2026, which printed this SHA-256.
PREFILTER_INPUT_SHA256 = "d1ae1fbe68f3f805eac720ab5bdbd7e8132333e3c1ae9ed8cfefa9106b3bcb1c"
# The Deviation 10 pre-filter run, recorded at 01f3d8a: the scores file and the model commit.
PREFILTER_SCORES_SHA256 = "689752f57ad851e56152754092136209739018a618a4728b34d5d415d8a74b6b"
PREFILTER_MODEL_COMMIT = "d7645e127eaf1aefc7862fd59a17a5aa8558b8ce"
TRANCHE2_ALLOCATION_SHA256 = "ce23e2290343cb87298ae1149a045728f9c54fa3bab446fc14dde8c067a5a560"
# Membership SHA-256: the ids sorted, joined by a newline, no trailing newline.
TRANCHE1_IDS_SHA256 = "8b214a961f3419fb14b2fb246b4a8e1cf91d94a05ef0f8d55404ee61594eb15c"
TRANCHE2_IDS_SHA256 = "3a1100cc537f4ec286563a28d8878e8e852cdf06583aa072f547d79331066b51"
TRANCHE2_RELIABILITY_IDS_SHA256 = "1a63e4f3de0f8e2f68855003fccdf7710deee59982487f9d455864e51183e8a9"
TRANCHE2_SHEET_IDS_SHA256 = {
    "A": "d096ced89e52320dfd2d9eff345091bf71358aa878175ff5a1182caef8f06d9f",
    "B": "d4e854fbb8a11ad30638d34a6d7e843d2d777457e715e754aab5f899513cb149",
    "C": "53f7c24712f6544eae0bf3586f7497f212841b4a1b1fe1e748a3fb432c6e3458",
}
# Tranche 1: one label per item (gold for reliability items, the single rating otherwise),
# as fixed in tranche2_common.py at 64a64a8.
TRANCHE1_LABELS_SHA256 = "d6f4eeeaf756831c3ba2a3165a7a548505d75a315b4f06069b9cf8ce580cd8d7"
TRANCHE1_LABEL_COUNTS = {"N": 203, "CONCERN": 120, "ENDORSEMENT": 95, "OTHER": 82}
# Tranche 1 subsystem gold (Deviation 7): 59 reliability items with two or more labels,
# 53 unanimous, 6 split two to one, none adjudicated.
TRANCHE1_SUBSYSTEM_RELIABILITY = {"two_or_more_labels": 59, "unanimous": 53, "two_to_one": 6}

# ---- the author's adjudications (docs/decision_register.md, 10 October 2026, commit dbd8a69) ----
ADJUDICATED_STAGE2 = {            # tranche 2, Deviation 2
    "cz1vh4t": "ENDORSEMENT",
    "dvznfp7": "ENDORSEMENT",
}
ADJUDICATED_SUBSYSTEM = {         # tranche 2, Deviation 7
    "epqj9r1": "in_vehicle_networks",
    "h4jy9ry": "data_governance",
    "lifeax3": "data_governance",
}

# ---- labels ---------------------------------------------------------------------
SEED = 24916660
ANNOTATORS = ["A", "B", "C"]
CLASSES = ["CONCERN", "ENDORSEMENT", "OTHER"]            # fixed label indices 0, 1, 2
SUBSYSTEMS = ["sensing", "in_vehicle_networks", "v2x", "cybersecurity", "privacy", "data_governance"]
PRIMARY_SUBSYSTEMS = SUBSYSTEMS + ["none"]
# Four-way gold label for folds (Deviation 12). An item that is relevant in the gold set but
# has no Stage 2 gold label (possible under the missing-rating rules) is marked NO_STAGE2; it
# fits none of the four strata, so models_01_prepare.py stops if there is one (there is none).
LABEL4 = ["N"] + CLASSES
NO_STAGE2 = "Y_NO_STAGE2"

# ---- folds (R5 and Deviation 12) ----------------------------------------------------
N_FOLDS = 5                     # StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
FOLD_LIBRARY_VERSIONS = {"scikit-learn": "1.9.0", "numpy": "2.5.1"}

# ---- label schemas for the zero-shot models (Deviation 12) ------------------------------
# Domain-specific: the three class hypotheses of Deviation 10, as phrases.
DOMAIN_LABELS = {
    "CONCERN": "expresses worry, doubt or criticism about self-driving or connected vehicle technology",
    "ENDORSEMENT": "expresses support, approval or optimism about self-driving or connected vehicle technology",
    "OTHER": "is neutral or factual and takes no position on self-driving or connected vehicle technology",
}
# Universal: the same phrases with the domain removed, so the two schemas differ in nothing else.
UNIVERSAL_LABELS = {
    "CONCERN": "expresses worry, doubt or criticism",
    "ENDORSEMENT": "expresses support, approval or optimism",
    "OTHER": "is neutral or factual and takes no position",
}
SCHEMAS = {"universal": UNIVERSAL_LABELS, "domain": DOMAIN_LABELS}
# BART-MNLI hypotheses: "This comment " + phrase + ".". The domain-specific ones are the
# Deviation 10 class hypotheses, word for word.
BART_HYPOTHESIS = "This comment {label}."

# ---- prompt for the generative models --------------------------------------------------
# Word for word the shared zero-shot template of the reference study: Lee et al. (2026),
# Social Network Analysis and Mining, doi:10.1007/s13278-026-01633-0, Appendix F.1
# (Section 4.1 of the Research Square preprint, doi:10.21203/rs.3.rs-9839922/v1).
# One template for both models and both schemas. (Section 4.1 of both versions says the
# commercial models' topic-specific variant ended "Output ONLY the exact label text."; Appendix
# F.1 calls its template shared by all generative models. The one template is used here so that
# the two schemas differ only in their label phrases.)
PROMPT_TEMPLATE = (
    "You are a careful annotator.\n"
    "Choose exactly ONE label for the comment.\n"
    "\n"
    "Candidate labels:\n"
    "{label_block}\n"
    "\n"
    "Comment:\n"
    "{text}\n"
    "\n"
    "Return ONLY the exact label text."
)
# The reference describes {label_block} as a bullet list without giving the bullet: here,
# one line per label in CLASSES order, each starting "- ".
LABEL_BLOCK_LINE = "- {label}"

# ---- Claude models (Anthropic API) ------------------------------------------------------
CLAUDE_MODELS = {
    "haiku": "claude-haiku-4-5-20251001",     # dated snapshot identifier
    "sonnet": "claude-sonnet-4-6",            # 4.6 identifiers carry no date; Anthropic documents a
}                                             # dateless 4.6 identifier as a fixed snapshot
CLAUDE_CONFIGS = ["haiku-universal", "haiku-domain", "sonnet-universal", "sonnet-domain"]
CLAUDE_SETTINGS = {
    "temperature": 0,                         # sent in the request body: SDK version 1 dropped the keyword
    "max_tokens": 50,
    "system_prompt": None,                    # no system prompt; the template is the user message
}
ANTHROPIC_SDK_VERSION = "1.13.0"              # the Python client the runs use (pip install anthropic==1.13.0)
NO_CLASS_RETRIES = 1                          # Deviation 12: retried once with the same prompt
CLAUDE_CONCURRENCY = 5                        # concurrent requests, as in the reference study
CLAUDE_TIMEOUT_SECONDS = 60                   # per call, as in the reference study
CLAUDE_TRANSPORT_RETRIES = 8                  # connection errors and overload; not a "no class" retry
# List prices in US dollars per million input / output tokens, checked on 10 October 2026
# (https://platform.claude.com/docs/en/about-claude/pricing). Cost = tokens x these prices.
CLAUDE_PRICES_USD_PER_MTOK = {
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
}
# Spending ceiling for the evaluation runs (governing document O26: the USD 25 paid-evaluation
# budget). Measured spend = every logged call, all four configurations and connection checks,
# at the prices above. At the ceiling the run halts for review.
CLAUDE_SPEND_CEILING_USD = 25.00
# Cost per 1,000 comments, as used by the deployment tie-breaks of Deviation 12.
COST_RULE = ("Claude configurations: the API charge of every call (retries and calls on items cut off "
             "included) at the prices above, divided by the 1,000 items, times 1,000. Models run on our own "
             "hardware or on Colab carry no API charge, so their cost is zero; where two of them must be "
             "separated on cost (an exact tie at Stage 1), the one with fewer parameters costs less.")

# ---- Hugging Face checkpoints, pinned to commits (read from the hub on 10 October 2026) -----
CHECKPOINTS = {
    "distilbert": {"repo": "distilbert/distilbert-base-uncased",
                   "commit": "12040accade4e8a0f71eabdb258fecc2e7e948be"},
    "roberta": {"repo": "FacebookAI/roberta-base",
                "commit": "e2da8e2f811d1448a5b465c236feacd80ffbac7b"},
    "bart_mnli": {"repo": "facebook/bart-large-mnli",
                  "commit": "d7645e127eaf1aefc7862fd59a17a5aa8558b8ce"},
}

# ---- fine-tuning (the reference study's settings; not tuned on any evaluation fold) ---------
FINETUNE = {
    "optimizer": "AdamW, PyTorch implementation (Trainer optim 'adamw_torch')",
    "learning_rate": 2e-5,
    "weight_decay": 0.01,                     # not applied to biases and LayerNorm weights
    "adam_betas": (0.9, 0.999),
    "adam_epsilon": 1e-8,
    "lr_schedule": "linear decay to zero over max_epochs, no warm-up",
    "max_grad_norm": 1.0,
    "batch_size": 8,
    "eval_batch_size": 8,
    "max_epochs": 10,
    "early_stopping_patience": 2,             # epochs without a higher validation macro-F1
    "validation_fraction": 0.15,              # stratified, drawn from the training folds only
    "max_length": 256,                        # sub-word tokens
    "class_weights": None,
    "precision": "fp32",
    "seed": "SEED + fold number (1 to 5); SEED for the final retraining",
}
STAGE2_FINETUNED = ["distilbert", "roberta"]
# Stage 1 (Deviation 1, Deviation 12): the candidates, their input, and the text-only variant.
STAGE1_CANDIDATES = ["distilbert", "roberta"]
STAGE1_SUBREDDIT_SEGMENT = "r/{subreddit}"     # first segment of a sentence pair; the comment is the
                                              # second segment and the only one truncated
STAGE1_TEXT_ONLY_VARIANT = ("the deployed Stage 1 model type, same settings and folds, "
                            "reading the comment text alone")
FINAL_RETRAINING = ("a deployed fine-tuned model is retrained on every eligible gold item of both tranches "
                    "(Stage 2: every item with a gold Stage 2 class; Stage 1: every item with a gold Stage 1 "
                    "label), with the settings above and no held-out split, for a fixed number of epochs: the "
                    "median of the best epochs of its five cross-validation folds, with the learning-rate "
                    "schedule of those runs (linear decay over 10 epochs) stopped after that epoch; seed SEED")
# Comment text that contains a special-token string of the tokenizer (such as "</s>") has that
# string spaced out for the model input, and the ids are logged: the rule of Deviation 10.
# Library versions for the GPU runs (checked by models_03_bart.py and models_04_finetune_cv.py).
RUN_LIBRARY_VERSIONS = {"transformers": "5.19.0", "scikit-learn": "1.9.0"}
