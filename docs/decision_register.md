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