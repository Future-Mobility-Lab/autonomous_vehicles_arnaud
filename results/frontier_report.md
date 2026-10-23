# Exploratory runs of Claude Opus 5.5 and Claude Fable 5.1

Deviation 15 of `docs/analysis_preregistration.md`; `analysis_06_frontier.py`. Every figure here is exploratory: these rules were fixed after every result of record had been seen (Deviation 15), so no figure here can confirm a result. Each is reported beside the figure of record it parallels, whatever its value. Shares are corrected by adjusted classify-and-count with each model's own rates and clipped to [0, 1] for display; slopes are in percentage points per year, on the values before clipping.

## 1. The runs; exploratory (Deviation 15)

| Run | Model | Prompt | Status | Comments | Calls | With a label | Refusals or unclassified (reasons) | Refusal categories |
|---|---|---|---|---|---|---|---|---|
| opus-eval-universal | Claude Opus 5.5 | universal | complete | 598 | 598 | 598 | 0 | none |
| opus-eval-domain | Claude Opus 5.5 | domain-specific | complete | 598 | 598 | 598 | 0 | none |
| opus-eval-subsystem | Claude Opus 5.5 | subsystem | complete | 598 | 599 | 598 | 0 | none |
| fable-eval-universal | Claude Fable 5.1 | universal | complete | 598 | 599 | 598 | 0 | none |
| fable-eval-domain | Claude Fable 5.1 | domain-specific | complete | 598 | 598 | 598 | 0 | none |
| fable-eval-subsystem | Claude Fable 5.1 | subsystem | complete | 598 | 609 | 590 | 8 (no_label 8) | none |
| opus-corpus-stage2 | Claude Opus 5.5 | domain-specific | complete | 6,503 | 6,503 | 6,503 | 0 | none |
| opus-corpus-subsystem | Claude Opus 5.5 | subsystem | complete | 6,503 | 6,507 | 6,503 | 0 | none |
| fable-corpus-stage2 | Claude Fable 5.1 | domain-specific | complete | 6,503 | 6,503 | 6,503 | 0 | none |
| fable-corpus-subsystem | Claude Fable 5.1 | subsystem | complete | 6,503 | 6,673 | 6,430 | 73 (no_label 72, refusal_stop 1) | cyber 1 |

- Inference regions reported by the answers of the complete runs: global 29,786, not_available 1 (the prices of Deviation 15 hold for global routing).

## 2. Stage 2 on the 598 evaluation items; exploratory (Deviation 15)

### Universal schema

| Classifier | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | No class | TPR (weighted) | FPR (weighted) | TPR - FPR (weighted) | TPR (unweighted) | FPR (unweighted) |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 (universal), of record | 0.6558 | 0.7417 | 0.6934 | 0.5324 | 0 | 0.9291 | 0.3717 | 0.5573 | 0.9378 | 0.3566 |
| Claude Opus 5.5 | 0.7070 | 0.7893 | 0.7582 | 0.5735 | 0 | 0.9743 | 0.3209 | 0.6534 | 0.9822 | 0.3056 |
| Claude Fable 5.1 | 0.7149 | 0.7774 | 0.7514 | 0.6159 | 0 | 0.9393 | 0.3153 | 0.6240 | 0.9467 | 0.2949 |


Three-class rates M_ij, universal schema (weighted; rows: gold class; columns: classified, a refusal counted as OTHER):

| Classifier | Gold | CONCERN | ENDORSEMENT | OTHER |
|---|---|---|---|---|
| Claude Opus 5.5 | CONCERN | 0.9743 | 0.0193 | 0.0064 |
| Claude Opus 5.5 | ENDORSEMENT | 0.2344 | 0.7206 | 0.0449 |
| Claude Opus 5.5 | OTHER | 0.4109 | 0.1860 | 0.4031 |
| Claude Fable 5.1 | CONCERN | 0.9393 | 0.0257 | 0.0349 |
| Claude Fable 5.1 | ENDORSEMENT | 0.2392 | 0.6725 | 0.0884 |
| Claude Fable 5.1 | OTHER | 0.3946 | 0.1278 | 0.4775 |

No M_ij of record: the sample analyses give M_ij for the deployed configuration only.

### Domain-specific schema

| Classifier | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | No class | TPR (weighted) | FPR (weighted) | TPR - FPR (weighted) | TPR (unweighted) | FPR (unweighted) |
|---|---|---|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 (domain-specific), of record | 0.7501 | 0.8145 | 0.7630 | 0.6728 | 0 | 0.9469 | 0.2376 | 0.7093 | 0.9467 | 0.2279 |
| Claude Opus 5.5 | 0.8407 | 0.8777 | 0.8513 | 0.7931 | 0 | 0.8775 | 0.0942 | 0.7833 | 0.8933 | 0.0858 |
| Claude Fable 5.1 | 0.8294 | 0.8628 | 0.8421 | 0.7833 | 0 | 0.8516 | 0.0949 | 0.7567 | 0.8667 | 0.0858 |


Three-class rates M_ij, domain-specific schema (weighted; rows: gold class; columns: classified, a refusal counted as OTHER):

| Classifier | Gold | CONCERN | ENDORSEMENT | OTHER |
|---|---|---|---|---|
| Claude Sonnet 4.6 (domain-specific), of record | CONCERN | 0.9469 | 0.0219 | 0.0311 |
| Claude Sonnet 4.6 (domain-specific), of record | ENDORSEMENT | 0.1770 | 0.6958 | 0.1272 |
| Claude Sonnet 4.6 (domain-specific), of record | OTHER | 0.3008 | 0.1117 | 0.5875 |
| Claude Opus 5.5 | CONCERN | 0.8775 | 0.0670 | 0.0555 |
| Claude Opus 5.5 | ENDORSEMENT | 0.0543 | 0.8731 | 0.0726 |
| Claude Opus 5.5 | OTHER | 0.1358 | 0.1263 | 0.7379 |
| Claude Fable 5.1 | CONCERN | 0.8516 | 0.0425 | 0.1059 |
| Claude Fable 5.1 | ENDORSEMENT | 0.0543 | 0.8138 | 0.1319 |
| Claude Fable 5.1 | OTHER | 0.1373 | 0.0647 | 0.7980 |

## 3. Subsystem classifier against the gold primary subsystems; exploratory (Deviation 15)

| Classifier | Items | Overall agreement, both tranches | Without the adjudicated items |
|---|---|---|---|
| Claude Sonnet 4.6, of record | 596 | 502/596 (84.2%; Wilson 81.1% to 86.9%) | 501/593 (84.5%; Wilson 81.4% to 87.2%) |
| Claude Opus 5.5 | 596 | 533/596 (89.4%; Wilson 86.7% to 91.7%) | 533/593 (89.9%; Wilson 87.2% to 92.1%) |
| Claude Fable 5.1 | 596 | 528/596 (88.6%; Wilson 85.8% to 90.9%) | 528/593 (89.0%; Wilson 86.3% to 91.3%) |


Per value, both tranches (of the items with a gold value, the share given it; of the items given a value, the share whose gold value it is):

| Value | Claude Sonnet 4.6, of record: given its gold value | Claude Sonnet 4.6, of record: right when given | Claude Opus 5.5: given its gold value | Claude Opus 5.5: right when given | Claude Fable 5.1: given its gold value | Claude Fable 5.1: right when given |
|---|---|---|---|---|---|---|
| sensing | 114/142 (80.3%) | 114/132 (86.4%) | 124/142 (87.3%) | 124/134 (92.5%) | 124/142 (87.3%) | 124/132 (93.9%) |
| in_vehicle_networks | 11/32 (34.4%) | 11/12 (91.7%) | 14/32 (43.8%) | 14/16 (87.5%) | 13/32 (40.6%) | 13/13 (100.0%) |
| v2x | 8/24 (33.3%) | 8/10 (80.0%) | 20/24 (83.3%) | 20/22 (90.9%) | 14/24 (58.3%) | 14/15 (93.3%) |
| cybersecurity | 1/2 (50.0%) | 1/4 (25.0%) | 1/2 (50.0%) | 1/3 (33.3%) | 1/2 (50.0%) | 1/2 (50.0%) |
| privacy | 7/10 (70.0%) | 7/13 (53.8%) | 6/10 (60.0%) | 6/8 (75.0%) | 6/10 (60.0%) | 6/6 (100.0%) |
| data_governance | 4/10 (40.0%) | 4/11 (36.4%) | 3/10 (30.0%) | 3/4 (75.0%) | 3/10 (30.0%) | 3/3 (100.0%) |
| none | 357/376 (94.9%) | 357/414 (86.2%) | 365/376 (97.1%) | 365/409 (89.2%) | 367/376 (97.6%) | 367/417 (88.0%) |

## 4. Comparisons on macro-F1; exploratory (Deviation 15): one family of their own, Holm-Bonferroni at 0.05

| Schema | a | b | Difference (a - b) | p | Holm-adjusted p | Result |
|---|---|---|---|---|---|---|
| universal | Claude Opus 5.5 | Claude Sonnet 4.6 (universal) | 0.0512 | 0.0022 | 0.0066 | significant |
| universal | Claude Fable 5.1 | Claude Sonnet 4.6 (universal) | 0.0591 | 0.0001 | 0.0008 | significant |
| universal | Claude Opus 5.5 | RoBERTa | 0.1843 | 0.0001 | 0.0008 | significant |
| universal | Claude Fable 5.1 | RoBERTa | 0.1922 | 0.0001 | 0.0008 | significant |
| universal | Claude Opus 5.5 | Claude Fable 5.1 | -0.0079 | 0.5711 | 0.6790 | not demonstrably significant |
| domain-specific | Claude Opus 5.5 | Claude Sonnet 4.6 (domain-specific) | 0.0906 | 0.0001 | 0.0008 | significant |
| domain-specific | Claude Fable 5.1 | Claude Sonnet 4.6 (domain-specific) | 0.0793 | 0.0001 | 0.0008 | significant |
| domain-specific | Claude Opus 5.5 | Claude Fable 5.1 | 0.0113 | 0.3395 | 0.6790 | not demonstrably significant |

- Comparison of record, universal schema (Family B): RoBERTa against Claude Sonnet 4.6 (universal), difference -0.1331, p = 0.0001, Holm-adjusted p = 0.0010 (significant).
- Comparison of record, domain-specific schema (Family C): RoBERTa against Claude Sonnet 4.6 (domain-specific), difference -0.2274, p = 0.0001.

## 5a. Corpus runs of Claude Opus 5.5; exploratory (Deviation 15)

Agreement with the evaluation run on the tranche items both cover: Stage 2 (domain-specific schema) 553/571 (96.8%) the same label (of record, Claude Sonnet 4.6: 567/571 (99.3%)); subsystem 561/571 (98.2%) (no figure of record).

| Evaluation run \ corpus run | CONCERN | ENDORSEMENT | OTHER | refusal |
|---|---|---|---|---|
| CONCERN | 223 | 0 | 1 | 0 |
| ENDORSEMENT | 1 | 186 | 6 | 0 |
| OTHER | 6 | 4 | 144 | 0 |
| refusal | 0 | 0 | 0 | 0 |

Error rates (the model's, from its domain-specific evaluation run; beside them those of record):

| Rate | Model | Of record |
|---|---|---|
| TPR | 0.8775 | 0.9469 |
| FPR | 0.0942 | 0.2376 |
| TPR - FPR | 0.7833 | 0.7093 |
| TPR, early block | 0.9284 | 0.9539 |
| FPR, early block | 0.0660 | 0.2029 |
| TPR, late block | 0.8353 | 0.9412 |
| FPR, late block | 0.1194 | 0.2687 |

| Series | Sen's slope | Gilbert 95% interval | MK p | Significant | Of record: Sen's slope | Gilbert 95% interval | MK p | Significant |
|---|---|---|---|---|---|---|---|---|
| Primary | +1.66 | +0.33 to +2.65 | 0.0062 | yes | +1.38 | -0.10 to +3.03 | 0.0701 | no |
| Block-specific (the model's block rates) | +1.63 | +0.45 to +2.68 | 0.0052 | yes | +0.54 | -0.75 to +2.12 | 0.4375 | no |
| Companion | +0.82 | -0.75 to +2.06 | 0.3335 | no | +0.53 | -1.25 to +2.10 | 0.4873 | no |
| Pooled | +1.71 | +0.59 to +2.78 | 0.0073 | yes | +1.21 | -0.06 to +2.81 | 0.0548 | no |
| Tier-level | +1.71 | +0.49 to +2.89 | 0.0090 | yes | +1.63 | +0.03 to +3.03 | 0.0437 | yes |
| Three-class correction, CONCERN | +1.72 | +0.37 to +2.79 | 0.0127 | yes | +1.31 | -0.17 to +2.94 | 0.0886 | no |
| Word floor 25 | +1.74 | +0.35 to +2.84 | 0.0079 | yes | +1.72 | +0.27 to +3.12 | 0.0246 | yes |
| Tier 1 | +1.78 | +0.02 to +3.53 | 0.0467 | yes | +1.21 | -0.88 to +3.18 | 0.2328 | no |
| Tier 2 | +1.54 | +0.09 to +3.22 | 0.0410 | yes | +1.70 | +0.17 to +3.58 | 0.0410 | yes |

Primary series by quarter:

| Quarter | Classified | Corrected | 95% interval | Of record: corrected | 95% interval |
|---|---|---|---|---|---|
| 2016 Q1 | 30.2% | 26.6% | 19.7% to 36.2% | 21.0% | 5.3% to 39.5% |
| 2016 Q2 | 30.1% | 26.4% | 12.4% to 41.3% | 37.5% | 19.7% to 51.3% |
| 2016 Q3 | 39.3% | 38.2% | 17.0% to 58.1% | 51.6% | 29.8% to 68.8% |
| 2016 Q4 | 24.1% | 18.7% | 7.0% to 30.3% | 15.3% | 0.0% to 29.4% |
| 2017 Q1 | 23.5% | 18.0% | 4.9% to 31.6% | 19.8% | 7.6% to 32.7% |
| 2017 Q2 | 28.8% | 24.7% | 11.6% to 39.2% | 36.8% | 20.5% to 51.0% |
| 2017 Q3 | 40.7% | 40.0% | 11.7% to 62.7% | 39.2% | 4.7% to 66.5% |
| 2017 Q4 | 35.4% | 33.1% | 15.0% to 48.7% | 42.0% | 16.8% to 64.1% |
| 2018 Q1 | 42.2% | 41.9% | 28.3% to 54.8% | 42.4% | 28.1% to 55.6% |
| 2018 Q2 | 51.9% | 54.2% | 37.7% to 72.4% | 63.7% | 45.2% to 79.3% |
| 2018 Q3 | 46.0% | 46.7% | 13.7% to 71.4% | 24.5% | 3.2% to 37.4% |
| 2018 Q4 | 38.3% | 36.8% | 22.6% to 53.9% | 30.7% | 14.3% to 48.7% |
| 2019 Q1 | 40.3% | 39.4% | 18.3% to 60.2% | 33.5% | 18.0% to 48.9% |
| 2019 Q2 | 42.4% | 42.1% | 30.8% to 53.1% | 37.8% | 26.4% to 48.4% |
| 2019 Q3 | 32.2% | 29.1% | 8.9% to 46.0% | 22.2% | 0.0% to 41.9% |
| 2019 Q4 | 32.6% | 29.6% | 19.4% to 40.1% | 31.3% | 17.7% to 44.0% |
| 2020 Q1 | 22.5% | 16.7% | 4.5% to 30.0% | 25.5% | 6.5% to 44.7% |
| 2020 Q2 | 40.7% | 40.0% | 23.9% to 57.2% | 41.5% | 26.4% to 58.5% |
| 2020 Q3 | 35.1% | 32.8% | 12.4% to 51.8% | 21.6% | 0.0% to 45.0% |
| 2020 Q4 | 34.8% | 32.4% | 23.0% to 42.3% | 32.7% | 20.1% to 44.9% |
| 2021 Q1 | 35.5% | 33.2% | 16.3% to 50.0% | 37.9% | 19.8% to 55.0% |
| 2021 Q2 | 35.6% | 33.5% | 21.4% to 44.3% | 37.1% | 19.5% to 51.4% |
| 2021 Q3 | 37.2% | 35.4% | 21.3% to 50.1% | 41.3% | 24.4% to 56.3% |
| 2021 Q4 | 40.5% | 39.7% | 26.8% to 52.1% | 36.1% | 20.9% to 49.9% |
| 2022 Q1 | 41.0% | 40.3% | 26.3% to 57.3% | 36.5% | 19.8% to 53.5% |
| 2022 Q2 | 48.0% | 49.3% | 34.3% to 63.9% | 57.3% | 43.5% to 70.4% |
| 2022 Q3 | 41.9% | 41.5% | 21.8% to 59.8% | 35.6% | 12.6% to 55.9% |
| 2022 Q4 | 45.6% | 46.2% | 33.6% to 58.7% | 45.0% | 31.3% to 57.6% |
| 2023 Q1 | 35.7% | 33.5% | 20.7% to 48.1% | 28.4% | 6.2% to 51.6% |
| 2023 Q2 | 47.2% | 48.2% | 33.4% to 61.9% | 40.3% | 26.6% to 53.4% |
| 2023 Q3 | 41.3% | 40.7% | 26.4% to 54.5% | 42.6% | 25.0% to 58.6% |
| 2023 Q4 | 43.3% | 43.3% | 31.1% to 55.6% | 52.1% | 38.4% to 65.6% |
| 2024 Q1 | 20.4% | 14.0% | 0.0% to 31.6% | 21.9% | 5.7% to 41.7% |
| 2024 Q2 | 41.2% | 40.6% | 29.7% to 51.6% | 47.1% | 35.7% to 58.7% |
| 2024 Q3 | 47.6% | 48.7% | 31.6% to 65.8% | 52.6% | 37.0% to 69.0% |
| 2024 Q4 | 41.7% | 41.2% | 34.0% to 48.5% | 36.8% | 28.6% to 44.5% |

RQ2: concern share C over 2016-2024 (corrected) 38.0%; of record 38.7%.

| Value | Reported as | pi_s 2016-2024 | C_s | E_s | Of record: reported as | pi_s | C_s | E_s |
|---|---|---|---|---|---|---|---|---|
| sensing | annual | 22.3% | 43.3% | 1.1383 | annual | 24.9% | 47.7% | 1.2313 |
| none | quarterly | 70.4% | 36.7% | 0.9647 | quarterly | 69.7% | 36.5% | 0.9414 |

Test of sensing (Family A's test, a family of one): Sen's slope -0.10 points per year (Gilbert -0.65 to +0.51), p = 0.9195; of record: Sen's slope -0.41, p = 0.7614, Holm-adjusted 0.7614.

| Value | Classified relevant, 2016-2024 | Median quarterly | Median annual | Of record: classified relevant | Median quarterly | Median annual |
|---|---|---|---|---|---|---|
| sensing | 1,118 | 27 | 125 | 1,132 | 27.5 | 122 |
| in_vehicle_networks | 98 | 2 | 10 | 55 | 1 | 5 |
| v2x | 175 | 4 | 16 | 97 | 2 | 10 |
| cybersecurity | 25 | 0 | 2 | 20 | 0 | 2 |
| privacy | 51 | 1 | 4 | 63 | 1 | 7 |
| data_governance | 64 | 1 | 7 | 97 | 2 | 12 |
| none | 4,033 | 94.5 | 461 | 4,099 | 98 | 468 |
| unclassified | 0 | 0 | 0 | 1 | 0 | 0 |

Not computed: changepoints, STL, the GLM, R4 (thread size), the half-year and year series, the seasonality analyses, the relevance-error series, Hamed-Rao and R3's criteria are not computed for these models (Deviation 15).

## 5b. Corpus runs of Claude Fable 5.1; exploratory (Deviation 15)

Agreement with the evaluation run on the tranche items both cover: Stage 2 (domain-specific schema) 554/571 (97.0%) the same label (of record, Claude Sonnet 4.6: 567/571 (99.3%)); subsystem 555/571 (97.2%) (no figure of record).

| Evaluation run \ corpus run | CONCERN | ENDORSEMENT | OTHER | refusal |
|---|---|---|---|---|
| CONCERN | 214 | 1 | 4 | 0 |
| ENDORSEMENT | 1 | 161 | 5 | 0 |
| OTHER | 2 | 4 | 179 | 0 |
| refusal | 0 | 0 | 0 | 0 |

Error rates (the model's, from its domain-specific evaluation run; beside them those of record):

| Rate | Model | Of record |
|---|---|---|
| TPR | 0.8516 | 0.9469 |
| FPR | 0.0949 | 0.2376 |
| TPR - FPR | 0.7567 | 0.7093 |
| TPR, early block | 0.8997 | 0.9539 |
| FPR, early block | 0.0675 | 0.2029 |
| TPR, late block | 0.8118 | 0.9412 |
| FPR, late block | 0.1194 | 0.2687 |

| Series | Sen's slope | Gilbert 95% interval | MK p | Significant | Of record: Sen's slope | Gilbert 95% interval | MK p | Significant |
|---|---|---|---|---|---|---|---|---|
| Primary | +2.21 | +1.12 to +3.22 | 0.0008 | yes | +1.38 | -0.10 to +3.03 | 0.0701 | no |
| Block-specific (the model's block rates) | +2.23 | +1.19 to +3.30 | 0.0007 | yes | +0.54 | -0.75 to +2.12 | 0.4375 | no |
| Companion | +1.39 | -0.02 to +2.44 | 0.0514 | no | +0.53 | -1.25 to +2.10 | 0.4873 | no |
| Pooled | +2.36 | +0.98 to +3.23 | 0.0020 | yes | +1.21 | -0.06 to +2.81 | 0.0548 | no |
| Tier-level | +2.43 | +1.16 to +3.49 | 0.0005 | yes | +1.63 | +0.03 to +3.03 | 0.0437 | yes |
| Three-class correction, CONCERN | +2.32 | +1.21 to +3.40 | 0.0007 | yes | +1.31 | -0.17 to +2.94 | 0.0886 | no |
| Word floor 25 | +2.34 | +1.27 to +3.47 | 0.0011 | yes | +1.72 | +0.27 to +3.12 | 0.0246 | yes |
| Tier 1 | +2.37 | +0.62 to +4.12 | 0.0119 | yes | +1.21 | -0.88 to +3.18 | 0.2328 | no |
| Tier 2 | +2.31 | +0.88 to +3.44 | 0.0035 | yes | +1.70 | +0.17 to +3.58 | 0.0410 | yes |

Primary series by quarter:

| Quarter | Classified | Corrected | 95% interval | Of record: corrected | 95% interval |
|---|---|---|---|---|---|
| 2016 Q1 | 26.1% | 22.0% | 8.7% to 34.8% | 21.0% | 5.3% to 39.5% |
| 2016 Q2 | 32.8% | 30.8% | 11.2% to 46.2% | 37.5% | 19.7% to 51.3% |
| 2016 Q3 | 38.4% | 38.2% | 17.2% to 58.1% | 51.6% | 29.8% to 68.8% |
| 2016 Q4 | 22.7% | 17.5% | 5.5% to 29.4% | 15.3% | 0.0% to 29.4% |
| 2017 Q1 | 28.2% | 24.7% | 12.0% to 38.2% | 19.8% | 7.6% to 32.7% |
| 2017 Q2 | 29.7% | 26.7% | 14.9% to 40.0% | 36.8% | 20.5% to 51.0% |
| 2017 Q3 | 39.4% | 39.5% | 19.0% to 56.9% | 39.2% | 4.7% to 66.5% |
| 2017 Q4 | 35.1% | 33.8% | 15.5% to 49.7% | 42.0% | 16.8% to 64.1% |
| 2018 Q1 | 40.6% | 41.1% | 28.8% to 53.4% | 42.4% | 28.1% to 55.6% |
| 2018 Q2 | 51.3% | 55.2% | 35.2% to 75.8% | 63.7% | 45.2% to 79.3% |
| 2018 Q3 | 45.5% | 47.6% | 19.4% to 66.2% | 24.5% | 3.2% to 37.4% |
| 2018 Q4 | 36.3% | 35.5% | 21.1% to 53.4% | 30.7% | 14.3% to 48.7% |
| 2019 Q1 | 35.7% | 34.7% | 15.5% to 54.9% | 33.5% | 18.0% to 48.9% |
| 2019 Q2 | 38.9% | 38.9% | 27.7% to 49.1% | 37.8% | 26.4% to 48.4% |
| 2019 Q3 | 30.2% | 27.4% | 5.1% to 45.8% | 22.2% | 0.0% to 41.9% |
| 2019 Q4 | 32.1% | 29.8% | 17.9% to 42.2% | 31.3% | 17.7% to 44.0% |
| 2020 Q1 | 24.5% | 19.8% | 7.1% to 33.9% | 25.5% | 6.5% to 44.7% |
| 2020 Q2 | 43.9% | 45.5% | 28.3% to 63.7% | 41.5% | 26.4% to 58.5% |
| 2020 Q3 | 33.5% | 31.7% | 10.7% to 50.5% | 21.6% | 0.0% to 45.0% |
| 2020 Q4 | 35.5% | 34.3% | 24.6% to 45.4% | 32.7% | 20.1% to 44.9% |
| 2021 Q1 | 34.8% | 33.5% | 15.0% to 50.8% | 37.9% | 19.8% to 55.0% |
| 2021 Q2 | 37.2% | 36.6% | 23.7% to 47.9% | 37.1% | 19.5% to 51.4% |
| 2021 Q3 | 37.1% | 36.5% | 22.4% to 51.8% | 41.3% | 24.4% to 56.3% |
| 2021 Q4 | 42.4% | 43.5% | 30.1% to 56.6% | 36.1% | 20.9% to 49.9% |
| 2022 Q1 | 40.4% | 40.8% | 27.1% to 57.3% | 36.5% | 19.8% to 53.5% |
| 2022 Q2 | 46.3% | 48.7% | 32.9% to 63.5% | 57.3% | 43.5% to 70.4% |
| 2022 Q3 | 46.8% | 49.2% | 29.1% to 65.7% | 35.6% | 12.6% to 55.9% |
| 2022 Q4 | 46.6% | 49.0% | 36.2% to 62.5% | 45.0% | 31.3% to 57.6% |
| 2023 Q1 | 39.5% | 39.7% | 25.5% to 54.7% | 28.4% | 6.2% to 51.6% |
| 2023 Q2 | 46.4% | 48.7% | 33.8% to 62.6% | 40.3% | 26.6% to 53.4% |
| 2023 Q3 | 46.1% | 48.3% | 34.2% to 62.9% | 42.6% | 25.0% to 58.6% |
| 2023 Q4 | 49.4% | 52.7% | 38.7% to 67.6% | 52.1% | 38.4% to 65.6% |
| 2024 Q1 | 23.4% | 18.3% | 2.5% to 38.9% | 21.9% | 5.7% to 41.7% |
| 2024 Q2 | 42.2% | 43.3% | 31.4% to 54.8% | 47.1% | 35.7% to 58.7% |
| 2024 Q3 | 48.5% | 51.5% | 37.1% to 66.5% | 52.6% | 37.0% to 69.0% |
| 2024 Q4 | 41.1% | 41.7% | 34.2% to 49.6% | 36.8% | 28.6% to 44.5% |

RQ2: concern share C over 2016-2024 (corrected) 39.7%; of record 38.7%.

| Value | Reported as | pi_s 2016-2024 | C_s | E_s | Of record: reported as | pi_s | C_s | E_s |
|---|---|---|---|---|---|---|---|---|
| sensing | annual | 20.8% | 43.8% | 1.1039 | annual | 24.9% | 47.7% | 1.2313 |
| none | quarterly | 71.8% | 38.7% | 0.9753 | quarterly | 69.7% | 36.5% | 0.9414 |

Test of sensing (Family A's test, a family of one): Sen's slope -0.15 points per year (Gilbert -1.21 to +0.32), p = 0.7614; of record: Sen's slope -0.41, p = 0.7614, Holm-adjusted 0.7614.

| Value | Classified relevant, 2016-2024 | Median quarterly | Median annual | Of record: classified relevant | Median quarterly | Median annual |
|---|---|---|---|---|---|---|
| sensing | 1,080 | 26.5 | 124 | 1,132 | 27.5 | 122 |
| in_vehicle_networks | 71 | 1 | 6 | 55 | 1 | 5 |
| v2x | 151 | 3 | 15 | 97 | 2 | 10 |
| cybersecurity | 13 | 0 | 1 | 20 | 0 | 2 |
| privacy | 59 | 1 | 6 | 63 | 1 | 7 |
| data_governance | 52 | 1 | 4 | 97 | 2 | 12 |
| none | 4,070 | 93.5 | 453 | 4,099 | 98 | 468 |
| unclassified | 68 | 2 | 9 | 1 | 0 | 0 |

Not computed: changepoints, STL, the GLM, R4 (thread size), the half-year and year series, the seasonality analyses, the relevance-error series, Hamed-Rao and R3's criteria are not computed for these models (Deviation 15).

## 6. Cost per 1,000 comments; exploratory (Deviation 15)

| Run | Comments | Calls | Tokens in | Tokens out | Of which thinking | Cost (US$, batch prices) | Per 1,000, batch | Per 1,000, standard | Thinking, per 1,000 (batch) | Of record, per 1,000 (single requests) |
|---|---|---|---|---|---|---|---|---|---|---|
| opus-eval-universal | 598 | 598 | 130,003 | 16,699 | 8,167 | 0.4270 | 0.7140 | 1.4281 | 0.1366 | 0.6047 |
| opus-eval-domain | 598 | 598 | 155,119 | 32,334 | 15,558 | 0.6336 | 1.0595 | 2.1190 | 0.2602 | 0.7995 |
| opus-eval-subsystem | 598 | 599 | 424,904 | 13,942 | 11,597 | 0.9892 | 1.6542 | 3.3085 | 0.1939 | none |
| fable-eval-universal | 598 | 599 | 130,249 | 9,995 | 0 | 0.9011 | 1.5069 | 3.0138 | 0.0000 | 0.6047 |
| fable-eval-domain | 598 | 598 | 155,119 | 18,664 | 95 | 1.2422 | 2.0772 | 4.1545 | 0.0040 | 0.7995 |
| fable-eval-subsystem | 598 | 609 | 433,011 | 6,233 | 0 | 2.3209 | 3.8811 | 7.7621 | 0.0000 | none |
| opus-corpus-stage2 | 6,503 | 6,503 | 1,738,148 | 357,358 | 175,036 | 7.0499 | 1.0841 | 2.1682 | 0.2692 | 0.8344 |
| opus-corpus-subsystem | 6,503 | 6,507 | 4,667,835 | 146,927 | 122,511 | 10.8049 | 1.6615 | 3.3231 | 0.1884 | 1.5249 |
| fable-corpus-stage2 | 6,503 | 6,503 | 1,738,148 | 201,381 | 3,254 | 13.7253 | 2.1106 | 4.2212 | 0.0125 | 0.8344 |
| fable-corpus-subsystem | 6,503 | 6,673 | 4,796,833 | 72,133 | 612 | 25.7875 | 3.9655 | 7.9310 | 0.0024 | 1.5249 |

Calls whose answer reported no thinking-token count (counted as none): fable-corpus-subsystem 1.

From the logged tokens of every answered call; batch prices are half the list prices (the runs of Deviation 15 were sent through the Message Batches API); thinking is billed as output and is part of the output tokens; standard prices are the list prices of single requests; the list prices of Deviation 15 hold for global routing, and the regions the answers report are given with each run.

