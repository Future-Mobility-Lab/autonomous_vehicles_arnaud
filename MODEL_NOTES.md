CAV Capstone Model Notes

Sentiment model:
cardiffnlp/twitter-roberta-base-sentiment

Label mapping:
LABEL_0 = negative
LABEL_1 = neutral
LABEL_2 = positive

Polarity score:
P(positive) - P(negative)

Why the mapping matters:
Swapping the negative and positive labels would silently invert the polarity results.

Zero-shot model:
facebook/bart-large-mnli

Usage:
Use later through the Hugging Face zero-shot-classification pipeline with project-defined candidate labels. The pipeline handles the model’s internal indices, so no manual index mapping is required.
