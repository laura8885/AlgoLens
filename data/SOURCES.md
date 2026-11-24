# AlgoLens source-code corpus

The corpus builder collects source files from these public repositories. It checks the GitHub API's SPDX license metadata and includes a repository only when the detected license matches the expected permissive license. Every included sample records its raw source URL, repository, source path, and license in `algorithm_samples.csv`.

| Repository | Expected license | Source |
|---|---|---|
| TheAlgorithms/Python | MIT | https://github.com/TheAlgorithms/Python |
| keon/algorithms | MIT | https://github.com/keon/algorithms |
| stefan-jansen/python-algorithms | Apache-2.0 | https://github.com/stefan-jansen/python-algorithms |
| rlishtaba/py-algorithms | MIT | https://github.com/rlishtaba/py-algorithms |
| xiaowang1105/algorithms-in-python | MIT | https://github.com/xiaowang1105/algorithms-in-python |

## Build the corpus

```bash
python -m src.build_corpus
```

The builder uses repository paths and filenames to assign labels for Linear Search, Binary Search, Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, Quick Sort, Breadth-First Search, Depth-First Search, Dijkstra's, and A* Search. It excludes test, documentation, example, and benchmark directories and deduplicates repeated source URLs and identical code/label pairs.

GitHub API access is unauthenticated by default. If you encounter API rate limits, set `GITHUB_TOKEN` in your shell and rerun the command. The token is read from the environment and is not written to project files.

## Label quality

The path-based labels are weak labels, not human-verified ground truth. A file may contain helper routines or multiple functions, and repository naming conventions can be imperfect. Inspect the generated CSV and correct questionable labels before treating the corpus as a research benchmark.
