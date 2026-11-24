# AlgoLens model results

Run `python -m src.build_corpus` to collect the configured public-source corpus, then run `python -m src.recognition` to train the classifier and write `results/metrics.json`.

The training script attempts a repository-held-out evaluation before fitting the final model on all collected rows. It records the actual sample count, class distribution, source repositories, held-out repositories, accuracy, macro F1, and class coverage when the data supports a valid split. If it cannot form a meaningful repository-held-out split, it records why evaluation was not run.

No new dataset size or accuracy figure should be quoted until the corpus builder and training command have completed successfully on the target machine.
