# AlgoLens source-code corpus

The bundled `algorithm_samples.csv` is a small, manually curated reference corpus of real Python implementations from the public **TheAlgorithms/Python** repository.

- Repository: https://github.com/TheAlgorithms/Python
- License: MIT (see https://github.com/TheAlgorithms/Python/blob/master/LICENSE.md)
- Each row records its algorithm label, repository, license, sample ID, and original raw source-file URL.
- The CSV contains 15 implementation excerpts covering 11 supported categories. Some source files contain more than one implementation (for example, iterative and recursive linear search and bubble sort, plus multiple binary-search variants).
- Excerpts are isolated into parseable snippets. Comments and documentation strings are omitted from the training examples because AlgoLens is designed not to use prose labels as recognition clues. The algorithmic operations and control flow are retained; the original source URL is included for verification.

## Source files represented

| Algorithm | Original source |
|---|---|
| Linear Search | https://raw.githubusercontent.com/TheAlgorithms/Python/master/searches/linear_search.py |
| Binary Search | https://raw.githubusercontent.com/TheAlgorithms/Python/master/searches/binary_search.py |
| Bubble Sort | https://raw.githubusercontent.com/TheAlgorithms/Python/master/sorts/bubble_sort.py |
| Selection Sort | https://raw.githubusercontent.com/TheAlgorithms/Python/master/sorts/selection_sort.py |
| Insertion Sort | https://raw.githubusercontent.com/TheAlgorithms/Python/master/sorts/insertion_sort.py |
| Merge Sort | https://raw.githubusercontent.com/TheAlgorithms/Python/master/sorts/merge_sort.py |
| Quick Sort | https://raw.githubusercontent.com/TheAlgorithms/Python/master/sorts/quick_sort.py |
| Breadth-First Search | https://raw.githubusercontent.com/TheAlgorithms/Python/master/graphs/breadth_first_search.py |
| Depth-First Search | https://raw.githubusercontent.com/TheAlgorithms/Python/master/graphs/depth_first_search.py |
| Dijkstra's | https://raw.githubusercontent.com/TheAlgorithms/Python/master/graphs/dijkstra.py |
| A* Search | https://raw.githubusercontent.com/TheAlgorithms/Python/master/graphs/a_star.py |

## Important dataset limitation

This is a source-derived starter corpus, not a published benchmark dataset and not a large, independently sampled collection. It is suitable for demonstrating source attribution, AST preprocessing, and a prototype classification workflow. It is not sufficient to support a credible generalization or accuracy claim. A stronger study should expand the corpus with independently authored repositories, verify each algorithm label, deduplicate near-identical code, and split training/testing by repository or author.
