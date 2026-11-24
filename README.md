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
- **Multi-repository corpus builder:** collects source-attributed Python implementations from three public repositories with verified MIT or Apache-2.0 license metadata.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.build_corpus
python -m src.recognition
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

The repository includes a starter corpus and a builder for collecting more source files from TheAlgorithms/Python, keon/algorithms, stefan-jansen/python-algorithms, rlishtaba/py-algorithms, and xiaowang1105/algorithms-in-python. The builder verifies repository license metadata and records each sample's algorithm label, repository, source path, raw source URL, and license. See `data/SOURCES.md` and `DATASET.md`.

The checked-in CSV remains a small starter corpus until the collection command is run. After collection, the training script attempts a repository-held-out evaluation and records the actual dataset size, source repositories, class coverage, accuracy, and macro F1 in `results/metrics.json`. Do not quote a dataset size or accuracy figure until that process has completed; path-derived labels should be reviewed before being treated as verified ground truth.

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


## Building the real-source training corpus

Run `python -m src.build_corpus` to collect Python implementation files from the configured public repositories. The script verifies the repository license metadata, records per-sample source URLs and licenses, filters to the 11 supported algorithm categories, and deduplicates the results. Then run `python -m src.recognition` to train and evaluate the classifier using repository-held-out splits when possible. See `DATASET.md` and `data/SOURCES.md` for collection details and labeling caveats.
