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

---

---

## Deviations

Changes made after the commit containing this pre-registration. Each is dated,
carries its reason, and states its consequence. Rules R1–R5 above are left as
originally written.

### Deviation 1 — Stage 1 presentation includes the subreddit label

**Recorded 6 September 2026, against commit 823270e.**

R1 and the annotation protocol specified that Stage 1 relevance be judged on the
comment text alone. Codebook development established that this is not workable
for a substantial minority of items: comments that are plainly on-topic within a
narrow community carry no internal marker of that topic. The subreddit label is
therefore shown to annotators at Stage 1, with an explicit rule governing when it
may be used:

- Relevance **may** be inferred from the subreddit for **r/SelfDrivingCars** and
  **r/waymo**, whose stated scope is autonomous vehicles.
- For the remaining eight subreddits, relevance **must** be established from the
  comment text. r/teslamotors, r/cars, r/technology, r/Futurology,
  r/electricvehicles, r/RealTesla, r/privacy and r/cybersecurity are each broad
  enough that community membership does not imply CAV content.

Thread title and parent comment remain hidden, so the R2 missing-context trigger
is unaffected.

**Consequence for RQ4.** The topicality estimate is therefore *comment plus
community*, not standalone text, and is more permissive than the pre-registered
estimand. It remains a lower bound on true topicality, since context-dependent
relevance beyond the community level is still unrecoverable. The lexical proxy
reported alongside it is unaffected, being computed on text alone.

**Consequence for the model comparison.** Whatever the annotators see, the models
must see. Subreddit is therefore included in the Stage 1 classifier input.

### Deviation 2 — Adjudication rule for the reliability subset

**Recorded 26 September 2026, against commit 823270e.**

R1 and the codebook fix a 200-item reliability subset rated by all three
annotators, and R5 stratifies folds on the Stage 2 gold class, but none of the
pre-registration, the codebook or the calibration instructions states how the
gold label is formed from three ratings. The rule applied is recorded here, on
26 September 2026, after tranche 1 annotation was complete and before any
tranche 1 agreement statistic was computed.

- The gold label is the majority of the three ratings.
- A three-way split is resolved by the author, who is also annotator A, and the
  item is flagged as adjudicated.
- Where two annotators code Stage 1 = Y with different Stage 2 classes and the
  third codes N, the Stage 1 majority (relevant) stands and the author chooses
  only between the two Stage 2 classes given. The item is flagged as
  adjudicated.

The raw-majority set and the adjudicated gold set are both reported, with every
adjudicated item listed.

**Consequence.** The author's own label is among those in disagreement on any
adjudicated item. Keeping every majority binding, and listing each adjudicated
item, limits that influence and makes it visible.

### Deviation 3 — Methods specified for the tranche 1 analyses

**Recorded 26 September 2026, against commit 823270e.**

Three details that R1–R5 leave open were specified on 26 September 2026, before
the corresponding results were computed.

- **Disagreement concentration.** `calibration_instructions.md` states in
  advance, from the reference study, that disagreement is expected to
  concentrate at the CONCERN/OTHER boundary rather than between CONCERN and
  ENDORSEMENT. The expectation is also assessed on the tranche 1 reliability
  items. The headline measure is the raw count of disagreeing annotator pairs
  at Stage 2, by class pair. Observed versus chance-expected coincidences are
  reported alongside; if the two point different ways, both are reported and
  the difference is stated.
- **Intervals for weighted prevalence.** 95% intervals are logit-transformed,
  from the era-stratified design variance with finite population correction.
  Class shares among relevant items are treated as ratio (domain) estimates.
- **RQ4 era comparison.** Besides direction and interval overlap, the 95%
  interval for the difference in relevance rate, 2022–2025 minus 2016–2018, is
  reported. The eras are sampled independently.

**Consequence.** No estimand or decision rule changes. The expectation stated
for the calibration round is extended to the production reliability items, and
reporting the difference interval offers no mechanism, consistent with the
relevance-rate pre-commitment in R5.

### Deviation 4 — Additional exploratory analyses

**Recorded 26 September 2026, against commit 823270e.**

Three analyses are added. Each is reported as exploratory, alongside the
primary figures and never in place of them.

- **Encoding sensitivity.** Annotator C's workbook displayed every non-ASCII
  character mis-decoded (see `docs/decision_register.md`). Stage 1 and Stage 2
  α are also computed on the 76 reliability items whose text was unaffected.
  Specified before any agreement statistic was computed.
- **Bootstrap intervals for α.** A 95% percentile interval for each tranche 1 α
  (Stage 1, Stage 2 and the three one-vs-rest), from 10,000 item-level
  bootstrap resamples of the 100 reliability items, all five computed on the
  same resamples with seed 24916660, together with the share of resamples below
  0.7, the R2 calibration threshold. Specified after the point estimates were
  seen and before any interval was computed, because Stage 2 α (0.739) exceeds
  0.7 by 0.04 on 59 items.
- **Annotator sensitivity for the class distribution.** Alongside the weighted
  class distribution, the distribution is estimated separately from each
  annotator's full sheet (the 100 reliability items plus that annotator's own
  items), with era weights recomputed for each sheet. Specified after the
  agreement results showed C coding OTHER 22 times on the shared items against
  11 each for A and B, and before any prevalence estimate was computed. It
  assumes assignment to annotators was random within era.

**Consequence.** No primary figure changes. The additions are reported as
exploratory, in line with Family C in R5.

### Deviation 5 — Tranche 2 allocation set from pre-filter hit rates

**Recorded 26 September 2026, against commit 823270e.**

R1 sets the tranche 2 per-class allocation after tranche 1, on BART-MNLI
predicted class, with the objective of equalising final class counts, and
anticipates that realised counts fall below allocated counts by the
pre-filter's precision. R1 does not say how the allocation is computed.

It is computed as follows. BART-MNLI, with the same model and hypothesis
templates that will screen the draw frame, is run on the 500 tranche 1 items.
For each targeted class, the share of targeted items that turn out relevant
and in that class is estimated against the tranche 1 labels. The allocation is
then chosen so that expected final counts are as close to equal as those rates
allow.

**Consequence.** The pre-filter and the objective are unchanged. Using measured
hit rates brings expected final counts closer to parity than allocating on
predicted counts alone. The boosted tranche still carries no inclusion
probabilities and is not used for prevalence.

### Deviation 6 — Subsystem labelling retrofit

**Recorded 26 September 2026, against commit 823270e.**

R5 pre-registered subsystem labels on the 100 reliability items only. The tranche 1 production sheets were built without the `subsystem` column, a construction error. The retrofit therefore extends subsystem labelling to every item the annotator marked relevant: 137 for A, 137 for B and 140 for C, comprising 414 judgements over 298 unique items. This extension was forced by the missing column, not chosen after seeing results. Six categories estimated on approximately 57 items cannot support RQ2's ranking claim.

A seventh primary value, `none`, is added for CAV-relevant comments that engage no identifiable subsystem. An optional `subsystem_secondary` field records multi-subsystem engagement while retaining a single primary nominal variable for the pre-registered Krippendorff's alpha.

#### Subsystem reliability fallback pre-commitment

Subsystem Krippendorff's alpha will be computed on the 57 reliability items marked relevant by all three annotators. If subsystem alpha is below 0.6, RQ2 will collapse the subsystem categories to three groups: perception (`sensing` + `in_vehicle_networks`), connectivity (`v2x` + `cybersecurity`), and data (`privacy` + `data_governance`). RQ2 will then be reported at that three-group level, with the six-way subsystem distribution retained as descriptive only.

This fallback rule is fixed before any subsystem labels are returned by the annotators. Its commit timestamp is the evidence that the rule was pre-committed before the subsystem reliability result was known.


### Deviation 7 — Gold rule extended to subsystem labels

**Specified 30 September 2026, against commit 823270e. Committed after that
date; the commit date is in the repository history.**

Deviation 2 fixes how gold Stage 1 and Stage 2 labels are formed from three
ratings. No committed document fixes the same for the primary subsystem label
collected in the subsystem retrofit. The Deviation 2 rule is extended to it,
before any subsystem share is computed:

- The gold primary subsystem of a reliability item is the majority of the
  primary labels given by the annotators who coded the item as relevant.
- A three-way split, or a one-to-one split between two labels, is resolved by
  the author, who is also annotator A, and the item is flagged as adjudicated.
- Only items that are relevant in the gold set take a gold subsystem label.
  Singly-rated items keep their single label.
- Secondary labels take no gold value and are reported descriptively.

In tranche 1, all 59 reliability items with two or more subsystem labels
resolve by majority: 53 are unanimous and six split two to one. None is
adjudicated.

**Consequence.** Subsystem shares use one label per item, formed in the same
way as the Stage 1 and Stage 2 labels. The author's influence is limited to one
vote on each reliability item.

### Deviation 8 — RQ4: subreddit composition statement not supported in tranche 1

**Specified 26 September 2026, against commit 823270e. Committed after that
date; the commit date is in the repository history.**

R5's pre-commitments state that the relevance-rate trend is reported
directionally, "with the statement that subreddit composition does not explain
it". To test that statement on tranche 1, an exploratory composition check was
added, with its method fixed before any relevance rate by subreddit and era was
computed: a Kitagawa decomposition of the 2022–2025 minus 2016–2018 difference
over seven subreddit groups (r/waymo merged with r/SelfDrivingCars, since r/waymo
has no tranche 1 items in 2016–2018), and era rates standardised to the pooled
frame mix.

The subreddit mix accounts for most of the difference: of +7.0 points, +6.1 come
from the change in mix and +0.9 from changes within subreddits. The statement
that subreddit composition does not explain the trend is therefore not made for
tranche 1. The trend is still reported directionally, the decomposition is
reported in place of the statement, and no mechanism is offered. The figures are
from a preview computed outside the repository; the figures of record come from
the committed pipeline.

**Consequence for RQ4.** The tranche 1 relevance estimates cannot be read as a
composition-free trend. The pre-commitment predates Deviation 1, which allows
relevance to be inferred from the subreddit in r/SelfDrivingCars and r/waymo,
the two subreddits whose share grows most across the eras. The composition check
is reported as exploratory, in line with Family C in R5.

### Deviation 9 — Subsystem estimands, sparsity rule and Family A

**Specified 4 October 2026, against commit 823270e. Committed after that date;
the commit date is in the repository history.**

R5 commits to reporting which subsystems appear in expressed concern and how
their shares develop, and defines Family A as "subsystem trend tests, one per
subsystem". R1–R5 do not define the subsystem shares, give a rule for sparse
subsystems, or say how Family A relates to the V2X pre-commitment. These are
fixed here. They were fixed after subsystem α was computed and after the
per-annotator label counts had been displayed (see `docs/decision_register.md`,
30 September 2026), and before any subsystem share or any corpus-wide subsystem
code was computed.

- **Estimands.** The headline for RQ2 is π_s(t), the share of CONCERN comments
  whose primary subsystem is s. Two secondary measures are reported: C_s(t), the
  CONCERN share among relevant comments whose primary subsystem is s, and
  E_s = C_s / C, the enrichment of concern in subsystem s. Only primary labels
  are counted; secondary labels are reported as a descriptive sensitivity.
- **Classifier error.** Subsystem shares are reported uncorrected for
  subsystem-classifier error. The subsystem classifier's accuracy against the
  retrofit labels is reported for each category, with intervals, alongside
  every subsystem result.
- **Sparsity rule.** Using corpus-wide counts of comments classified as
  relevant, by primary subsystem: a subsystem whose median quarterly count over
  2016 Q1–2024 Q4 is 50 or more is analysed at quarterly resolution; otherwise,
  if its median annual count over 2016–2024 is 50 or more, it is analysed at
  annual resolution; otherwise it is reported as counts only, with no trend
  test. Cell counts are reported in every case.
- **Family A.** Family A is one trend test on π_s(t) for each subsystem other
  than V2X that meets the sparsity rule at quarterly or annual resolution: at
  most five tests, with Holm–Bonferroni applied within the family. V2X is
  reported as a count, as R5 requires, and `none` is reported descriptively;
  neither is tested. D28 Rule 1 did not fire, so subsystems are not collapsed
  into groups.

**Consequence.** R5's "one per subsystem" becomes at most five tests, set by a
count-based rule before any test is run. Subsystem results carry
subsystem-classifier error that is reported but not removed.

### Deviation 10 — Tranche 2: codebook, pre-filter, allocation rule, gate, draw and subsystem labels; R1's statement of bias direction withdrawn

**Recorded 4 October 2026, against commit 823270e.**

R1 fixes the design of tranche 2 and Deviation 5 fixes how its allocation is
estimated. Neither states the pre-filter's wording, an objective that can be
computed, or the draw procedure, and R1 leaves open whether the codebook is
revised first. These are fixed here. The pre-filter wording below was written
on 4 October 2026 and had not been run on any frame item when this was
recorded. The scripts were tested on synthetic scores only.
They are `tranche2_common.py`, `tranche2_01_export_prefilter_input.py`,
`tranche2_02_score_prefilter.py`, `tranche2_03_allocate.py`,
`tranche2_04_draw.py` and `tranche2_gate_null_simulation.py`, committed with
this deviation.

**Codebook.** Not revised. Tranche 2 is annotated under codebook v1.0, as
tranche 1 was. Nothing in R1 or R2 requires a revision: R1 allows one, and R2's
0.7 threshold governs the calibration round. Tranche 1 Stage 2 α was 0.739
(Deviation 4), and the disagreement that remains is concentrated in OTHER.
Revising Rule 8 now would put the two tranches under different rules, with the
difference confounded with natural against boosted sampling, and a revised
codebook would first have to be calibrated on fresh items. The cost is
accepted, and it is larger than for tranche 1: the boosted tranche is designed
to add most to the class on which the annotators agree least, and four-fifths
of it is rated once. Agreement is reported per class for both tranches. B and
C have not been shown the tranche 1 agreement results.

One instruction differs from tranche 1. Codebook §3.2 states expected relevance
rates for a natural sample, which do not hold here. Annotators are told, in
these words: "This batch was chosen by an automated filter and is not a random
sample. Some of the comments are not about connected or autonomous vehicles.
The expected rates in section 3.2 do not apply and nothing replaces them: judge
each comment on its own. Everything else in the codebook applies as before."
They are not told which classes were targeted.

**Pre-filter.** `facebook/bart-large-mnli`; the commit of the model files is
recorded in the run manifest. The premise is the comment text alone
(`clean_body`, corpus v2.2), truncated to the model's maximum input length.
The subreddit is not used. There are four hypotheses:

- relevance: "This comment is about self-driving or connected vehicles,
  driver-assistance systems such as Autopilot, robotaxis, or the sensors,
  software or data of such vehicles."
- CONCERN: "This comment expresses worry, doubt or criticism about
  self-driving or connected vehicle technology."
- ENDORSEMENT: "This comment expresses support, approval or optimism about
  self-driving or connected vehicle technology."
- OTHER: "This comment is neutral or factual and takes no position on
  self-driving or connected vehicle technology."

Logits are rounded to six decimal places before anything is derived from them.
The relevance probability is the entailment share of a softmax over the
entailment and contradiction logits of the relevance hypothesis, and an item is
predicted relevant at 0.5 or above. The predicted class is the class hypothesis
with the highest entailment logit (a tie goes to the first of CONCERN,
ENDORSEMENT, OTHER). The **predicted label** is "not relevant" for an item not
predicted relevant, and the predicted class otherwise. A comment containing a
literal control string of the tokenizer (such as "</s>") has that string spaced
out for the model input, and its id is logged. Control characters that a
workbook cell cannot hold are removed from a comment before it is scored, so
that the model and the annotators get the same text; the number of comments
affected is recorded. All 12,166 frame items are scored once. The scores file
is frozen by its SHA-256 and is the reference; a later re-run is not a
substitute for it.

Hit rates, the allocation, the draw and the reliability subset use the
predicted label, and only its three values other than "not relevant". An item
below the relevance threshold is never drawn.

**Hit rates.** For each predicted label, the share of tranche 1 items with that
predicted label that have each tranche 1 label (not relevant, CONCERN,
ENDORSEMENT, OTHER), weighted by the R1 design weights. The tranche 1 label is
the gold label under Deviation 2 for the 100 reliability items and the single
rating otherwise.

**Allocation.** Let T_c be the tranche 1 count of class c, for the three
classes CONCERN, ENDORSEMENT and OTHER; a_p the number of tranche 2 items drawn
with predicted label p; and h_pc the hit rates. The expected final count is
F_c = T_c + Σ_p a_p h_pc. The allocation is the set of whole numbers a_p ≥ 0
with Σ_p a_p = 500 that maximises the smallest F_c. Ties are broken by the
larger second-smallest F_c, then the larger maximum F_c, then the smaller
a_CONCERN, then the smaller a_ENDORSEMENT. Expected counts are compared after
rounding to six decimal places. No a_p exceeds the number of eligible items
with that predicted label, and a predicted label with no tranche 1 items,
having no measurable hit rate, receives none. Every allocation is examined.

The limits of this rule are stated now. The hit rates rest on a few hundred
tranche 1 items at most, and the allocation is sensitive to them. The rule
gives no weight to the other classes once the smallest is fixed, so it can
spend relevant items for a small gain in the smallest class. The expected
counts are computed from the same rates that chose the allocation and so tend
to overstate the smallest class; a realised count below them is expected and
is not a shortfall.

**Gate.** The draw goes ahead only if the smallest F_c is at least 200. A
second natural tranche would be expected to leave the smallest class near 164,
twice its tranche 1 count. With predicted labels unrelated to the tranche 1
labels, the smallest F_c averaged about 178 in simulation and reached 200 in
about 5% of runs at most (`tranche2_gate_null_simulation.py`, which uses the
tranche 1 labels and random predicted labels only). The bar is a judgement
call. Its value is that it is fixed before any hit rate is computed. The script
reports pass or fail and nothing else. If the gate fails, nothing is drawn
under this deviation, the files stay sealed, and what replaces tranche 2 is
recorded as a further deviation before any draw.

**Draw.** Eligible items are the 12,166 frame items less the 500 tranche 1
items and any of the 30 calibration items that are in the frame. For each
predicted label, a_p items are drawn by simple random sampling without
replacement from the eligible items with that predicted label. There is no era
stratification and no selection on confidence beyond the relevance threshold.
Random numbers come from NumPy's `default_rng([24916660, 2, k])`, where k
indexes the step as listed in `tranche2_common.py`. The draw is a fixed
function of the frozen scores and the tranche 1 labels: no other seed or
allocation is tried, no override in the scripts is used without a recorded
deviation, and no item is replaced or added afterwards, whatever the realised
class counts and however many items are skipped.

**Reliability subset and assignment.** 100 of the 500 are rated by all three
annotators. They are allocated across predicted labels in proportion to a_p
(largest remainder, ties in the order CONCERN, ENDORSEMENT, OTHER) and drawn at
random within label. The other 400 are shuffled within predicted label and
dealt to A, B and C in turn. Each annotator's sheet is in its own random order.

**Random pool.** A simple random sample of 500 eligible items, drawn without
reference to the predicted label, is the random pool for R1's confidence
comparison. It is not annotated. It may overlap tranche 2, and the overlap is
recorded.

**Presentation.** As in tranche 1: comment text and subreddit, Stage 1 then
Stage 2. The text shown is the text that was scored. Predicted labels, scores
and the reliability flag are not shown. Sheets are .xlsx workbooks with fixed
choices for the label columns, to avoid the text-encoding fault recorded for
one tranche 1 sheet (see `docs/decision_register.md`).

**Subsystem labels.** Collected in the same workbook, not on a separate sheet
returned later as in tranche 1 (Deviation 6). Two columns, `subsystem` and
`subsystem_secondary`, sit beside the Stage 2 class and are hidden when the
workbook is opened. Each annotator first completes Stage 1 and Stage 2 for
every row, then reveals the two columns and labels every row they marked
relevant, under `docs/subsystem_retrofit_instructions.md`: the same seven
primary values and optional secondary value as in tranche 1. As in tranche 1,
the annotator's own Stage 2 class is in view while the subsystem is chosen.
Annotators are asked to finish the first pass before starting the second and
not to change a Stage 1 or Stage 2 answer during it. That order is an
instruction and cannot be enforced.

Tranche 2 subsystem labels are not used to estimate subsystem shares, which
rest on the natural tranche. They have two uses. The first is D28, whose α
conditions cover the reliability units of both tranches ("57 in tranche 1,
plus the tranche 2 equivalent"). The D28 results recorded so far rest on
tranche 1 alone and are provisional. When tranche 2 is complete, subsystem α
is computed on the reliability items of both tranches, pooled, in the two
forms recorded on 30 September 2026: on the items with two or more subsystem
labels, and on the items labelled by all three annotators. Rule 1 and
condition (i) of Rule 2 are applied to the lower of the two figures. α is also
reported for each tranche. Condition (ii) of Rule 2 is not recomputed, because
it rests on the natural tranche. If the pooled figure changes either outcome,
the change and its effect on Family A (Deviation 9) are recorded as a further
deviation. The second use is validation of the subsystem classifier, where
accuracy on boosted items is reported separately from accuracy on natural
items.

**Blinding.** The author is annotator A. From the pre-filter run onwards the
scripts display checks, the gate result and file hashes only: no hit rate,
allocation, expected count, count by predicted label or item-level prediction.
The scores file and its manifest, the hit-rate and allocation files, the master
key, the draw manifest and B's and C's workbooks are not opened by the author
until all three sheets are returned, their hashes are recorded and any
Deviation 2 adjudication is entered. If a sheet has not
been returned by 11 October 2026, the files are unsealed on that date and the
missing ratings are recorded as not returned. This is an undertaking by the
author and cannot be checked. The author knows the rule and the tranche 1
counts, and so knows that every item passed the relevance threshold and that
the allocation favours OTHER and ENDORSEMENT, but not the measured rates or
the numbers drawn. The author also has an interest in those classes reaching
parity, and Rule 8 leaves room for judgement, so tranche 2 class counts on
single-rated items are reported by annotator. B and C are asked not to read
the repository until their sheets are returned, because the targeted classes
can be worked out from it.

**What changes in R1 and Deviation 5.** R1's design is unchanged. Five
statements are changed or narrowed.

1. "Equalising final class counts" (R1) and "as close to equal as those rates
   allow" (Deviation 5) become a rule that maximises the smallest expected
   count. Where a more even allocation would leave the smallest class smaller,
   the less even one is chosen. The least-spread allocation and its expected
   counts are written to the allocation file for comparison and are not used.
2. All three predicted labels may receive items, not only those of the sparse
   classes.
3. Deviation 5's rate, "the share of targeted items that turn out relevant and
   in that class", becomes the full design-weighted table of predicted label
   against tranche 1 label. The design document's sketch, in which each
   class's allocation is inflated by one over its precision, is not used: it
   does not hold the total at 500.
4. R1 says the boosted tranche carries no inclusion probabilities. Under this
   draw it is a stratified simple random sample of the eligible items that are
   predicted relevant: an item with predicted label p has inclusion probability
   a_p / N_p, where N_p is the number of eligible items with that label. Both
   are recorded in the allocation file. Items predicted not relevant have
   probability zero, so the tranche cannot estimate prevalence in the frame,
   and under R1 it is not used for prevalence.
5. R1's statement of bias direction is withdrawn (below).

Three features of the boosted tranche follow from these rules and are reported
with it. It is not stratified by era, so its era composition is not controlled
and will differ from tranche 1's; comparisons between the tranches are reported
within era as well as overall, and the full-set form of R5's temporal
calibration check inherits the difference. The pre-filter reads the text alone,
so a relevant comment that it scores below 0.5 is absent from the boosted
tranche, not merely rarer; this includes comments in r/SelfDrivingCars and
r/waymo that are relevant only by the subreddit rule. The size of the gap is
the pre-filter's Stage 1 recall on tranche 1, reported overall and for those
two subreddits. Within each class the boosted items are those BART-MNLI
recognises, so they may be more explicit than the class as a whole. Tranche 1
holds all of these at the rates its design gives.

**Withdrawal of R1's statement of bias direction.** R1 says the pre-filter
inflates BART-MNLI's measured performance on the boosted portion, so that a
supervised advantage measured there is a lower bound. That statement is
withdrawn. It assumed that confidently classified items would be selected;
this draw selects on predicted label and a relevance threshold only. For the
pre-filter as specified above:

- precision for a predicted label does not depend on a_p, but it is measured
  only among items above the relevance threshold and may differ from precision
  in the frame;
- recall for a class depends on the mix of predicted labels drawn and is zero
  where a_p is zero, so it can be higher or lower than in the frame;
- every boosted item is predicted relevant, so Stage 1 recall is 1 and
  specificity is 0, and the not-relevant class has an F1 of zero.

Macro-F1 on the boosted portion can therefore move either way. Every model is
scored on the same selected items, so figures on the boosted portion and on
the pooled set describe those item sets and are not estimates of performance
on the frame. R1's other statement stands: the natural tranche carries no
pre-filter and provides the unbiased comparison. How the model comparison uses
the two tranches is fixed before the first model run. The zero-shot
configurations to be evaluated are fixed before the sealed files are opened,
because the hit-rate file shows BART-MNLI's performance on tranche 1.

### Deviation 11 — Tranche 2 replaced by a second natural tranche after the Deviation 10 gate failed

**Recorded 4 October 2026, against commit 823270e. The commit date is in the
repository history.**

Deviation 10 set a gate for the boosted tranche: the draw would go ahead only
if the smallest expected final class count was at least 200, and if the gate
failed nothing would be drawn and what replaces tranche 2 would be recorded as
a further deviation before any draw. Deviation 10 and its scripts were
committed at 64a64a8, the pre-filter was then run, and the gate failed. The
result and the file hashes are in `docs/decision_register.md`. Nothing has
been drawn. This deviation records what replaces the boosted tranche. It was
written with the pre-filter scores, the hit rates and the allocation still
sealed. The author has opened none of them: he knows the gate result and the
checks the scripts displayed, and nothing else.

**Replacement.** Tranche 2 is a second natural tranche of 500 items, drawn as
R1 draws tranche 1: a simple random sample without replacement within each of
the three eras, with no pre-filter. The pre-filter of Deviation 10 plays no
part in which items are drawn.

**Why this and not another attempt.** The bar of 200 was fixed before any hit
rate existed, so that going ahead could not be decided after the result.
Lowering the bar, or trying other wordings, thresholds or models until one
passed, would be that decision made after the result, and each further attempt
would have its own chance of passing by noise. A natural tranche needs no
pre-filter and makes no use of the failed one. Stopping at tranche 1 was the
other course that needs no pre-filter; it would leave 500 annotated items and
a 100-item reliability subset where R1 fixes 1,000 and 200.

**What is given up.** R1's objective of equalising final class counts is not
met. A natural tranche is expected to add to each class about what tranche 1
gave it (120, 95 and 82), so the smallest class is expected near 164 and not
at 200 or more. The class counts are whatever the draw gives.

**Draw.** Eligible items are the 12,166 frame items less the 500 tranche 1
items and the 30 calibration items, all of which are in the frame: 11,636
items, as frozen by `tranche2_01_export_prefilter_input.py`. Within each era a
simple random sample without replacement is drawn from the eligible items of
that era, with the tranche 1 allocation: 167 (2016–2018), 167 (2019–2021) and
166 (2022–2025). Random numbers come from NumPy's
`default_rng([24916660, 2, k])` with k from 10 to 17, as listed in
`tranche2_05_draw_natural.py`; none of these values is used by the Deviation
10 scripts. The draw is made once. No other seed or allocation is tried, and
no item is replaced or added afterwards, whatever the realised class counts
and however many items are skipped. The script is committed with this
deviation. Its draw was tested on synthetic data only; before this commit it
was run once on the real inputs with `--check`, which draws and writes
nothing. `tranche2_04_draw.py` is not run.

**Reliability subset and assignment.** 100 of the 500 are rated by all three
annotators: 34, 33 and 33 from the three eras (in proportion to the draw, by
largest remainder, a tie going to the earlier era), drawn at random within
era. The other 400 are shuffled within era and dealt to A, B and C in turn.
Each annotator's sheet is in its own random order.

**Presentation and instructions.** The sheets are as Deviation 10 specifies
under Presentation and Subsystem labels: .xlsx workbooks with fixed choices,
comment text and subreddit, Stage 1 then Stage 2, and the two subsystem
columns hidden until the first pass is finished. The text shown is the text
prepared for the pre-filter under Deviation 10. Tranche 2 is annotated under
codebook v1.0. The special instruction of Deviation 10 is not given: the batch
is a random sample, annotators are told that it was drawn in the same way as
tranche 1, and the codebook applies unchanged, including §3.2.

**Inclusion probabilities and weights.** Within an era, tranche 1 is a simple
random sample of the frame items and contains no calibration item, and tranche
2 is a simple random sample of the items that remain once tranche 1 and the
calibration items are set aside. Taken together they are a simple random
sample, without replacement, of the era's frame items other than the
calibration items: 334, 334 and 332 items. Every item of either tranche
carries the pooled weight N_h / n_h, where N_h is the frame size of its era
(2,495, 3,633 and 6,038) and n_h the pooled draw. The weights use the frame
sizes, as the tranche 1 weights do. That treats the 30 calibration items as
represented by the sample, which is exact if they were drawn at random from
the frame and an approximation otherwise. Leaving them out of N_h would change
no estimate within an era and would move the share of any era by at most 0.2
of a percentage point. For each tranche 2 item the key records the pooled
weight and the weight for its own draw, N_h over 167 or 166, as the tranche 1
key does.

**Missing ratings.** A skipped or unreturned rating is missing, and no item is
replaced. A reliability item with two ratings takes their label if they agree.
If they agree at Stage 1 only, it keeps its Stage 1 label and has no Stage 2
label; if they differ at Stage 1, it has no gold label. A reliability item
with one rating, and a singly-rated item, take that rating. An item with no
rating has no gold label. Items without a gold label are listed by era,
tranche and annotator.

**Prevalence.** R1 estimates prevalence on the natural tranche only. Both
tranches are now natural, so the relevance rate, the class shares and the RQ4
era comparison are estimated on the pooled sample, with the pooled weights and
the intervals of Deviation 3. An item with no gold Stage 1 label is left out,
and n_h in the weight and the interval is then the number of items of the era
that have one; class shares are taken over the relevant items that have a
Stage 2 label. The tranche 1 figures recorded so far are previews on half of
the sample. Each estimate is also reported for the two tranches separately,
each with N_h over its own draw as weight; a difference between the two
annotation rounds is reported and is not used to choose between them. The
composition check of Deviation 8 is repeated on the pooled sample by the same
method, and the decomposition is reported in place of the composition
statement, as there.

**Subsystem labels.** They are collected as Deviation 10 specifies. Because
tranche 2 is now a natural sample, its subsystem labels are used with those of
tranche 1: the shares of the D28 Rule 2 specification are estimated on the
pooled sample with the pooled weights, and the subsystem classifier of
Deviation 9 is validated against the labels of both tranches. Two sentences of
Deviation 10 lapse: the one that keeps tranche 2 subsystem labels out of the
shares, and "Condition (ii) of Rule 2 is not recomputed". In item 3 of the D28
Rule 2 specification, "the tranche 1 natural sample" becomes the pooled
sample. When this was decided, the tranche 1 shares and the outcome of
condition (ii) on them had been seen as a preview. The pooled evaluation is
the one of record whichever way it falls, and the tranche 1 outcome is
reported beside it. Subsystem α is re-applied to D28 as Deviation 10 fixes. If
the pooled sample changes an outcome of D28, the change and its effect on
Family A (Deviation 9) are recorded as a further deviation.

**Blinding.** The pre-filter scores and their manifest, the hit-rate and
allocation files and the sealed register text stay sealed on the terms of
Deviation 10: until all three tranche 2 sheets are returned, their hashes are
recorded and any Deviation 2 adjudication is entered, or 11 October 2026. They
hold BART-MNLI's prediction for every frame item, including the items about to
be annotated, and its performance on tranche 1. Deviation 10's condition that
the zero-shot configurations are fixed before those files are opened stands.
The tranche 2 master key and draw manifest show which items are reliability
items. The author is annotator A and does not open them, or B's and C's
workbooks, until all three sheets are returned or, failing that, 11 October
2026, when outstanding ratings are recorded as not returned. This is an
undertaking by the author and cannot be checked. B and C are still asked not
to read the repository until their sheets are returned, because it holds the
tranche 1 class counts and agreement figures. Tranche 2 class counts on
single-rated items are still reported by annotator.

**What changes in R1, R5, D28 and Deviations 5 and 10.**

1. R1's boosted tranche, its allocation on predicted class and its objective
   of equal class counts are replaced by the natural tranche above. Deviation
   5 and the allocation of Deviation 10 are not used.
2. R1's pre-filter bias analysis lapses, because there is no boosted portion.
   The random pool of Deviation 10 is not drawn. The pre-filter's hit rates on
   tranche 1, the allocation that was not used and the gate result are
   reported once the files are unsealed.
3. R1's statement that the boosted tranche is never used for prevalence has
   nothing left to apply to: tranche 2 carries inclusion probabilities and is
   used for prevalence as set out above.
4. R5's first form of the temporal calibration check, "the natural tranche
   alone", is now both tranches. That form is the one of record, including for
   R5's condition on the corrected series. The check is also reported on each
   tranche alone; a divergence between the tranches is reported as a
   difference between annotation rounds or as sampling variation and is not
   used to choose a form. The confound R5 names does not arise.
5. D28's Rule 2 is evaluated on the pooled sample, as set out under Subsystem
   labels.
6. In Deviation 10, the paragraphs on the draw, the reliability subset and
   assignment, the random pool and the annotator instruction, the account of
   the boosted tranche's features and bias, and the sentence on what the
   author knows of the allocation describe a draw that was not made. The
   codebook decision, the pre-filter specification and its frozen scores, the
   form of the sheets, the collection of subsystem labels, the re-application
   of subsystem α to D28 and the sealing of the pre-filter outputs stand.

R1's reliability subset of 200 items, 100 in each tranche, is unchanged. How
the model comparison uses the two tranches, and what part the frozen
pre-filter scores play in it, are fixed in a further deviation before any
model is run and before the sealed files are opened.

### Deviation 12 — Model comparison, classifier deployment and reliability reporting across the two tranches

**Specified 4 October 2026, against commit 823270e. The commit date is in the
repository history.**

R1, R2 and R5 fix the two tranches, the evaluation protocol, the inference
families and the prevalence correction, and Deviations 1, 2, 10 and 11 fix the
Stage 1 input, the gold label, the pre-filter, the tranche 2 draw and the
treatment of missing ratings. None of them states what the Stage 2 models
receive as input, how folds are formed across two tranches, which items carry
the model comparison and the prevalence correction, how the deployed
classifiers are chosen, or how agreement on the 200 reliability items is
reported. Deviation 10 requires the zero-shot configurations to be fixed
before its sealed files are opened, and Deviation 11 leaves the use of the two
tranches in the model comparison to this deviation. The rules are fixed here,
and the zero-shot configurations are named here with their wording to follow
as stated below. This was done after the tranche 1 agreement, prevalence and
subsystem figures had been seen as previews (see `docs/decision_register.md`)
and after the author knew that the Deviation 10 gate had failed. That result,
and the checks the scripts displayed, are all he knows of BART-MNLI's output.
It was done before the author had seen any classifier's output set against a
label, before B's and C's tranche 2 sheets were returned, and before any
sealed file was opened.

**Configurations.** Five models are compared at Stage 2: DistilBERT and
RoBERTa, fine-tuned; and BART-MNLI (`facebook/bart-large-mnli`), Claude Haiku
4.5 and Claude Sonnet 4.6, zero-shot. Each zero-shot model is run under a
universal and a domain-specific label schema, giving eight configurations. For
BART-MNLI the domain-specific schema is the three class hypotheses of
Deviation 10, unchanged. Its Stage 2 prediction is the predicted class defined
there, whatever the relevance probability, taken from the frozen pre-filter
scores and not re-run. The universal schema, the prompts for the two Claude
models, the checkpoints, the dated model identifiers and the fine-tuning
settings are committed word for word with the model scripts, before the first
comparison run and before the sealed files are opened. Fine-tuning settings
are fixed in that commit and are not tuned on any evaluation fold. A response
that names no class is retried once with the same prompt; a second such
response is recorded as a refusal and scored as an error. No further model is
run on any item of either tranche, for piloting or otherwise, until the model
scripts are committed and all three tranche 2 sheets are returned, their
hashes recorded and any adjudication under Deviations 2 and 7 entered, or 11
October 2026 on the terms of Deviation 10.

**Input.** Every Stage 2 configuration receives the comment text alone
(`clean_body`), as the pre-filter did. R2 says the models see what the
annotators see, and Deviation 1 applies that to Stage 1 by adding the
subreddit to the Stage 1 classifier input. At Stage 2 the annotators could see
the subreddit, but the codebook's subreddit rule concerns relevance only, and a
classifier that used the subreddit could carry the subreddit mix into the
concern series that R3 reweights. The subreddit is therefore withheld from the
Stage 2 models.

**Folds.** Within each tranche, the items with a gold label are sorted by
comment id and assigned to five folds by
`StratifiedKFold(n_splits=5, shuffle=True, random_state=24916660)`, stratified
on the four-way gold label (not relevant, CONCERN, ENDORSEMENT, OTHER). Fold k
of the annotated set is the union of fold k from each tranche. Among relevant
items this is stratification on the Stage 2 gold class, as R5 requires. An
item that is relevant in the gold set but has no Stage 2 gold label (Deviation
11, Missing ratings) forms a fifth stratum and takes no part in Stage 2
training or evaluation. The tranche 1 assignment is committed before any model
is run, and the tranche 2 assignment when its gold labels are formed.

For each fold k, each fine-tuned model is trained on the relevant items of the
other four folds, from both tranches, and predicts the relevant items of fold
k. Each zero-shot configuration predicts every item once.

**Comparison (Family B).** The primary item set is the items of both tranches
that are relevant in the gold set, with the predictions above. Both tranches
are probability samples of the frame (Deviation 11), so no figure rests on
pre-filtered items. Family B is the ten pairwise comparisons of macro-F1 among
the five models, the zero-shot models under the universal schema, each by R5's
item-level permutation test, with Holm–Bonferroni across the ten at 0.05.
Every permutation test in this deviation is seeded with 24916660. Metrics are
unweighted. Per-class F1 is reported for every configuration and
is not tested. Figures under the domain-specific schema, and figures for each
tranche separately, are reported beside them, uncorrected and labelled
exploratory (Family C).

**Stage 2 deployment.** The candidates are the eight configurations. The
deployed classifier is the one with the highest CONCERN-class F1 on the primary
item set. A configuration is tied with it if a two-sided item-level
permutation test of the difference in CONCERN-class F1 (N = 10,000, no
adjustment) gives p ≥ 0.05; this test only defines ties and is not a reported
comparison. Among that configuration and those tied with it, the choice is the
larger TPR − FPR for CONCERN against the other two classes, weighted by the
pooled design weights of Deviation 11; then the lower measured cost per 1,000
comments; then the first in the order DistilBERT, RoBERTa, BART-MNLI, Haiku,
Sonnet, universal before domain-specific. A fine-tuned model that is deployed
is retrained on every relevant gold item from both tranches before it is run
on the corpus.

**Stage 1 deployment.** The deployed relevance classifier receives the
subreddit and the comment text (Deviation 1). It is trained and evaluated on
the gold items of both tranches, on the folds above. The candidates are named
in the model scripts' commit. The one with the highest balanced accuracy is
deployed, an exact tie going to the lower cost, and it is retrained on all
gold items of both tranches before it is run on the corpus. Accuracy is
reported for each class and each subreddit. The text-only variant needed for
the subreddit-rule sensitivity is specified before it is run.

**Prevalence correction.** The true-positive and false-positive rates used by
adjusted classify-and-count are estimated on the primary item set, from the
cross-validated predictions above, weighted by the pooled design weights of
Deviation 11. The same items choose the deployed classifier and supply its
error rates, so the rates are somewhat optimistic; this is stated with the
corrected series. What counts as a material temporal effect under R5 is
defined in a further deviation before the temporal calibration check is run.

**Reliability.** Stage 1 and Stage 2 α are reported for the 200 reliability
items in one matrix and for each tranche's 100, overall and for each class
against the rest, with intervals by the method of Deviation 4.

**Missing ratings.** Gold labels where a rating is missing are formed as
Deviation 11 fixes. Items without a gold label are left out of training and
evaluation. α uses every item with two or more ratings.

**Predictions.** Two predictions are recorded before the author has seen any
model's output set against a label. The pre-filter has been scored against the
tranche 1 labels by the Deviation 10 scripts; of that the author knows only
that the gate failed, which bears weakly on the second prediction.

1. "The reference study finds that the supervised advantage concentrates on its
   implicit, affective class. If CONCERN behaves in this domain as that class
   behaved in theirs, the same concentration should appear here. This is stated
   as a prediction before the evaluation is run, and is reported as confirmed
   or not confirmed rather than as a post-hoc interpretation." It is confirmed
   if, on the primary item set, the gap in per-class F1 between the better
   fine-tuned model and the best zero-shot model under the universal schema,
   each chosen by macro-F1, is largest for CONCERN.
2. Human agreement in tranche 1 is highest on CONCERN (α = 0.836) and lowest on
   OTHER (α = 0.547). If model difficulty tracks human difficulty, the hard
   class here will be OTHER, not CONCERN, the reverse of the reference study.
   It is confirmed if OTHER has the lowest per-class F1 for at least three of
   the five models under the universal schema.

Each is reported as confirmed or not confirmed.

**Events.** The three events named in the 41029 proposal are kept as markers on
the plots only: the Uber ATG fatality in Tempe (2018 Q1), the Cruise robotaxi
suspension (2023 Q4) and the Tesla Cybercab unveil (2024 Q4). No
cross-correlation is run and no causal reading is offered. Changepoints are
reported wherever they fall.

**Success criteria.** The criteria are executional and are fixed here.

1. Krippendorff's α is at least 0.7 at Stage 1 and at Stage 2 on the 200
   reliability items. Any per-class α below 0.7 is reported beside it.
2. The model comparison is completed under R5 and this deviation, with a
   measured cost and refusal rate for every configuration.
3. The concern share is reported with the prevalence correction and intervals,
   and the subsystem measures are reported as Deviation 9 specifies.
4. The temporal calibration check is reported on both tranches, and on each
   alone, before the corrected series (Deviation 11).
5. The relevance rate is reported with a design-weighted interval, beside the
   composition check of Deviation 8 and the text-only sensitivity.
6. The deployed Stage 2 classifier has a TPR − FPR for CONCERN of at least 0.25
   on the primary item set. The bar is a judgement call; its value is that it
   is fixed before the author has seen any classifier scored. If it is not
   met, the uncorrected series is reported beside the corrected one and the
   instability is stated.

Whether the series contain changepoints is a finding, not a criterion.

**Consequence.** R2's statement that the models see what the annotators see is
narrowed at Stage 2, where the subreddit is withheld. R5's fold procedure is
applied within each tranche and over the four-way label. Family B is ten
comparisons on the relevant items of both tranches, and the prevalence
correction takes its error rates from the same items.

### Deviation 13 — Corpus deployment, the temporal calibration check, the subsystem classifier and the series analyses

**Specified 11 and 12 October 2026, against commit 823270e. The commit date is
in the repository history.**

R3, R4 and R5 fix the reweighted and pooled series, the thread-size
decomposition, the trend statistic, the prevalence correction and the temporal
calibration check. Deviations 9, 11 and 12 fix the subsystem estimands, the
pooled sample, the rules that chose the deployed classifiers and the items that
supply their error rates. None of them states what counts as a material
temporal effect, which Deviation 12 requires to be defined before the check is
run; how the deployed classifiers are run over the corpus; what the subsystem
classifier is; what the reweighting target of R3 is; how the intervals of the
corrected series are formed; with what settings the trend statistic is
computed; which changepoint, decomposition and sensitivity procedures are run;
or which analyses planned earlier are not run. These are fixed here. Where this
deviation reads an earlier rule in one of two possible ways, narrows it or
changes it, that is listed under "What changes" below.

**What had been seen.** The rules were fixed after the evaluation of record had
been seen in full (`docs/decision_register.md`, "11 October 2026 — Evaluation
of record; the Deviation 10 files unsealed"): the model comparison with its
results by tranche and by fold, the Stage 1 comparison with accuracy by class
and by subreddit for both candidates and for the deployed model's text-only
variant, the deployed classifiers, their error rates, the reliability figures
and the unsealed figures of Deviation 10.

The author also knew the gold labels of both tranches, including the subsystem
labels. Figures computed from them as previews had been seen. On tranche 1
these were the design-weighted relevance rate overall and by era, the
difference between the 2022–2025 and 2016–2018 rates and its decomposition by
subreddit (Deviation 8), the design-weighted class shares among relevant items,
the agreement figures (Deviation 4), the subsystem α and the shares of the D28
Rule 2 specification (register, 30 September and 4 October 2026). On both
tranches they were the agreement figures (register, 10 October 2026) and the
class counts of the evaluation of record. The register records no tabulation of
the gold Stage 2 classes or of the subsystem labels by era, year or temporal
block, and the author states that none had been made. He also knew the corpus
description figures of `docs/corpus_manifest.md`, which describes corpus v1, of
R3 and R5, and of the design document: counts by tier, by year and by
subreddit, the sizes of the subreddit-year and subreddit-quarter cells that R3
summarises, the lexical proxy, capture by thread size and the within-year
sampling position. Thread size had not been tabulated by year.

The rules were fixed before the deployed Stage 1 classifier or the deployed
Stage 2 classifier had been run on any comment outside the 1,000 items of the
two tranches, and before any output of either existed for such a comment. The
subsystem classifier had been run on no comment, and its prompt had been sent
to no model. Beyond the tranche items, on which every model of the evaluation
of record was run, one model named in this pre-registration had been run more
widely: BART-MNLI, as the pre-filter of Deviation 10, scored the 12,166
comments of the draw frame on 4 October 2026. Its figures stayed sealed until
11 October 2026, apart from the gate result and the checks the scripts
displayed, which the author knew from 4 October 2026 (Deviations 11 and 12).
They are in the register entry named above: its hit rates and its Stage 1
precision and recall on the tranche 1 items, counts by predicted label for
those items and for the 11,636 comments then eligible, the allocation and the
gate figures. The author has made no tabulation of its predictions by quarter,
year, era or temporal block, by subreddit or tier, or by thread size. BART-MNLI
is not deployed, and its scores enter no analysis fixed here. No other model
had been run on any comment of corpus v2.2, or of an earlier version of it, to
classify relevance, stance, sentiment or subsystem: the sentiment model and the
zero-shot subsystem coding that the repository's `README.md` and
`MODEL_NOTES.md` still describe belong to the 41029 proposal and were not run
on this corpus, and the two files are out of date.

No error rate had been computed from the predictions by temporal block or by
era, for either deployed classifier. The results file of the evaluation of
record gives the deployed Stage 2 classifier's results by tranche and by
cross-validation fold, and none by block, era or year; the author states that
the report and the tables written by the same run give none either. The results
file does give the CONCERN rates of every configuration both with the design
weights and without them: for the deployed classifier a false-positive rate of
0.237641 against 0.227882 (85 of 373 items) and a true-positive rate of
0.946922 against 0.946667 (213 of 225). The weights differ by era, so a
weighted figure above the unweighted one means that the rate leans higher where
the weights are larger, in the later eras. For the false-positive rate, if the
items were spread evenly over the three eras and the two earlier eras shared
one rate, the latest era's rate would be about 0.06 higher, about one and a
quarter standard errors from zero; the true-positive rates show no such lean.
The figures hold more than a lean. Given the numbers of gold CONCERN items and
of other gold-relevant items in each era, which follow from the gold labels and
keys the author holds, the weighted rates as the output gives them (to six
decimals, and their difference as an exact fraction) are enough to fix the
classifier's true and false positives in each era exactly, and the latest era
is the late block of the check below but for the comments created between the
boundary and the end of 2021. That reconstruction had not been made: not by the
author, and not in the review and redrafting of this deviation, in which no
annotation data and no prediction file was used. The approximate inference
above is the only use made of the figures. If the false-positive rate is higher
in the late block, correcting with block-specific rates lowers the late
quarters and raises the early ones, so the block-specific series would have a
lower slope than the primary series (both are defined below). The figures were
in view when the trigger for a material effect was decided; the inference was
drawn afterwards, while this deviation was reviewed, and before the
qualification of a material effect was added.

The prediction files, gold labels and timestamps needed to compute rates by
block are held by the author. The statements in this section about what had not
been run, computed, tabulated or seen are the author's and cannot be checked
from the files.

**Corpus runs.** Periods are calendar quarters, half-years and years of a
comment's creation time in UTC; the eras and the two temporal blocks are not
periods in this sense. The comment text of every run is `clean_body` of corpus
v2.2 prepared as Deviation 10 prepared it for the pre-filter, the text every
evaluation input used; for the 12,166 frame comments it is checked against the
pre-filter input file of record, from which the evaluation inputs were taken.

The deployed Stage 1 classifier (RoBERTa, subreddit and comment) is retrained
once on the 1,000 tranche items under the final-retraining rule of the model
scripts' commit (`bb3fbfe`): the settings of the evaluation runs, no held-out
split, seed 24916660, and 5 epochs, the median of its best epochs (5, 5, 5, 2
and 2). It is run once over all 12,776 comments of corpus v2.2, with the input
of that commit (the sentence pair "r/" + subreddit and comment, only the
comment truncated; Deviation 1). A comment is classified relevant by the
decision rule of the cross-validation runs of record (the model scripts'
commit, `bb3fbfe`), unchanged.

The deployed Stage 2 classifier (Claude Sonnet 4.6, `claude-sonnet-4-6`,
domain-specific schema, with the prompt, settings, identifier checks, reading
of the answer and retry rule of that commit) is run once over every Tier 1+2
comment classified relevant, on the comment text alone. Tier 3 comments receive
Stage 1 only: R5 analyses Tier 3 qualitatively, "subject to the same relevance
filter as the other tiers".

The 1,000 tranche items are classified like every other comment, so that the
series rest on one instrument. For them the Stage 1 prediction is in-sample,
because the retrained model has seen their labels; this is stated with the
series. On the tranche items that both runs cover, the Stage 2 labels of the
corpus run and of the evaluation run are compared: the number and share given
the same label are reported with the table of the two runs' labels, a refusal
being a fourth value. The error rates of record are those of the evaluation run
and are not re-estimated.

A response that names no class is retried once, and a second such response is a
refusal (Deviation 12). On the corpus a refusal counts as not CONCERN in the
concern share, as the register fixed for the rates before any prediction was
scored (11 October 2026, the entry on the evaluation script), and as OTHER in
the three-class correction below. Refusals are counted by quarter. A call that
fails after the client's retries with a connection error, a timeout, a
rate-limit response (status 429) or a server error (status 500 or above) is not
a refusal: the run stops and resumes from its log. The run also stops on any
other error from the API, as the evaluation runs did. When it is resumed, the
comment that was rejected is sent first. If it is rejected again it is set
aside and the run goes on; if the next 20 comments are all answered without an
API error, the comment set aside is recorded as a refusal (in the subsystem
run, as unclassified) and listed in the register, and otherwise the run stops
again. The request is not altered to get it through.

Every call is logged as in the evaluation runs, and each run's outputs are
hashed and recorded in the register. The two API runs, Stage 2 and the
subsystem classifier below, are held under one spending ceiling of US$23: the
Claude Console's monthly limit of US$25 less the US$1.8737 spent on the
evaluation runs, rounded down. It is measured over every logged call of both
runs and their connection checks at the list prices of the model scripts'
commit. A call under way at a hard stop is not logged and may still be billed
(register, 11 October 2026, the entry on the model scripts), so the measured
spend can fall short of the true spend by up to five calls at each stop. The
Stage 2 run is made first. Before the subsystem run its cost is estimated as
((IN + n × D) × 3 + OUT × 15) / 1,000,000 US dollars, where 3 and 15 are the
list prices in US dollars per million input and output tokens, IN and OUT are
the input and output tokens logged by the Stage 2 run, n is the number of its
calls, and D is the number of input tokens the API reports for the subsystem
prompt on the connection-check sentence less the number it reports for the
Stage 2 prompt (domain-specific schema) on the same sentence. OUT overstates
the output of a run that returns a label name, and nothing is added for retries
or for the tranche items classified for validation only. The subsystem run is
not started if the estimate, added to the spend so far, is above the ceiling,
and a run halts if the ceiling is reached while it is under way. In either case
the only thing that may change is the ceiling: the new ceiling is recorded in
the register with the reason, the run then starts or resumes from its log, each
comment keeping the answer it already has, and the model, prompt, settings and
set of comments stay as fixed here. No output of the Stage 2 run is tabulated
before the subsystem run is complete.

**Subsystem classifier (Deviation 9).** The corpus-wide primary subsystem is
assigned by Claude Sonnet 4.6 (`claude-sonnet-4-6`), zero-shot, with the
settings, identifier checks, concurrency and retry rule of the deployed Stage 2
classifier. It chooses one of the seven primary values of the subsystem
retrofit (Deviation 6), and it is given the comment text alone. The annotators
chose the subsystem with their own Stage 2 class in view (Deviation 10) and
could see the subreddit, which the instructions tell them not to let decide;
the classifier is given neither, so that neither is an input to the subsystem
label. Its prompt is the Stage 2 template with two changes: each label line
gives the value's name and its definition, and the last line asks for the name
alone, so that the definitions can be given in full without being repeated in
every answer. The definitions are those the annotators were given for the
subsystem labels of both tranches (`docs/subsystem_retrofit_instructions.md`,
version 1.0, "The seven values"; Deviations 6 and 10), word for word with the
Markdown marks removed; the definition of `none` ends with the first sentence
of that document's rule 7. The other rules of its section "How to choose" are
not given. The prompt reads as follows, each label on one line:

```
You are a careful annotator.
Choose exactly ONE label for the comment.

Candidate labels:
- sensing: the vehicle's perception of the world outside it. Cameras, lidar, radar, ultrasonics, sensor fusion, what the car can and cannot see, sensor failure or degradation, camera-only versus lidar arguments.
- in_vehicle_networks: data moving inside the vehicle. CAN bus, ECUs, domain controllers, infotainment (IVI) as a networked component, over-the-air software updates to vehicle systems, onboard compute.
- v2x: the vehicle talking to something outside itself. V2V, V2I, vehicle-to-cloud, fleet telemetry uplink, connected infrastructure, traffic signal communication, remote operation or teleoperation links.
- cybersecurity: attack, defence, or vulnerability. Hacking, remote takeover, spoofing a sensor or GPS, ransomware, key or access control, security of updates.
- privacy: what is collected about people and who can see it. Cabin cameras, location history, driver monitoring, footage handed to police or insurers, surveillance framing, whether owners can opt out.
- data_governance: the rules and ownership around data rather than the data path itself. Who owns the recorded data, regulation and compliance, disclosure obligations, data retention, consent regimes, standards bodies, liability framed around data or evidence.
- none: the comment is CAV-relevant but engages no identifiable subsystem. This is a real and common answer. Use it for comments about autonomy in general, company or market commentary, timelines, safety statistics with no mechanism, and jokes. When genuinely torn between a subsystem and none, choose none.

Comment:
{comment text}

Return ONLY the label name.
```

The codebook's reference table of subsystems (`docs/annotation_codebook.md`,
§4.3), which the annotators also had, is not the source of the definitions. It
differs from the instructions: it lists teleoperation and "the driving system
itself" under in-vehicle networks and "Who owns or accesses vehicle data,
liability, accountability, regulation" under data governance, where the
instructions put teleoperation links under V2X, who can see what is collected
under privacy, liability under data governance only when it is framed around
data or evidence, and autonomy in general under `none`. It also lists
localisation under sensing, which the instructions do not mention. The
subsystem labels were assigned under the instructions, so the classifier is
given the instructions.

The answer is read by the rule of the evaluation runs, adapted to label names.
It is cleaned as in those runs (white space collapsed, lower case, the same
characters stripped from both ends). If the cleaned answer is one of the seven
label names, that name is the label. Otherwise each name is searched for in it:
an underscore of the name may be matched by an underscore, one space or one
hyphen, and a match counts only where the character before it and the character
after it, if there is one, is not a letter from a to z, a digit or an
underscore (`re.search("(?<![a-z0-9_])" + name.replace("_", "[ _-]") +
"(?![a-z0-9_])", answer)`). The answer is not altered, and if exactly one name
is matched, once or more, it is the label. The evaluation runs looked for a
label phrase anywhere in the answer; a name is matched here as a whole word
because `none` occurs inside other words. An answer that names no label, or
more than one, is retried once with the same prompt; after a second such answer
the comment is unclassified. Unclassified comments form an eighth value, which
is reported and never tested. The classifier assigns no secondary label: the
descriptive sensitivity on secondary labels that Deviation 9 names is reported
from the annotators' secondary labels on the pooled sample (Deviation 7), and
none is made corpus-wide.

The classifier is run once over every Tier 1+2 comment classified relevant, and
over any tranche item that is relevant in the gold set and not among them, so
that it is validated on every item of both tranches that has a gold primary
subsystem (Deviation 7); items without one are counted, and labels given only
for validation enter no corpus figure. Two shares are reported for each value,
with Wilson 95% intervals on the unweighted counts: of the items with that gold
value, the share to which the classifier gives the same value; and of the items
to which the classifier gives that value, the share whose gold value is the
same. They are given for both tranches together and for each tranche, with the
table of gold value against classifier value and the overall agreement. The
three tranche 2 items whose gold subsystem was adjudicated (register, 10
October 2026) were decided with reasons that follow the codebook's table, so
the figures are also given without them. Subsystem shares are not corrected for
the subsystem classifier's error (Deviation 9).

The design document's keyword-then-BART-MNLI coding is not used. In the Stage 2
comparison of record BART-MNLI had the lowest macro-F1 of the five models under
either schema (0.328 and 0.356) and predicted OTHER for none of the 598 items
under the universal schema and for one under the domain-specific schema. Claude
Sonnet 4.6 under the domain-specific schema had the highest macro-F1 (0.750)
and was deployed at Stage 2 after a tie with Claude Haiku 4.5 on CONCERN-class
F1 (Deviation 12). No model has been compared on subsystem coding: the choice
carries a result on stance to a different task, and the classifier's agreement
with the gold labels is measured as above and not assumed.

If the pooled subsystem α brings D28 Rule 1 into effect (Deviations 10 and 11),
the change is recorded as a further deviation, as Deviation 11 requires, before
any corpus output of the subsystem classifier is tabulated. The classifier is
not run again: its six subsystem values are collapsed into the three groups of
Deviation 6, `none` staying apart.

**Temporal calibration check (R5, Deviation 12).** The check is reported before
the corrected series and conditions it (R5). R5 lists the chronological
two-block split at the frozen boundary as the evaluation structure of the
check, in a protocol whose primary metrics are macro-F1 and per-class F1, and
does not say which classifier is evaluated on the split or which quantity
conditions the corrected series. Here the error rates of the deployed Stage 2
classifier, which are what the correction uses, are estimated on it. The items
of the primary item set (Deviation 12) are split at `2021-12-29T21:39:22Z` into
an early block (created before the boundary) and a late block (created at or
after it), and the TPR and FPR for CONCERN against the other two classes,
weighted by the pooled design weights of Deviation 11, are computed for each
block from the predictions of record. This is done on both tranches together,
the form of record (Deviation 11), and on each tranche alone. Each block rate
and each late-minus-early difference is reported with a 95% percentile interval
from the item resamples defined below, a figure for one tranche being formed
from those items of each resample that belong to that tranche, with the pooled
design weights and no separate draw; the unweighted counts behind each rate are
given with a Wilson 95% interval, because a percentile interval cannot move off
a rate of exactly 1. The macro-F1 and per-class F1 of the deployed Stage 2
classifier are reported for each block, unweighted, as description. The
deployed classifier is zero-shot, so no model is trained on one block and
tested on the other, and the fine-tuned models, none of which is deployed at
Stage 2, are not run on the split. For the deployed Stage 1 classifier, which
is trained on items of every era and run over comments of every era, the
accuracy on each class, with Wilson 95% intervals, and the balanced accuracy
are reported for each block from its cross-validated predictions, unweighted as
in the evaluation of record, as description.

The *primary series* is the corrected reweighted concern share by quarter, 2016
Q1 to 2024 Q4, with the overall rates of record; the same series by year or
half-year is named as such. A temporal effect is *material* when the series
recomputed with block-specific error rates fails either of R3's two criteria
against the primary series. The *block-specific series* is the primary series
recomputed with the early-block rates for every quarter up to and including
2021 Q4 and the late-block rates from 2022 Q1, the block rates being those of
both tranches together. The boundary falls at 21:39 UTC on 29 December 2021, so
comments created from then to the end of 31 December 2021 lie in the late block
and take the early rates. The criteria are R3's, with the block-specific series
in the place of the pooled one: agreement of conclusion (the sign of Sen's
slope, and whether the Mann–Kendall test is significant) and overlap of
estimate (the block-specific Sen's slope falls inside the interval of the
primary series' Sen's slope). Here and wherever this deviation applies R3's two
criteria, the interval is the Gilbert interval defined under Trend statistics,
computed on the 36 quarterly values before clipping; a test is significant when
its p-value is below 0.05; a Sen's slope of exactly zero agrees in sign only
with another of zero; and the quarters of 2025 enter neither criterion.

Each block's rates rest on part of the 598 items, so the block-specific series
can fail the criteria through sampling error in those rates alone. A material
effect is therefore qualified. In each of the 2,000 resamples defined below the
primary and the block-specific series are both recomputed, from the overall and
the block rates of the redrawn items and the classified shares of the redrawn
comments, and the difference between their Sen's slopes, block-specific minus
primary, is taken. The 95% percentile interval of that difference is reported
whatever the outcome. A material effect is described as *established* if the
interval excludes zero, and as *not distinguishable from sampling error in the
block rates* if it includes zero.

Whatever the outcome, both series are reported with their Sen's slopes and
Gilbert intervals, beside the block rates and their differences. If the effect
is not material, the primary series is the result and one sentence records that
the block-specific series agrees. If it is material, the conclusion drawn from
the primary series, a trend or the absence of one, is stated as holding only
under error rates that are stable over time, with the qualification above, and
the finding is carried into the discussion and the limitations. The primary
series keeps the overall rates in either case: R5 treats a material effect as a
condition on the corrected series and does not provide for another series to
take its place. The rule rests on R3's criteria and not on a cut-off on the
rates themselves, because a difference in rates matters to RQ1 only through
what it does to the corrected trend.

**Prevalence correction (R5, Deviation 12).** The concern share of a period is
the reweighted share of comments classified CONCERN among the Tier 1+2 comments
classified relevant in the period, corrected by adjusted classify-and-count
with the weighted CONCERN rates of record of the deployed Stage 2 classifier
(TPR 0.946922 and FPR 0.237641 in the evaluation output of record, 0.9469 and
0.2376 in the register): corrected share = (classified share − FPR) / (TPR −
FPR). The rates are recomputed at full precision from the predictions of record
and checked against these figures. A share for a half-year or a year is formed
from the comments of that period, not from quarterly values. An out-of-range
value is clipped to [0, 1] and the raw value is reported beside it (R5). R5
does not say which of the two enters a statistic: trend statistics, the
changepoint search, the decompositions and all differences use the values
before clipping, except in the two relevance-error series below, and the
clipped values are those plotted and tabulated.

R5's robustness check by SLD expectation-maximisation is not run: it needs
class posterior probabilities, and the deployed classifier returns a label
only. In its place the three-class adjusted classify-and-count is reported for
every quarter. Let M_ij be the weighted rate at which items of gold class i are
classified j on the primary item set, and q_j the quarter's reweighted share of
comments classified j, a refusal counted as OTHER. The corrected class shares
p_i of the quarter solve the three equations Σ_i p_i M_ij = q_j. For display,
negative components are set to zero and the rest rescaled to sum to one, with
the raw solution beside them; Sen's slope, the Mann–Kendall test, R3's criteria
and every resample use the CONCERN component of the raw solution. The binary
correction is the special case in which, among the comments that are not
CONCERN, ENDORSEMENT and OTHER keep in every quarter the proportions they have
in the weighted sample; the classifier takes the two for CONCERN at different
rates (32 of 189 and 53 of 184 items in the evaluation output of record), and
the three-class correction estimates their proportions for each quarter
instead. Both corrections assume that the rates M_ij are the same in every
quarter. The CONCERN component carries the intervals defined below and is
compared with the primary series by R3's two criteria; the comparison is
exploratory (Family C) and leaves the primary series unchanged. The same items
chose the deployed classifier and supply its rates, so the rates are somewhat
optimistic; this is stated with the series (Deviation 12).

**Intervals for the corrected series.** Every corrected share of a corpus
series that is reported, and every reported difference between two of them,
carries a 95% percentile interval (the 2.5th and 97.5th percentiles,
`numpy.percentile` with its default method) from 2,000 bootstrap resamples. The
two relevance-error series below and the ENDORSEMENT and OTHER components of
the three-class correction carry none. One resample is one redraw of the
primary item set and one redraw of the corpus comments: resample k uses row k
of every index array below, and every statistic of that resample, differences
and slopes included, is formed from those same two draws. Percentiles are taken
before the ends of an interval for a share are clipped to [0, 1]. The number of
resamples is a judgement call; its value is that it is fixed before any corpus
output exists.

The floors of ten comments, the subreddit-years left out and the periods that
have a value are fixed on the full corpus and are not applied again in a
resample. Where a statistic has no value in a resample, because its denominator
is empty there or its equations have no solution, that resample is left out for
that statistic only: the percentiles are taken over those that remain
(`numpy.nanpercentile`), the number left out is reported, and no interval is
given where it exceeds 100 of the 2,000.

*Items.* The 598 items are redrawn with replacement within each era stratum,
the tranches pooled, and every rate (TPR, FPR, the block rates and the rates
M_ij) is re-estimated from the redrawn items with the pooled design weights.
The 2,000 item resamples are drawn first and on their own generator,
`numpy.random.default_rng([24916660, 3, 1])`: stratum by stratum in era order,
the items of a stratum sorted by comment id as strings in code-point order,
each stratum's draw being `rng.integers(0, n, size=(2000, n))` for its n items.
They are the resamples of the temporal calibration check, and they serve every
period and every series, so that all intervals share one draw of the rates. The
SHA-256 of the three index arrays (each as little-endian 64-bit integers in
row-major order, the three joined in era order) is recorded in the register
when they are first generated, and every later script checks it.

*Comments.* The Tier 1+2 comments classified relevant are redrawn by thread
within each quarter, 2016 Q1 to 2025 Q2. Among the m threads (`parsedPostId`)
with at least one such comment in the quarter, m threads are drawn with
replacement, and every such comment of a drawn thread in that quarter is taken.
The generator is `numpy.random.default_rng([24916660, 3, 2])`, quarter by
quarter in time order, the threads of a quarter sorted by id as strings in
code-point order, each quarter's draw being `rng.integers(0, m, size=(2000,
m))`. Comments of one thread are not independent of each other, and redrawing a
thread's comments of a quarter together keeps that dependence in the interval.
Each comment keeps the reweighting weight it has in the full corpus: the target
shares, the year weights and the subreddit-years left out are not recomputed in
a resample, while every share and composition formed from the comments is
recomputed from the redrawn comments with those weights.

The interval reflects sampling error in the Stage 2 error rates and the
variability of the classified share among the threads of a period. It does not
reflect Stage 1 error (examined below), error in the gold labels, the choice of
the deployed classifier on the same items, or change in the error rates over
time, which is the subject of the temporal calibration check. Design-weighted
prevalence and class-share estimates on the annotated sample keep the intervals
of Deviation 3.

**Reweighting (R3).** The reweighted series is primary. R3 weights by subreddit
at annual resolution, over the eight Tier 1+2 subreddits, and does not state
the target composition or what is done with a subreddit that is absent or
nearly absent in a year (`docs/corpus_manifest.md`, which describes corpus v1,
shows r/RealTesla with no comment in 2016 and r/waymo with none in 2016 or
2017). Both are fixed here, on the Tier 1+2 comments classified relevant.

The target share of a subreddit is its share of all such comments in 2016–2024,
computed once: the mix of the comments that the trend statistic covers, in
which each year counts in proportion to its number of such comments. A
subreddit is *retained* in a year when it has ten or more such comments in that
year, ten being the figure R3 uses to describe a sparse cell; the comments of a
subreddit-year that is not retained are left out of that year's reweighted
series. In year y a retained comment of subreddit g has weight w(g, y) = t(g,
y) / s(g, y), where t(g, y) is the target share of g divided by the summed
target shares of the subreddits retained in y, and s(g, y) is g's share of the
retained comments of y. The weights of a year sum to its number of retained
comments, so a figure pooled over years weights each year by that number. The
weights of a year are applied to its quarters, as R3 requires, and to its
half-years, so a year's mix equals the target of its retained subreddits
exactly and a quarter's only approximately; no further rule applies when a
retained subreddit has no comment in a quarter. Weights are not trimmed. The
subreddit-years left out, their comment counts, the largest weight and the
effective sample size of each quarter (the square of the summed weights over
the sum of the squared weights) are tabulated. The quarters of 2025 are
weighted by the same rule on its four months, with the 2016–2024 target; under
R3 they enter no trend statistic and no annual table, and are shown on the
quarterly plot only. The target and the floor of ten are judgement calls; their
value is that they are fixed before any corpus output exists.

A year with a subreddit left out is standardised to a different mix from the
other years. The series restricted, in every year, to the subreddits retained
in all nine years 2016–2024 is therefore reported beside the primary series and
compared with it by R3's two criteria. Its target shares are those of the
primary series renormalised over those subreddits, and its year weights are
recomputed on them; in 2025 it uses those of them that are also retained
in 2025. If either criterion fails, both series are reported in full, and the
difference is stated as the effect of leaving out the subreddits not retained
in every year.

The pooled series weights every Tier 1+2 comment classified relevant equally,
including those left out of the reweighted series; it is corrected as the
primary series is and compared with it as R3 states. R3's tier-level quarterly
reweighting gives each quarter the value v_1 p_1 + v_2 p_2, where p_1 and p_2
are the shares classified CONCERN among that quarter's Tier 1 and Tier 2
comments classified relevant, and v_1 and v_2 are the two tiers' shares of all
such comments in 2016–2024. A quarter in which either tier has fewer than ten
comments classified relevant has no value. The series is corrected and
reported, with its Sen's slope, Gilbert interval and Mann–Kendall p-value, as
the robustness check R3 names.

**Trend statistics (R3).** The primary trend statistic is Sen's slope, the
median of the pairwise slopes, on the 36 quarterly values of the primary
series, reported per quarter and per year, the yearly slope and its limits
being four times the quarterly ones. R3 asks for a distribution-free confidence
interval and gives neither its level nor its method. It is the 95% interval of
Gilbert (1987) with ranks rounded to the nearest whole number, which
`scipy.stats.theilslopes(y, x, alpha=0.95)` returns and which is used because
`pymannkendall` returns the slope without an interval; for 36 untied values its
limits are the 243rd and 388th of the 630 ordered pairwise slopes. This is the
*Gilbert interval* of this deviation. Significance is by the Mann–Kendall test
that R3 commits, two-sided, from `pymannkendall.original_test` (normal
approximation with continuity correction and tie-corrected variance). R3 asks
whether the test is significant "at the Holm-corrected level" and names no
family; RQ1's test belongs to none of the families of R5, so it is taken as a
family of one and the level is 0.05.

For the primary series the Hamed and Rao (1998) variance correction for serial
correlation, `pymannkendall.hamed_rao_modification_test` with `lag=1`, is
reported beside the test and does not replace it. One lag is a judgement call:
36 values support no more. As implemented, the correction changes the variance
only when the lag-1 autocorrelation of the detrended ranks lies more than 1.96
divided by the square root of the number of values from zero (0.327 for 36
values), and otherwise returns the uncorrected test. The autocorrelation, as
the library computes it (the summed products of successive deviations of the
ranks from their mean, over their summed squares), is reported, and if the
corrected variance is not positive the corrected test is reported as not
computable. A series of fewer than ten values is tested by the exact two-sided
permutation p-value of the Mann–Kendall statistic over all orderings of its
values, because the normal approximation is poor at that length; the
`pymannkendall` value is given beside it. A period with no comment in the
denominator of its share has no value: it is left out of the Mann–Kendall
statistic, pairwise slopes use the true distance in time, and the Hamed–Rao
correction, the changepoint search and STL are not computed for a series with a
gap.

R3's two criteria are applied to the pooled series against the reweighted
series as written, with the readings above. Where this deviation compares
another series with the primary series by R3's two criteria and states no other
consequence, both are reported with their Sen's slopes, Gilbert intervals and
Mann–Kendall p-values whichever way the criteria fall; a criterion that fails
is stated with the series and in the limitations, and the primary series stays
the result. The corpus manifest records that sampling within a year is uneven
and does not support claims at quarterly resolution; the 36 quarterly values
are used as R3 commits, as repeated measurements of one trend, and no claim is
made about a single quarter.

**Changepoints and decomposition (Deviation 12).** Changepoints are sought in
the primary series and, where stated below, in the block-specific series, and
in no other: the 36 quarterly values of a series before clipping, standardised
to zero mean and unit variance (divisor 36). For each penalty of the fixed grid
1, 2, 3, 4, 6, 8, 12 and 16, the segmentation is the one that minimises the sum
of squared deviations from the segment means plus the penalty times the number
of changepoints, every segment being at least four quarters long. It is found
exactly, by dynamic programming over zero to eight changepoints
(`ruptures.Dynp`, least-squares cost, minimum size 4, jump 1), because the
pruned search of `ruptures.Pelt` is not exact under a minimum segment length. A
changepoint is named by the first quarter of the new segment and counts as
appearing at a grid value only if that same quarter is returned. Every
changepoint is reported with the number of grid values at which it appears.

A least-squares cost for a change in mean places changepoints along any steady
trend, and at small penalties in noise alone, so appearing across the grid is
not by itself evidence of a step. The report calls a changepoint *supported*
only if (a) the same quarter is returned at every grid value from 4 to 16 and
(b) a single step at that quarter fits the 36 values better than a straight
line by BIC, both fitted by least squares: 36 ln(RSS_step / 36) + 3 ln 36 < 36
ln(RSS_line / 36) + 2 ln 36. The label is descriptive and carries no error
rate: a steady trend with noise, or serially correlated noise, can meet both
conditions. Of a changepoint that does not meet both, and of the series when
none does, the report states that the series does not distinguish a step from a
steady trend or from noise. A supported changepoint at 2021 Q4, 2022 Q1 or 2022
Q2 is reported with the note that a difference in error rates between the two
blocks of the temporal calibration check would put a step near the boundary;
the search is repeated on the block-specific series, with the same grid and the
same two conditions, and the changepoint keeps the label only if the same
quarter is supported there. Because no claim is made about a single quarter, a
supported changepoint is described by its year. The grid, the range from 4 to
16 and the minimum segment of four quarters are judgement calls and are not
derived; their value is that they are fixed before the series exists.

STL decomposition of the 36 values before clipping, not standardised
(`statsmodels.tsa.seasonal.STL`: period 4, robust, seasonal smoother 7, trend
smoother 9, low-pass filter 5, all of degree 1, no jumps, 2 inner and 15 outer
iterations), is reported in an appendix as a description of the trend component
and not as a test. As a supporting estimate labelled exploratory (Family C), a
binomial generalised linear model with logit link, unweighted, of the
classified CONCERN indicator (a refusal counted as not CONCERN) on calendar
year, as a number centred at 2020, and subreddit, as an eight-level factor,
over every Tier 1+2 comment classified relevant in 2016–2024, is reported with
the year odds ratio and its Wald 95% interval from standard errors clustered on
thread (`cov_type="cluster"` with the library's defaults). It rests on
classified labels and is not corrected for classifier error, which draws the
odds ratio towards one if the error rates do not change over time and can move
it either way if they do. The three events of Deviation 12 appear as markers on
the plots only.

**Thread-size composition (R4).** `commentsCount` is joined from the post
record of each comment's thread (`parsedPostId`); where a thread has more than
one post record, the largest reported count is used. The buckets are those of
`docs/corpus_manifest.md`: 1–5, 6–15, 16–50, 51–200, 201–1,000 and more than
1,000 reported comments. A comment whose thread has no post record, no reported
count or a reported count of zero is left out of the decomposition and counted.
The decomposition is annual, 2016–2024. It uses the Stage 2 labels as
classified, on the remaining comments that the reweighting retains, each with
its weight from the primary series. For bucket b and year y, a(b, y) is the
weighted share of the year's comments in the bucket and r(b) is the weighted
share classified CONCERN among all the bucket's comments of 2016–2024. The
synthetic series is S(y) = Σ_b a(b, y) r(b), and the observed series O(y) is
the weighted share classified CONCERN in year y on the same comments.

R4 calls C and T the "change across the study span" and does not say how the
change is measured or over which years. The plain reading, the last year minus
the first, is not used, because it would carry the noise of both years: C is
eight times Sen's slope of the nine values of S, and T is eight times Sen's
slope of the nine values of O, over 2016–2024, the span of R3's trend
statistic. |C| is compared with 0.20 × |T| and 0.50 × |T| as R4 fixes. The
correction is the same increasing straight-line map of the classified share in
every year, and the a(b, y) of a year sum to one, so C / T is the same
corrected or uncorrected. Because r(b) is pooled over the years, S also moves
when the concern share and the bucket mix both trend, even if no bucket differs
from another within a year. The ratio that a straight-line trend common to
every bucket would produce is therefore reported beside C / T: it is Sen's
slope over the nine years of Σ_b a(b, y) y_b, where y_b is the weighted mean
year of the comments of bucket b.

R4's outcomes use two terms it does not define. The trend "stated net of" C is
T − C, given also on the corrected scale as (T − C) / (TPR − FPR). The
"size-stratified series" is the annual series Z(y) = Σ_b a(b) r(b, y), where
a(b) is the bucket's weighted share of the comments of 2016–2024 and r(b, y) is
the weighted share classified CONCERN in bucket b and year y; a bucket with no
comment in a year is left out of that year and the a(b) of the others are
rescaled. It is corrected like the primary series, and its trend is eight times
its Sen's slope, with the exact test for nine values. It is reported, with its
trend, whatever the outcome. If R4's third outcome applies, it is reported
first as the result for RQ1, with the primary series beside it; every
comparison in this deviation is still made against the quarterly reweighted
series, which keeps the name primary series here.

R4's comparison presupposes a trend to be explained. If the Mann–Kendall test
of the primary series is not significant, T cannot be told from zero and the
ratio is governed by noise: |C|, 0.20 × |T| and 0.50 × |T| are then reported,
R4's outcomes are not applied, and |C| / (TPR − FPR) is reported as a change in
corrected share.

**Relevance error.** The Stage 1 classifier's error is reported, not corrected.
From its cross-validated predictions on the 1,000 tranche items two shares are
estimated for each era stratum (within a stratum the design weights are equal,
so each is a sample proportion): e_in, the share of comments classified
relevant that are not relevant, and e_out, the share of comments classified not
relevant that are relevant. Take a quarter with n_in Tier 1+2 comments
classified relevant and n_out classified not relevant (unweighted counts over
the subreddit-years that the reweighting retains) and reweighted classified
CONCERN share x, with e_in and e_out those of the era that contains the
quarter. The expected number wrongly included is e_in × n_in and the expected
number wrongly left out is e_out × n_out. A comment wrongly included has no
stance; what is unknown is whether Stage 2 classified it CONCERN. A comment
wrongly left out was never classified; what is unknown is its stance. Two
series are formed by taking the two unknowns to opposite extremes.

- Low series: every comment wrongly included was classified CONCERN and no
  comment wrongly left out is CONCERN. The classified share among the comments
  rightly included is max(x − e_in, 0) / (1 − e_in); it is corrected as the
  primary series is and clipped to [0, 1], giving p_lo, and the value is p_lo ×
  (n_in − e_in × n_in) / (n_in − e_in × n_in + e_out × n_out).
- High series: no comment wrongly included was classified CONCERN and every
  comment wrongly left out is CONCERN. The classified share among the comments
  rightly included is min(x, 1 − e_in) / (1 − e_in); it is corrected and
  clipped, giving p_hi, and the value is (p_hi × (n_in − e_in × n_in) + e_out ×
  n_out) / (n_in − e_in × n_in + e_out × n_out).

The two series are reported with the primary series, each with its Sen's slope.
In them p_lo and p_hi are clipped as written and the slope is taken on the
values so formed, the one exception to the rule that trend statistics use the
values before clipping. They bound the series at the estimated e_in and e_out
if the comments wrongly included and wrongly left out carry the average weight
of their quarter; where such comments are concentrated in subreddits with large
or small weights the series can lie outside them. They carry no interval, their
slopes are not bounds on the slope, and they are wide by construction. Where
the series is likely to lie between them is shown by two figures from the
annotated sample, with Wilson 95% intervals on the unweighted counts: the share
of the wrongly included items that the Stage 2 predictions of record classify
CONCERN, and the gold CONCERN share of the wrongly left out items. The shares
e_in and e_out are applied to every comment of a quarter, the tranche items
included, although their Stage 1 predictions in the corpus run are in-sample.

On the annotated sample, with the pooled design weights, the CONCERN share is
also reported three ways: among the gold-relevant items, from the gold labels;
among the items that the cross-validated Stage 1 prediction classifies
relevant, as the share that the Stage 2 prediction of record classifies
CONCERN; and that second share corrected by the binary adjusted
classify-and-count with the rates of record. The first two carry the intervals
of Deviation 3 and the third carries none. The Stage 2 rates were estimated on
the gold-relevant items of this sample, so the third figure differs from the
first only through Stage 1 error.

**RQ4 and the subreddit rule (Deviations 1, 8 and 11).** The relevance rate
overall and by era is the design-weighted estimate on the pooled sample with
the intervals of Deviation 3, and the composition check of Deviation 8 is
repeated on the pooled sample, as Deviation 11 fixes. Beside it, as the
text-only sensitivity of Deviation 12, the design-weighted era rates are
reported (a) from the cross-validated predictions of the text-only Stage 1
variant on the same 1,000 items and (b) from the gold labels of the items in
the six Tier 1+2 subreddits where relevance must be established from the text
(all but r/SelfDrivingCars and r/waymo), each decomposed by the method of
Deviation 8. The text-only variant was trained on labels formed under the
subreddit rule, so (a) shows how far those labels can be recovered from the
text and not what annotation from the text alone would give; (b) rests on
labels that were judged from the text. The text-only variant is not run over
the corpus. The lexical proxy is applied to the 1,000 tranche items and
compared item by item with the gold Stage 1 label, by subreddit, and is
recomputed over corpus v2.2 by subreddit and era for the bound it provides. Its
term list and matching rule are those in the repository when this deviation is
committed, unchanged, and the register names the file and the commit when the
sample-analysis script is committed. The composition check of Deviation 8 is
applied to the proxy's era rates before any statement about composition is made
for it. The relevance-rate trend is reported directionally and without a
mechanism (R5).

**RQ2 (Deviations 9 and 11).** π_s(t), C_s(t) and E_s are the measures
Deviation 9 defines. They are computed from the Tier 1+2 comments classified
relevant that the reweighting retains, with the weights of the primary series,
over 2016 Q1 to 2024 Q4; 2025 is shown descriptively. Deviation 9 leaves the
subsystem classifier's error uncorrected and is silent on the Stage 2
classifier's. In the evaluation of record about three in ten of the items
classified CONCERN are not CONCERN (85 of 298), and on the corpus that share
moves with the concern share, so a measure formed from classified comments
would partly repeat the trend of RQ1. The measures of record are therefore
corrected for Stage 2 error with the rates of record. With K_s and N_s the
weighted numbers of comments of primary subsystem s classified CONCERN and
classified relevant in a period, s running over the seven values and the
unclassified comments, A_s = (K_s − FPR × N_s) / (TPR − FPR). The A_s enter
every sum, ratio, trend statistic and resample as computed, negative values
included: π_s = A_s / Σ_s A_s, C_s = A_s / N_s, and E_s = C_s / C over
2016–2024, where C in this ratio is Deviation 9's concern share, Σ_s A_s / Σ_s
N_s on the same comments, and E_s has no value if C is not positive. For
display a value of π_s or C_s outside [0, 1] is clipped to [0, 1] and the raw
value is reported beside it. A period in which Σ_s A_s is not positive has no
value of π_s, a period with nothing in a measure's denominator has no value of
it, and a zero share is a zero. The correction assumes that the Stage 2 rates
are the same in every subsystem, and the measures formed from the Stage 2
labels as classified are reported beside the corrected ones. Each reported
value carries a 95% percentile interval from the bootstrap above. A material
temporal effect conditions the corrected subsystem measures in the same words
as the primary series.

The sparsity rule of Deviation 9 is applied to the unweighted counts of Tier
1+2 comments classified relevant, by primary subsystem, whether or not the
reweighting retains them; Deviation 9 says "corpus-wide counts", and the
subsystem classifier is run on Tiers 1 and 2 only. Family A is one two-sided
Mann–Kendall test with Sen's slope on π_s(t) for each of sensing, in-vehicle
networks, cybersecurity, privacy and data governance that meets the sparsity
rule, at the resolution the rule gives; the family is the tests so run, with
Holm–Bonferroni within it, a test being significant when its Holm-adjusted
p-value is below 0.05. A subsystem analysed on nine annual values takes the
exact test defined above. V2X is reported as a count and `none` descriptively
(R5, Deviation 9). The design-weighted subsystem shares of the D28 Rule 2
specification are reported on the pooled sample, as Deviation 11 fixes.

**Sensitivity analyses (Family C).** Three analyses are reported without
correction for multiple comparisons and labelled exploratory, as R5 states for
Family C. Each is run on the comments and predictions above and needs no
further model run. The registered rules R3 (the pooled series) and R4
(thread-size composition) are applied as set out above; they are not
exploratory and keep their own consequences, R4 as changed above.

1. *Seasonality.* As `docs/corpus_manifest.md` plans: for each complete year
   2016–2024, the corrected reweighted share in January–June and in
   July–December, and the mean over the nine years of the first minus the
   second, with its bootstrap interval. The two halves differ in their mix of
   subreddits and queries, because the supplementary sampling added
   January–June posts for saturated queries only (corpus manifest), so the
   difference describes the half-years as sampled; it is reported as
   description and decides nothing. The manifest records a drift in the
   within-year sampling position of about 0.10 of a year across the span, which
   can bias the annual series only if concern varies with the season. Its
   effect is measured directly, by the decomposition of R4 with the month of
   the year in place of the thread-size bucket, on every comment that the
   reweighting retains: the twelve month-of-year concern shares are held at
   their pooled 2016–2024 values, each year's composition by month is applied
   to them, and C_m is eight times Sen's slope of the resulting annual series,
   with T recomputed on the same comments. |C_m| is compared with 0.20 × |T|,
   R4's first cut-point, and this comparison decides the manifest's two
   outcomes: below the cut-point the drift is reported as not consequential,
   and otherwise as a material limitation with the trend also stated net of
   C_m. If the primary trend is not significant, the outcome is not applied
   and |C_m| / (TPR − FPR) is reported. The ratio that a straight-line trend
   common to every month would produce is reported beside C_m / T, as for the
   thread-size buckets. The drift moves comments between the months of a year,
   which can change an annual share and changes a quarterly share only through
   the mix of months within the quarter; the check therefore bears on the
   annual series, and so on T and R4, more than on the 36 quarterly values of
   the primary statistic.
2. *Word floor at 25 words.* The primary series recomputed on the comments of
   25 words or more, by the word count that `02_preprocess.py` applies for its
   20-word floor: the target shares stay those of the primary series, the
   retained subreddit-years and the year weights are recomputed on the subset,
   and the rates of record are unchanged. It is compared with the primary
   series by R3's two criteria.
3. *Tier strata.* The corrected quarterly series for Tier 1 and for Tier 2
   separately, each weighting its own comments equally, with the bootstrap
   intervals above and the Sen's slope, Gilbert interval and Mann–Kendall
   p-value of each, beside the primary series. A quarter with fewer than ten
   comments classified relevant in the tier has no value. No criterion is
   applied.

Three analyses planned in the project's design are not run. A floor at 15
words: the frozen corpus has no comment below 20 words, so it would need the
corpus rebuilt from the raw files and the added comments classified. Relevance
classification with the post title added: R2 keeps Stage 1 blind to the title
in every case, no title was shown to the annotators, and labels assigned with
the title in view do not exist, so its gain could not be measured. The
re-annotation held open as O17(c) in the governing document, which would show
how the subreddit rule of Deviation 1 bears on the relevance labels: its
question is answered only in part, by the era rates on the six subreddits and
the text-only variant described under RQ4. The subreddit-rule sensitivity
itself is reported under RQ4 above.

**Tier 3.** Tier 3 comments are classified at Stage 1 only. No Tier 3 comment
is in the draw frame or in either tranche (R5), so the classifier's accuracy on
Tier 3 is unmeasured, and it met neither Tier 3 subreddit in training; the Tier
3 figures are therefore descriptive. The share of all comments classified
relevant that Tier 3 supplies is reported, and the Tier 3 comments classified
relevant are read by the author for the qualitative account, any quotation
being kept to 15 words or fewer.

**Scripts of record.** The corpus runs, the sample analyses (the pooled
prevalence and class-share estimates, the RQ4 era comparison and its
composition check, the text-only sensitivity and the lexical-proxy comparison,
the subsystem α and the D28 outcomes on the pooled sample, the tranche 1 checks
of Deviations 3 and 4, the weighted three-class rates, the relevance-error
shares and the three-way comparison, and the block rates and block metrics of
the temporal calibration check) and the series analyses are each run by a
script committed before it is run on the data of record, and the figures of
record are the outputs of those scripts. The corpus description figures (year
totals, composition by year, thread counts, the preprocessing funnel, the
lexical proxy, the reweighting cell sizes and the within-year sampling
position) are regenerated from corpus v2.2 by a committed script, and
`commentsCount` is joined from the raw post records by the same script. Figures
recorded so far as previews are superseded by the outputs of the committed
scripts wherever the two differ, and any difference is recorded.

The scripts that make the corpus runs print progress, the number of comments
each run covers, counts of refusals and of unclassified comments, spend and
file hashes only. No output of a corpus run is tabulated or read against
period, era, subreddit, tier, subsystem or thread size before the
series-analysis script is committed, and no rate is computed by temporal block
before the sample-analysis script is committed; this is an undertaking by the
author and cannot be checked. A script found to be in error after it has run on
the data of record is corrected by a new commit, and the register records the
error, both outputs and which stands. Every figure that this deviation says is
reported, given, tabulated, counted, shown or stated appears whatever its
value: in the report, in its appendices, or in a results file committed to the
repository and cited in the report. Library versions are recorded with each
output: those of the project's pinned environment for the scripts run on the
author's PC, and for the Stage 1 retraining and corpus run, which need a GPU
session, the versions that the model scripts' commit fixes (transformers 5.19.0
and scikit-learn 1.9.0) with the others as the session provides them.

**What changes in R2, R3, R4, R5 and Deviations 9, 11 and 12, and in the corpus
manifest's plan.**

1. R2's statement that the models see what the annotators see is narrowed
   again, for the subsystem classifier, as Deviation 12 narrowed it at Stage 2.
   The annotators chose the subsystem with their own Stage 2 class in view,
   could see the subreddit, and had the seven rules of the instructions'
   section "How to choose"; the classifier receives the comment text and the
   seven definitions, with the first sentence of rule 7.
2. R3 is applied over its eight subreddits, with the readings and additions
   stated here. Readings: its "Holm-corrected level" is taken as 0.05, because
   R3 names no family and RQ1's test is a family of one; its tier-level check,
   which R3 justifies by "three strata", has two, because the series cover
   Tiers 1 and 2 only (R5); and a Sen's slope of exactly zero agrees in sign
   only with another of zero. Fixed here, where R3 is silent: the target
   composition; the rule for a subreddit with fewer than ten comments in a
   year, with the companion series on the subreddits retained in every year;
   the application of a year's weights to its half-years; the form of the
   tier-level reweighting, with no value in a quarter where either tier has
   fewer than ten comments classified relevant; the correction of the pooled
   and tier-level series as the primary series is corrected; the level (95%)
   and method of the interval of Sen's slope; and what is reported when a
   comparison by R3's criteria carries no stated consequence.
3. R4 is applied with three readings, three additions and one change. Readings:
   the "change across the study span" is eight times Sen's slope of the annual
   values 2016–2024, for C and for T, and not the last year minus the first;
   the buckets are those of the corpus manifest, with comments whose thread has
   no post record, no reported count or a reported count of zero left out; and
   R4's third outcome, in which "the size-stratified series is reported as
   primary", is read as reported first as the result for RQ1, with the
   quarterly reweighted series beside it, which keeps the name primary series
   in this deviation. Additions: the trend "stated net of" C and the
   "size-stratified series" are defined as above, and the ratio that a common
   straight-line trend would produce is reported beside C / T. Change: R4's
   outcomes are not applied when the primary series shows no significant trend.
4. R5's SLD expectation-maximisation check is replaced by the three-class
   adjusted classify-and-count. R5 lists the chronological two-block split as
   an evaluation structure beside the cross-validation, with macro-F1 and
   per-class F1 as the primary metrics; here the split decides the check
   through the weighted TPR and FPR of the deployed Stage 2 classifier in each
   block, the two F1 metrics are reported by block as description, and no model
   is trained on one block and tested on the other. A material temporal effect
   is defined by R3's criteria, with the qualification above. R5's clipping of
   out-of-range estimates is applied to the values displayed, and statistics
   use the values before clipping, on which R5 is silent; the two
   relevance-error series are the one exception. R5 computes concern shares
   over the Tier 1+2 analysis corpus of 12,212 comments; here they are computed
   among the comments of that corpus classified relevant, and the reweighted
   series and every analysis that uses its weights also leave out the comments
   of subreddit-years that are not retained, whose number is reported, while
   the pooled series keeps them.
5. Deviation 9's subsystem classifier is Claude Sonnet 4.6, zero-shot, as
   above, in place of the design document's keyword-then-BART-MNLI coding.
   Deviation 9's measures are computed on the comments that the reweighting
   retains, with the weights of the primary series, and are corrected for Stage
   2 error; Deviation 9 is silent on weighting and on Stage 2 error. Its
   sparsity rule is applied to counts over Tiers 1 and 2. The classifier
   assigns no secondary label, so Deviation 9's descriptive sensitivity on
   secondary labels rests on the annotators' labels alone. Family A's tests on
   nine annual values are exact.
6. Deviation 11's temporal check "on each tranche alone" and the definition
   that Deviation 12 leaves to "a further deviation" are specified here.
   Deviation 12's refusal, a second answer that names no class, is extended to
   a comment that the API rejects again when a run is resumed, as set out under
   Corpus runs. Deviation 12's success criteria are unchanged; the analyses
   fixed here are those by which criteria 3, 4 and 5 are judged, the subsystem
   measures of criterion 3 being Deviation 9's as amended in item 5.
7. The seasonality check that `docs/corpus_manifest.md` plans is carried out as
   sensitivity 1. Its outcome is decided by a direct measure of the drift's
   effect, judged against R4's first cut-point, and not by the size of the
   half-year difference, which the manifest names and does not define.

**Cost.** The robustness check on the correction no longer comes from a second
method: the three-class correction uses the same items and the same assumption
of stable rates as the binary one. No model is trained on one temporal block
and tested on the other, so RQ3 cannot say how the fine-tuned models hold
across the boundary, and the deployed Stage 1 model's behaviour over time is
described only from random folds. The temporal check has little power on 598
items: it can establish only a large difference in rates, and a smaller one
would bias the corrected trend unseen. The qualification of a material temporal
effect was added after the evaluation output had been read as pointing to a
higher false-positive rate in the latest era. A difference of that size, about
0.06, would if real raise the late quarters of the primary series against the
early ones by about five points at the sample's concern share, and is too small
for the check to establish reliably.

R3's "Holm-corrected level" is read as 0.05, the least strict reading. The
Mann–Kendall test of record treats the 36 quarterly values as independent,
although they share annual weights and one set of error rates and the manifest
holds that the sampling supports annual claims only; the Hamed–Rao figure is
reported beside it and does not replace it. R4's outcomes are not applied
without a significant trend, so a composition effect that hides a trend is
reported and not acted on. Some subreddit-years are left out of the reweighted
series. The subsystem classifier is chosen without a comparison on its own task
and is given less than the annotators had, the gold labels it is measured
against were assigned with two descriptions of the subsystems in view, and its
error is measured but not corrected. The correction of the subsystem measures
assumes Stage 2 error rates that are equal across subsystems, which is not
tested, and their intervals leave out the subsystem classifier's error. The
Stage 1 predictions of the 1,000 tranche items, about 8% of the Tier 1+2
corpus, are in-sample. The error rates of record are not re-estimated whatever
the agreement between the corpus run and the evaluation run. The 15-word floor
and title-augmented relevance are not examined, and the effect of the subreddit
rule on the gold relevance labels is examined only through a classifier trained
on those labels and through the era rates on the six subreddits.

**Mitigation.** Both versions of the corrected series, the block rates and the
interval of the difference in slope are reported whatever the temporal check
finds. The three-class correction is reported for every quarter in the place of
SLD expectation-maximisation. The subsystem classifier is validated against
every gold primary subsystem of both tranches, with and without the three
adjudicated items, and the subsystem measures are given as classified beside
the corrected ones. The companion series, the pooled series and the tier-level
series stand beside the primary series. Stage 1 error is shown by the two
relevance-error series and by the three-way comparison on the annotated sample.
The Stage 2 labels of the corpus run are compared with those of the evaluation
run on the tranche items. Every script is committed before it is run on the
data of record.

**Consequence.** The rules stated here were fixed before any output of the
deployed classifiers or of the subsystem classifier existed for a comment
outside the two tranches. What they leave to the scripts is fixed when the
scripts are committed. The temporal check decides, by a rule written before it
was run, how the corrected trend is qualified, and both versions of the series
are reported whatever it finds. The subsystem measures rest on a classifier
that is given less than the annotators had, whose agreement with the gold
labels is measured and whose error is not corrected.

### Deviation 14 — Matching rule of the lexical proxy; the reach of Deviation 2's raw-majority report

**Specified 13 October 2026, against commit 823270e. The commit date is in the
repository history.**

Deviation 13 applies the lexical proxy to the 1,000 tranche items, compares it
item by item with the gold Stage 1 label by subreddit, and recomputes it over
corpus v2.2 by subreddit and era. It takes the proxy's term list and matching
rule from the repository as they stood when it was committed, at `be001c7`. The
repository then held the term list, `CORE_TERMS` in `config.py`, but no
matching rule: no committed script applies the term list to the text of
comments. The proxy figures of the design document were computed outside the
repository, on corpus v1 with the project's term list and on corpus v2 with a
separately written term list that is not in the repository. Its rates by era,
among them 42.7% for 2022–2025, are of the second kind.

**Rule.** A comment carries a CAV term if its `clean_body` in corpus v2.2
contains one of the eight terms of `CORE_TERMS` as a whole word, in any letter
case. The words of a term may be joined by one hyphen (U+002D), one space
(U+0020) or nothing, and a final "s" is allowed. In Python 3.12, with
`re.IGNORECASE`, a comment carries a CAV term if `re.search` finds one of these
patterns in its `clean_body`:

```
\bself[- ]?drivings?\b
\bautonomous[- ]?vehicles?\b
\brobotaxis?\b
\bautopilots?\b
\bfsds?\b
\bwaymos?\b
\bv2xs?\b
\blidars?\b
```

"Whole word" and "letter case" mean what `\b` and `re.IGNORECASE` mean for text
patterns in Python: a word character is a letter or digit of any script, or an
underscore. The rule counts "self driving", "selfdriving", "Waymo's" and
"robotaxis". It does not count a term inside a longer word ("waymore",
"FSDv12"), beside a digit or an underscore ("waymo2", "_Waymo_"), or in another
spelling ("robo-taxi"). The five quoted Tier 3 search phrases in `config.py`
(`LEGACY_ISSUE_TERMS`) are not used. The term list is read from `config.py` as
committed at `be001c7`, unchanged. The rule applies wherever the proxy is
computed, on the tranche items and over corpus v2.2. Deviation 13's sentence
"Its term list and matching rule are those in the repository when this
deviation is committed, unchanged" stands for the term list; the matching rule
is the one above. When the sample-analysis script is committed, the register
names `config.py` and `be001c7` for the term list and this deviation for the
rule.

**Figures already seen.** When this rule was fixed, the author knew every proxy
figure of the design document (Revision 4), among them the rates by subreddit,
by reply depth, by era and by year, the thread-level and Tier 3 counts, and the
proxy set beside the tranche 1 relevance rate, overall and by subreddit. They
were computed with other term lists or on an earlier corpus, and they are
previews, not figures of record. The author states that no proxy figure for
any tranche item had been seen. Before the sample-analysis script is
committed, its preflight computes the proxy on the 1,000 items in a dry run and
discards it unseen. The design document's statement that a second, separately
written term list agrees with the project's list within one to five points is
not made, because that list is not in the repository.

**Deviation 2's raw-majority report.** Deviation 2 reports the raw-majority set
beside the adjudicated gold set, with every adjudicated item listed. The
raw-majority report covers the estimates of the sample-analysis script listed
in its rule 9: the class shares, the weighted CONCERN rates, the three-class
rates, the subsystem shares π_s and condition (ii) of D28 Rule 2. The model
comparison of the evaluation of record (11 October 2026) was reported on the
adjudicated gold set only and is not recomputed on the raw-majority set.

**Consequence.** The proxy figures of record are those that the committed
scripts compute under this rule. They are not the design document's, which
used other term lists or an earlier corpus, and they may differ from them. The
model comparison of record rests on the adjudicated gold set alone. Nothing
else in Deviations 2 and 13 changes.

### Deviation 15 — Exploratory runs of Claude Opus 5.5 and Claude Fable 5.1 at the supervisor's request

**Specified 20 October 2026, against commit 823270e. The commit date is in the
repository history.**

At the final supervision session on 20 October 2026, held after every result of
record had been presented, the supervisor asked for the comments to be
classified with Claude Opus 5.5 and Claude Fable 5.1, two models released after
the evaluation of record, to see what they give. Neither model is named in R1
to R5 or in Deviations 1 to 14. This deviation fixes how the two models are
run, what is computed from their outputs and how it is reported. It changes no
rule of record and no result of record.

**What had been seen.** Every result of record: the evaluation of record
(Deviation 12), the corpus runs and the series analyses (Deviation 13), the
sample analyses (Deviation 14), the corpus description, the report tables, and
the calibration and cost analysis, each in full. The analyses fixed here are
therefore exploratory, and none of them can confirm a result. The rules were
fixed before either model had been sent any prompt of this study through the
API and before any output of either existed for any comment; this statement is
the author's and cannot be checked from the files. The cost estimate used below
to choose the effort level was formed from the token counts of the corpus runs
of record and the published prices, not from any output of either model.

**What does not change.** The deployed classifiers (RoBERTa with the subreddit
and the comment at Stage 1; Claude Sonnet 4.6 with the domain-specific schema
at Stage 2; Claude Sonnet 4.6 for the subsystem), the comparison of record and
its Holm family (Family B), the error rates of record, the primary series, and
every series, test, family and success criterion of Deviations 12 to 14 stand
as they are. Whatever the two models give, neither replaces a deployed
classifier and no result of record is recomputed with them in its place. Their
results are reported beside the results of record, not instead of them.

**Models and prompts.** `claude-opus-5-5` and `claude-fable-5-1`, through the
Anthropic API with the client of record (`anthropic` 1.13.0). Each identifier
names one model version and carries no date. Every answer must be returned
under the identifier asked for, and every answer from one model by the same
model version, by the rule of `models_02_claude.py`; otherwise the run stops for
good and a further deviation decides what is done. The prompts are those of
record, unchanged: at Stage 2 the universal and the domain-specific prompt,
built by `models_02_claude.py` (`bb3fbfe`); for the subsystem the prompt of
Deviation 13, built by `models_06_deploy.py` (`b436b24`). There is no system
prompt. Before a run sends any comment, the SHA-256 of each prompt it will send
is compared with the `prompt_sha256` that the run of record logged for the same
comment and prompt (the evaluation runs at Stage 2, the corpus runs for the
corpus and the subsystem), and the run stops if any differs.

**Settings that cannot be those of record.** Both models reject a temperature
other than the default and cannot run without thinking, so the requests of
record (temperature 0, at most 50 output tokens, no thinking) cannot be sent to
them. Every request to either model sends the user message alone with
`max_tokens` 4,000, which covers thinking and answer together,
`output_config` `{"effort": "low"}`, and `inference_geo` `"global"`, the
default routing, set so that the list prices below hold whatever default the
account has (inference restricted to the United States costs 10% more). It
sends no temperature, top-p, top-k or thinking setting, so the models use
their default sampling and adaptive thinking. Effort `low` is fixed for both
models and every call: it is the cheapest of the five levels, the closest to
the runs of record without thinking, and the only level at which the author's
estimate fits the full order of runs below within the credit available. The
thinking is neither requested nor stored. The answer is the text of the
response's text blocks, as `models_02_claude.py` reads it, and it is read by
the rule of record: `parse_answer` of that file at Stage 2, and the rule of
Deviation 13 for the subsystem. An answer that names no class or label, an
empty answer included, is retried once with the same prompt (Deviation 12);
after a second such answer the comment is a refusal at Stage 2 and unclassified
in a subsystem run.

**Refusals.** A response whose stop reason is `refusal` is recorded as a
refusal at Stage 2, or as unclassified in a subsystem run, with the category the
API gives. It is not retried, because the request would not change. No fallback
to another model is requested, so every label comes from the model named.
Refusals are counted by model, run and category. In the corrections a refusal
counts as not CONCERN in the binary correction and as OTHER in the three-class
correction, as Deviation 13 fixes.

**Batches.** The evaluation and corpus runs are sent through the Message
Batches API, at its prices; the connection check and the pilot are sent as
single requests. A run is sent one batch at a time: at most 100 requests until
it has 50 answered calls, so that its own cost per call is measured before
larger batches go out, and at most 1,000 after that. A batch is created once,
without automatic retries; if its creation is not confirmed, the API's list of
batches is read before anything more is sent, so that no batch is created twice
or left unread. A request that expired or was cancelled, or that errored for a
reason that is not about the request (an API, overload, rate-limit or timeout
error), is sent again. A request that errored as invalid is sent again once; if
it errors again, the comment is a refusal (unclassified in a subsystem run) and
is listed. An authentication, permission, not-found or billing error, an error
of any other type, any error about a spending limit or a credit balance, or
errors on more than 5% of a batch's requests, stop the run without being counted
against any comment; the run resumes from its log. A comment with five sends
whose outcome was logged, and no result, stops the run for good, and a further
deviation decides. Every answered request is logged as in the runs of record
(identifier, stop reason, refusal category, tokens, thinking tokens, message
identifier and batch identifier), and the outputs of every run are hashed and
recorded in the register.

**Items and order of runs.** In this order, each step only when the one before
it is complete or was not made under the pilot gate:

1. *Connection check*: each model with each of the three prompts on the
   connection-check sentence of `models_02_claude.py`. No comment is sent.
2. *Pilot*: 30 comments drawn from the 6,503 Tier 1+2 comments classified
   relevant at Stage 1, the 1,000 tranche items left out, with
   `numpy.random.default_rng([24916660, 15]).choice(n, 30, replace=False)` over
   the n remaining comments sorted by id as strings in code-point order. Each is
   sent to each model with the three prompts (180 comment-prompts). The pilot
   measures tokens per call, refusals and answers that name no label, and
   nothing else: its answers are not tabulated, enter no figure and are not
   reused, and no prompt or setting is changed in the light of it. If more than
   10% of a model's 90 pilot answers are refusals, or more than 10% name no
   label after the retry, that model's later runs are not made and the other
   model's runs go on.
3. *Evaluation, Claude Opus 5.5*: the 598 tranche items with a gold Stage 2
   class, with each Stage 2 prompt and with the subsystem prompt. The evaluation
   runs of record sent all 1,000 items, but only these 598 enter the Stage 2
   metrics, and the subsystem classifier of record labelled the same 598, of
   which 596 have a gold primary subsystem.
4. *Evaluation, Claude Fable 5.1*: the same.
5. *Corpus, Claude Opus 5.5*: the Stage 2 run with the domain-specific schema
   over the 6,503 comments, then the subsystem run over the same comments.
6. *Corpus, Claude Fable 5.1*: the same two runs.

**Credit and the stopping rule.** No credit is added for these runs. The
credit available on 20 October 2026, read from the Claude Console before the
connection check, was US$107.73 (US$7.73 bought and US$100.00 promotional).
Spending is measured as in Deviation 13, over every logged call of this
deviation, at the list prices of 20 October 2026: US$4 and US$20 per million
input and output tokens for Claude Opus 5.5, and US$10 and US$50 for Claude
Fable 5.1, for single requests; half those prices through the Batches API;
thinking billed as output. The ceiling is US$104.73, the credit less US$3.00
held back. Before each run of steps 3 to 6, its cost is estimated from the
pilot: the run's number of comments times the pilot's calls per comment and
mean cost per call at batch prices for that model and prompt, plus 20%. A run
starts only if this estimate, added to the measured spend, is within the
ceiling. Before each later batch the rest of the run is estimated again, from
the run's own calls once it has 50 answered calls, plus 20%, and the run halts
if the estimate no longer fits. Every estimate is recorded with the batch it
preceded. A run that does not start for cost, or halts, ends this deviation's
runs: no later run is made. The rule looks at cost only, never at an output. A
run that halts is reported as incomplete with its counts, and its outputs enter
no figure.

**What is computed.** All of it is exploratory and is reported whatever the
values.

- From each evaluation run: on the 598 items, the Stage 2 metrics of the
  evaluation of record for each schema (macro-F1, per-class F1, the weighted and
  unweighted CONCERN true- and false-positive rates, and the three-class rates
  M_ij), computed by the functions of `models_05_evaluate.py`, and M_ij by those
  of `analysis_01_sample.py`; and, on the 596
  items with a gold primary subsystem, the subsystem classifier's agreement with
  the gold label, with the share of each gold value given that value and the
  share of each assigned value that is right, with Wilson 95% intervals, as
  Deviation 13 reports them for the classifier of record.
- Comparisons on macro-F1 by the item-level permutation test of the evaluation
  of record (`models_05_evaluate.py`, 10,000 permutations): under the universal
  schema, each new model against Claude Sonnet 4.6, each against RoBERTa, and
  the two new models against each other; under the domain-specific schema, each
  new model against Claude Sonnet 4.6 and the two against each other. These
  tests form one family of their own, outside every family of R5 and
  Deviation 12, with Holm's correction within it at 0.05. A test whose model was
  not run is dropped from the family.
- From each model whose two corpus runs are complete: the agreement between its
  corpus run and its evaluation run (domain-specific schema, and subsystem) on
  the tranche items that both cover, reported as for the classifier of record,
  a refusal being a fourth value; the primary series and each series of
  Deviation 13 that carries a Sen's slope and a Gilbert interval (the pooled
  series, the companion series, the tier-level series, the three-class
  correction, the block-specific series with that model's own block rates, the
  series with a 25-word floor, and the Tier 1 and Tier 2 series), each with its
  Sen's slope, Gilbert interval and Mann–Kendall p-value, computed as the series
  analyses of record compute them but with that model's labels and its own
  weighted rates from its evaluation run in place of the rates of record; and
  the RQ2 measures π_s, C_s and E_s for sensing and none, with the counts of the
  other five values; and, if the sparsity rule gives sensing a series, its test
  as Family A computes it, with no other value tested. Changepoints,
  decompositions, R4, and the seasonality and relevance-error analyses are not
  computed for these instruments.
- Cost per 1,000 comments, at batch and at standard list prices, from the logged
  tokens, with thinking tokens reported separately.

**Reporting.** Every figure listed above is reported beside the figure of
record it parallels, labelled exploratory, with the statement that these rules
were fixed after every result of record had been seen. A run that was not made,
or halted, is reported as such with the reason. The script that makes the runs,
and the script that computes the figures above, are each committed before they
are run on the data of record. The run script prints progress, counts of calls,
of refusals with their categories and of comments with no label, spend, and file
hashes only. No output of these runs is tabulated by class, period, era,
subreddit, tier, subsystem or thread size before the analysis script for them is
committed; this is an undertaking by the author and cannot be checked.

**What changes in R2, R5 and Deviations 12 and 13.** Nothing changes for the
instruments of record. For the two further models: the settings of record are
replaced as set out above, because the models do not accept them; the
evaluation runs cover the 598 gold-relevant items and not all 1,000; Deviation
13's rule for API errors is replaced by the batch rule above; and the
comparisons above form a family of their own.

**Cost.** The two models differ from the models of record in more than the
model: they think before answering, at a level the author set, and sample in a
way the author cannot fix, so their runs are less reproducible than the runs of
record. The agreement between the corpus and evaluation runs on the tranche
items measures this in part. Effort `low` is one of five levels and was chosen
for cost; other levels might give other results. The same 598 items supply each
new model's error rates and judge it, as for the models of record, so the rates
are somewhat optimistic. Every rule here was fixed after every result of record
had been seen, so the comparisons cannot be confirmatory. The credit may not
reach the last runs, and the order puts the Claude Fable 5.1 corpus runs last.

**Mitigation.** The rules are committed before any call. Every prompt is checked
against the prompt of record for the same comment. The order of runs and any
stop are decided by cost and by the pilot gate alone. Every figure listed is
reported whatever its value, beside the figure of record.

**Consequence.** The results of the two models show how far RQ3's comparison
and the answers to RQ1 and RQ2 depend on the classifier chosen. They are
exploratory and change no result of record.
