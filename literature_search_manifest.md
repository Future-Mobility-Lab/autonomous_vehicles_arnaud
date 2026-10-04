# Literature Search Manifest

**File:** `docs/literature_search_manifest.md`  
**Version:** 0.4, 4 October 2026. Updated following completion of the citation-search arm, application of the E8 amendment, screening-log corrections and final reconciliation of the literature-search records.  
**Evidence files:** `PRISMA_search_evidence_log.xlsx` (search phase, 20–21 Sep: verbatim strings for every variant, known-item tests, year histograms) and `PRISMA_Search_and_Screening_Log_20260921.xlsx` (rebuild, screening, PRISMA Summary). Both are primary evidence.  
**Governs:** §2.0 of the final report; supervisor feedback items FB1 and FB2.

## Purpose

This is the literature-search counterpart of `corpus_manifest.md`. It holds every fact, number and draft sentence that §2.0 needs, each beside the evidence for it. §2.0 is assembled from this file. The pre-submission check "PRISMA counts match the saved screening records" (governing document, Part 15) is run against it.

**Status labels**

- **VERIFIED:** checked against the named file, export or screenshot.
- **LOGGED:** recorded in the evidence workbook. Arithmetic checked; figure not independently re-derived from the exports.
- **PENDING:** not yet final.

---

## 1. Scope and design

- A structured search reported with a PRISMA-style flow diagram. It is **not** an exhaustive systematic review, and §2.0 says so.
- **Diagram template:** the supervisor's. Its phases (Identification → Screening → Eligibility → Included) follow the PRISMA 2009 structure, so the diagram is labelled with the version it actually follows (governing document 8B-10). Confirm the template version at the next supervision meeting (Part 14, item 4). **PENDING**
- **Two arms:** database searches, and other sources. Strands A and B are reported separately at the Included box.
- **Methods, model and tool references** enter through the other-sources arm, not the database funnel, in accordance with governing document FB2 and §13.4.

| Strand | Literature | Report section it supports |
|---|---|---|
| A | Public perception of, trust in and concern about CAVs, including privacy, data handling and security | §2.1–§2.3 |
| B-i | Empirical comparisons of zero-shot or prompted classifiers against supervised fine-tuned classifiers on short user-generated text | §2.4, classification approaches |
| B-ii | Class-prevalence estimation and correction for prior or label shift (quantification) | §2.4, quantification |

---

## 2. Eligibility criteria

### 2.1 Window and language

| Strand | From | Language |
|---|---|---|
| A | 2015 | English |
| B-i | 2019 | English |
| B-ii | 2000 | English |

### 2.2 Publication types

- Journal articles, conference papers, preprints and theses are eligible.
- **Preprints:** eligible where they ground the methodology. Publication status is recorded as a column and never used as a filter.
- **Theses:** eligible by amendment of E8, dated 26 September 2026. Rationale, to be quoted as written:

> Theses are eligible publication types across all strands. This aligns E8 with the eligibility position already recorded for preprints: a source is judged on whether it grounds the methodology, not on its publication wrapper, with publication status recorded as a column rather than applied as a filter. Where a thesis's contribution also appears as a paper already in the corpus, the paper is retained and the thesis excluded at full text under E7 as a duplicate contribution, not under E8.

### 2.3 Exclusion codes

| Code | Meaning |
|---|---|
| E1 | Not about CAVs / not the target technology |
| E2 | Fails the strand test (see 2.4) |
| E3 | No empirical content: editorial, commentary, position piece, keynote, poster abstract, panel or workshop summary |
| E4 | Not English |
| E5 | Outside the publication window |
| E6 | No abstract **and** no locatable full text |
| E7 | Duplicate missed at deduplication, or duplicate contribution (thesis vs paper) |
| E8 | Wrong publication type: whole proceedings volume, front matter, table of contents |

### 2.4 Strand tests

The Stage 2 strand tests were fixed on 26 September 2026.

**Gate 1, applied to every strand:** is it a study? Proceedings volumes → E8. Editorials, commentaries, keynotes, poster abstracts, panel or workshop summaries → E3. No abstract and no locatable full text → E6.

**Strand A.** Include if the study reports empirical evidence (survey, interview, experiment, observational data, or discourse or social-media analysis) about how people perceive, accept, trust or express concern about CAVs, bearing on privacy, data handling, security or concern. Exclude under E2 if it builds a system rather than measuring a perception: protocols, architectures, intrusion detection, key management, blockchain, authentication, simulation. Exclude under E1 if the technology is not CAVs or a closely coupled component (V2X, in-vehicle networks, ADAS, robotaxi services).

**Strand B-i.** Criterion locked 26 September 2026; quote as written:

> Strand B-i includes a study only if it reports an empirical comparison between a zero-shot or prompted approach and a supervised fine-tuned approach on short user-generated text. Studies whose primary contribution is cross-lingual or low-resource-language transfer are excluded under E2, because the performance gap in those studies reflects pretraining resource availability rather than the supervision axis under examination. Multilingual studies are retained where they report a zero-shot versus fine-tuned comparison, whether or not English is among the languages tested.

Operative question: *is the comparison between zero-shot and fine-tuned, or between languages?* Short user-generated text covers social-media posts, forum threads, comments, and product and app reviews. It does not cover clinical notes, legal documents, news articles, scientific abstracts or transcripts.

**Strand B-ii.** Include if the study estimates class prevalence in unlabelled data, or corrects classifier output for prior or label shift: quantification learning, classify-and-count and its adjusted variants, SLD/EM prior adjustment, distribution matching, label-shift correction. Exclude under E2 for confidence calibration only, for domain adaptation with no prevalence or class-prior estimand, and for uncertainty quantification in the numerical-methods sense.

**MAYBE** is reserved for a missing or truncated abstract, or a study design that cannot be determined without the methods section.

---

## 3. Sources and searches

**The as-run search strings and search dates are held in the Search Log, and §2.0 quotes them verbatim from there.** Do not use the planning strings from earlier drafts: several searches had to be executed differently from their design, including IEEE Xplore sequential execution, arXiv field-based searches and the ACM DL title-bound concept block.

### 3.1 Accepted sources

| Strand | Database | Records | Note |
|---|---|---:|---|
| A | IEEE Xplore | 336 | Sequential execution: vehicle block 83,626 → privacy/security 13,492 → perception/discourse 451 → year limit 409 → conference and journal records 336. No language facet, so language was deferred to screening. RIS in four batches (100 + 100 + 100 + 36). Known-item criterion recorded as not applicable; see 3.3. |
| A | Scopus | 476 | Database count retained; two within-source duplicates were later merged in Zotero (474 items). |
| B-i | Scopus | 1,124 | Correct database result count. The earlier 1,117 figure was a carry-forward error. |
| B-i | arXiv | 301 | All fields, 2019-01-01 to 2026-09-20; a 2-record run caused by a silently retained Title field was excluded as invalid. |
| B-ii | ACM Digital Library | 118 | Concept block restricted to Title; 50 + 50 + 18 BibTeX batches; one malformed record repaired, 118/118 reconciled. |
| | **Total identified** | **2,355** | |

### 3.2 Superseded and rejected searches

| Search | Result | Why |
|---|---|---|
| B-i Scopus, `evaluat*` removed | 773 | Known item Yin, Hay & Roth (2019) not retrieved; narrowing rejected under the pre-set terminal rule; original query restored. |
| B-ii Scopus, early variants | 8,850 → 3,590 → 1,980 → 2,120 database hits | Bare *quantification* retrieved uncertainty-quantification, chemistry and metrology literature. The final superseded broad Scopus variant returned 2,120 database hits and produced 2,131 Zotero-imported records. Both figures are retained with their respective labels. |
| B-ii Scopus, reopened | 1,981 → 978 with the Computer Science filter | Generic terms replaced with the exact Saerens title phrase; count still above the precision threshold. |
| B-ii Scopus, title-restricted | 325 (year analyser showed 322; three-record discrepancy retained) | Known item González et al. (2017) was not retrieved; Saerens et al. (2002) was not tested once the terminal rule fired. Audit of 26 Sep 2026 confirmed that Scopus indexes González et al. under the malformed title "A review onquantification learning", so the failure reflects a title-indexing/tokenisation defect. Decision: do not reopen calibration; retain the search as SUPERSEDED. |
| B-ii arXiv | 449 candidates | Known items González et al. (2017) and Saerens et al. (2002) not retrieved; rejected at calibration, 0 exported. |
| First combined build | 4,468 identified, 4,293 after dedup | Superseded by a clean rebuild after recalibration; never entered screening. |

### 3.3 Known-item tests

Each search was calibrated against papers already known to belong in its strand.

- **A:** Lee & Hess (2022); Kyriakidis et al. (2015); Khan et al. (2024)
- **B-i:** Yin, Hay & Roth (2019); Hardalov et al. (2022); Hedderich et al. (2021); Schick & Schütze (2021)
- **B-ii:** González et al. (2017), *A Review on Quantification Learning*, ACM Computing Surveys 50(5), DOI 10.1145/3117807; Saerens, Latinne & Decaestecker (2002)

**Limits of the known-item test identified during the audit:**

- **IEEE Xplore, Strand A:** all three Strand A known items are published by Springer Nature or Elsevier and are not indexed by IEEE Xplore. The original FAIL therefore could not validly assess IEEE coverage. IEEE was retained for engineering coverage of V2X, in-vehicle networks and CAV security. The known-item criterion is recorded as not applicable to IEEE Xplore. A dated correction was entered on 4 October 2026.
- **Scopus, B-ii:** González et al. is indexed under a malformed title, so it fails the title-restricted search while passing a DOI lookup.
- **ACM DL, B-i:** Yin, Hay & Roth (2019) is an EMNLP paper outside ACM's scope. The failure was expected and ACM DL was not used for B-i.

---

## 4. Deduplication

- 2,355 identified − 163 duplicates removed = **2,192** records screened.
- Zotero's Duplicate Items view was empty afterwards.
- Proceedings with identical titles but different LNCS volumes were distinguished and not merged.
- Frozen database corpus: `ALL ACCEPTED - DEDUPED.ris`.
- An earlier single RIS-derived screening log contained 2,190 rows because two records were omitted during export. This was resolved by separately exporting the final INCLUDE and EXCLUDE title-stage collections and reconciling them to the 2,192-record corpus.
- The superseded first-build export remains audit evidence only and did not enter screening.

---

## 5. Stage 1: title screening

| | Records | Status |
|---|---:|---|
| Screened | 2,192 | VERIFIED |
| Excluded | 1,008 | VERIFIED after E8 amendment application |
| Carried forward | 1,184 | VERIFIED after E8 amendment application |

- **Rules:** permissive. Where the title was uninformative, the record was retained for abstract screening.
- The original mechanical thesis exclusion under E8 was superseded by the amendment of 26 September 2026.
- On 4 October 2026, the three affected thesis records were re-screened under the amended E8 criterion and all three were carried forward.
- The three thesis records were moved from the title-stage EXCLUDE collection to INCLUDE without deleting them from the Zotero library.
- **Evidence:** `S1_title_screening_v2.xlsx`, the reconstructed Stage 1 log and the final Zotero decision collections.

Arithmetic:

`1,008 + 1,184 = 2,192`

---

## 6. Stage 2: abstract screening

### 6.1 Final result

The file of record is `stage_2_abstract_screening_FINAL_20260927.xlsx`, with the three E8 thesis additions and the dated correction to S2-0307 applied.

| | Records |
|---|---:|
| Screened | 1,184 |
| INCLUDE | 353 (A 207 · B-i 74 · B-ii 72) |
| MAYBE | 11 (A 2 · B-i 9) |
| EXCLUDE | 820 (E2 783 · E1 28 · E3 6 · E6 3) |
| Carried forward to full text | 364 (A 209 · B-i 83 · B-ii 72) |

Arithmetic:

`353 + 11 + 820 = 1,184`

`353 + 11 = 364`

`209 + 83 + 72 = 364`

`783 + 28 + 6 + 3 = 820`

The three E8 thesis records are included in the B-ii Stage 2 total.

On 4 October 2026, S2-0307 was corrected from EXCLUDE E2 to INCLUDE. The study directly benchmarks zero-shot inference against LoRA/PEFT fine-tuning on annotated social-media comments. The author judged the supervision-axis comparison, rather than low-resource-language transfer, to be the primary contribution. The previous generic exclusion rationale is superseded by the dated correction.

### 6.2 Abstract repair

**352** records had a missing or truncated abstract in the export. Full abstracts were retrieved where available and the records were then screened against the applicable strand test.

Three final exclusions have neither an abstract nor locatable full text and are coded E6.

### 6.3 Code transcription

Twenty-five EXCLUDE rows had their exclusion code recorded in the screening-note field rather than the decision field.

The codes were transcribed into the decision field without changing the underlying screening decisions:

- E2 × 20
- E6 × 3
- E3 × 1
- E1 × 1

Two notes reading "Abstract missing and no full text" were recorded under E6, consistent with the E6 definition.

The file's Change log tab records the affected rows.

### 6.4 Calibration and consistency check

**Design:** a blind re-screen of the first 17 records of Strand A, the first 17 of B-i and the first 16 of B-ii, in sheet order, giving 50 records.

**Pre-set rules:**

- Primary measure: screening outcome, carried forward (INCLUDE or MAYBE) versus excluded.
- Stop below 45/50.
- Stop also if three or more primary disagreements trace to the same criterion.
- Secondary measure: exact label.

**Original blind re-screen result:** primary 47/50 (94%); secondary 46/50 (92%). Neither stop rule was triggered.

| ID | Strand | Original | Re-screen | Type | Final position |
|---|---|---|---|---|---|
| S2-0306 | B-i | EXCLUDE | INCLUDE | Primary | Original EXCLUDE retained |
| S2-0307 | B-i | EXCLUDE | INCLUDE | Primary | Corrected to INCLUDE on 4 October 2026 after review of the complete abstract and primary-contribution criterion |
| S2-0460 | B-ii | INCLUDE | EXCLUDE | Primary | Original INCLUDE retained |
| S2-0314 | B-i | MAYBE | INCLUDE | Secondary only | MAYBE retained; both labels carry the record forward |

The 47/50 figure remains the measured agreement from the original blind re-screen. S2-0307 was subsequently corrected as a separate dated audit decision.

The generic note `"abstract does not establish all required elements"` occurred across 118 excluded records. An optional catch-all re-screen of those 118 records was offered and **not run**. This was logged on 4 October 2026.

---

## 7. Full-text stage: NOT STARTED

The current Full-text Screening Log contains **402 records**.

### 7.1 Database-derived records

364 records were carried forward from Stage 2:

- Strand A: 209
- Strand B-i: 83
- Strand B-ii: 72

### 7.2 Backward-citation records

A further 38 B-ii records were carried forward from backward citation searching of González et al. (2017).

### 7.3 Current full-text population

| Source / strand | Records |
|---|---:|
| Database-derived, Strand A | 209 |
| Database-derived, Strand B-i | 83 |
| Database-derived, Strand B-ii | 72 |
| Backward citation searching, Strand B-ii | 38 |
| **Total** | **402** |

By strand:

- A = 209
- B-i = 83
- B-ii = 110
- **Total = 402**

The full-text stage has not yet started. Decision, exclusion code, Method, Sample/Data, Key Finding and Relation to gap remain to be completed during full-text screening.

---

## 8. Other-sources arm

### 8.1 Backward citation searching from González et al. (2017)

Evidence workbook:

`lit_search/other_sources/gonzalez_backward_citation_audit_20261002.xlsx`

Final audit:

- References examined: 77
- Already in database corpus: 7
- New records: 70
- Excluded at title: 27
- Progressed beyond title: 43
- Excluded at abstract under E2: 5
- Carried forward to full text: 38
  - INCLUDE: 37
  - MAYBE: 1

The 38 carried records are entered in the Full-text Screening Log with IDs `GZ-<Ref no.>` and Strand B-ii.

### 8.2 Forward citation searching

Forward citation searching from González et al. (2017) was **not run**.

The search log records that backward citation searching cannot identify literature published after the 2017 review, so literature from 2017 onwards relies on the database search, principally the ACM Digital Library for B-ii.

### 8.3 ACL Anthology fallback

The proposed ACL Anthology hand-search was **not run**.

It was a fallback to be used if Scopus failed to retrieve the B-i known items associated with ACL-family venues. Scopus passed all four B-i known-item tests, so the fallback condition was not triggered.

### 8.4 Supervisor recommendation

Lee et al. (2026), preprint, is logged as one record identified through supervisor recommendation.

### 8.5 References carried over from the 41029 proposal

These references enter through the other-sources arm and are **to be counted at drafting**.

### 8.6 Methods, model and tool references

Methods, model and tool references enter through the PRISMA other-sources arm rather than the database funnel, under governing document FB2 and §13.4.

These are **to be counted at drafting**.

---

## 9. PRISMA figure: assembly table

| Box | Value | Status | Evidence |
|---|---|---|---|
| Identified, by accepted database | IEEE A 336 · Scopus A 476 · Scopus B-i 1,124 · arXiv B-i 301 · ACM B-ii 118 | VERIFIED | Search Log |
| Identified, database total | 2,355 | VERIFIED | Search Log |
| Duplicates removed | 163 | VERIFIED | Zotero / frozen corpus |
| Screened at title | 2,192 | VERIFIED | Stage 1 records |
| Excluded at title | 1,008 | VERIFIED | Final title-stage decisions after E8 amendment |
| Carried after title | 1,184 | VERIFIED | Final title-stage decisions after E8 amendment |
| Screened at abstract | 1,184 | VERIFIED | Stage 2 FINAL + E8 addendum |
| Excluded at abstract | 820 | VERIFIED | E2 783 · E1 28 · E3 6 · E6 3 |
| Carried from database arm to full text | 364 | VERIFIED | A 209 · B-i 83 · B-ii 72 |
| Backward citations examined | 77 | VERIFIED | Citation audit workbook |
| Backward citations already in corpus | 7 | VERIFIED | Citation audit workbook |
| New backward-citation records | 70 | VERIFIED | Citation audit workbook |
| Backward-citation title exclusions | 27 | VERIFIED | Citation audit workbook |
| Backward-citation abstract exclusions | 5 E2 | VERIFIED | Citation audit workbook |
| Backward-citation records carried to full text | 38 | VERIFIED | 37 INCLUDE · 1 MAYBE |
| Current full-text Screening Log population | 402 | VERIFIED | 364 database-derived + 38 backward citation |
| Excluded at full text | — | PENDING | Full-text Screening Log |
| Included after full text | — | PENDING | Full-text Screening Log |
| Remaining other-sources references | To be counted at drafting | PENDING | Search Log / bibliography |

Whether title and abstract screening appear as one Screening box or two is decided by the supervisor's template.

The publications-per-year chart required under FB6 is built from the year histograms captured during the search phase and retained in `PRISMA_search_evidence_log.xlsx`.

---

## 10. Draft sentences for §2.0

Past tense; Australian English. Bracketed items remain provisional until the corresponding open item closes.

**Scope.**

> A structured search strategy was used to identify the literature reviewed in this section; exhaustive retrieval was not attempted. Identification and screening are reported in a flow diagram based on the supervisor-supplied template.

**Strands.**

> The search comprised two strands: Strand A, on public perception of and concern about connected and autonomous vehicles; and Strand B, on classifying and quantifying social-media text under limited supervision, searched as B-i (zero-shot versus supervised classifier comparisons) and B-ii (prevalence estimation and prior-shift correction).

**Databases.**

> Strand A was searched in Scopus and IEEE Xplore, Strand B-i in Scopus and arXiv, and Strand B-ii in the ACM Digital Library on 20–21 September 2026.

**Calibration of searches.**

> Search strings were calibrated before screening against known-item tests. Where a known-item test was later found to be structurally incapable of assessing a database, the limitation and resulting search decision were documented in the search log.

**B-ii coverage.**

> The Scopus search for Strand B-ii failed its title-bound known-item test because Scopus indexes the key review under a malformed title that the calibrated query could not match. The search was not reopened; direct database coverage for B-ii therefore came from the ACM Digital Library and was supplemented by backward citation searching from González et al. (2017).

**IEEE Xplore.**

> The pre-specified Strand A known items were all published outside IEEE Xplore's index and therefore could not validly assess IEEE coverage. IEEE Xplore was retained for its coverage of engineering literature on V2X, in-vehicle networks and CAV security.

**Deduplication.**

> After deduplication in Zotero, 163 duplicates were removed, leaving 2,192 records for title screening.

**Screening.**

> Screening was carried out in two stages by a single screener, first on titles and then on abstracts, against predefined eligibility criteria. An amendment admitting theses as an eligible publication type was subsequently applied to the three affected title-stage records.

**Abstract repair.**

> Where an exported abstract was missing or truncated, the complete abstract was retrieved where available and the record was screened against the applicable strand criterion. In total, 352 abstracts were retrieved or repaired before completion of abstract screening.

**Calibration of screening.**

> A stratified 50-record blind re-screen gave agreement of 47/50 (94%) on the screening outcome and 46/50 (92%) on the exact label. One record, S2-0307, was subsequently corrected from EXCLUDE to INCLUDE after a dated review of the complete abstract and the Strand B-i primary-contribution criterion.

**Other sources.**

> Backward citation searching examined all 77 references of González et al. (2017). Seven were already present in the database corpus and 70 were new records. After title and abstract screening, 38 citation-search records were carried forward to full-text assessment. Forward citation searching and the proposed ACL Anthology fallback search were not undertaken. One additional record was identified through supervisor recommendation, while proposal-carried and methods-related references are recorded through the other-sources arm and will be counted during drafting.

---

## 11. Status and open items

### Closed items

- [x] **11.1 The three theses.** Closed 4 October 2026. All three were re-screened under the E8 amendment, carried through title and abstract screening as B-ii INCLUDE records, added to the Stage 2 file and Zotero collections, and entered into the Full-text Screening Log.
- [x] **11.2 S2-0211.** Closed. Strand A INCLUDE.
- [x] **11.3 Calibration adjudications.** Original calibration adjudication completed. The optional 118-record catch-all check was offered and not run. S2-0307 was subsequently corrected separately on 4 October 2026.
- [x] **11.4 Two-item export gap.** Closed 26 September 2026. Two real records were omitted from one RIS export; PRISMA counts were unaffected.
- [x] **11.5 B-ii Scopus rationale.** Closed 26 September 2026. The malformed Scopus title was identified and the search was not reopened.
- [x] **11.6 Other-sources search arm.** Backward citation audit completed; forward citation searching and ACL fallback decisions recorded; supervisor recommendation logged; proposal and methods references deferred for drafting count.
- [x] **11.10 IEEE Xplore correction.** Dated correction added to the Search Log and corresponding evidence-workbook notes updated.
- [x] **11.11 Log consistency.** Evidence-workbook Stage 2 pointer, B-i 1,117/1,124 correction, B-ii 2,120/2,131 labels, disk filenames, search-phase evidence provenance line and FB2 other-sources routing correction completed.
- [x] **11.12 S2-0307.** Closed 4 October 2026. Corrected from EXCLUDE E2 to INCLUDE, moved in Zotero, added to the Full-text Screening Log and reflected in PRISMA counts.

### Repository commit

- [x] **11.9 Commit.** Closed 4 October 2026. Main literature-search commit: `fe69005` (`Literature search: citation arm, E8 addendum and log corrections`). The commit hash is recorded in the Search Log.

### Remaining substantive work

- [ ] **11.7 Full-text stage.** Full-text screening has not started. Current population: 402 records.
- [ ] **11.8 PRISMA figure and publications-per-year chart.** Build using the supervisor's template and the final reconciled evidence.
- [ ] **11.13 Full-text workload.** Decide the screening order, retrieval procedure and per-record workflow before full-text screening starts.

---

## Change log

| Version | Date | Commit | Change |
|---|---|---|---|
| 0.1 | 27 Sep 2026 | *record on commit* | Created from the working literature-search record. |
| 0.2 | 27 Sep 2026 | *record on commit* | Reconciled against both evidence logs; the two-item export gap and B-ii Scopus rationale were closed; IEEE known-item and log-consistency issues were recorded; the B-ii Scopus variant chain was reconciled. |
| 0.3 | 2 Oct 2026 | *record on commit* | Updated from the 2 October status handover: Stage 2 figures, Zotero reconciliation and calibration results recorded; backward-citation audit added; outstanding correction and filing items documented. |
| 0.4 | 4 Oct 2026 | fe69005 | Applied the E8 thesis amendment to the three affected records; completed backward-citation screening; recorded decisions not to run forward citation searching or the ACL fallback; corrected S2-0307 to INCLUDE; reconciled Stage 2 and full-text counts; completed IEEE and search-log corrections; recorded the optional 118-record check as offered and not run. |