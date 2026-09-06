# Calibration Round — Instructions

**Study:** A Longitudinal Analysis of Public Concern about Connected and Autonomous Vehicle Data Infrastructure in Online Discourse
**Version:** 1.0 · 6 September 2026

Governed by R2 of `docs/analysis_preregistration.md`. Read alongside `docs/annotation_codebook.md`.

---

## Purpose

Thirty items, labelled independently by all three annotators, then reviewed together. The round exists to find out whether the codebook works before 700 ratings are made against it.

The thirty items are **discarded afterwards**. They do not enter the annotated set and contribute to no estimate. Nothing you decide here is wasted, but nothing here is a result either.

---

## What each annotator does

You receive `calibration_annotator_X.csv` and the codebook. Thirty items, same thirty for everyone, in a different order each.

**Work alone.** Do not discuss any item with the other annotators until the review meeting. The whole point is to find out where the codebook leaves room for disagreement, and that is invisible if you converge by conversation first.

Fill in, for each row:

| Column | What to enter |
|---|---|
| `stage1_relevant` | `Y` or `N` |
| `stage1_seconds` | roughly how long that judgement took |
| `stage2_class` | `CONCERN`, `ENDORSEMENT`, `OTHER` — blank if Stage 1 was `N` |
| `stage2_seconds` | roughly how long |
| `subsystem` | which of the six, semicolon-separated if more than one — blank if unclear |
| `subsystem_seconds` | roughly how long |
| `skip` | `Y` if you would rather not read it; leave the labels blank |
| `notes` | anything that made you hesitate |

**On the timings.** Rough is fine — five seconds, twenty seconds, a minute. Nobody is being assessed. The numbers decide whether subsystem labelling is affordable across the whole sample, which is a pre-registered decision that has been left open pending this measurement.

**On the notes.** The most useful row in the file is one where you genuinely could not decide. Write down what made it hard. That is what the review is for.

**Do not look anything up.** No searching for the thread, the article or the product. Judge what is in front of you.

---

## What the researcher does after

### 1. Collect all three sheets. Do not compute agreement yet.

This ordering is pre-registered and it matters. If you know the agreement figure before attributing disagreements, the figure colours the attribution.

### 2. Fill the review sheet with all three labels

`calibration_review_sheet.csv`, one row per item. Enter `label_A`, `label_B`, `label_C` and mark `disagreement` as `stage1`, `stage2` or `none`.

### 3. Review every disagreement together, and assign exactly one cause

For each disagreeing item, all three discuss it and agree a single cause:

| Cause | Meaning |
|---|---|
| **a** | **missing context** — the comment is not judgeable as standalone text |
| **b** | **codebook ambiguity** — no rule covers the case |
| **c** | **misapplication** — a rule exists and was applied incorrectly |

Record it in `cause`. Also record `agreed_label` and whether a codebook change is needed.

Assign every cause before moving to step 4.

### 4. Now compute Krippendorff's α

On the thirty items, across three annotators, for Stage 1 and Stage 2 separately.

### 5. Apply the pre-registered branch

Determined by α and the plurality cause. No discretion:

| Condition | Action |
|---|---|
| **α ≥ 0.7** | Proceed to production annotation, context-free, unchanged. |
| **α < 0.7**, plurality **(a)** | Add the post title to the Stage 2 presentation for annotators, **and** run the Stage 2 model comparison on title-plus-comment for all five models. Stage 1 stays blind. |
| **α < 0.7**, plurality **(b)** | Revise the codebook. Re-run calibration on 30 fresh items. Discard both rounds. |
| **α < 0.7**, plurality **(c)** | Retrain on the existing codebook. Re-run calibration on 30 fresh items. No codebook change. |

Branch (a) has a cost worth knowing before you get there: whatever the annotators see, the models must see, so all five models are re-run.

### 6. Record three things

**Per-item timing by stage.** Median seconds for Stage 1, Stage 2 and subsystem. This resolves the subsystem-coverage decision, which was deliberately left open pending measurement. The threshold: if subsystem labelling adds 90 minutes or less per annotator across the relevant items, extend it beyond the reliability subset; if more, keep it restricted and RQ2 makes no ranking claim.

**Realised class counts.** How many CONCERN, ENDORSEMENT and OTHER among the relevant items. First read on class balance, and an input to the tranche 2 allocation.

**Whether the codebook changed**, and if so, version it. R2 branch (b) requires a fresh round if it did.

### 7. Then send the production sheets

Not before. If the codebook changes after someone has started, their early items were annotated against a superseded version.

---

## What gets written up

The calibration round is reported in the methodology: thirty items, three annotators, α on Stage 1 and Stage 2, the disagreement-cause distribution, which branch was taken, and whether the codebook was revised.

The expectation stated in advance, from the reference study, is that disagreement will concentrate at the CONCERN/OTHER boundary rather than between CONCERN and ENDORSEMENT. Report whether it did. Stating the expectation beforehand is what makes the confirmation worth anything.
