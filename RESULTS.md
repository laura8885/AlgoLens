# Recognition results and interpretation

The bundled classifier is trained on the 15 curated, source-attributed Python implementation excerpts in `data/algorithm_samples.csv`.

No held-out accuracy or F1 score is reported. The available corpus is a small starter set from one public repository, so a random split would give a misleading impression of generalization. The model is intended to demonstrate AST normalization, structural feature extraction, and candidate ranking. Its output scores are relative ranking values, not calibrated probabilities.

A meaningful next evaluation would require a substantially larger set of independently authored examples, manually verified labels, deduplication, and repository- or author-held-out test partitions.
