# Dataset and recognition methodology

AlgoLens uses a curated reference corpus of 15 real Python implementation excerpts across 11 algorithm categories. The excerpts are sourced from the MIT-licensed TheAlgorithms/Python repository. Every row in `data/algorithm_samples.csv` includes a sample ID, algorithm label, repository, original raw source URL, and license. See `data/SOURCES.md` for the source inventory and limitations.

The recognition pipeline does not depend on algorithm names in submitted code:

1. Python source is parsed with the standard-library `ast` module.
2. Comments are absent from the AST, and function docstrings are removed.
3. Function names, variable names, argument names, and ordinary attribute names are normalized. Selected behavioral APIs (such as `append`, `pop`, `popleft`, `heappop`, and `heappush`) are retained because their operations are meaningful structural evidence.
4. AST node/operator patterns and structural counts are extracted, including loops, nested loops, recursion, indexed reads/writes, slices, comparisons, queue/stack operations, and priority-queue operations.
5. A LinearSVC classifier ranks candidates. Transparent structural rules are combined with the model ranking to make the output more interpretable.

The visualizer is independent of the submitted-code classifier. It provides step-by-step reference traces for all 11 supported algorithms: Linear Search, Binary Search, Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, Quick Sort, Breadth-First Search, Depth-First Search, Dijkstra's, and A* Search.

## Evaluation

No held-out accuracy is reported. The corpus is too small and too concentrated in one repository to support a meaningful independent test. In particular, training and testing on multiple snippets from the same source repository would not establish generalization to independently authored implementations. Future evaluation should use repository-held-out samples and identifier-renaming stress tests.

## Limitations

- The current model is a prototype, not a formal program verifier.
- Different algorithms can share similar syntax; a small reference corpus may lead to incorrect or uncertain rankings.
- Only Python source is supported.
- The system does not execute submitted code.
- The animation illustrates a separate reference implementation and controlled input; it does not replay the submitted program's actual runtime.
