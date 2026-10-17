# Series analyses of record

Deviation 13 of `docs/analysis_preregistration.md`; `analysis_03_series.py`. Shares are corrected by adjusted classify-and-count with the rates of record and clipped to [0, 1] for display; slopes are in percentage points per year, on the values before clipping. Exploratory figures are labelled (Family C).

## 1. The corpus runs

- Comments: 12,776; classified relevant at Stage 1: 6,532 (Tier 1 4,414, Tier 2 2,089, Tier 3 29).
- Population of the series (Tier 1+2 classified relevant): 6,503; Stage 2 refusals 0; subsystem unclassified 1; validation-only subsystem items 27.

## 2. Error rates and the temporal calibration check

Rates of record: TPR 0.9469, FPR 0.2376 (TPR - FPR 0.7093), reproduced exactly. Item index arrays: same as the register.

| Block (both tranches) | TPR | 95% interval | FPR | 95% interval |
|---|---|---|---|---|
| early | 0.9539 | 0.9175 to 0.9837 | 0.2029 | 0.1517 to 0.2569 |
| late | 0.9412 | 0.8851 to 0.9878 | 0.2687 | 0.1985 to 0.3475 |
| late minus early, TPR | -0.0127 | -0.0755 to 0.0476 | | |
| late minus early, FPR | 0.0658 | -0.0234 to 0.1600 | | |

Block-specific against primary: criterion 1 yes, criterion 2 yes; material: no. Difference in Sen's slope (block-specific minus primary): -0.85 points per year, 95% interval -2.26 to +0.53 (not applied: Deviation 13 qualifies a material effect only).

The block-specific series agrees with the primary series by R3's two criteria: the temporal effect is not material, and the primary series is the result.

## 3. RQ1: the primary series

- 2025 Q1 and Q2 are in this file for the quarterly plot only and enter no statistic and no annual table (R3, Deviation 13).
- The corrected values are clipped to [0, 1] for display only; every statistic uses them before clipping (Deviation 13).
- The Stage 1 predictions of the 1,000 tranche items, about 8% of the Tier 1+2 corpus, are in-sample: the retrained model had seen their labels (Deviation 13).
- The items that chose the deployed Stage 2 classifier also supply its error rates, so the rates are somewhat optimistic (Deviations 12 and 13).

Sen's slope +1.38 points per year (Gilbert 95% interval -0.10 to +3.03); Mann-Kendall S = 134, p = 0.0701 (not significant at 0.05). Hamed-Rao (lag 1): autocorrelation -0.0697 (bound 0.3267), p = 0.0701.

| Quarter | Comments | Retained | ESS | Classified | Corrected | 95% interval |
|---|---|---|---|---|---|---|
| 2016 Q1 | 61 | 61 | 57.0 | 38.7% | 21.0% | 5.3% to 39.5% |
| 2016 Q2 | 55 | 53 | 48.6 | 50.4% | 37.5% | 19.7% to 51.3% |
| 2016 Q3 | 89 | 88 | 82.5 | 60.3% | 51.6% | 29.8% to 68.8% |
| 2016 Q4 | 99 | 96 | 89.8 | 34.6% | 15.3% | 0.0% to 29.4% |
| 2017 Q1 | 100 | 97 | 84.2 | 37.8% | 19.8% | 7.6% to 32.7% |
| 2017 Q2 | 98 | 98 | 86.4 | 49.9% | 36.8% | 20.5% to 51.0% |
| 2017 Q3 | 24 | 24 | 22.2 | 51.5% | 39.2% | 4.7% to 66.5% |
| 2017 Q4 | 124 | 122 | 109.2 | 53.6% | 42.0% | 16.8% to 64.1% |
| 2018 Q1 | 228 | 228 | 201.0 | 53.8% | 42.4% | 28.1% to 55.6% |
| 2018 Q2 | 122 | 121 | 102.5 | 69.0% | 63.7% | 45.2% to 79.3% |
| 2018 Q3 | 65 | 57 | 50.2 | 41.1% | 24.5% | 3.2% to 37.4% |
| 2018 Q4 | 125 | 125 | 110.9 | 45.5% | 30.7% | 14.3% to 48.7% |
| 2019 Q1 | 82 | 82 | 68.1 | 47.5% | 33.5% | 18.0% to 48.9% |
| 2019 Q2 | 306 | 306 | 248.2 | 50.6% | 37.8% | 26.4% to 48.4% |
| 2019 Q3 | 75 | 75 | 63.5 | 39.5% | 22.2% | 0.0% to 41.9% |
| 2019 Q4 | 198 | 198 | 172.8 | 46.0% | 31.3% | 17.7% to 44.0% |
| 2020 Q1 | 126 | 126 | 120.1 | 41.9% | 25.5% | 6.5% to 44.7% |
| 2020 Q2 | 107 | 107 | 100.2 | 53.2% | 41.5% | 26.4% to 58.5% |
| 2020 Q3 | 76 | 76 | 70.6 | 39.0% | 21.6% | 0.0% to 45.0% |
| 2020 Q4 | 237 | 237 | 224.4 | 47.0% | 32.7% | 20.1% to 44.9% |
| 2021 Q1 | 151 | 148 | 146.4 | 50.6% | 37.9% | 19.8% to 55.0% |
| 2021 Q2 | 165 | 163 | 160.1 | 50.1% | 37.1% | 19.5% to 51.4% |
| 2021 Q3 | 153 | 153 | 150.5 | 53.0% | 41.3% | 24.4% to 56.3% |
| 2021 Q4 | 189 | 189 | 185.7 | 49.3% | 36.1% | 20.9% to 49.9% |
| 2022 Q1 | 148 | 148 | 127.7 | 49.7% | 36.5% | 19.8% to 53.5% |
| 2022 Q2 | 169 | 169 | 158.0 | 64.4% | 57.3% | 43.5% to 70.4% |
| 2022 Q3 | 61 | 60 | 57.3 | 49.0% | 35.6% | 12.6% to 55.9% |
| 2022 Q4 | 251 | 250 | 216.1 | 55.7% | 45.0% | 31.3% to 57.6% |
| 2023 Q1 | 127 | 124 | 99.9 | 43.9% | 28.4% | 6.2% to 51.6% |
| 2023 Q2 | 185 | 185 | 141.1 | 52.3% | 40.3% | 26.6% to 53.4% |
| 2023 Q3 | 145 | 143 | 129.1 | 54.0% | 42.6% | 25.0% to 58.6% |
| 2023 Q4 | 213 | 213 | 161.4 | 60.7% | 52.1% | 38.4% to 65.6% |
| 2024 Q1 | 86 | 86 | 77.2 | 39.3% | 21.9% | 5.7% to 41.7% |
| 2024 Q2 | 294 | 294 | 208.7 | 57.2% | 47.1% | 35.7% to 58.7% |
| 2024 Q3 | 173 | 173 | 124.0 | 61.0% | 52.6% | 37.0% to 69.0% |
| 2024 Q4 | 657 | 657 | 423.6 | 49.8% | 36.8% | 28.6% to 44.5% |

2025 Q1 and Q2 are shown on the quarterly plot only (R3, Deviation 13).

| Year | Corrected | 95% interval |
|---|---|---|
| 2016 | 31.2% | 20.6% to 40.5% |
| 2017 | 33.7% | 22.0% to 44.6% |
| 2018 | 43.1% | 33.4% to 52.1% |
| 2019 | 33.3% | 24.7% to 40.9% |
| 2020 | 31.3% | 21.8% to 40.3% |
| 2021 | 38.0% | 28.7% to 46.5% |
| 2022 | 45.2% | 35.7% to 53.9% |
| 2023 | 42.4% | 32.6% to 51.3% |
| 2024 | 41.5% | 34.4% to 48.2% |

### Series beside the primary series

| Series | Sen's slope | Gilbert 95% interval | MK p | Significant | Criterion 1 | Criterion 2 |
|---|---|---|---|---|---|---|
| Block-specific | +0.54 | -0.75 to +2.12 | 0.4375 | no | yes | yes |
| Companion | +0.53 | -1.25 to +2.10 | 0.4873 | no | yes | yes |
| Pooled (R3) | +1.21 | -0.06 to +2.81 | 0.0548 | no | yes | yes |
| Tier-level | +1.63 | +0.03 to +3.03 | 0.0437 | yes | n/a | n/a |
| Three-class CONCERN (exploratory) | +1.31 | -0.17 to +2.94 | 0.0886 | no | yes | yes |
| Word floor 25 (exploratory) | +1.72 | +0.27 to +3.12 | 0.0246 | yes | no | yes |
| Tier 1 (exploratory) | +1.21 | -0.88 to +3.18 | 0.2328 | no | n/a | n/a |
| Tier 2 (exploratory) | +1.70 | +0.17 to +3.58 | 0.0410 | yes | n/a | n/a |

- Pooled series (R3): both of R3's criteria hold; the series agrees with the primary series.
- Companion series: both of R3's criteria hold; the series agrees with the primary series.
- Three-class correction (CONCERN component): both of R3's criteria hold; the series agrees with the primary series.
- Word floor of 25: R3's criterion 1 fails. Exploratory (Family C): the primary series is unchanged.

### Changepoints (Deviation 12)

| Changepoint | Grid values | Every penalty 4-16 | Step better than line (BIC) | Supported | Statement |
|---|---|---|---|---|---|
| 2017 Q3 | 1, 2, 3 | no | no | no | the series does not distinguish a step here from a steady trend or from noise (Deviation 13) |
| 2018 Q3 | 1, 2, 3 | no | no | no | the series does not distinguish a step here from a steady trend or from noise (Deviation 13) |
| 2021 Q1 | 1, 2, 3 | no | no | no | the series does not distinguish a step here from a steady trend or from noise (Deviation 13) |


The series does not distinguish a step from a steady trend or from noise (Deviation 13).

GLM (exploratory): year odds ratio 1.0327 (Wald 95% interval 1.0038 to 1.0625), 5,564 comments in 1,266 threads; classified labels, not corrected.

## 4. Thread-size composition (R4)

- C = +3.03 points, T = +7.55 points (eight times Sen's slope, 2016-2024, classified shares); |C| = 3.03, 0.20 x |T| = 1.51, 0.50 x |T| = 3.77.
- C / T = 0.4016; the ratio a common straight-line trend would produce: 0.0787.
- Outcome: not applied: the primary series' Mann-Kendall test is not significant, so T cannot be told from zero (Deviation 13); |C| / (TPR - FPR) is reported as a change in corrected share.
- |C| / (TPR - FPR) = 4.27 points of corrected share.
- Comments: 5,532 joined of 5,532 retained in 2016-2024; left out: no post record 0, no reported count 0, reported count of zero 0.
- Size-stratified series (corrected): trend +6.56 points over the span, exact p = 0.1802.

## 5. Sensitivity analyses (Family C, exploratory)

- Seasonality: mean January-June minus July-December, 2016-2024: +0.67 points (95% interval -4.80 to +6.25).
- Month-of-year decomposition: C_m = +1.76 points, T = +7.55 points; 0.20 x |T| = 1.51; C_m / T = 0.2329; ratio of a common trend 0.0483. Outcome: not applied: the primary series' Mann-Kendall test is not significant (Deviation 13); |C_m| / (TPR - FPR) is reported; |C_m| / (TPR - FPR) = 2.48 points of corrected share.
- Word floor 25: Word floor of 25: R3's criterion 1 fails. Exploratory (Family C): the primary series is unchanged.

## 6. Relevance error (no interval)

Low series: Sen's slope +2.70 points per year; high series: -0.24. Wrongly included items classified CONCERN: 24 of 75; wrongly left out items gold CONCERN: 15 of 43.

## 7. RQ2 (Deviations 9 and 13)

Concern share C over 2016-2024 (corrected): 38.7%. The temporal effect is not material: the temporal calibration check puts no condition on the corrected subsystem measures (Deviation 13).

| Value | Median quarterly | Median annual | Reported as | pi_s 2016-2024 | C_s | E_s | Family A p (Holm) |
|---|---|---|---|---|---|---|---|
| sensing | 27.5 | 122 | annual | 24.9% | 47.7% | 1.2313 | 0.7614 (0.7614) |
| in_vehicle_networks | 1 | 5 | counts only | counts | counts | counts | n/a |
| v2x | 2 | 10 | counts (R5) | counts | counts | counts | n/a |
| cybersecurity | 0 | 2 | counts only | counts | counts | counts | n/a |
| privacy | 1 | 7 | counts only | counts | counts | counts | n/a |
| data_governance | 2 | 12 | counts only | counts | counts | counts | n/a |
| none | 98 | 468 | quarterly | 69.7% | 36.5% | 0.9414 | n/a |
| unclassified | 0 | 0 | counts (Deviation 13: reported and never tested) | counts | counts | counts | n/a |

## 8. Subsystem classifier against the gold subsystems

Items with a gold primary subsystem: 596 (relevant items without one: 2). Overall agreement, both tranches: 502 of 596 (84.2%, Wilson 81.1% to 86.9%).

| Value | Recall | Precision |
|---|---|---|
| sensing | 114/142 | 114/132 |
| in_vehicle_networks | 11/32 | 11/12 |
| v2x | 8/24 | 8/10 |
| cybersecurity | 1/2 | 1/4 |
| privacy | 7/10 | 7/13 |
| data_governance | 4/10 | 4/11 |
| none | 357/376 | 357/414 |

## 9. The two Stage 2 runs on the tranche items

Items both runs cover: 571; same label: 567 (99.3%).

## 10. Tier 3 (descriptive)

Tier 3 supplies 29 of the comments classified relevant (0.4%).

## 11. Stage 1 shares (added after the counts were seen; description)

Corpus, Tier 1+2: 6,503 of 12,212 (53.3%); frame comments: 53.3%. Annotated sample (design-weighted): cross-validated predictions 64.1%, gold 61.1%.

## 12. Reweighting

Left out (subreddit-years with fewer than ten comments): 32 comments in 2016-2024, 0 in 2025. Largest weight: 4.673 (r/teslamotors, 2025). Companion subreddits: teslamotors, selfdrivingcars, cars, futurology, technology.

