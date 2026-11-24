# AlgoLens source-code corpus

The corpus is assembled from public Python repositories. Collection checks each repository's SPDX license metadata against an explicit permissive-license allowlist, records the source URL for every sample, and labels samples from algorithm-specific source paths. The path-derived labels should be reviewed before making research claims.

## Collection results

- Total deduplicated source files: 84
- Algorithms represented: 11 of 11
- Repositories represented: 5

## Repository status

- TheAlgorithms/Python: included; license: MIT; samples: 46; https://github.com/TheAlgorithms/Python
- keon/algorithms: included; license: MIT; samples: 21; https://github.com/keon/algorithms
- stefan-jansen/python-algorithms: included; license: Apache-2.0; samples: 5; https://github.com/stefan-jansen/python-algorithms
- rlishtaba/py-algorithms: included; license: MIT; samples: 8; https://github.com/rlishtaba/py-algorithms
- xiaowang1105/algorithms-in-python: included; license: MIT; samples: 4; https://github.com/xiaowang1105/algorithms-in-python

## Samples by algorithm and repository

| Algorithm | TheAlgorithms/Python | keon/algorithms | rlishtaba/py-algorithms | stefan-jansen/python-algorithms | xiaowang1105/algorithms-in-python |
|---|---|---|---|---|---|
| A* Search | 4 | 1 | 0 | 0 | 0 |
| Binary Search | 6 | 2 | 2 | 1 | 0 |
| Breadth-First Search | 6 | 4 | 0 | 1 | 0 |
| Bubble Sort | 2 | 1 | 1 | 0 | 0 |
| Depth-First Search | 2 | 5 | 0 | 1 | 1 |
| Dijkstra's | 7 | 2 | 2 | 0 | 1 |
| Insertion Sort | 4 | 1 | 0 | 0 | 0 |
| Linear Search | 4 | 1 | 0 | 0 | 0 |
| Merge Sort | 7 | 2 | 1 | 0 | 1 |
| Quick Sort | 3 | 1 | 1 | 2 | 1 |
| Selection Sort | 1 | 1 | 1 | 0 | 0 |

## Labeling and provenance

Each row in `algorithm_samples.csv` includes the repository, original raw source URL, SPDX license identifier, source path, and labeling method. Files are selected by explicit algorithm-related path or filename patterns. Duplicate source URLs and identical code/label pairs are removed. Test, documentation, example, and benchmark folders are excluded.

## Important interpretation

This is a source-derived corpus, not a pre-labeled academic benchmark. A path-based label is a useful starting point, but it is not proof that every file implements only the named algorithm. Review samples before using them in a publication or claiming a verified dataset size. The training script reports repository-held-out metrics only when the corpus supports that split.