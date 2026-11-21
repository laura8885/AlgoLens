# AlgoLens dataset documentation

## Dataset currently included

File: `data/processed/algorithm_samples.csv`

- 240 examples total.
- 6 labels, 40 examples per label.
- 8 hand-written base templates per label.
- 5 controlled variable-name/formatting variants per template.
- Each row records a `template_group`, `source_type`, and `source` field.

All included code examples were written specifically for this project. They are original controlled examples, not third-party repository content and not an external benchmark dataset. This means the dataset is suitable for an initial pipeline demonstration but not enough to establish real-world algorithm-recognition performance.

## Labels

- `binary_search`
- `linear_search`
- `bubble_sort`
- `insertion_sort`
- `quick_sort`
- `merge_sort`

## Splitting strategy

`src/train_model.py` uses `GroupShuffleSplit` with `template_group`. Variants of one base template remain together in either training or test data. This reduces the most direct form of near-duplicate leakage. Because the number of distinct templates is still small, the evaluation remains preliminary.

## External source candidates for a future expanded corpus

These repositories document algorithm implementations and can be inspected to collect independently sourced examples. They are **not included** in the current CSV because this build environment could not retrieve their source files, and their contents have not been individually checked or imported.

- `mr-karan/Algorithm-Implementations--Python`: https://github.com/mr-karan/Algorithm-Implementations--Python — search results indicate an MIT-licensed Python repository containing binary search, insertion sort, merge sort, and quicksort files.
- `TheAlgorithms/Python`: https://github.com/TheAlgorithms/Python — broad Python algorithm collection with a directory listing that includes sorting and searching algorithms. Verify the exact repository license and each file's provenance before redistribution.

A future external-data ingestion process should record, for every sample: exact source URL, repository, commit hash, file path, license, algorithm label, and review status. Verify the implementation actually performs the assigned algorithm; filenames and README headings alone are not sufficient. Deduplicate exact and near-identical code, then split by repository so code from the same project cannot appear in both training and test sets.

## Rebuilding

```bash
python src/generate_dataset.py
```

This regenerates the controlled dataset deterministically. It does not download external data.
