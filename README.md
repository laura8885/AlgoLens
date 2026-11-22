# AlgoLens — Interactive Algorithm Studio

AlgoLens is a Streamlit application for learning and exploring searching, sorting, and graph algorithms. It combines step-by-step execution visualizations with a Python code-recognition prototype that analyzes implementation structure rather than relying on algorithm names in the source.

## Highlights

- **11 algorithms:** Linear Search, Binary Search, Bubble Sort, Selection Sort, Insertion Sort, Merge Sort, Quick Sort, Breadth-First Search, Depth-First Search, Dijkstra's, and A* Search.
- **Visualizer for every supported algorithm:** array comparisons, swaps, shifts, pivots, recursion-driven partitions, graph expansion, weighted edges, frontier/visited states, and path highlighting.
- **Step controls:** move forward and backward through an execution trace and reset the visualization.
- **Code Recognition:** Python AST parsing, identifier normalization, structural feature extraction, and a LinearSVC classifier with supporting structural evidence.
- **Code-specific complexity estimate:** best-, average-, and worst-case time complexity estimates for the submitted snippet.
- **Recognition animation:** Play/Pause controls and a timeline animate the detected algorithm using a user-selected demonstration input.
- **Complexity Table:** best-, average-, and worst-case complexity references plus interactive growth curves.
- **Source-attributed corpus:** 15 curated implementation excerpts from the MIT-licensed TheAlgorithms/Python repository, with source URLs and labels.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src
streamlit run app.py
```

On Windows, activate with `.venv\\Scripts\\activate`.

## How code recognition works

1. Parse submitted Python with the built-in `ast` module.
2. Ignore comments and remove module, class, and function docstrings.
3. Normalize function names, variable names, argument names, and ordinary attribute names.
4. Extract AST node/operator patterns and structural signals such as nested loops, recursion, indexed reads/writes, slicing, comparisons, FIFO queue operations, stack operations, and priority-queue behavior.
5. Combine a LinearSVC ranking with transparent structural rules to produce candidate algorithm matches and supporting evidence.

The intent is to identify algorithmic structure even if a user renames functions and variables or removes comments. The system is a prototype, not a formal program verifier. Its score is a relative ranking, not a probability.

## Dataset provenance and evaluation

The bundled corpus contains 15 curated implementation excerpts across 11 classes, sourced from TheAlgorithms/Python. Each CSV row includes a sample ID, algorithm label, repository, original source URL, and license. The excerpts are isolated into standalone snippets and documentation/comment text is omitted; the algorithmic control flow and operations are retained. See `data/SOURCES.md` and `DATASET.md`.

The corpus is small and comes from one repository. No held-out accuracy is reported because that would imply a level of independent evaluation the current data cannot support. Renaming-stress tests confirm that the bundled examples retain their expected classifications after identifiers are consistently renamed, but this is not an independent generalization test. A stronger evaluation needs many more manually verified implementations from independent repositories, deduplication, and repository- or author-held-out testing.

## Visualization scope

The algorithm explorer and Code Recognition animations generate traces from reference implementations using controlled or user-selected inputs. For safety, AlgoLens does not execute arbitrary submitted Python. The Code Recognition animation uses the algorithm detected in the pasted source, but it is a reference trace—not an instruction-by-instruction replay of the exact submitted function. Complexity values are static estimates based on the detected algorithm and visible AST patterns; helper functions, data structures, and implementation details can change the actual bounds.

## Graph-search assumptions

- BFS finds a shortest path by number of edges in an unweighted graph.
- DFS demonstrates depth-first traversal and does not guarantee a shortest path.
- Dijkstra assumes non-negative edge weights.
- A* performance depends on the heuristic; the sample graph uses a conservative heuristic for its displayed edge costs.

## Project structure

```text
AlgoLens/
├── app.py
├── src/
│   ├── algorithms.py
│   ├── recognition.py
│   └── __main__.py
├── data/
│   ├── algorithm_samples.csv
│   └── SOURCES.md
├── models/
├── results/
├── tests/
├── licenses/
├── requirements.txt
├── DATASET.md
└── README.md
```
