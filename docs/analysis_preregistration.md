# Analysis Pre-registration

**Project:** A Longitudinal Analysis of Public Concern about Connected and Autonomous Vehicle Data Infrastructure in Online Discourse

**Author:** Arnaud Dorasamy (24916660) · UTS, Bachelor of Electrical Engineering

**Subject:** 41030 Engineering Research Project

**Supervisor:** A/Prof. Simona Mihaita

**Written:** 6 September 2026

## Status and purpose

This document fixes the analysis decisions for the study **before the annotation draw, production annotation, classification-model evaluation, and primary labelled analyses**. It governs corpus v2.2 (12,776 comments), whose identity is recorded in R5.

The collection audit, corpus preprocessing audit, topicality diagnostics, bot-residue investigation, and other corpus-construction checks preceded this pre-registration and informed several of the decisions recorded here. Those diagnostic findings are therefore not presented as pre-registered results. The purpose of this document is to freeze the analytical decisions that remain to be executed before labels, model-comparison results, prevalence estimates, subsystem results, and primary temporal results are produced.

Any methodological change made after the commit containing this file must be recorded as an explicit, dated deviation, with the reason stated. It must not be made silently. The Git commit containing this version is cited in the final report's methodology wherever one of these rules is reported, so that the ordering of analytical decisions and subsequent execution is auditable rather than asserted.

---

## R1 — Annotation sampling

Tranche 1 is 500 items drawn from the 12,166-item Tier 1+2 annotatable frame derived from corpus v2.2, era-stratified across 2016–2018 (2,495 items), 2019–2021 (3,633) and 2022–2025 (6,038), with allocation 167 / 167 / 166 and corresponding sampling fractions 0.0669, 0.0460 and 0.0275. Inclusion probabilities are recorded for every drawn item.

Tranche 2 is 500 boosted items, pre-filtered with BART-MNLI for Stage 1 relevance and for the sparse Stage 2 classes. Per-class allocation is set after tranche 1 with the objective of equalising final class counts. Allocation is on predicted class, so realised counts are expected to fall below allocated counts by the pre-filter's precision; this is anticipated here and is not treated as a shortfall when it occurs.

The pre-filter bias analysis — a confidence comparison against a random pool, and inter-model agreement across the zero-shot classifiers — is reported. The direction of the bias is stated rather than assumed away: enriching the boosted portion with items BART-MNLI classifies confidently inflates that model's measured performance on that portion, so any supervised advantage measured on the boosted portion is a lower bound. The natural tranche carries no pre-filter and provides the unbiased comparison.

Prevalence is estimated on the natural tranche only, inverse-probability weighted. The boosted tranche carries no inclusion probabilities and is never used for prevalence estimation.

The reliability subset is 200 items, split 100 in each tranche, so that an agreement estimate is available after tranche 1 and can inform codebook revision before tranche 2 is drawn.

---

## R2 — Calibration disagreement handling

Every disagreement in the 30-item calibration round is assigned exactly one cause **before Krippendorff's α is computed**, by consensus of all three annotators, and is recorded per item:

- **(a) missing context** — the comment is not judgeable as standalone text;
- **(b) codebook ambiguity** — no rule covers the case;
- **(c) misapplication** — a rule exists and was applied incorrectly.

Causes are assigned before α so that the α result cannot colour the attribution. The following branches are then applied mechanically:

- **α ≥ 0.7** → proceed context-free, unchanged.
- **α < 0.7, plurality cause (a)** → the post title is added to the Stage 2 presentation for annotators, and the Stage 2 model comparison is run on title-plus-comment for all five models. Stage 1 remains blind in all cases, because comment-level topicality is the estimand.
- **α < 0.7, plurality cause (b)** → revise the codebook, re-run calibration on 30 fresh items, discard both rounds.
- **α < 0.7, plurality cause (c)** → retrain on the existing codebook, re-run calibration on 30 fresh items. No codebook change.

Whatever input the annotators see, the models must see. If the trigger fires, all five models are re-run on the new input.

---

## R3 — Pooled versus reweighted comparison

The **reweighted** series is primary. Composition weights are estimated at **annual** resolution and applied within year to quarterly cells, because subreddit-quarter cells are too sparse to support stable weights: over the trend span there are 258 non-empty subreddit-quarter cells with a median of 34 observations, 10.9% below ten observations and 30 structurally empty, against 69 subreddit-year cells with a median of 143 and 7% below ten. A tier-level quarterly reweighting is reported as a robustness check, since three strata are stable at quarterly resolution where eight are not.

The primary trend statistic is Sen's slope with a distribution-free confidence interval, computed on the quarterly series over **2016 Q1 – 2024 Q4**. 2025 is excluded from the trend statistic and from annual tables, because it covers four months only.

The pooled series is compared with the reweighted series on two criteria:

1. **Agreement of conclusion** — do both series agree on the sign of Sen's slope, and on whether the Mann–Kendall test is significant at the Holm-corrected level?
2. **Overlap of estimate** — does the pooled Sen's slope fall inside the confidence interval of the reweighted Sen's slope?

If both hold, the reweighted series is reported and one sentence records that the pooled series agrees. If either fails, both series are reported in full and the divergence is stated in the results, the discussion and the limitations, with subreddit composition named as the mechanism.

---

## R4 — Thread-size composition bias

After joining `commentsCount` from the post metadata to `parsedPostId`, bucket-level concern shares are held fixed at their pooled across-year values, and each year's actual thread-size bucket composition is applied to those fixed shares. The resulting synthetic series is the concern trajectory that composition drift alone would produce. Its change across the study span is the composition-induced component *C*. Let *T* be the observed change in reweighted concern share across the same span. This is a rate decomposition of the Kitagawa type.

- **|C| < 0.20 × |T|** → bias bounded as non-consequential; reported in one sentence with the bound stated.
- **0.20 ≤ |C| < 0.50 × |T|** → material limitation; *C* reported explicitly and the trend stated net of it.
- **|C| ≥ 0.50 × |T|** → the pooled trend is not interpretable; the size-stratified series is reported as primary.

The 20% and 50% cut-points are a judgement call and are not derived. Their value is that they are fixed before *C* is observed.

---

## R5 — Frozen parameters and pre-commitments

### Corpus version

The analysed corpus is **v2.2, 12,776 comments**.

| Quantity | Value |
|---|---|
| Membership SHA-256 (sorted ids, newline-joined, no trailing newline) | `d187adac10d98ccda1f0145713139f008705349ea6e0b4921092b1ad099559d4` |
| Tier 1 / Tier 2 / Tier 3 | 6,650 / 5,562 / 564 |
| Date range | 2016-01-04 to 2025-04-30 |
| Location | `data/clean_v2_2/` |

Per-subreddit composition:

| Tier | Subreddit | Comments |
|---|---|---:|
| 1 | r/teslamotors | 2,435 |
| 1 | r/SelfDrivingCars | 2,143 |
| 1 | r/RealTesla | 1,189 |
| 1 | r/waymo | 883 |
| 2 | r/electricvehicles | 1,757 |
| 2 | r/cars | 1,469 |
| 2 | r/Futurology | 1,411 |
| 2 | r/technology | 925 |
| 3 | r/privacy | 371 |
| 3 | r/cybersecurity | 193 |

Corpus v1 contains 12,820 comments and is retained at `data/clean/`. Its membership SHA-256, computed over sorted comment ids joined by newline with no trailing newline, is:

`a18c2249eb787b989fcb797aa1cf525affe46300fdf473f02a8fabdbc0613a68`

Corpus v2 (12,779 comments, membership SHA-256 `528c06ef26f20685358513a0b5e8d55135ad67633c83f43d44287f51ccb524cd`) and corpus v2.1 (12,750 comments) are intermediate, superseded versions. Neither is used for analysis. v2.1 was produced by an author-based filter configuration that removed the r/Futurology submission-statement relay wholesale; that configuration was reverted because the relay comments carry human-written text, which is handled by wrapper stripping instead. The reasoning is recorded beside `KNOWN_BOTS` in `02_preprocess.py`.

**v1 → v2.2 changelog.** Content-based corrections were applied after the v1 freeze, implemented in `preprocess_content_filters.py` and integrated into `02_preprocess.py` after `clean_body` is computed and before the word floor:

| Stage | Effect on the pipeline population |
|---|---|
| Author-based bot filter, expanded from 8 to 14 accounts | 22,181 → 22,165 |
| Content-based bot and moderator filter | 7 removed |
| Submission-statement wrapper stripping | 79 rows modified in place; 7 subsequently fall below the word floor |
| Relay-duplicate resolution | 22 removed |
| Username masking | 61 rows modified; no rows removed |
| Word floor re-applied to stripped text | final 12,776 |

**Reproducibility.** The pipeline regenerates v2.2 from the 694 raw JSON files and reproduces the v2.2 membership SHA-256 exactly. Independently, a post-hoc application of the same content filters to frozen v1 reproduces a 12,777-item reference with membership SHA-256:

`0d9d0fca1bd3f9d4cd06e07e3b0fed6037e6176610ce61196d590a4cea50f675`

The two routes operate on different intermediate populations: the raw-data pipeline sees every in-window comment, whereas the post-hoc route begins from the 12,820 comments that had already cleared the original preprocessing stages. The exact membership relationship is established by the id-set comparison in `verify_v2_membership.py`, not assumed from filter ordering: the post-hoc reference contains exactly one additional comment id, `mi38xx2`, and there are no v2.2-only ids.

That one-comment difference is expected. `mi38xx2` is removed by the author-based bot filter, which the post-hoc route cannot reproduce because frozen v1 predates the expansion of `KNOWN_BOTS`. The row-removal and wrapper-stripping stages are monotone with respect to membership; username masking changed no word counts in the audited matches, and the subsequent English-language filter removed no additional rows in the v2.2 run.

### Analysis corpus

The annotation draw frame is **not** the analysis corpus. Concern shares are computed over the **Tier 1+2 analysis corpus: 12,212 items**, being all Tier 1 and Tier 2 comments in corpus v2.2.

The 59 surviving codebook worked examples and the 8 organic duplicate-text rows are excluded from the annotation draw only, not from the analysis corpus, since both are genuine retrieved comments. Tier 3 is excluded from the quantitative series and analysed qualitatively, subject to the same relevance filter as the other tiers.

### Draw frame

| Step | n |
|---|---:|
| Corpus v2.2 | 12,776 |
| less codebook worked examples surviving into v2.2 | −59 |
| **Annotatable pool** | **12,717** |
| less organic duplicate-text rows | −8 |
| less remaining Tier 3 items | −543 |
| **Tier 1+2 draw frame** | **12,166** |

Frame membership SHA-256:

`ce85a3b046fedf3648861d446832a364ab89e7b60a0e58f10272b33b1997d7b3`

Frame id list:

`data/frozen/draw_frame_ids.txt`

Sixty comments were used as worked examples in the codebook and held out of the annotatable pool; 59 survive into v2.2, one (`hqeuc79`) having been removed as a relay duplicate.

The frame is derived by rule rather than by hand, and `emit_frozen_frame.py` regenerates it, verifies it against every value recorded in this section, and refuses to write if any check fails.

### Duplicate-text rule

Among rows sharing identical `clean_body` text, the row with the lexicographically smallest comment id is retained for the draw and the remainder dropped. This applies to the draw only; all such rows are retained in the analysis corpus, because they are separate comments by separate users and their exclusion from a share estimate would be unjustified.

Eight rows are dropped under this rule:

`dvs2u4h`, `enziq4y`, `hor8auq`, `hotobpc`, `la9c737`, `ld9bg9q`, `lwpypak`, `mnxfknf`

### Temporal fold boundary

`2021-12-29T21:39:22Z` — the `created` timestamp of the 6,084th record when the 12,166-item frame is ordered by ascending `created`, splitting the frame into 6,083 records strictly before the boundary and 6,083 records at or after the boundary.

The temporal calibration check is reported in two forms: on the natural tranche alone, which carries no pre-filter selection but is small, and on the full annotated set, which is better powered but mixes naturally drawn and pre-filtered items across the boundary. Agreement between the two forms is the robust result; divergence is reported with the sample-source confound named.

### Fold assignments

Realised stratified 5-fold cross-validation assignments **cannot** be frozen in this commit, because folds are stratified by Stage 2 gold class and no labels exist before annotation. This pre-registration therefore freezes the fold-generation procedure, not the realised assignments:

- k = 5;
- stratification on the Stage 2 gold class;
- `sklearn.model_selection.StratifiedKFold`;
- fixed random seed **24916660**, used for both the tranche 1 draw and the fold assignments;
- library versions: **scikit-learn 1.9.0; NumPy 2.5.1**.

Realised fold assignments are committed after annotation and must be reproducible from the recorded procedure and seed.

### Evaluation protocol

Two evaluation structures are pre-specified and serve different purposes.

The first is the **stratified 5-fold cross-validation procedure** above for the model comparison. Its generation rule is frozen in this pre-registration; its realised item-to-fold assignments are frozen after Stage 2 gold labels exist.

The second is the **chronological two-block split** at the frozen temporal boundary above for the temporal calibration check.

Macro-F1 and per-class F1 are the primary metrics. Significance is assessed by an item-level permutation test with N = 10,000, two-sided, with gold labels never permuted, and Holm–Bonferroni correction applied within the declared comparison family.

The paired Wilcoxon signed-rank test is not used as the primary inferential instrument because, with five folds, its minimum achievable two-sided p-value is 0.0625.

### Inference families

Three families are declared in advance.

**Family A:** subsystem trend tests, one per subsystem.

**Family B:** the model comparisons.

**Family C:** the sensitivity analyses, reported uncorrected and labelled exploratory.

Holm–Bonferroni correction is applied within Families A and B and not across them. The collection-audit tests were conducted before the analysis plan was fixed and are reported with uncorrected p-values, labelled diagnostic.

### Prevalence correction

Adjusted classify-and-count is the primary correction; the SLD expectation-maximisation procedure is a robustness check.

Out-of-range ACC estimates are clipped to [0,1], with the raw value reported alongside.

Both corrections assume prior-probability shift, which the temporal calibration check tests directly. The calibration check is therefore reported before the correction, and a material temporal effect is treated as a condition on the corrected series.

### Pre-commitments

- **V2X** is reported as a count with no ranking claim.
- **RQ2** makes no subsystem ranking claim, following the restriction of subsystem labels to the 200-item reliability subset. This restriction and its consequence are fixed before production subsystem annotation. RQ2 is stated as: *which CAV subsystems appear in expressed concern, and how do their shares develop over time?*
- **The relevance-rate trend** is reported directionally, with the statement that subreddit composition does not explain it, and **no mechanism is offered**. The candidate explanations are not separable with the available data.

### Name-screen review

Sixteen candidates surfaced by the broad bot-name screen in `reconcile_bot_filters.py`, accounting for 19 retained rows, were manually inspected on **6 September 2026**.

Two were automated, and each was removed by correcting the rule responsible rather than by excluding the comment by hand:

- A unit-conversion bot that self-identified as "I'm a bot". The `BOT_BOILERPLATE` alternative matched only the expanded form `i am a bot`, so the contraction passed through both filters. The alternative now accepts both forms.
- A third subreddit moderator-team account posting a submission-rule notice. It was absent from `KNOWN_BOTS` while the other two moderator-team accounts were listed, and has been added. No content pattern was introduced for it: every candidate pattern tested against the corpus matched that one comment and nothing else, so a content rule would have been fitted to a single observation, whereas an account rule generalises to anything else the account posts.

The remaining fourteen candidates showed ordinary context-specific human discourse with no textual evidence of automation and are retained. Their Reddit account names are held only in the gitignored audit at `data/clean_v2_2/bot_reconciliation.csv` and are not committed.

Both filters have now failed once in this corpus, in complementary ways: the author-based filter on an account nobody had listed, and the content-based filter on automated text that no pattern happened to match. Neither is complete on its own, which is why both are retained.

### Known limitation of author-based filtering

10.7% of retained comments have `authorName` recorded as `[deleted]`. No account list, however complete, can attribute those comments to a named account.

Content-based filtering is therefore not a redundant second check but a necessary complement, because it operates on the one attribute every retained comment still has: the comment text.
