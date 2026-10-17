# Literature Search Manifest

**File:** `docs/literature_search_manifest.md`  
**Version:** 0.7, 17 October 2026. Records the completed full-text stage and the final PRISMA counts (carried from the uncommitted 0.6 draft of 10 October), the verification of every count against the files of record on 14 October, the four Longitudinal-tag corrections, the other-sources count as at Section 2, the figures as built on 14 October, the published status of Lee et al. (2026), and the recovery and confirmation of the IEEE Xplore strings on 17 October. Supersedes 0.5 (committed) and 0.6 (drafted, not committed).  
**Evidence files:** `PRISMA_search_evidence_log.xlsx` (search phase, 20–21 Sep: verbatim strings for every variant, known-item tests, year histograms; IEEE Xplore strings and confirmation re-run added 17 Oct) and `PRISMA_Search_and_Screening_Log_20260921.xlsx` (rebuild, screening, Full-text Screening Log, PRISMA Summary). Both are primary evidence. Files of record for the stages: `stage_2_abstract_screening_FINAL_20260927.xlsx` (Stage 2), the Full-text Screening Log (full text), `lit_review_reading_notes_20261010.xlsx` (reading and tags), `included_studies_final_20261010.xlsx` (PRISMA counts tab). Verification record: `prisma_verification_20261014.md`.  
**Governs:** §2.1 (search strategy and screening) and Appendix F of the final report; supervisor feedback items FB1, FB2 and FB6.

## Purpose

This is the literature-search counterpart of `corpus_manifest.md`. It holds every fact and number that §2.1, the PRISMA figure and Appendix F rest on, each beside the evidence for it. The pre-submission check "PRISMA counts match the saved screening records" (governing document, Part 15) is run against it.

**Status labels**

- **VERIFIED:** checked against the named file, export or screenshot.
- **LOGGED:** recorded in the evidence workbook. Arithmetic checked; figure not independently re-derived from the exports.
- **PENDING:** not yet final.

---

## 1. Scope and design

- A structured search reported with a PRISMA-style flow diagram. It is **not** an exhaustive systematic review, and §2.1 says so.
- **Diagram template:** the supervisor's. Its phases (Identification → Screening → Eligibility → Included) follow the PRISMA 2009 structure, so the diagram is labelled with the version it actually follows (governing document 8B-10). Confirm the template version at the next supervision meeting (Part 14, item 4). **PENDING.** A 2009-phase single-flow figure was built on 14 October 2026 (`prisma_flow_20261014.tex`); if the template proves to follow the 2020 two-column layout, the database arm screens 2,192 and the other-sources arm 70, with OS-1 entering at "sought", and the figure is redrawn with the same counts.
- **Two arms:** database searches, and other sources. Strands A and B are reported separately at the Included box.
- **Methods, model and tool references** enter through the other-sources arm, not the database funnel, in accordance with governing document FB2 and §13.4.

| Strand | Literature | Report section it supports |
|---|---|---|
| A | Public perception of, trust in and concern about CAVs, including privacy, data handling and security | §2.2–§2.4 |
| B-i | Empirical comparisons of zero-shot or prompted classifiers against supervised fine-tuned classifiers on short user-generated text | §2.3 (third debate), §2.5 |
| B-ii | Class-prevalence estimation and correction for prior or label shift (quantification) | §2.5 |

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
- **Preprints:** eligible where they ground the methodology. Publication status is recorded as a column and never used as a filter. Where an included preprint has since been published, the report cites the published version (full-text decision D5); see §7.3.
- **Theses:** eligible by amendment of E8, dated 26 September 2026. Rationale, to be quoted as written:

> Theses are eligible publication types across all strands. This aligns E8 with the eligibility position already recorded for preprints: a source is judged on whether it grounds the methodology, not on its publication wrapper, with publication status recorded as a column rather than applied as a filter. Where a thesis's contribution also appears as a paper already in the corpus, the paper is retained and the thesis excluded at full text under E7 as a duplicate contribution, not under E8.

### 2.3 Exclusion codes

| Code | Meaning |
|---|---|
| E1 | Not about CAVs / not the target technology |
| E2 | Fails the strand test (see 2.4) |
| E3 | No empirical content: editorial, commentary, position piece, keynote, poster or abstract-only item, tutorial outline, panel or workshop summary |
| E4 | Not English |
| E5 | Outside the publication window |
| E6 | Full text unavailable (at Stage 2: no abstract and no locatable full text) |
| E7 | Duplicate missed at deduplication, or duplicate contribution |
| E8 | Wrong publication type: whole proceedings volume, front matter, table of contents. Theses are eligible |

This wording was aligned with the code key of the Full-text Screening Log on 5 October 2026 (ruling R1), and the key now carries the same text. At Stage 2, E6 was applied where a record had neither an abstract nor a locatable full text; at the full-text stage it means the full text could not be obtained. Appendix F of the report reproduces this table.

### 2.4 Strand tests

The Stage 2 strand tests were fixed on 26 September 2026.

**Gate 1, applied to every strand:** is it a study? Proceedings volumes → E8. Editorials, commentaries, keynotes, poster abstracts, panel or workshop summaries → E3. No abstract and no locatable full text → E6.

**Strand A.** Include if the study reports empirical evidence (survey, interview, experiment, observational data, or discourse or social-media analysis) about how people perceive, accept, trust or express concern about CAVs, bearing on privacy, data handling, security or concern. Exclude under E2 if it builds a system rather than measuring a perception: protocols, architectures, intrusion detection, key management, blockchain, authentication, simulation. Exclude under E1 if the technology is not CAVs or a closely coupled component (V2X, in-vehicle networks, ADAS, robotaxi services).

**Strand B-i.** Criterion locked 26 September 2026; quote as written:

> Strand B-i includes a study only if it reports an empirical comparison between a zero-shot or prompted approach and a supervised fine-tuned approach on short user-generated text. Studies whose primary contribution is cross-lingual or low-resource-language transfer are excluded under E2, because the performance gap in those studies reflects pretraining resource availability rather than the supervision axis under examination. Multilingual studies are retained where they report a zero-shot versus fine-tuned comparison, whether or not English is among the languages tested.

Operative question: *is the comparison between zero-shot and fine-tuned, or between languages?* Short user-generated text covers social-media posts, forum threads, comments, and product and app reviews. It does not cover clinical notes, legal documents, news articles, scientific abstracts or transcripts.

**Strand B-ii.** Include if the study estimates class prevalence in unlabelled data, or corrects classifier output for prior or label shift: quantification learning, classify-and-count and its adjusted variants, SLD/EM prior adjustment, distribution matching, label-shift correction. Exclude under E2 for confidence calibration only, for domain adaptation with no prevalence or class-prior estimand, and for uncertainty quantification in the numerical-methods sense.

**MAYBE** is reserved for a missing or truncated abstract, or a study design that cannot be determined without the methods section.

**Full-text stage.** The same strand tests are applied to the full paper. The rules of application, workflow decisions D1–D10 and rulings R1–R12 are set out in `full_text_screening_instructions_v1.0_20261005.md`, adopted on 5 October 2026. MAYBE is not used at full text: every record ends INCLUDE or EXCLUDE (decision D4). Appendix F of the report reproduces the strand tests, with the B-i criterion quoted as locked.

---

## 3. Sources and searches

**The as-run search strings and search dates are held in the Search Evidence tab of `PRISMA_search_evidence_log.xlsx`, and Appendix F of the report quotes them verbatim from there** (§2.1 points to Appendix F). Do not use the planning strings from earlier drafts: several searches had to be executed differently from their design, including IEEE Xplore sequential execution, arXiv field-based searches and the ACM DL title-bound concept block.

### 3.1 Accepted sources

| Strand | Database | Records | Note |
|---|---|---:|---|
| A | IEEE Xplore | 336 | Sequential execution: vehicle block 83,626 → privacy/security 13,492 → perception/discourse 451 → year limit 409 → conference and journal records 336. No language facet, so language was deferred to screening. RIS in four batches (100 + 100 + 100 + 36). Known-item criterion recorded as not applicable; see 3.3. Strings recovered and confirmed 17 October 2026; see below. |
| A | Scopus | 476 | Database count retained; two within-source duplicates were later merged in Zotero (474 items). 735 unfiltered, 621 after the 2015–2025 year filter, 476 after the language and document-type filters. |
| B-i | Scopus | 1,124 | Correct database result count. The earlier 1,117 figure was a carry-forward error. |
| B-i | arXiv | 301 | All fields, 2019-01-01 to 2026-09-20; a 2-record run caused by a silently retained Title field was excluded as invalid. |
| B-ii | ACM Digital Library | 118 | Concept block restricted to Title; 50 + 50 + 18 BibTeX batches; one malformed record repaired, 118/118 reconciled. |
| | **Total identified** | **2,355** | |

**IEEE Xplore, Strand A: the three block strings as entered on 20 September 2026.** The strings were not recorded verbatim in either evidence log at search time. On 17 October 2026 they were recovered from the record of the 20 September session (the strings supplied for entry immediately before each recorded count) and confirmed by a re-run in the same sequence, which returned 84,356 → 13,610 → 452 → 410 (2015–2025) → 337 (Conferences and Journals) against the September counts 83,626 → 13,492 → 451 → 409 → 336. The unfiltered counts grew with records dated 2026; the two filtered counts differ by one record each. Screenshot `ieee_strandA_rerun_20261017.png`; commit `adf5354`. **VERIFIED.**

- Basic search box: `("connected vehicle*" OR "connected and automated vehicle*" OR "autonomous vehicle*" OR "automated vehicle*" OR "self-driving" OR driverless OR "automated driving" OR V2X OR "vehicle-to-everything" OR "vehicle-to-vehicle" OR "vehicle-to-infrastructure")`
- Search within results: `privacy OR "data protection" OR "data security" OR "data sharing" OR "data collection" OR cybersecurity OR "cyber security" OR surveillance OR hacking OR security`
- Search within results: `("public perception*" OR "public opinion" OR "public attitude*" OR "user perception*" OR acceptance OR "risk perception" OR "social media" OR reddit OR twitter OR forum* OR discourse OR sentiment)`

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

Verified from the row-level decisions of the file of record on 14 October 2026: 1,184 = 1,181 (main sheet) + 3 (E8 addendum); INCLUDE 353 (A 207 · B-i 74 · B-ii 72); MAYBE 11 (A 2 · B-i 9); EXCLUDE 820 (E2 783 · E1 28 · E3 6 · E6 3); every exclusion carries a code in the decision field and a note. The sheet's own summary cell reads INCLUDE 350 because it counts the main sheet only; a note was added at cell M2 of the main sheet on 14 October 2026.

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

On 14 October 2026 the Calibration tab's "Original decision" column (E2:E51) was frozen to the decisions as they stood at the re-screen; it had been an XLOOKUP to the live main-sheet decision, so the 4 October correction of S2-0307 had silently moved the tab's own tally to 48/50. The tab now reproduces 47/50 and 46/50; E23 reads EXCLUDE – E2 with a dated note in F23 and a dated line in G6.

At the 4 October 2026 review, the generic note "abstract does not establish all required elements" had occurred across 118 excluded records; an optional catch-all re-screen of those records was offered and not run, which was logged on the same date. In the file of record every one of the 820 Stage 2 exclusions carries an exclusion code in the decision field and a screening note; the generic notes were replaced before the file was frozen, and one note still uses the generic wording (verified 14 October 2026).

---

## 7. Full-text stage: COMPLETE

Full-text screening was carried out between 5 and 10 October 2026 on the **403 records** entered in the Full-text Screening Log: the 402 records below plus the supervisor-recommended study (OS-1, Lee et al., 2026, Strand B-i; the version read was the preprint), entered on 4 October 2026 and recorded in Search Log row 18 and PRISMA Summary row 31.

### 7.1 Database-derived records

364 records were carried forward from Stage 2:

- Strand A: 209
- Strand B-i: 83
- Strand B-ii: 72

### 7.2 Backward-citation records

A further 38 B-ii records were carried forward from backward citation searching of González et al. (2017).

### 7.3 Full-text population and result

| Source / strand | Sought | Not retrieved (E6) | Assessed | Excluded with reasons | Included |
|---|---:|---:|---:|---:|---:|
| Database-derived, Strand A | 209 | 2 | 207 | 2 | 205 |
| Database-derived, Strand B-i | 83 | 0 | 83 | 26 | 57 |
| Supervisor recommendation, Strand B-i | 1 | 0 | 1 | 0 | 1 |
| Database-derived, Strand B-ii | 72 | 2 | 70 | 4 | 66 |
| Backward citation searching, Strand B-ii | 38 | 0 | 38 | 0 | 38 |
| **Total** | **403** | **4** | **399** | **32** | **367** |

By strand: A 205 · B-i 58 · B-ii 104 = **367** (VERIFIED against the Full-text Screening Log: 367 INCLUDE, 36 EXCLUDE, no blank decision, no duplicate ID). Re-derived cell by cell from the Screening Log rows on 14 October 2026: every cell agrees (`prisma_verification_20261014.md`).

Exclusions with reasons (32): E2 fails the strand test 28 (B-i 26, A 1, B-ii 1) · E3 no empirical content 2 (both tutorial outlines, S2-0449 and S2-0460) · E1 not about CAVs 1 (S2-0067) · E7 duplicate contribution 1 (S2-0512, superseded by S2-0509). Full text not retrievable, E6: 4 (S2-0194, S2-0273, S2-0529, S2-0450). E6 is reported in the figure as *not retrieved*, separately from the exclusions, so that the reasons sum to 32 and the assessed count is 399.

E2 sub-reasons at full text (28): Bi-direct 10 · Bi-zeroshot 5 · Bi-task 4 · Bi-language 3 · Bi-text 2 · Bi-modality 1 · Bi-finetuned 1 · A-evidence 1 · Bii-othersense 1.

Every included record carries Method, Sample/Data, Version assessed, Date assessed, Evidence and the three strand tags (D7). Key Finding and Relation to gap were written for all 58 B-i and all 104 B-ii records and for eight Strand A records (the online-discourse analyses and comparison-table studies). The consistency check planned under D9 (blind re-assessment of the first ten records per strand) is **not recorded** in the log; §2.1 does not report a full-text agreement figure.

**Published versions cited (D5).** Two included B-i preprints are cited in the report as their published versions: S2-0421 (NAACL 2024, doi 10.18653/v1/2024.naacl-short.51) and S2-0436 (LREC 2026, doi 10.63317/2b6xmbq3kphf); a D5 note naming the version read and the version cited was added to each row's Evidence cell on 14 October 2026. OS-1 is cited as the published article (§8.4).

**Rows and records changed after 5 October.** S2-0189: title restored. OS-1: added. Column entries moved between cells on 9 October for four records (S2-0003, S2-0529, S2-0450, S2-0449); Source entries restored for rows 365–406. Search Log row 26 and PRISMA Summary rows 31–53 record these. The Version-assessed cells of the three E6 records S2-0273, S2-0529 and S2-0450 are blank by decision of 14 October 2026 (nothing was retrieved to assess).

**Strand A tag counts and corrections (14 October 2026), recorded in `lit_review_reading_notes_20261010.xlsx` by dated note.**

- (a) The Longitudinal tag (Tag 2) of four Strand A records, S2-0142, S2-0186, S2-0231 and S2-0254, was set to Y at screening but each study proves on reading to rest on a single wave; corrected to N on 14 October 2026. S2-0059, listed earlier as a fifth case, is retained at Y because its before-and-after trust rating within one test-drive programme meets the tag definition (the same measure at two or more points in time). Corrected Strand A tag counts of the 205 included studies: measured privacy, data-handling or security concern 145 · subsystem-resolved 87 · longitudinal 13 · measured and longitudinal 2 · measured and subsystem-resolved 78 · all three 0. The decision and the PRISMA counts are unaffected; §2.4 states these counts.
- (b) S2-0754: the byline is Priyanka, Sushama Nagpal and Sangeeta Sabharwal; the Cite-as entry was corrected to Priyanka et al. (2026) on 14 October 2026.
- (c) S2-0163: the cyberattack-concern range recorded at screening (67 to 76%) was corrected to 67 to 75% on 14 October 2026; the paper gives 67% and about 75%. §2.2 and the comparison table carry 67–75%.

### 7.4 Rules and log

Full-text screening followed `full_text_screening_instructions_v1.0_20261005.md`, adopted on 5 October 2026 (editorial change of 10 October: one sentence removed from Part 0 item 3).

On the same date the Full-text Screening Log was corrected and extended, before any full-text decision had been recorded:

- the exclusion-code key was aligned with §2.3, E1 was restored, and the key was moved to the `Codes` tab;
- the decision and exclusion-code dropdowns, previously one column to the left, were moved to the `Decision` and `Exclusion code` columns;
- seven columns were added to the right of `Source`: Version assessed, Date assessed, Sub-reason, Evidence, Tag 1, Tag 2 and Tag 3;
- the tabs `Codes`, `FT rulings` and `FT sessions` were added.

These changes are recorded in Search Log rows 24 and 25.

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

Lee et al. (2026) is logged as one record identified through supervisor recommendation. The study is now published (Social Network Analysis and Mining, online 29 July 2026, doi 10.1007/s13278-026-01633-0) and is cited as such; the version read and screened was the preprint. Its volume and article number are to be added to `biblio.bib` if assigned before submission.

### 8.5 Other relevant references

Works cited in the body of the report that are not among the 367 included studies enter through the other-sources arm without screening and are counted in the dashed box of the figure. Counted at Section 2 drafting on 14 October 2026: **17**, comprising four reviews named in supervisor feedback (FB4) that the searches did not retrieve (Becker & Axhausen, 2017; Golbabaei et al., 2020; Othman, 2021; Lee & Hess, 2022), eight references held before the search (Acquisti et al., 2015; Barth & de Jong, 2017; Kokolakis, 2017; Chen & Tomblin, 2021; Proferes et al., 2021; Ahangar et al., 2021; Yoshizawa et al., 2023; Glancy, 2012) and five methods, model and tool references (§8.6). The list is in `prisma_verification_20261014.md`. Section 1 (14 October) cites only works already in this count. Appendix-only citations are not counted (Nordhoff, 2024, appears in the comparison table only). To be recounted from `biblio.bib` when Sections 3–7 are drafted (11.17).

### 8.6 Methods, model and tool references

Methods, model and tool references enter through the PRISMA other-sources arm rather than the database funnel, under governing document FB2 and §13.4. As at Section 2: five (Lewis et al., 2020; Yin et al., 2019; the `facebook/bart-large-mnli` model card; O'Connor & Joffe, 2020; Krippendorff, 2019), included in the 17 of §8.5.

---

## 9. PRISMA figure: assembly table

| Box | Value | Status | Evidence |
|---|---|---|---|
| Identified, by accepted database | IEEE A 336 · Scopus A 476 · Scopus B-i 1,124 · arXiv B-i 301 · ACM B-ii 118 | VERIFIED | Search Log rows; re-derived 14 Oct |
| Identified, database total | 2,355 | VERIFIED | Search Log |
| Duplicates removed | 163 | VERIFIED | Zotero / frozen corpus |
| Screened at title | 2,192 | VERIFIED | Stage 1 records |
| Excluded at title | 1,008 | VERIFIED | Final title-stage decisions after E8 amendment |
| Carried after title | 1,184 | VERIFIED | Final title-stage decisions after E8 amendment |
| Screened at abstract | 1,184 | VERIFIED | Stage 2 FINAL + E8 addendum; row-level re-derivation 14 Oct |
| Excluded at abstract | 820 | VERIFIED | E2 783 · E1 28 · E3 6 · E6 3; row-level re-derivation 14 Oct |
| Carried from database arm to full text | 364 | VERIFIED | A 209 · B-i 83 · B-ii 72 |
| Backward citations examined | 77 | VERIFIED | Citation audit workbook |
| Backward citations already in corpus | 7 | VERIFIED | Citation audit workbook |
| New backward-citation records | 70 | VERIFIED | Citation audit workbook |
| Backward-citation title exclusions | 27 | VERIFIED | Citation audit workbook |
| Backward-citation abstract exclusions | 5 E2 | VERIFIED | Citation audit workbook |
| Backward-citation records carried to full text | 38 | VERIFIED | 37 INCLUDE · 1 MAYBE |
| Full-text Screening Log population | 403 | VERIFIED | 364 database-derived + 38 backward citation + 1 supervisor recommendation; Screening Log rows |
| Full text not retrievable (E6) | 4 | VERIFIED | Full-text Screening Log |
| Assessed for eligibility | 399 | VERIFIED | 403 − 4 |
| Excluded at full text, with reasons | 32 | VERIFIED | E2 28 (B-i 26 · A 1 · B-ii 1) · E3 2 · E1 1 · E7 1 |
| Included after full text | 367 | VERIFIED | A 205 · B-i 58 · B-ii 104; by source: database 328 · citation searching 38 · supervisor recommendation 1 |
| Other relevant references, not screened (dashed box) | 17 as at Section 2 | VERIFIED against `biblio.bib` and the Section 1–2 text, 14 Oct; recount at submission (11.17) | §8.5 |

**Figure as built (14 October 2026):** `prisma_flow_20261014.pdf` (vector; source `prisma_flow_20261014.tex`, every count set once in its header; `\nOtherCited` = 17). Phases Identification → Screening → Eligibility → Included (PRISMA 2009), a database arm and an other-sources arm merging after deduplication, strands split at Included, and a dashed box for other relevant references cited through the other-sources arm without screening. Combined counts across both arms: identified 2,433 (2,355 + 78) · duplicates removed 170 (163 + 7) · screened 2,263 · excluded at title or abstract 1,860 (title 1,035 = 1,008 + 27; abstract 825 = 820 + 5) · sought 403 · not retrieved 4 · assessed 399 · excluded with reasons 32 · included 367. Every box was re-derived on 14 October 2026 from the row-level records where the rows are held and by arithmetic where they are not (`prisma_verification_20261014.md`). The `PRISMA counts` tab of `included_studies_final_20261010.xlsx` recomputes the same counts from the included-studies list. The 10 October figure (`prisma_flow_20261010.pdf`) is superseded.

Whether title and abstract screening appear as one Screening box or two is decided by the supervisor's template (11.20).

**Publications-per-year chart (FB6), built 14 October 2026:** `publications_per_year.pdf` (vector; data in `pubs_data.json`), from the `Year Histograms` tab of `PRISMA_search_evidence_log.xlsx`: 2015–2025, three strands stacked; Strand A 957 (Scopus 621 after the year filter + IEEE Xplore 336 after all filters), Strand B-i 980 of 1,425, Strand B-ii 90 of 118. What the window omits (436 B-i and 10 B-ii records dated 2026, nine B-i records dated 2027, 18 ACM records dated 1988–2014) is stated in the figure note.

---

## 10. Section 2.1 as written

The draft sentences of versions 0.5 and 0.6 are superseded by the final text of 13 October 2026 (`section2_final_20261013.tex`; figures added in `section2_block_20261014.tex`). The search subsection reads:

> A structured search was used; exhaustive retrieval was not attempted. Strand A covered concern about CAVs bearing on privacy, data or security; Strand B-i, zero-shot or prompted against fine-tuned classifiers on short user-generated text; and Strand B-ii, class-prevalence estimation and prior-shift correction. Searches were run on 20–21 September 2026 in Scopus and IEEE Xplore (A), Scopus and arXiv (B-i) and the ACM Digital Library (B-ii); the as-run strings and filters are in Appendix F. Journal and conference papers, preprints and theses in English were eligible from 2015 (A), 2019 (B-i) and 2000 (B-ii). A single screener assessed titles, abstracts and full texts, recording one exclusion reason per record, the first failed check in a fixed order; a blind re-screen of 50 abstracts agreed on 47 (94%).

> Figure 1 reports the flow: database searches identified 2,355 records and other sources 78, namely 77 references from backward citation searching of González et al. (2017) and one supervisor-recommended study (Lee et al., 2026). After 170 duplicates were removed, 2,263 records were screened and 1,860 excluded; of 403 full texts sought, four were not retrieved, and 32 of the 399 assessed were excluded, 28 for failing the strand test, leaving 367 included studies (A 205, B-i 58, B-ii 104).

> Other relevant references enter through the other-sources arm; Appendix G compares the studies closest to the gap.

Appendix F (`appendixF_search_20261014.tex`) carries the five as-run strings with dates, filters and counts, the strand tests of §2.4 with the B-i criterion quoted as locked, and the exclusion codes of §2.3.

---

## 11. Status and open items

### Closed items

- [x] **11.1 The three theses.** Closed 4 October 2026. All three were re-screened under the E8 amendment, carried through title and abstract screening as B-ii INCLUDE records, added to the Stage 2 file and Zotero collections, and entered into the Full-text Screening Log.
- [x] **11.2 S2-0211.** Closed. Strand A INCLUDE.
- [x] **11.3 Calibration adjudications.** Original calibration adjudication completed. The optional 118-record catch-all check was offered and not run. S2-0307 was subsequently corrected separately on 4 October 2026.
- [x] **11.4 Two-item export gap.** Closed 26 September 2026. Two real records were omitted from one RIS export; PRISMA counts were unaffected.
- [x] **11.5 B-ii Scopus rationale.** Closed 26 September 2026. The malformed Scopus title was identified and the search was not reopened.
- [x] **11.6 Other-sources search arm.** Backward citation audit completed; forward citation searching and ACL fallback decisions recorded; supervisor recommendation logged; other relevant references counted at Section 2 (§8.5).
- [x] **11.7 Full-text stage.** Closed 10 October 2026. 403 sought, 4 not retrieved, 399 assessed, 32 excluded with reasons, 367 included (§7.3). The D9 consistency check was not recorded.
- [x] **11.8 Publications-per-year chart.** Closed 14 October 2026: `publications_per_year.pdf` built from the `Year Histograms` tab (§9).
- [x] **11.10 IEEE Xplore correction.** Dated correction added to the Search Log and corresponding evidence-workbook notes updated.
- [x] **11.11 Log consistency.** Evidence-workbook Stage 2 pointer, B-i 1,117/1,124 correction, B-ii 2,120/2,131 labels, disk filenames, search-phase evidence provenance line and FB2 other-sources routing correction completed.
- [x] **11.12 S2-0307.** Closed 4 October 2026. Corrected from EXCLUDE E2 to INCLUDE, moved in Zotero, added to the Full-text Screening Log and reflected in PRISMA counts.
- [x] **11.13 Full-text workload.** Closed 5 October 2026. Workflow decisions D1–D10 and rulings R1–R12 were adopted as recommended and are recorded in `full_text_screening_instructions_v1.0_20261005.md`.
- [x] **11.15(c) Generic notes and unexplained exclusions.** Closed 14 October 2026: in the file of record every one of the 820 Stage 2 exclusions carries a code and a note; wording corrected in §6.4.
- [x] **11.16 PRISMA figure.** Closed 14 October 2026: `prisma_flow_20261014.pdf` replaces the 10 October figure; counts unchanged; dashed box filled (§9).
- [x] **11.18 Longitudinal-tag corrections.** Closed 14 October 2026: four corrections adopted (S2-0142, S2-0186, S2-0231, S2-0254), S2-0059 retained; recorded by dated note in the reading-notes workbook (§7.3).
- [x] **11.19 IEEE Xplore Strand A confirmation re-run.** Closed 17 October 2026: the three IEEE Xplore block strings were recovered from the session record of 20 September 2026 and confirmed by re-run (84,356 / 13,610 / 452 / 410 / 337); recorded verbatim in Appendix F of the report and in the Search Evidence tab of PRISMA_search_evidence_log.xlsx (§3.1). Commit `adf5354`.

### Repository commits

- [x] **11.9 Commit.** Closed 4 October 2026. Main literature-search commit: `fe69005` (`Literature search: citation arm, E8 addendum and log corrections`). The commit hash is recorded in the Search Log.
- [x] **IEEE re-run commit.** `adf5354` (`docs: confirm IEEE Strand A search re-run`), 17 October 2026: evidence workbook, re-run screenshot and manifest 11.19.

### Remaining work

- [ ] **11.14 S2-1182 DOI field.** In the Stage 2 file of record (sheet `E8 addendum`, cell H2) the DOI recorded is that of the arXiv e-print of the thesis, not of the dissertation, which has none. Clear it by dated correction before submission; the full-text stage has since closed, so the original deadline ("before the first full-text decision") has passed.
- [ ] **11.15(a)–(b) Record corrections.** (a) The counts and export file recorded for the superseded B-ii Scopus search (§3.2; Search Log row 8). (b) The wording on what the known-item tests showed (§3.2, §3.3, §8.3; Search Log row 10). Details and proposed wording: `literature_search_corrections_20261005.md`. Neither changes a PRISMA count. Status at 17 October 2026: not recorded as done.
- [ ] **11.17 Other-sources count at submission.** 17 as at Section 2 (§8.5); recount from `biblio.bib` when Sections 3–7 are drafted, update `\nOtherCited` in `prisma_flow_20261014.tex` and recompile. Report-body citations only.
- [ ] **11.20 Template version.** Confirm with the supervisor whether her template follows the 2009 single flow or the 2020 two-column layout (§1). If 2020, redraw with two columns; counts unchanged.

---

## Change log

| Version | Date | Commit | Change |
|---|---|---|---|
| 0.1 | 27 Sep 2026 | *record on commit* | Created from the working literature-search record. |
| 0.2 | 27 Sep 2026 | *record on commit* | Reconciled against both evidence logs; the two-item export gap and B-ii Scopus rationale were closed; IEEE known-item and log-consistency issues were recorded; the B-ii Scopus variant chain was reconciled. |
| 0.3 | 2 Oct 2026 | *record on commit* | Updated from the 2 October status handover: Stage 2 figures, Zotero reconciliation and calibration results recorded; backward-citation audit added; outstanding correction and filing items documented. |
| 0.4 | 4 Oct 2026 | fe69005 | Applied the E8 thesis amendment to the three affected records; completed backward-citation screening; recorded decisions not to run forward citation searching or the ACL fallback; corrected S2-0307 to INCLUDE; reconciled Stage 2 and full-text counts; completed IEEE and search-log corrections; recorded the optional 118-record check as offered and not run. |
| 0.5 | 5 Oct 2026 | *record on commit* | Recorded the full-text workflow decisions and rulings (11.13 closed); aligned the exclusion-code wording in §2.3 with the Full-text Screening Log; recorded the corrected and extended log (§7.4); opened 11.14 and 11.15. |
| 0.6 | 10 Oct 2026 | not committed; merged into 0.7 | Recorded the completed full-text stage (§7, 11.7 closed), the final PRISMA counts and the 10 October figure (§9, 11.16), and the §2.0 full-text sentences (§10); opened 11.17 and 11.18; 11.8 narrowed to the publications-per-year chart. |
| 0.7 | 17 Oct 2026 | *record on commit* | Counts re-derived from the files of record (14 Oct); four Longitudinal-tag corrections, the S2-0163 and S2-0754 corrections and the Calibration-tab freeze recorded; D5 notes; other relevant references counted (17 at Section 2); PRISMA figure and publications-per-year chart as built on 14 Oct; Lee et al. (2026) recorded as published; §10 replaced by the final §2.1 text; IEEE Xplore strings recovered and confirmed (17 Oct); 11.8, 11.15(c), 11.16, 11.18 and 11.19 closed; 11.20 opened; 11.14, 11.15(a)–(b) and 11.17 remain open. |
