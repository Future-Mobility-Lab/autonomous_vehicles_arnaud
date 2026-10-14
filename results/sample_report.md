# Sample analyses of record (Deviation 13)

The main figures. Every figure, with the counts behind it, is in `sample_results.json`.

## Prevalence (design-weighted; 95% intervals of Deviation 3, and Wald intervals for the tranche difference)

| Estimate | Pooled sample | Tranche 1 | Tranche 2 | Tranche 2 minus tranche 1 |
|---|---|---|---|---|
| Relevance rate, overall | 61.1% (58.0% to 64.2%) | 60.7% (56.2% to 65.1%) | 61.6% (57.0% to 65.9%) | +0.8 points (-5.6 points to +7.2 points) |
| Relevance rate, 2016-2018 | 58.7% (53.7% to 63.5%) | 58.7% (51.3% to 65.7%) | 58.7% (51.3% to 65.7%) | +0.0 points (-10.6 points to +10.6 points) |
| Relevance rate, 2019-2021 | 54.8% (49.6% to 59.8%) | 53.9% (46.4% to 61.2%) | 55.7% (48.2% to 62.9%) | +1.8 points (-8.9 points to +12.5 points) |
| Relevance rate, 2022-2025 | 66.0% (60.8% to 70.8%) | 65.7% (58.2% to 72.5%) | 66.3% (58.8% to 73.0%) | +0.6 points (-9.7 points to +10.9 points) |
| CONCERN share among relevant | 38.0% (34.1% to 42.1%) | 40.6% (34.9% to 46.6%) | 35.4% (29.9% to 41.3%) | -5.2 points (-13.6 points to +3.1 points) |
| ENDORSEMENT share among relevant | 31.6% (27.9% to 35.6%) | 32.2% (26.9% to 38.1%) | 31.0% (25.8% to 36.8%) | -1.2 points (-9.2 points to +6.8 points) |
| OTHER share among relevant | 30.4% (26.7% to 34.3%) | 27.1% (22.2% to 32.7%) | 33.6% (28.2% to 39.4%) | +6.5 points (-1.4 points to +14.3 points) |
| Relevance rate, 2022-2025 minus 2016-2018 | +7.3 points (+0.3 points to +14.3 points) | +7.0 points (-3.2 points to +17.2 points) | +7.6 points (-2.6 points to +17.8 points) | |

The tranche difference is description (Deviation 11); it is not used to choose between the tranches.

## RQ4 composition check (Deviation 8; exploratory)

| Sample | Groups | Difference | Mix part | Within-group part | Standardised era rates |
|---|---|---|---|---|---|
| pooled | seven groups | +7.3 points | +3.7 points | +3.6 points | 59.5% / 55.0% / 63.8% |
| pooled | two groups | +7.3 points | +7.0 points | +0.3 points | 62.4% / 56.8% / 62.9% |
| tranche 1 | seven groups | +7.0 points | +6.1 points | +0.9 points | 60.8% / 54.6% / 62.3% |
| tranche 1 | two groups | +7.0 points | +10.5 points | -3.6 points | 63.9% / 56.7% / 60.8% |

Standardised era rates: 2016-2018 / 2019-2021 / 2022-2025, at the pooled frame mix. Flags: none.

## Text-only sensitivity (Deviations 12 and 13; exploratory)

| Source | 2016-2018 | 2019-2021 | 2022-2025 | 2022-2025 minus 2016-2018 | Mix part | Within-group part |
|---|---|---|---|---|---|---|
| (a) text-only variant, all items | 63.5% (58.5% to 68.2%) | 57.5% (52.3% to 62.5%) | 63.9% (58.7% to 68.7%) | +0.4 points | -4.5 points | +4.9 points |
| (b) gold labels, six subreddits | 53.2% (47.7% to 58.6%) | 45.4% (39.7% to 51.2%) | 51.4% (44.9% to 57.7%) | -1.8 points | -4.6 points | +2.8 points |

Decomposition of (a) over the seven groups of Deviation 8; of (b) over its six subreddits.

## Lexical proxy against the gold Stage 1 label (items with a gold Stage 1 label)

| Subreddit | Items | Proxy and gold | Proxy only | Gold only | Neither | Agreement |
|---|---|---|---|---|---|---|
| teslamotors | 226 | 78 | 2 | 69 | 77 | 68.6% |
| selfdrivingcars | 180 | 57 | 0 | 105 | 18 | 41.7% |
| realtesla | 91 | 36 | 2 | 20 | 33 | 75.8% |
| waymo | 54 | 23 | 0 | 30 | 1 | 44.4% |
| electricvehicles | 135 | 35 | 1 | 17 | 82 | 86.7% |
| cars | 136 | 27 | 2 | 23 | 84 | 81.6% |
| futurology | 115 | 30 | 3 | 24 | 58 | 76.5% |
| technology | 63 | 13 | 3 | 11 | 36 | 77.8% |
| all eight subreddits | 1000 | 299 | 13 | 299 | 389 | 68.8% |

Term list: `CORE_TERMS` in `config.py` as committed at `be001c7`; matching rule: Deviation 14 (whole words, in any letter case). Text: clean_body of corpus v2.2; annotated items whose clean_body differs from the text given to the models: 0, of which the proxy gives another result on 0.

## Subsystem agreement and D28

| Reliability items | Form | Alpha | Units | Pairable values |
|---|---|---|---|---|
| both tranches (200 items) | two or more labels | 0.7789 | 120 | 351 |
| both tranches (200 items) | all three annotators | 0.7685 | 111 | 333 |
| tranche 1 (100 items) | two or more labels | 0.8683 | 59 | 175 |
| tranche 1 (100 items) | all three annotators | 0.8671 | 57 | 171 |
| tranche 2 (100 items) | two or more labels | 0.7039 | 61 | 176 |
| tranche 2 (100 items) | all three annotators | 0.6797 | 54 | 162 |

| Subsystem | pi_s, pooled sample | Items | pi_s, tranche 1 | Items |
|---|---|---|---|---|
| sensing | 24.0% (18.9% to 29.9%) | 60 | 27.8% (20.3% to 36.8%) | 35 |
| in_vehicle_networks | 5.1% (2.9% to 8.7%) | 13 | 3.7% (1.5% to 8.8%) | 5 |
| v2x | count only (R5) | 9 | count only (R5) | 6 |
| cybersecurity | 0.6% (0.2% to 2.4%) | 2 | 0.0% (no interval) | 0 |
| privacy | 1.8% (0.7% to 4.7%) | 4 | 0.7% (0.1% to 4.8%) | 1 |
| data_governance | 1.9% (0.8% to 4.7%) | 5 | 0.0% (no interval) | 0 |
| none | 62.7% (56.2% to 68.8%) | 132 | 63.5% (54.2% to 71.8%) | 73 |

D28, pooled sample (of record): lower subsystem alpha 0.7685. Rule 1 (alpha below 0.6) fires: no. Rule 2: condition (i), alpha at least 0.7: yes; condition (ii), the intervals of sensing and in_vehicle_networks do not overlap (18.9% against 8.7%): yes; met: yes.

D28, tranche 1 (beside it): lower subsystem alpha 0.8671. Rule 1 (alpha below 0.6) fires: no. Rule 2: condition (i), alpha at least 0.7: yes; condition (ii), the intervals of sensing and in_vehicle_networks do not overlap (20.3% against 8.8%): yes; met: yes.

Against the tranche 1 outcome (Rule 1 did not fire; Rule 2 met with sensing first): Rule 1 changed no; Rule 2 changed no; first place changed no. A further deviation is required (Deviations 10 and 11): no.

## Tranche 1 checks (Deviations 3 and 4)

| Class pair | Disagreeing pairs | Observed coincidences | Expected coincidences | Observed / expected |
|---|---|---|---|---|
| CONCERN/ENDORSEMENT | 0 | 0.000 | 48.828 | 0.000 |
| CONCERN/OTHER | 14 | 14.000 | 36.414 | 0.384 |
| ENDORSEMENT/OTHER | 16 | 16.000 | 29.839 | 0.536 |

Disagreement concentrates at CONCERN/OTHER rather than CONCERN/ENDORSEMENT: by count yes; by observed over expected coincidences yes.
Encoding sensitivity (exploratory; 76 reliability items): Stage 1 alpha 0.9649, Stage 2 alpha 0.7232; on all 100 items (of record) 0.9589 and 0.7393.

Class distribution by annotator's sheet (exploratory), beside the design-weighted tranche 1 figures:

| Source | Relevance share | CONCERN | ENDORSEMENT | OTHER |
|---|---|---|---|---|
| Tranche 1, design-weighted | 60.7% | 40.6% | 32.2% | 27.1% |
| Annotator A's sheet | 59.3% | 41.6% | 34.0% | 24.4% |
| Annotator B's sheet | 60.6% | 40.6% | 38.5% | 20.9% |
| Annotator C's sheet | 63.4% | 36.1% | 27.1% | 36.7% |

## Deviation 2: adjudicated items and the raw-majority set

| Item | Tranche | Level | Adjudicated | Given |
|---|---|---|---|---|
| cz1vh4t | 2 | Stage 2 | ENDORSEMENT | A N, B OTHER, C ENDORSEMENT |
| dvznfp7 | 2 | Stage 2 | ENDORSEMENT | A ENDORSEMENT, B OTHER, C CONCERN |
| epqj9r1 | 2 | primary subsystem | in_vehicle_networks | A sensing, B none, C in_vehicle_networks |
| h4jy9ry | 2 | primary subsystem | data_governance | A none, B v2x, C in_vehicle_networks |
| lifeax3 | 2 | primary subsystem | data_governance | A privacy, B none, C data_governance |

| Figure | Adjudicated gold set (of record) | Raw-majority set |
|---|---|---|
| CONCERN share among relevant, pooled | 38.0% (34.1% to 42.1%) | 38.1% (34.2% to 42.2%) |
| ENDORSEMENT share among relevant, pooled | 31.6% (27.9% to 35.6%) | 31.5% (27.8% to 35.5%) |
| OTHER share among relevant, pooled | 30.4% (26.7% to 34.3%) | 30.4% (26.8% to 34.3%) |
| Weighted TPR / FPR for CONCERN | 0.946922 / 0.237641 | 0.946922 / 0.236789 |
| D28 condition (ii): first place; met | sensing; yes | sensing; yes |

## Error rates of the deployed classifiers

Rates of record, recomputed: TPR 0.946922, FPR 0.237641.

Weighted three-class rates M_ij (rows: gold class; columns: classified as):

| Gold class | CONCERN | ENDORSEMENT | OTHER |
|---|---|---|---|
| CONCERN | 0.9469 | 0.0219 | 0.0311 |
| ENDORSEMENT | 0.1770 | 0.6958 | 0.1272 |
| OTHER | 0.3008 | 0.1117 | 0.5875 |

| Era | e_in | e_out |
|---|---|---|
| 2016-2018 | 31/209 (14.8%) | 18/125 (14.4%) |
| 2019-2021 | 26/194 (13.4%) | 15/140 (10.7%) |
| 2022-2025 | 18/227 (7.9%) | 10/105 (9.5%) |

Items wrongly included that Stage 2 classifies CONCERN: 24/75 (32.0%; 22.5% to 43.2%). Items wrongly left out that are gold CONCERN: 15/43 (34.9%; 22.4% to 49.8%).
CONCERN share three ways: gold labels 38.0% (34.1% to 42.1%); classified 49.1% (45.1% to 53.1%); classified and corrected 35.7%.

## Temporal calibration check

| Scope | Rate | Early | Late | Late minus early |
|---|---|---|---|---|
| both tranches | TPR | 0.954 (0.918 to 0.984; 133/140) | 0.941 (0.885 to 0.988; 80/85) | -0.013 (-0.075 to 0.048) |
| both tranches | FPR | 0.203 (0.152 to 0.257; 49/239) | 0.269 (0.199 to 0.348; 36/134) | 0.066 (-0.023 to 0.160) |
| tranche 1 | TPR | 0.929 (0.868 to 0.979; 69/75) | 0.911 (0.816 to 0.980; 41/45) | -0.018 (-0.123 to 0.082) |
| tranche 1 | FPR | 0.182 (0.110 to 0.256; 21/113) | 0.281 (0.181 to 0.397; 18/64) | 0.099 (-0.029 to 0.231) |
| tranche 2 | TPR | 0.982 (0.939 to 1.000; 64/65) | 0.975 (0.918 to 1.000; 39/40) | -0.007 (-0.073 to 0.050) |
| tranche 2 | FPR | 0.221 (0.149 to 0.296; 28/126) | 0.257 (0.159 to 0.367; 18/70) | 0.036 (-0.081 to 0.173) |

Weighted by the pooled design weights; intervals: 95% percentile intervals from the 2,000 item resamples; counts: unweighted (Wilson intervals in the results file).

| Block | Macro-F1 | F1 CONCERN | F1 ENDORSEMENT | F1 OTHER | Stage 1 accuracy, relevant | Stage 1 accuracy, not relevant | Stage 1 balanced accuracy |
|---|---|---|---|---|---|---|---|
| early | 0.758 | 0.826 | 0.767 | 0.682 | 346/379 | 227/284 | 0.856 |
| late | 0.735 | 0.796 | 0.756 | 0.655 | 209/219 | 100/118 | 0.901 |

Both tranches, unweighted, descriptive.

Item index arrays: SHA-256 `5e3eea48169360cb9e8f85c2826373d4bf92a0d85759a3c3b41ed4eaa35da394` (strata of 196, 183, 219 items).

## Previews

| Preview | Same as this run |
|---|---|
| tranche1 subsystem alpha register 30 september | yes |
| tranche1 pi s register 4 october | yes |
| tranche1 decomposition deviation 8 | yes |
| pooled subsystem alpha register 10 october | yes |
