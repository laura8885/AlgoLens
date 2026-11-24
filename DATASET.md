# AlgoLens dataset and recognition methodology

AlgoLens includes a corpus builder that collects real Python source files from public repositories. The configured sources are TheAlgorithms/Python (MIT), keon/algorithms (MIT), stefan-jansen/python-algorithms (Apache-2.0), rlishtaba/py-algorithms (MIT), and xiaowang1105/algorithms-in-python (MIT). The builder checks each repository's GitHub SPDX license metadata before downloading its source archive. It only includes repositories whose detected license matches the configured permissive license.

Run the following from the project root to build the corpus and train the classifier:

```bash
python -m src.build_corpus
python -m src.recognition
```

The builder selects files using algorithm-specific source-path patterns for the 11 supported categories, excludes test/documentation/example/benchmark folders, records raw source URLs and license identifiers, and removes duplicate source URLs and identical code/label pairs. The resulting `data/algorithm_samples.csv` records each sample's algorithm, repository, source path, license, and source URL.

The recognition pipeline parses Python source with the standard-library `ast` module, removes comments and docstrings by operating on the AST, normalizes function and variable identifiers, and extracts AST/operator/API patterns and structural counts. A LinearSVC classifier ranks the 11 algorithm categories.

## Evaluation

Training first attempts a repository-held-out evaluation using `GroupShuffleSplit`, keeping each repository entirely in either training or test data. The report includes accuracy, macro F1, held-out repositories, and class coverage only when the available corpus supports a split with multiple represented classes. The final model is then fitted on the full collected corpus.

The source paths provide weak labels rather than formal proof of algorithm correctness. Review the collected examples and the class distribution before using the results in research or application materials. Repository-held-out scores describe this collected corpus and should not be presented as performance on arbitrary Python code.

## Scope

The classifier supports Python source only and does not execute submitted code. The algorithm animations use separate reference implementations and controlled inputs; they do not replay the submitted function's runtime.
