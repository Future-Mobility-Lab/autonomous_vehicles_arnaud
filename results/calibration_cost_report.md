# Calibration agreement and the cost break-even

Written by `analysis_05_calibration_cost.py` from the files of record (rules 1-9 of its docstring). No comment identifier is written here.

## 1. Calibration round (R2)

| Measure | Alpha | Items | Values |
|---|---|---|---|
| Stage 1 | 0.780 | 30 | 90 |
| Stage 2 | 0.733 | 16 | 44 |
| CONCERN against the rest | 0.795 | 16 | 44 |
| ENDORSEMENT against the rest | 0.712 | 16 | 44 |
| OTHER against the rest | 0.693 | 16 | 44 |

Ratings missing (skip cell marked): A 0, B 0, C 0.
Disagreements from the three sheets: 9 (Stage 1 5, Stage 2 4); Stage 1 disagreements whose relevant ratings also differ in class: 0.
Recorded on the review sheet: 9 (Stage 1 6, Stage 2 3); causes (a) missing context 6, (b) codebook ambiguity 0, (c) misapplication 3.
Items whose recorded stage differs from the sheets: 1 recorded stage1, stage2 from the sheets.
Disagreements in the sheets without a recorded cause: 0; causes on items the sheets agree on: 0.
Review-sheet labels differing from the annotators' sheets: A 0, B 0, C 0.
Agreed labels on the 21 unanimous items that differ from the unanimous label: 1.
Codebook change needed: 0 items.
R2's branch: proceed context-free, unchanged.

## 2. Times on the calibration sheets (seconds per rating)

| Annotator | Stage | Ratings | With a time | Mean | Median | Times without a label (not used) |
|---|---|---|---|---|---|---|
| A | Relevance (Stage 1) | 30 | 30 | 6.7 | 5.0 | 0 |
| A | Stance (Stage 2) | 14 | 12 | 6.7 | 5.0 | 0 |
| A | Subsystem | 14 | 11 | 5.9 | 5.0 | 0 |
| B | Relevance (Stage 1) | 30 | 30 | 9.2 | 7.0 | 0 |
| B | Stance (Stage 2) | 16 | 16 | 8.1 | 8.5 | 14 |
| B | Subsystem | 15 | 15 | 7.1 | 7.0 | 0 |
| C | Relevance (Stage 1) | 30 | 30 | 7.9 | 7.0 | 0 |
| C | Stance (Stage 2) | 15 | 15 | 12.0 | 5.0 | 0 |
| C | Subsystem | 14 | 12 | 8.3 | 7.5 | 0 |

Seconds per rating (mean of the annotators' means): Relevance (Stage 1) 7.9; Stance (Stage 2) 8.9; Subsystem 7.1.

## 3. Annotation hours (estimate; time on the items only)

| | Relevance | Stance | Subsystem |
|---|---|---|---|
| Tranche 1: ratings | 700 | 414 | 414 |
| Tranche 1: hours | 1.5 | 1.0 | 0.8 |
| Tranche 2: ratings | 700 | 419 | 419 |
| Tranche 2: hours | 1.5 | 1.0 | 0.8 |
| Calibration round: hours | 0.20 | 0.11 | 0.09 |

Charged under full accounting (relevance and stance, calibration included): 5.5 hours. Subsystem labelling, not charged: 1.7 hours.

## 4. Cost break-even (D17)

- Deployed Stage 2 configuration: Claude Sonnet 4.6 (domain-specific). Corpus run: 6,503 comments, US$5.4260; US$0.834 per 1,000 comments (evaluation run: US$0.799).
- Australian dollars per US dollar of credit: 1.5832 (A$39.58 charged for US$25.00 of credit; the card was charged US$27.50, 10.0% above the credit; card rate 1.4393). Zero-shot cost: A$1.321 per 1,000 Stage 2 comments; the corpus run cost A$8.59.
- Incremental accounting: the fine-tuned classifier costs A$0 per comment, so it is cheaper at every corpus size.
- Full accounting: 5.5 hours at A$59.76 an hour = A$325.90. Break-even: 246,711 Stage 2 comments (about 247,000, 37.9 times the corpus run); 41,284 comments for each A$10 an hour of the rate. Zero-shot is cheaper below the break-even.
- Macro-F1 (evaluation of record): Claude Sonnet 4.6 (domain-specific) 0.750; RoBERTa 0.523 (best fine-tuned).

## 5. Spend

| Line | Paid |
|---|---|
| Collection (Apify) | A$125.76 |
| Model API (Anthropic credit) | A$39.58 |
| GPU (Google Colab) | A$0.00 |
| Total paid | A$165.34 |
