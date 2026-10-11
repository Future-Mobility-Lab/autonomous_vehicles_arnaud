# Decision register

Operational records for the analysis that are not deviations from the
pre-registration. Deviations are recorded in `docs/analysis_preregistration.md`.

## 26 September 2026 — Tranche 1 annotation data

### Inputs

    tranche1_annotator_A.xlsx  SHA-256 2fe9b29ff2fb3298c4581e2bb79de711b4713abc40cdd065f2070ca0be39e50e
    tranche1_annotator_B.xlsx  SHA-256 e80439ae671a21c69ffe5307cdebcf96b16bb33599015361304bff3dc71b4c04
    tranche1_annotator_C.xlsx  SHA-256 4ec6a12a215edb3c4a0c2ac86d92c7871de0fa88ea84fc50d25cdf2f239ba6f6
    tranche1_master_key.csv    SHA-256 ce50173525fd7ac74a3d720bf5f1a395b131066383f5c121002eb7dfc357755f

### Integrity checks

500 distinct items and 700 ratings. The 100 reliability items appear in all
three sheets and match `is_reliability` in the master key; the 400 singly-rated
items are disjoint and match `assigned_to`. No blank, malformed or
out-of-vocabulary label. None of the 500 items is a codebook worked example or
one of the eight duplicate-text rows dropped under R5, and every item's tier
matches R5.

### Incident: text encoding in annotator C's workbook

Every non-ASCII character in `tranche1_annotator_C.xlsx` is mis-decoded (UTF-8
read as Mac Roman): 56 rows, being 24 reliability items and 32 of C's own
items. Words are intact; apostrophes, quotes, dashes and guillemets appear as
symbol strings (e.g. ’ as ‚Äô). A's and B's workbooks are unaffected. Labels
are unaffected, being joined by id.

Comment text is taken from the frozen draw, never from annotator sheets. The
items are not re-annotated, because C has seen them and a second pass would not
be independent. The sensitivity check is in Deviation 4.

**Method note.** Annotator C's completed sheet contained non-ASCII encoding corruption on 56 of 232 comments; 54 carried the reversible mojibake patterns handled by the retrofit repair, including all 24 affected reliability items. After repair, those 24 reliability-item comments matched A and B character-for-character. On the affected reliability items C was the Stage 2 minority voice on 3/24 (12.5%), compared with 8/76 (10.5%) of unaffected reliability items, providing no material indication that the encoding defect changed judgement.

Reliability ids: ds21b4y dw7geu4 dwocqws fbz20u9 fgo2xaz fho1pgo fos7eho
fowxn1d ghmx30k gir0isd gqa1dm9 gqsqbb7 hwd5iin j0mfukj jnqo9ty kerb4rm
kyxo91r lq3tkav lym5o6h m39gk6k me7mbuk mhamb4s movxknc mp4k05p

C own ids: d1whe5t dq7qyow dw7r03x dwuux42 ecqiguo epicld9 fc0v2nq fokovyn
gdeykm2 gelox85 h0knknc h665qwv hb0gnxb hhqqf3l hj83jdw hqghrap i0td0oo
i97lyv7 ibmhf9g j19psxf je8svjj jtm4uwt kcrrxz7 l9l1aj9 ljhxa3h m0kk0zn
m9gg2os mibx38n mic7qxq moycqcm mp079cc mplybbt

### Username flag: gqsqbb7

Annotator A flagged "(DirtyTesla?)" as a possible unmasked username, as section
8 of the codebook asks. It appears to name a public YouTube channel rather than
a Reddit user. No unmasked usernames, raw URLs or email addresses appear in any
of the 500 tranche 1 texts. The data are unchanged; the name is masked in any
quotation.

### Skips and missing context

No annotator skipped any item. Eleven ratings on 8 items carry notes that
relevance could not be established without the thread; all are coded N, as the
codebook's quick-reference card directs.

### Pending

- Check the copy of the workbook distributed to C, to establish whether C
  annotated the garbled text.
- BART-MNLI scores for the 500 tranche 1 items (Deviation 5).
- Confirm that assignment to annotators was random within era (Deviation 4).

## 30 September 2026 — Subsystem retrofit returned; D28 applied

### Inputs

    tranche1_subsystem_A_filled.xlsx  SHA-256 bec8eec480569df8d957df2fb048fc887095a477a732fbf9f6c811d2699c6f6b
    tranche1_subsystem_B_filled.xlsx  SHA-256 b14d11bb09ae4a47af95d5c8513313c391324c9787af718a5a79a1667742ba8c
    tranche1_subsystem_C_filled.xlsx  SHA-256 f466866e741e605503b449a812768e049a753e95eaec9b9ac1609fd946bb19ff

Last saved (workbook metadata, AEST): A 27 September 2026 18:11; B 30 September
2026 19:28; C 30 September 2026 20:48. D28 was committed at [hash] on
[date and time].

### Integrity checks

Each sheet holds exactly its annotator's Stage 1 = Y items (137 / 137 / 140),
in original row order with original row numbers, and with Stage 2 classes
unchanged. Every primary label is one of the seven permitted values and none is
blank. Every secondary label is one of the six subsystems, never repeats the
primary and never accompanies `none`.

### D28 applied

Subsystem α (nominal, primary label, seven values): 0.868 on the 59 reliability
items with two or more labels (175 pairable values); 0.867 on the 57 items
labelled by all three annotators. Both reproduced exactly by the krippendorff
package (0.8.2). 53 of the 59 items are unanimous; the other six are two-to-one
splits, with no three-way splits or ties. Five of the seven categories occur in
the reliability items. Computed outside the repository as a preview; the figure
of record comes from the committed pipeline.

Rule 1 (α < 0.6) does not fire. Rule 2's α condition (α ≥ 0.7) is met. Its
interval condition has not been evaluated; the specification it needs is to be
committed before any subsystem share is computed.

### Update to the 26 September encoding incident

The retrofit sheet for annotator C repaired 54 of the 56 mis-decoded comments.
`l9l1aj9` and `fokovyn` were still mis-decoded, so C assigned their subsystem
labels from garbled text (one emoji and one apostrophe affected).

### Label counts displayed

Per-annotator subsystem label counts appeared in the analysis session's
validation output on 30 September 2026, between 22:00 and 22:10 AEST.

### Pending

- Commit the Rule 2 specification and the subsystem gold rule before any
  subsystem share is computed.
- Correct R4 §7.14 from 54 to 56 mis-decoded comments at Rev 5.

### Rules recorded before any subsystem share was computed

Deviation 7 extends the Deviation 2 gold rule to subsystem labels. D28 Rule 2 is
specified in R4 (D28, Rule 2 specification, 30 September 2026): design-weighted
π_s among CONCERN comments with the Deviation 3 interval, V2X and `none`
excluded, first place only. This resolves the first Pending item of this
section.

## 4 October 2026 — Records entered late, and corrections

Drafted on the date shown; the commit date is in the repository history.

### Implementation of the tranche 1 prevalence estimates (26 September 2026)

Implements Deviations 2 and 3; no new rule. Computed outside the repository as
a preview; the figures of record come from the committed pipeline.

- One label per item: the Deviation 2 gold label for the 100 reliability items,
  the single rating for the other 400.
- Design weights from the master key (sum 12,166). No item was skipped, so none
  is excluded and the weights need no adjustment.
- Standard errors: era-stratified, without-replacement variance with finite
  population correction; class shares among relevant items use the linearised
  ratio variance.
- 95% intervals: logit scale (delta-method standard error), with the t quantile
  on design degrees of freedom: 497 overall and for class shares, n_h − 1 within
  an era.
- All estimates, standard errors and intervals were reproduced exactly by
  samplics 0.6.1 (TaylorEstimator).

### Implementation of the tranche 1 RQ4 comparison (26 September 2026)

Implements Deviations 3 and 8; no new rule. Computed outside the repository as
a preview; the figures of record come from the committed pipeline.

- Difference interval: 2022–2025 minus 2016–2018, Wald interval using the two
  eras' design standard errors from the prevalence estimates (with finite
  population correction), t quantile on 331 degrees of freedom (167 + 166 − 2).
- Only the first-to-last difference is pre-specified. Other pairwise era
  differences are not used for the RQ4 claim.
- Composition check: subreddit mix within each era estimated from the sample
  (simple random sampling within era); pooled frame mix weighted by era frame
  size; seven groups as in Deviation 8, plus a two-group version
  (r/SelfDrivingCars and r/waymo against the other six) reported alongside.
  Descriptive; no intervals on the components.

### Pending items carried from 26 September 2026

- Decide whether to revise the OTHER rule (codebook Rule 8) before tranche 2 is
  drawn; the tranche 2 allocation input depends on it.
- Fix the Deviation 5 allocation objective (for example, maximise the smallest
  expected final class count) before the allocation is computed.
- Apply the same composition check to the full-corpus lexical proxy before the
  pre-committed composition statement is used for it.

### Correction to the D28 commit sentence in the 30 September section

D28 was written in the design document (Revision 4, 26 September 2026), which is
kept outside the repository, and had not been committed to the repository when

the retrofit sheets were returned. The sentence in the 30 September section that
refers to a D28 commit is superseded. The Rule 2 specification was first
committed, in summary, at 8ec6612.

### Subsystem rules recorded before any subsystem share was computed

Deviation 9 fixes the subsystem estimands, the treatment of subsystem-classifier
error, the sparsity rule and Family A. Deviation 8 records that the RQ4
composition statement is not made for tranche 1.

## 4 October 2026 — D28 Rule 2 applied

Applied as specified in R4 (D28, Rule 2 specification) and summarised in this
register at 8ec6612, after Deviation 9 was committed at 575b3af. Computed
outside the repository as a preview; the figures of record come from the
committed pipeline.

- Labels: one primary subsystem per item under Deviation 7. All 297 items that
  are relevant in the gold set take a label; none needed adjudication.
- π_s among the 120 CONCERN comments, design-weighted, with 95% intervals:
  sensing 27.8% (20.3–36.8%; 35 items); in-vehicle networks 3.7% (1.5–8.8%;
  5 items); privacy 0.7% (0.1–4.8%; 1 item); cybersecurity and data governance
  0 items. Not ranked: V2X 6 items; `none` 63.5% (54.2–71.8%; 73 items).
- Test: the two largest eligible shares are sensing and in-vehicle networks.
  Their intervals do not overlap (20.3% against 8.8%).
- Outcome: Rule 2 is met. The ranking claim is restored, limited to sensing
  having the largest share of expressed concern. No other ordering is claimed.
- The figures were reproduced exactly by samplics 0.6.1.

## 4 October 2026 — Tranche 2: decisions before the draw, and the draw

- The two tranche 2 items listed as pending on 4 October are closed by
  Deviation 10: the OTHER rule (codebook Rule 8) is not revised, and the
  Deviation 5 allocation objective is fixed.
- Decisions taken by the author on 4 October 2026, before the pre-filter was
  run, and recorded in Deviation 10: the codebook is not revised; the
  pre-filter wording (the design document gives none); the allocation rule; a
  minimum bar of 200 for going ahead; hit rates and allocation sealed until the
  sheets are returned or 11 October 2026; subsystem labels collected in the
  same workbook; no era stratification. B and C are asked to return their
  sheets by 7 October 2026.
- Order of work. The governing document places tranche 2 after tranche 1 is
  closed, and the tranche 1 results of record have not yet been produced by the
  committed pipeline. The draw does not wait for them. The allocation needs only
  the tranche 1 labels, which `tranche2_common.py` derives from the completed
  sheets and checks item by item against a recorded fingerprint (SHA-256
  `d6f4eeeaf756831c3ba2a3165a7a548505d75a315b4f06069b9cf8ce580cd8d7`: 203 not
  relevant, CONCERN 120, ENDORSEMENT 95, OTHER 82).
- Calibration items: 30 ids from `data/annotation/calibration_annotator_A.csv`, of which
  `30` are in the frame and are excluded from the draw.
- Data handling. `data/tranche2/` holds comment text, the pre-filter scores and
  the researcher-only key, and is not committed to the repository. The
  pre-filter input (ids and text of the 12,166 frame items) is uploaded to
  Google Colab for scoring and deleted from it afterwards.
- Deviation 10 and the six scripts are committed with this entry, before the
  pre-filter is run; the commit date is in the repository history. The gate
  simulation was run before the pre-filter and printed the table below. The
  blocks appended after it are printed by the scripts and carry hashes only.
  The measured figures are sealed under the Blinding clause of Deviation 10
  and are added when the files are unsealed.

random predicted labels                          mean  95th pct  share at or above the bar
40% predicted not relevant, classes equal       178.2     193.1                       1.8%
25% predicted not relevant, classes equal       177.6     190.2                       0.5%
30% predicted not relevant, OTHER rare          178.3     195.9                       3.0%
30% predicted not relevant, OTHER very rare     179.2     202.9                       5.2%

- Pre-filter run: `facebook/bart-large-mnli` at commit `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`; 12,166 frame items
  scored; `prefilter_scores.csv` SHA-256 `689752f57ad851e56152754092136209739018a618a4728b34d5d415d8a74b6b`.
- Allocation computed by `tranche2_03_allocate.py`; `tranche2_allocation.json` SHA-256
  `ce23e2290343cb87298ae1149a045728f9c54fa3bab446fc14dde8c067a5a560`.
- Gate (expected smallest final class count at least 200): FAIL. Nothing is drawn under Deviation 10.
- Hit rates and allocation sealed under the Blinding clause of Deviation 10.

## 4 October 2026 — Tranche 2 gate failed; replaced by a second natural tranche

Drafted on the date shown; the commit date is in the repository history.

- The gate of Deviation 10 failed (see the block above: pre-filter run,
  allocation hash, gate result). Nothing was drawn under Deviation 10 and
  `tranche2_04_draw.py` was not run.
- State of the files when the replacement was decided. The author had opened
  none of `prefilter_scores.csv`, `prefilter_scores_manifest.json`,
  `tranche2_allocation.json`, `tranche2_hit_rates.csv` or the sealed register
  text, and had seen no hit rate, allocation, expected count, count by
  predicted label or item-level prediction. He knew the gate result and the
  checks the scripts displayed.
- Decision taken by the author on 4 October 2026 and recorded in Deviation 11:
  tranche 2 is a second natural tranche, drawn like tranche 1 with no
  pre-filter. Lowering the bar and trying other pre-filters were rejected
  because each would decide after the result. Stopping at tranche 1 was
  rejected because R1 fixes 1,000 items and a 200-item reliability subset.
- Also recorded in Deviation 11: prevalence and the D28 Rule 2 shares are
  estimated on the two tranches pooled; the tranche 1 figures recorded so far
  are previews on half of that sample; the pre-filter outputs stay sealed on
  the terms of Deviation 10.
- Before this entry was committed, `tranche2_05_draw_natural.py --check` was
  run. It draws nothing. The block appended after this entry is printed by the
  draw and carries hashes only.

Lines printed by the `--check` run:

frame by era: 2,495 / 3,633 / 6,038 (matches R1)
tranche 1 by era: 167 / 167 / 166 (matches R1)
calibration items by era: 10 / 10 / 10 (30 in the frame, excluded)
eligible by era: 2,318 / 3,456 / 5,862 = 11,636
Deviation 10 gate, as recorded in tranche2_allocation.json: FAIL (file SHA-256 ce23e2290343cb87298ae1149a045728f9c54fa3bab446fc14dde8c067a5a560)
text: prefilter_input.csv matches step 1 and the corpus
tranche 2 allocation by era: 167 / 167 / 166 | pooled draw of both tranches: 334 / 334 / 332

- Tranche 2 (natural, Deviation 11) drawn 2026-10-05T06:58:26+11:00 by `tranche2_05_draw_natural.py`:
  500 items, 167 / 167 / 166 by era, membership SHA-256
  `3a1100cc537f4ec286563a28d8878e8e852cdf06583aa072f547d79331066b51`.
- Reliability subset: 100 items, 34 / 33 / 33 by era, SHA-256
  `1a63e4f3de0f8e2f68855003fccdf7710deee59982487f9d455864e51183e8a9`.
- Sheets, by membership SHA-256:
  A, 234 items, `d096ced89e52320dfd2d9eff345091bf71358aa878175ff5a1182caef8f06d9f`;
  B, 233 items, `d4e854fbb8a11ad30638d34a6d7e843d2d777457e715e754aab5f899513cb149`;s
  C, 233 items, `53f7c24712f6544eae0bf3586f7497f212841b4a1b1fe1e748a3fb432c6e3458`.
- `tranche2_master_key.csv` SHA-256 `ae116f8df5f33bfc9231b35519db7a992c6acd7ae5f5bb23bf50ef2524c22d5e`;
  `tranche2_manifest.json` SHA-256 `9aea7be28652220c8fbb75db9cba81e7c7507b8920826a0ac96389cc47dcea91`.
  Neither file is committed to the repository. Both show which items are reliability items and are
  not opened by the author until the three sheets are returned.
- No pre-filter output was used. The Deviation 10 gate result was read from `tranche2_allocation.json`
  (SHA-256 `ce23e2290343cb87298ae1149a045728f9c54fa3bab446fc14dde8c067a5a560`): FAIL.
- Seed 24916660, components 10 to 17; NumPy 2.5.1; pandas 3.0.3.


## 4 October 2026 — Model comparison rules recorded before any classifier's results were seen

Drafted on the date shown; the commit date is in the repository history.

### Rules fixed in Deviation 12

Deviation 12 fixes the Stage 2 configurations and their input, the fold
assignment across the two tranches, the item set for Family B and for the
prevalence correction, the deployment rules for both classifiers, the reporting
of agreement on the 200 reliability items, two predictions, the event markers
and the success criteria. Tranche 2 is the natural tranche of Deviation 11, so
the item set is the relevant items of both tranches. It also fixes that no
further model is run on any annotated item until the tranche 2 sheets are
returned.

### State of the work when Deviation 12 was committed

- No classifier output had been set against a label where the author could see
  it. The pre-filter scores, hit rates and allocation computed under Deviation
  10 were sealed; the author knew only that its gate had failed.
- B's and C's tranche 2 sheets had not been returned.
- The author had not started his own tranche 2 sheet.

### Pending

- Commit the universal schema, the Claude prompts, the checkpoints, the dated
  model identifiers and the fine-tuning settings with the model scripts, before
  the first comparison run and before the sealed files are opened.
- Commit the tranche 1 fold assignment before any model is run.
- Define a material temporal effect for R5's calibration check before the check
  is run.

  ## 10 October 2026 — Tranche 2 sheets returned: checks, handling and adjudication

Drafted on the date shown; the commit date is in the repository history.

### Files of record

- All three tranche 2 sheets had been returned by 10 October 2026 and were
  checked that day. The files of record are the copies kept in
  `data/tranche2/returned/` (not committed), last saved at 14:36–14:37 on
  10 October 2026 (Sydney time). SHA-256:
  - A `bbf4f4f62a72b58db73bb5239798a91e577dc0fce23b1ffc732171a1a0fa406d`
  - B `6dd5d25735b1214d74b28bbee6947f9e6778945950610b6c04675158a993b504`
  - C `ad73b59b1126f7813dfa295dfcca0a51d240359d7b8ee5c23b95efe0f9ecc33a`
- They are identical in every cell to the earliest copies seen, last saved at
  13:31 the same day and checked cell by cell, which are not kept in the
  repository. SHA-256:
  - A `b3f4ad01aa25deeaf3231460d621cc4cd65ae6dec9bd164b153250d161edf898`
  - B `25147296194b947cd71de0c5cec432d555890d6257bdeba17d87e4124b068e14`
  - C `4211590eb548006ac4fee1c063051824ea21e7243fa43de363a63d9d12f07b28`
- Other copies saved the same day are also identical in every cell.

### Handling (the author's statements; they cannot be checked from the files)

- B and C each completed their sheet alone, on the author's PC, unobserved by
  him.
- The author finished his own sheet before he first opened B's or C's.
- He reformatted the three files on receipt, and no rating changed. The files
  as B and C saved them could not be found. The 13:31 copies were saved on a
  family computer the author uses.

### Checks

- Membership: the SHA-256 of the 500 items, of the 100 reliability items and of
  each sheet (A 234, B 233, C 233) match the draw block committed at `c7edc7f`.
- 500 distinct items: 100 in all three sheets and 400 in one (A 134, B 133,
  C 133). No item is in two annotators' own sets, and none is from tranche 1.
- Rows are numbered in order, with no formulas and no skips. Every value comes
  from the allowed lists. Every row coded Y has a Stage 2 class and a primary
  subsystem, except four primary subsystems left blank by C; no row coded N has
  either. A secondary subsystem appears only beside a different primary one.
- The 100 shared comments have identical text and subreddit in all three
  sheets.

### Missing ratings (Deviation 11)

C left the primary subsystem blank on four items coded Y: `dogu859` and
`lsdjnzn` (C's own items) and `doh1fdn` and `dgw6fsc` (reliability items). They
are recorded as missing; no item is re-rated or replaced. `dogu859` and
`lsdjnzn` have no gold subsystem. `doh1fdn` takes `none`, the only primary
label given by an annotator who coded it relevant (A coded it N). `dgw6fsc`
takes `none` from A's and B's labels.

### Adjudication (Deviations 2 and 7)

Five reliability items had no majority. The author resolved each, with the
reason given, and each is flagged as adjudicated. Secondary labels take no gold
value.

1. `cz1vh4t`, Stage 2. A N, B OTHER, C ENDORSEMENT. Relevant by majority, so
   the choice was between OTHER and ENDORSEMENT. **ENDORSEMENT.** Rhetorical
   question defending camera-only sensing as enough without lidar; a defence
   of the technology is ENDORSEMENT (codebook §4.1, Rule 4).
2. `dvznfp7`, Stage 2. A ENDORSEMENT, B OTHER, C CONCERN. **ENDORSEMENT**, the
   author's own rating. Mixed comment (Rule 6): the closing edit gives the
   commenter's settled view that the benefits will be enormous and such
   accidents shouldn't be overblown; the worry about value decisions is a
   hypothetical the commenter sets aside, so endorsement dominates.
3. `epqj9r1`, primary subsystem. A sensing, B none, C in_vehicle_networks.
   **in_vehicle_networks.** Doubts the car's on-board decision-making for
   pothole avoidance, which is the driving system itself; what the car must
   sense is secondary.
4. `h4jy9ry`, primary subsystem. A none, B v2x, C in_vehicle_networks.
   **data_governance**, a label none of the three gave. About liability cover
   for accidents under Smart Summon; the codebook places liability under data
   governance.
5. `lifeax3`, primary subsystem. A privacy, B none, C data_governance.
   **data_governance.** About who controls and sees a teen's trip data
   (approvals, destinations, history), which is access to vehicle data;
   tracking by parents is secondary.

The subsystems of `cz1vh4t` (sensing) and `dvznfp7` (none) are settled by
majority. In all, two Stage 2 labels and three primary subsystems are
adjudicated; one decision takes the author's own rating and one takes a label
no annotator gave.

### What the author had seen

Before adjudicating, the author had seen preview agreement figures computed on
these sheets. They are not of record, and adjudication does not enter α. On
the 200 reliability items of both tranches: Stage 1 α 0.896, Stage 2 α 0.757,
primary-subsystem α 0.779 (items with two or more labels) and 0.769 (items
labelled by all three). On tranche 2 alone: Stage 1 0.832, Stage 2 0.774. The
figures of record come from the committed pipeline.

### Sealing

All three sheets are returned, their hashes are recorded here and the
adjudication is entered. Under Deviation 11 the tranche 2 master key and draw
manifest may now be opened. The pre-filter outputs of Deviation 10 stay sealed
until the zero-shot configurations are committed with the model scripts
(Deviations 10 and 12), whatever the date, and no model is run before that
commit.

## 10 October 2026 — Edited copies of the tranche 1 sheets found and set aside

Drafted on the date shown; the commit date is in the repository history.

- On 10 October 2026 the tranche 1 annotation sheets in `data/annotation/` were
  found to be copies that differ from the files recorded on 26 September 2026:
  compared cell by cell, labels differed on 22 items (27 labels across the
  three sheets), 7 of them reliability items, and notes had been rewritten on
  23 items. Their comment text showed signs of a round trip through CSV files.
  How they arose is not recorded.
- No analysis used them. Every tranche 1 figure so far was computed from the
  files recorded on 26 September, and the tranche 2 scripts checked the
  tranche 1 labels against those files on 4 October.
- They, re-saved copies of the three subsystem sheets (identical in every cell
  to the files recorded on 30 September) and three .csv copies of the tranche 1
  sheets were moved to `data/annotation/not_for_analysis/` and are not used.
  The recorded files were restored to `data/annotation/`, and all seven tranche
  1 files there match their recorded SHA-256. `models_01_prepare.py` checks
  them again each time it runs.

## 11 October 2026 — Model scripts, zero-shot configurations and fold files committed before any model run

Drafted on the date shown; the commit date is in the repository history.

### What this commit fixes

Deviation 12 left to the model scripts' commit the universal schema, the prompts
for the two Claude models, the checkpoints, the dated model identifiers, the
fine-tuning settings, the Stage 1 candidates and the text-only variant. They are
fixed word for word in `models_config.py`, committed here with the scripts that
use it:

- `models_01_prepare.py`: gold labels, fold files and model inputs (runs no model);
- `models_02_claude.py`: Claude Haiku 4.5 and Claude Sonnet 4.6, both schemas;
- `models_03_bart.py`: BART-MNLI, both schemas;
- `models_04_finetune_cv.py`: DistilBERT and RoBERTa, Stage 2 and Stage 1, five folds;
- `models_common.py`: shared helpers.

Nothing in `models_config.py` below its file-location block may change after
this commit without a recorded deviation.

**Label schemas.** The domain-specific schema is the three class phrases of
Deviation 10, unchanged. The universal schema is the same phrases with the
domain removed, so the two schemas differ in nothing else:

- CONCERN: "expresses worry, doubt or criticism"
- ENDORSEMENT: "expresses support, approval or optimism"
- OTHER: "is neutral or factual and takes no position"

The BART-MNLI hypothesis is "This comment " + phrase + ".". Under the
domain-specific schema these are the Deviation 10 class hypotheses word for word.

**Prompt for the Claude models.** One template for both models and both
schemas: the reference study's shared zero-shot template, word for word (Lee
et al. 2026, *Social Network Analysis and Mining*, doi:10.1007/s13278-026-01633-0,
Appendix F.1; Section 4.1 of the Research Square preprint). It is sent as a
single user message, with no system prompt. The reference describes the label
block as a bullet list without giving the bullet; here it is one line per label,
in the order CONCERN, ENDORSEMENT, OTHER, each starting "- ". The comment is
the comment text alone. Under the universal schema the prompt reads:

```
You are a careful annotator.
Choose exactly ONE label for the comment.

Candidate labels:
- expresses worry, doubt or criticism
- expresses support, approval or optimism
- is neutral or factual and takes no position

Comment:
{comment text}

Return ONLY the exact label text.
```

The reference is not consistent on one point: Section 4.1 of both versions says
the commercial models' prompt under topic-specific labels ended "Output ONLY the
exact label text.", while Appendix F.1 calls its template shared by all
generative models. The F.1 wording is used for both schemas, so that the two
schemas differ only in their label phrases.

**Claude models and calls.**

- Claude Haiku 4.5: `claude-haiku-4-5-20251001`, a dated snapshot.
- Claude Sonnet 4.6: `claude-sonnet-4-6`. From the 4.6 generation Anthropic
  issues no dated identifier; its documentation states that the dateless
  identifier is the canonical model ID and maps to a single, fixed snapshot.
- On 10 October 2026 both models were listed as active, with no deprecation
  notice. Claude Haiku 4.5's retirement is listed as not sooner than
  15 October 2026, and Anthropic gives at least 60 days' notice; the Claude
  runs are to be made soon after this commit.
- Each response must report the identifier requested, or that identifier
  followed by a date, and every call of a configuration must report the same
  one; otherwise the run stops. The identifier reported and the access window
  (first and last call) are recorded for each configuration.
- Every one of the 1,000 annotated items is sent once per configuration
  (Deviation 12), at temperature 0, with at most 50 output tokens and no system
  prompt, through the Anthropic Python SDK 1.13.0. That version no longer
  accepts temperature as a keyword, so it is sent in the request body. The main
  run refuses to start until a connection check (one call per model on a test
  sentence, no annotated item) has passed under these settings, so a refusal of
  temperature 0 would stop the work before any annotated item is sent.
- Five concurrent requests and a 60-second timeout per call, as in the
  reference study. Connection errors, rate limits and overload are retried by
  the client, up to eight times; these are not the retry of Deviation 12.
- Reading the answer: an exact match to one label phrase, ignoring case and any
  spaces, quotation marks, asterisks, underscores, backticks, full stops,
  colons, semicolons, exclamation marks, hyphens or bullets at either end;
  failing that, the class whose label phrase is the only one contained in the
  answer. An answer that names no class, or more than one, is retried once with
  the same prompt; a second such answer is recorded as a refusal and scored as
  an error (Deviation 12). Under the domain-specific schema an answer must
  contain the whole domain-specific phrase, so an answer that gives only the
  universal wording names no class there.
- Each answered call is logged before its retry is sent, so an item cut off
  part-way resumes from its recorded answers and no recorded item has more than
  the one retry. A call under way at a hard stop (a closed window, a power cut)
  is lost unanswered, as a connection error would be, and its tokens are not
  counted; at most five calls, one per concurrent request, can be lost at each
  hard stop.

**Cost.** The cost of a Claude configuration is the tokens of every recorded
call, including retries and calls on items cut off by an interruption, at Anthropic's
list prices on 10 October 2026: Claude Haiku 4.5 US$1 and US$5, Claude Sonnet
4.6 US$3 and US$15, per million input and output tokens. Cost per 1,000
comments is that cost divided by the 1,000 items, times 1,000. Models run on our
own hardware or on Colab carry no API charge, so their cost is zero; where two
of them must be separated on cost (an exact tie at Stage 1), the one with fewer
parameters costs less.

**Spending ceiling (governing document, O26).** US$25 for the evaluation runs,
the paid-evaluation budget, measured as above over all four Claude
configurations and the connection checks. At the ceiling the run stops for
review.

**BART-MNLI.** `facebook/bart-large-mnli` at commit
`d7645e127eaf1aefc7862fd59a17a5aa8558b8ce`, the commit recorded for the
pre-filter run at `01f3d8a`, so both schemas use one model version. The
universal schema is a new run by the pre-filter's method
(`tranche2_02_score_prefilter.py` at `64a64a8`): the comment as premise,
truncated to the model's maximum length, with any special-token string spaced
out; predicted class the hypothesis with the highest entailment logit, a tie
going to CONCERN, ENDORSEMENT, OTHER in that order; fp32. The domain-specific
predictions are taken from the frozen pre-filter scores and not re-run
(Deviation 12).

**Fine-tuned models.** `distilbert/distilbert-base-uncased` at commit
`12040accade4e8a0f71eabdb258fecc2e7e948be` and `FacebookAI/roberta-base` at
commit `e2da8e2f811d1448a5b465c236feacd80ffbac7b`, with the reference study's
settings (`run_finetune_cv_all.py`): AdamW (the PyTorch implementation),
learning rate 2e-5, weight decay 0.01, batch size 8, at most 10 epochs with
evaluation after each, early stopping after 2 epochs without a higher
validation macro-F1 and the best checkpoint restored, linear learning-rate
decay without warm-up, 256 sub-word tokens, no class weights, fp32. The
validation split for early stopping is a stratified 15% of the training folds
(random_state 24916660); the seed is 24916660 plus the fold number. Nothing is
tuned on an evaluation fold, and the held-out fold is predicted without its
labels, so no score is computed on it. A special-token string of the tokenizer
inside a comment (such as "</s>") is spaced out and its id logged, as
Deviation 10 does. The runs use transformers 5.19.0 and scikit-learn 1.9.0,
which the scripts check.

**Stage 1.** The candidates are DistilBERT and RoBERTa, fine-tuned as above on
the gold items of both tranches, on the same folds, with the labels N and Y.
Their input is the sentence pair ("r/" + subreddit, comment), with only the
comment truncated (Deviation 1). The text-only variant for the subreddit-rule
sensitivity is the deployed Stage 1 model type, with the same settings and
folds, reading the comment alone.

**Final retraining.** A deployed fine-tuned model is retrained on every eligible
gold item of both tranches (Stage 2: every item with a gold Stage 2 class;
Stage 1: every item with a gold Stage 1 label), with the settings above and no
held-out split, for a fixed number of epochs: the median of the best epochs of
its five cross-validation folds, with the learning-rate schedule of those runs
(linear decay over 10 epochs) stopped after that epoch. The seed is 24916660.

### Gold labels and folds

- `models_01_prepare.py` read the ten files of record, each checked against its
  recorded SHA-256, and formed the gold labels of both tranches by Deviations 2,
  7 and 11 with the five adjudications recorded at `dbd8a69`. The tranche 1
  labels match the fingerprint recorded at `64a64a8`. Tranche 2 four-way label
  fingerprint: `d934aadf914d677085d1d75c0d9a284aabe6871e1da72dad9a793f1d4727e89b`.
- Every item with a gold Stage 1 label also has a gold Stage 2 label or is not
  relevant, so the four labels of Deviation 12 cover every item; the script
  stops if one does not.
- Fold files, committed here (StratifiedKFold, five folds, shuffle, seed
  24916660, scikit-learn 1.9.0, NumPy 2.5.1, on the four-way gold label within
  each tranche, items sorted by id):
  - `splits/tranche1_folds.csv`, 500 items, SHA-256 `a3a7a23acdd98a7fcb7be639f49cd614c8ca27ffeefe783898f1a7cd11a627c3`
  - `splits/tranche2_folds.csv`, 500 items, SHA-256 `1026d74f8566bd08576adb220cb57a335ab8c333702eafc544cac8a8d953d324`
- The tranche 2 assignment is committed now because its gold labels are formed
  now (Deviation 12). `.gitattributes` switches off line-ending conversion for
  the fold files, so their bytes, and their SHA-256, do not change on checkout.
- The comment text of every model input comes from
  `data/tranche2/prefilter_input.csv`: the `clean_body` text of corpus v2.2 as
  Deviation 10 prepared it for the pre-filter. `models_01_prepare.py` checks it
  against the SHA-256 printed when it was exported on 4 October 2026
  (`d1ae1fbe68f3f805eac720ab5bdbd7e8132333e3c1ae9ed8cfefa9106b3bcb1c`).
- Model inputs, not committed: `data/models/zero_shot_input.csv`, 1,000 items,
  SHA-256 `2f8d48c3c66ac608d557cc03eb5c2070b357e8f0bd8fdd01b43bce380a7a181f`;
  `data/models/finetune_input.csv`, 1,000 items with a gold Stage 1 label, 598
  with a gold Stage 2 class, SHA-256
  `bcae83e718ebfa16b2f66b640f23acb5e091d775c2d53e549fa15a424e25d702`.

### State of the work at this commit

- `models_02_claude.py`, `models_03_bart.py` and `models_04_finetune_cv.py`
  were tested on synthetic comments and tiny, randomly initialised models only,
  the Claude script against a simulated API. `models_01_prepare.py`, which runs
  no model, was run on the files of record.
- No model has been run on any annotated item, and no classifier output has
  been set against a label.
- The Deviation 10 files (`prefilter_scores.csv`, `prefilter_scores.smoke.csv`,
  `prefilter_scores_manifest.json`, `tranche2_allocation.json`,
  `tranche2_hit_rates.csv` and the `SEALED_*.txt` files) are unopened. With this
  commit their seal lifts (Deviations 10 and 12). The two whose SHA-256 was
  recorded at `01f3d8a` are checked against it before they are opened:
  `prefilter_scores.csv`
  (`689752f57ad851e56152754092136209739018a618a4728b34d5d415d8a74b6b`), which
  `models_03_bart.py` also checks before reading it, and
  `tranche2_allocation.json`
  (`ce23e2290343cb87298ae1149a045728f9c54fa3bab446fc14dde8c067a5a560`).
- The script that scores the predictions (Family B, the deployment rules and
  the two predictions of Deviation 12) will be committed before any prediction
  is scored.

  ## 11 October 2026 — Claude runs: Claude Haiku 4.5 and Claude Sonnet 4.6, both schemas

Drafted on the date shown; the commit date is in the repository history.

- Run on 11 October 2026 by `models_02_claude.py` at `bb3fbfe`, on the
  author's PC (Python 3.12.10, anthropic 1.13.0), with
  `data/models/zero_shot_input.csv` (SHA-256
  `2f8d48c3c66ac608d557cc03eb5c2070b357e8f0bd8fdd01b43bce380a7a181f`): every
  one of the 1,000 annotated items once per configuration, in the order
  haiku-universal, haiku-domain, sonnet-universal, sonnet-domain. No restart
  was needed and no item was cut off.
- A connection check at 09:47 (Sydney time) sent one test sentence to each
  model and no annotated item. Both models answered under the identifiers asked
  for, `claude-haiku-4-5-20251001` and `claude-sonnet-4-6`, and every call of
  each configuration was answered under the same identifier.
- Spend guards: the script's US$25 ceiling, and a US$25 monthly spend limit set
  in the Claude Console, with automatic top-up off.

| Configuration | Access window (Sydney time) | Calls | Refusals | Input / output tokens | Cost (US$) |
|---|---|---|---|---|---|
| haiku-universal | 09:48:20–09:50:39 | 1,003 | 3 | 148,189 / 10,579 | 0.201084 |
| haiku-domain | 09:50:40–09:53:10 | 1,008 | 8 | 172,617 / 19,071 | 0.267972 |
| sonnet-universal | 09:53:11–09:56:30 | 1,000 | 0 | 147,507 / 10,809 | 0.604656 |
| sonnet-domain | 09:56:31–10:00:10 | 1,000 | 0 | 171,507 / 18,996 | 0.799461 |

- Each configuration has 1,000 items, so its cost per 1,000 comments equals the
  cost shown. Total measured spend US$1.8737, including the two
  connection-check calls (US$0.000572).
- Every retried item ended as a refusal: Claude Haiku 4.5 had 3 under the
  universal schema and 8 under the domain-specific schema; Claude Sonnet 4.6
  retried none. Refusals are scored as errors (Deviation 12). Every call ended
  with stop reason `end_turn`.
- Files, kept in `data/models/claude/` and not committed, SHA-256:
  - `haiku-universal_predictions.csv` `56d4dac6e9fdef0755df5a57e6595bfa3ea01aa529e9be43da7a71cd8d7d51fd`
  - `haiku-universal_log.jsonl` `25ac03f499e4c859466e3b8c9bdea5829bd938d309a9724ed6d5cfd426c0858f`
  - `haiku-domain_predictions.csv` `1381ea3de49f61c5ff2beadd04469766715b177bfdf168ab1cc8a6f1b7906cd2`
  - `haiku-domain_log.jsonl` `b61432e10c2829792397c1bf1ace11da28f3f469221ae15055ccaab7f3ffe712`
  - `sonnet-universal_predictions.csv` `d421907b0a87800834b6379b667c88fca945c1cd6ad937ccfe3fbd67ad3afbf3`
  - `sonnet-universal_log.jsonl` `a35898b422af3ad40b76d9b394d556f944e2cd3169fa59b152f6719b6bbc5a98`
  - `sonnet-domain_predictions.csv` `71b56f7270545d131a6cfe5649a1162a1b244b5f91298ff770e1ac80a4abbbaa`
  - `sonnet-domain_log.jsonl` `50dbfacad8fd9f0d2129f5ac9ee74a9d184ac32059e0e1fde9b5dcb01ac72baa`
- No prediction has been set against a label. The prediction and log files
  were sent to Claude with the manifests on 11 October; Claude checked their
  SHA-256 against the manifests and did not open them.

  ## 11 October 2026 — Colab runs, BART-MNLI domain-specific predictions, and the evaluation script committed before any prediction is scored

Drafted on the date shown; the commit date is in the repository history.

### Colab runs: BART-MNLI (universal schema), DistilBERT and RoBERTa

- Run on 11 October 2026 on Google Colab (NVIDIA A100-SXM4-40GB) by
  `models_03_bart.py` and `models_04_finetune_cv.py` at `bb3fbfe`. The four
  scripts uploaded (`models_config.py`, `models_common.py` and the two run
  scripts) and the two inputs, `data/models/zero_shot_input.csv` (`2f8d48c3…`)
  and `data/models/finetune_input.csv` (`bcae83e7…`), were checked against
  their SHA-256 before any run. Python 3.13.15, torch 2.11.0+cu130,
  transformers 5.19.0, scikit-learn 1.9.0, accelerate 1.15.0, NumPy 2.1.3;
  fp32. The manifests were written between 10:41 and 11:07 (Sydney time).
- No restart, disconnection or stop. No held-out fold was scored and no
  prediction was set against a label. Both Stage 1 text-only variants were
  run, to save a second session; only the deployed Stage 1 type's variant is
  scored (Deviation 12, `models_config.py`).
- BART-MNLI, universal schema: `facebook/bart-large-mnli` at the pinned commit
  `d7645e127eaf1aefc7862fd59a17a5aa8558b8ce` (the library reported no loaded
  commit); 1,000 items; none truncated at the 1,024-token limit; no
  special-token string had to be spaced out.
- Fine-tuning, five folds each. The best epoch is the epoch of the checkpoint
  restored by early stopping; a deployed model's final retraining uses the
  median of its five.

| Run | Items | Train / early stopping / held out, per fold | Best epochs, folds 1–5 | Minutes |
|---|---|---|---|---|
| stage2_distilbert | 598 | 405–407 / 72 / 119–121 | 4, 3, 4, 4, 4 | 1.51 |
| stage2_roberta | 598 | 405–407 / 72 / 119–121 | 5, 2, 9, 4, 7 | 3.41 |
| stage1_distilbert | 1,000 | 680 / 120 / 200 | 5, 3, 2, 6, 3 | 2.38 |
| stage1_roberta | 1,000 | 680 / 120 / 200 | 5, 5, 5, 2, 2 | 4.40 |
| stage1_distilbert_textonly | 1,000 | 680 / 120 / 200 | 3, 4, 4, 3, 1 | 2.06 |
| stage1_roberta_textonly | 1,000 | 680 / 120 / 200 | 9, 3, 3, 2, 3 | 4.40 |

- No special-token string had to be spaced out in any fine-tuning run.

### BART-MNLI, domain-specific schema

- `models_03_bart.py --schema domain --confirm-unsealed` at `bb3fbfe`, on the
  author's PC, 11 October 2026 at 11:57 (Sydney time). The predictions are the
  predicted classes held in the frozen pre-filter scores (`prefilter_scores.csv`,
  checked against `689752f5…` recorded at `01f3d8a`; model commit
  `d7645e12…`), not re-run (Deviation 12). The script displayed no prediction.

### Prediction files (in `data/models/`, not committed), SHA-256

- `bart/bart_universal_predictions.csv` `c7f6b1eccc433cd805b96a322ea3c82d086d016b2b8440feb6bb7b90e88be5e5`
- `bart/bart_domain_predictions.csv` `9e9280679dc6696332c896f763b33bd64fabc3eabe82a35aa5806e2accbe5e10`
- `finetune/stage2_distilbert_predictions.csv` `985b45605edf54fa9e95d311a3a9f86eea11e599eb49e8c350b0778feb93a6db`
- `finetune/stage2_roberta_predictions.csv` `b17357f25060ed91ad2d9a9a51ea093b85afc9a2210db491c2e107811cac1597`
- `finetune/stage1_distilbert_predictions.csv` `ae59ab2d9b29f539744056da9fbd4dec3826beefa07d1d50b9ed9d4b046e6cfd`
- `finetune/stage1_roberta_predictions.csv` `7258458df43c047ff8b8088fa8a855468acd1e6b8835dddcd42e85c3d8502b57`
- `finetune/stage1_distilbert_textonly_predictions.csv` `2c3bb9ed8dcd7e71617df2c31f85ca8544cbc7db6898d9e50d6212d6f7dd400b`
- `finetune/stage1_roberta_textonly_predictions.csv` `24d8e3a0de3e8d03d1c6be09fc162b74ff3a51265859bd7248580d0a8c40d94e`
- The four Claude prediction files are recorded at `a7ad389`.
- The manifests and these eight files were sent to Claude on 11 October. Claude
  checked each file's SHA-256 against its manifest and each manifest against
  the committed settings, by script, reading selected fields only (hashes,
  epochs, minutes, versions). No prediction file and no validation score was
  opened.

### Evaluation script, committed before any prediction is scored

- `models_05_evaluate.py`, SHA-256
  `98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734`. It is the
  first and only step that sets predictions against the gold labels. It
  implements R5 and Deviation 12: macro-F1 and per-class F1 of the eight Stage 2
  configurations; Family B (ten comparisons, Holm–Bonferroni at 0.05); Family C;
  the Stage 2 and Stage 1 deployment rules; the weighted error rates for
  adjusted classify-and-count; the two predictions; α for the 200 reliability
  items and for each tranche's 100; success criteria 1, 2 and 6.
- Before it scores anything it checks every input against the record and stops
  at the first difference: the scripts committed at `bb3fbfe`, the fold files,
  the gold-label fingerprints, the two inputs, the twelve prediction files
  (SHA-256 above and at `a7ad389`) and their manifests, the files of record,
  and `tranche2_master_key.csv` against the SHA-256 recorded with the draw at
  `c7edc7f` (its era column sets every design weight). It also checks that its
  α code reproduces the tranche 1 figures recorded under Deviation 4 (0.959,
  0.739, 0.836, 0.797 and 0.547, to three decimals). Run with `--preflight`, it
  makes all of these checks and scores nothing; it was run that way on the
  author's PC before this commit and passed.
- Permutation tests (R5, Deviation 12): two-sided, 10,000 permutations, gold
  labels never permuted, every test seeded with 24916660. As in the reference
  study (Lee et al. 2026, Appendix E.1), each permutation swaps the two
  configurations' predictions of each item with probability one half, and p is
  the share of permutations whose absolute difference is at least the observed
  one, floored at 1/10,000.
- α intervals (Deviation 12, by the method of Deviation 4): for each set of
  reliability items (the 200 in one matrix, and each tranche's 100), 10,000
  item-level bootstrap resamples of the set's items with seed 24916660, all
  five α computed on the same resamples; the 95% percentile interval and the
  share of resamples below 0.7. For the 200, items are resampled from both
  tranches together.

### Rules fixed in this commit where the committed text is silent

Decided by the author on 11 October 2026, before any prediction was scored:

1. The p-value is computed as the reference study computes it (above). A
   comparison is significant when its Holm-adjusted p is below 0.05, and
   otherwise "not demonstrably significant"; a configuration is tied when its
   unadjusted p is 0.05 or more (Deviation 12).
2. Family C (exploratory, uncorrected): the nine Family B comparisons that
   involve a zero-shot model, repeated with the zero-shot models under the
   domain-specific schema; the ten Family B comparisons within each tranche;
   and universal against domain-specific for each zero-shot model: 32 tests.
3. In the CONCERN rates (the deployment tie-break and the prevalence
   correction) a refusal counts as "not CONCERN": a miss on a CONCERN item and
   never a false positive, as a deployed configuration's refusals would be
   counted on the corpus. In F1 a refusal is scored as an error (Deviation 12).
4. Success criterion 6 is judged on the weighted TPR − FPR, the rates the
   correction uses; the unweighted figure is reported beside it.
5. Prediction 1: the gap is the fine-tuned minus the zero-shot model's
   per-class F1, signed, as written; "largest for CONCERN" means strictly
   larger than both other gaps. The report states any class on which the
   zero-shot model is better.
6. Exact ties: if two configurations share the highest CONCERN-class F1, the
   first in the committed order is the reference for the tie test; in
   prediction 1, "chosen by macro-F1" takes the first in the committed order;
   in prediction 2, "lowest" means strictly lowest.
7. Descriptive and untested: the mean and standard deviation (n − 1) over the
   five folds of macro-F1 and per-class F1, and Wilson 95% intervals for the
   Stage 1 accuracies by class and by subreddit.

### State of the work at this commit

- The script was tested on synthetic data only: six scenarios covering every
  path of both deployment rules, each recomputed independently (scikit-learn,
  statsmodels, the krippendorff package, and a separate permutation and
  bootstrap loop), and more than twenty cases in which an input was altered,
  each of which stops it. It was reviewed independently twice, and every
  finding was fixed.
- No prediction has been set against a label. `tranche2_hit_rates.csv`,
  `tranche2_allocation.json` and the `SEALED_*.txt` files are unopened; they
  are opened after this commit, `tranche2_allocation.json` after its SHA-256 is
  checked against `ce23e229…`.
- The Google Drive folder used for the Colab runs (`capstone_models_2026`,
  holding the scripts, the two inputs and the outputs) is deleted after this
  commit; the outputs are kept in `data/models/`.

## 11 October 2026 — Evaluation of record; the Deviation 10 files unsealed

Drafted on the date shown; the commit date is in the repository history.

### Evaluation of record

- `models_05_evaluate.py` at `34403e6` (SHA-256
  `98ac1d519414206d86153dcecd44e505629533a5a92395c60a944b6bfb88c734`) was run
  once on the author's PC on 11 October 2026 at 13:08 (Sydney time), with
  `--confirm-committed`, after its preflight had passed. Every input matched its
  recorded SHA-256. Python 3.12.10, NumPy 2.5.1, pandas 3.0.3, scikit-learn 1.9.0.
- Outputs, in `data/models/evaluation/` (not committed), SHA-256:
  - `evaluation_results.json` `411f6c23ef6525b077c74fec15b8e5a06c59c550a8f3f2d15e99eb7d354d32e4`
  - `evaluation_report.md` `5bad3bf0a7b176496138d3df307e23555a1b1e3cd233e2b1c7c9d6cc462ff09a`
  - `stage2_metrics.csv` `053a6d1582e7125366124a7dec2ec779f95926dc0bc710a82959d0da91c3a563`
  - `pairwise_tests.csv` `0f56926e99437e62a19af99edb473e0d0b788aef470f90fd9aa3143872e7ca87`
  - `stage1_metrics.csv` `2d8682a5cfa1e98703dd44558c60df1484c2b4048cc7fc654ac4d79953260418`
  - `reliability_alpha.csv` `18619e8544b7cdfe4377b8c06d51f27132a9c78fd4aee803370d301ded17d8e1`
- Item sets: 598 items relevant in the gold set with a Stage 2 class (tranche 1
  297, tranche 2 301; CONCERN 225, ENDORSEMENT 189, OTHER 184); 1,000 items with
  a Stage 1 label (598 relevant, 402 not relevant).

| Configuration | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | Weighted TPR − FPR | Cost per 1,000 (US$) |
|---|---|---|---|---|---|---|
| DistilBERT | 0.456 | 0.513 | 0.405 | 0.450 | 0.166 | 0 |
| RoBERTa | 0.523 | 0.580 | 0.493 | 0.495 | 0.329 | 0 |
| BART-MNLI, universal | 0.328 | 0.586 | 0.399 | 0.000 | 0.192 | 0 |
| BART-MNLI, domain-specific | 0.356 | 0.602 | 0.454 | 0.011 | 0.233 | 0 |
| Claude Haiku 4.5, universal | 0.618 | 0.715 | 0.628 | 0.510 | 0.512 | 0.2011 |
| Claude Haiku 4.5, domain-specific | 0.725 | 0.809 | 0.695 | 0.670 | 0.700 | 0.2680 |
| Claude Sonnet 4.6, universal | 0.656 | 0.742 | 0.693 | 0.532 | 0.557 | 0.6047 |
| Claude Sonnet 4.6, domain-specific | 0.750 | 0.815 | 0.763 | 0.673 | 0.709 | 0.7995 |

- Family B (Holm–Bonferroni across ten): all ten differences in macro-F1 are
  significant (Holm-adjusted p from 0.0010 to 0.0363). The narrowest is Claude
  Haiku 4.5 against Claude Sonnet 4.6 under the universal schema (difference
  −0.038, adjusted p 0.0363).
- Family C (exploratory, uncorrected): the domain-specific schema raised
  macro-F1 for every zero-shot model (BART-MNLI +0.027, p 0.0034; Claude Haiku
  4.5 +0.107 and Claude Sonnet 4.6 +0.094, both p 0.0001, the floor).
- Stage 2 deployment: Claude Sonnet 4.6 under the domain-specific schema had
  the highest CONCERN-class F1 (0.815). Claude Haiku 4.5 under the
  domain-specific schema was tied with it (difference 0.006, p 0.727); no other
  configuration was (p 0.0001 each). Between the two, the larger weighted
  TPR − FPR decided, 0.709 against 0.700. **Deployed: Claude Sonnet 4.6,
  domain-specific schema.** It is zero-shot, so no retraining applies.
- Error rates for adjusted classify-and-count, weighted by the pooled design
  weights: TPR 0.9469, FPR 0.2376, TPR − FPR 0.7093 (unweighted 0.9467, 0.2279,
  0.7188). The same items chose the classifier, so the rates are somewhat
  optimistic.
- Prediction 1: **not confirmed.** RoBERTa, the better fine-tuned model, against
  Claude Sonnet 4.6, the best zero-shot model under the universal schema: gaps
  in per-class F1 of −0.161 (CONCERN), −0.200 (ENDORSEMENT) and −0.038 (OTHER).
  The zero-shot model is better on every class.
- Prediction 2: **confirmed.** OTHER has the lowest per-class F1 for three of the
  five models, the three zero-shot models. For DistilBERT and RoBERTa the
  lowest is ENDORSEMENT (RoBERTa 0.493, against 0.495 for OTHER).
- Stage 1 deployment: RoBERTa with subreddit and comment, balanced accuracy
  0.871 (DistilBERT 0.847). **Deployed: RoBERTa.** Accuracy 0.928 on relevant
  and 0.813 on not-relevant items. Its text-only variant: balanced accuracy
  0.801. Final retraining: 5 epochs, the median of its best epochs 5, 5, 5, 2, 2.
- Reliability (nominal α; 95% bootstrap interval and share of resamples below
  0.7, Deviation 4): on the 200 items, Stage 1 0.896 (0.843–0.944; 0.0%) and
  Stage 2 0.757 (0.675–0.830; 8.5%); CONCERN against the rest 0.844, ENDORSEMENT
  0.801, OTHER 0.604 (0.471–0.720; 94.4%). Tranche 1: Stage 1 0.959 and Stage 2
  0.739, as recorded in September; tranche 2: 0.832 and 0.774.
- Success criteria: 1 met, with OTHER against the rest (0.604) reported beside
  it; 2 met; 6 met (0.709 against the bar of 0.25). Criteria 3, 4 and 5 are
  settled by later analyses.

### Deviation 10 files unsealed

- After the evaluation script was committed at `34403e6`, `tranche2_allocation.json`
  was checked against the SHA-256 recorded at `01f3d8a` (`ce23e229…`; it
  matches) and opened, with `tranche2_hit_rates.csv` (SHA-256
  `621d0d152f93369ee39d368df173cb8307167bea3f702b3f212ee434f67c5df4`) and
  `SEALED_step3_register_figures.txt` (SHA-256
  `4fd62a1a1b7a07f234b821c457a911eb296c32b2c7c7f0309b75eb17d07c3f79`). The
  sealed text, as the script wrote it on 4 October, follows unchanged.

### Tranche 2 allocation: measured figures

Unsealed under the Blinding clause of Deviation 10. Produced by `tranche2_03_allocate.py`;
the file hashes were recorded before the draw.

- Tranche 1 items by predicted label: N 162, CONCERN 271, ENDORSEMENT 67, OTHER 0.
- Design-weighted hit rates: the share of tranche 1 items with each predicted label whose
  tranche 1 label is CONCERN / ENDORSEMENT / OTHER / not relevant:
    - predicted CONCERN: 39.5% / 20.8% / 17.8% / 21.9% (271 items)
    - predicted ENDORSEMENT: 7.9% / 41.9% / 22.3% / 28.0% (67 items)
    - predicted OTHER: n/a / n/a / n/a / n/a (0 items)
- Stage 1 pre-filter against the tranche 1 labels, design-weighted: precision 76.9%, recall 85.9%.
- Eligible items: 11,636; by predicted label N 3,970, CONCERN 5,838, ENDORSEMENT 1,824, OTHER 4.
- Allocations examined: 501.
- Allocation on predicted label: CONCERN 95, ENDORSEMENT 405, OTHER 0 (sum 500).
- Expected final counts: CONCERN 189.4, ENDORSEMENT 284.4, OTHER 189.1; expected not relevant among the 500: 134.1.
- Gate: expected smallest final count 189.1 against the minimum of 200: FAIL.
- For comparison only, the least-spread allocation: CONCERN 275, ENDORSEMENT 225, OTHER 0, with expected final counts CONCERN 246.4, ENDORSEMENT 246.5, OTHER 181.0.
- No tranche 1 item had predicted label OTHER, so it had no measurable hit rate and received no allocation.

- In short: BART-MNLI predicted OTHER for none of the 500 tranche 1 items and
  for 4 of the 11,636 eligible items, so OTHER could grow only as a by-product
  of the other predicted labels. The allocation that maximised the smallest
  expected final count (CONCERN 95, ENDORSEMENT 405) left OTHER at 189.1,
  below the bar of 200; with random predicted labels the simulation committed
  with Deviation 10 gave a mean near 178. The evaluation of record agrees:
  BART-MNLI's OTHER F1 is 0.000 under the universal schema and 0.011 under the
  domain-specific schema.
- The allocation file also records that the three tranche 1 workbooks read by
  the pre-filter scripts on 4 October differed byte for byte from the files of
  record (SHA-256 `c58943e7…`, `63152e44…`, `3a2c1fe5…`; the master key
  matched), and the scripts printed a note saying so at the time. Every label
  they used matched the recorded tranche 1 label fingerprint (`d6f4eeea…`), and
  the hit rates and the gate use those labels only, so neither is affected.

### Next

- Final retraining of the deployed Stage 1 classifier, and the corpus runs of
  both deployed classifiers.
- A further deviation defining a material temporal effect, committed before the
  temporal calibration check is run (Deviation 12).

