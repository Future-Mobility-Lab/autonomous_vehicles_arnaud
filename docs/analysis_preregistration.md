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
