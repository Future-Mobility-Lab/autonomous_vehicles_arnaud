# Model notes

The classifiers of record, as fixed by Deviations 12 and 13 of
`docs/analysis_preregistration.md` and configured in `models_config.py`. The sentiment
model and the keyword-then-zero-shot subsystem coding of the earlier proposal were not
run on this corpus and are not part of the analysis.

## Labels

- **Stage 1 (relevance):** Y (the comment is about connected or autonomous vehicles) or N.
- **Stage 2 (stance), on relevant comments:** CONCERN, ENDORSEMENT or OTHER, with fixed
  indices 0, 1 and 2 (`models_config.CLASSES`).
- **Primary subsystem**, on relevant comments: sensing, in_vehicle_networks, v2x,
  cybersecurity, privacy, data_governance or none (`models_config.PRIMARY_SUBSYSTEMS`).

## Deployed classifiers

| Task | Model | Input | Notes |
|---|---|---|---|
| Stage 1 | RoBERTa base (`FacebookAI/roberta-base`, commit `e2da8e2f811d1448a5b465c236feacd80ffbac7b`), fine-tuned | Sentence pair: "r/" + subreddit, then the comment (only the comment is truncated, 256 tokens) | Chosen by the evaluation of record; retrained once on the 1,000 annotated items for 5 epochs (the median best epoch of its cross-validation folds), seed 24916660; a comment is classified relevant when its probability of Y is greater than that of N (an exact tie is N) |
| Stage 2 | `claude-sonnet-4-6` (Anthropic API), zero-shot | The comment text alone, in the shared prompt template with the domain-specific label phrases | Temperature 0, at most 50 output tokens, no system prompt; an answer that names no class is retried once, and a second such answer is a refusal |
| Subsystem | `claude-sonnet-4-6`, zero-shot | The comment text alone, with the seven definitions of the annotators' instructions | The prompt is given word for word in Deviation 13; an answer that names no value, or more than one, is retried once, and a second such answer is unclassified |

The Stage 2 classifier's error rates for CONCERN, used for the prevalence correction,
are those of the evaluation of record (weighted TPR 0.946922, FPR 0.237641).

## Corpus runs (`models_06_deploy.py`)

- Stage 1 over all 12,776 comments of corpus v2.2: 6,532 classified relevant (Tier 1 4,414,
  Tier 2 2,089, Tier 3 29). Tier 3 receives Stage 1 only.
- Stage 2 over the 6,503 Tier 1+2 comments classified relevant: no refusals. On the 571
  tranche items both runs cover, the corpus run and the evaluation run give the same label
  for 567.
- Subsystem classifier over the same 6,503 comments and the 27 gold-relevant tranche items
  outside them (for validation only): one comment unclassified. Against the gold primary
  subsystem of 596 tranche items it agrees on 502 (84.2%); per-value recall and precision
  are in `results/series_report.md`.

## Compared and not deployed (RQ3)

- Fine-tuned: DistilBERT base uncased (`distilbert/distilbert-base-uncased`, commit
  `12040accade4e8a0f71eabdb258fecc2e7e948be`) at both stages, and RoBERTa base at
  Stage 2.
- Zero-shot: BART-MNLI (`facebook/bart-large-mnli`, commit
  `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`) and `claude-haiku-4-5-20251001`, each under
  the universal and the domain-specific label schema; `claude-sonnet-4-6` under the
  universal schema.
- The deployed Stage 1 model's text-only variant (the comment without the subreddit),
  reported as a sensitivity.

Fine-tuning settings (all models): AdamW, learning rate 2e-5, weight decay 0.01, batch
size 8, at most 10 epochs with early stopping after 2 epochs without a higher
validation macro-F1, 15% stratified validation split from the training folds, maximum
length 256 sub-word tokens, fp32, no class weights (`models_config.FINETUNE`).

## Why the label order matters

The fine-tuned models' outputs are read by the fixed index order above, and the
zero-shot answers by matching the label text. Changing either order without changing
the reading code would silently swap classes, so both are fixed in `models_config.py`.
