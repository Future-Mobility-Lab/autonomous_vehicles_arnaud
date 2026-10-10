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

