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

