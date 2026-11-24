from __future__ import annotations

import argparse
import io
import json
import re
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATASET_PATH = DATA_DIR / "algorithm_samples.csv"
SOURCES_PATH = DATA_DIR / "SOURCES.md"

REPOSITORIES = [
    {"name": "TheAlgorithms/Python", "expected_license": "MIT"},
    {"name": "keon/algorithms", "expected_license": "MIT"},
    {"name": "stefan-jansen/python-algorithms", "expected_license": "Apache-2.0"},
    {"name": "rlishtaba/py-algorithms", "expected_license": "MIT"},
    {"name": "xiaowang1105/algorithms-in-python", "expected_license": "MIT"},
]

ALGORITHM_PATTERNS = {
    "Linear Search": ["linear_search", "linearsearch", "sequential_search"],
    "Binary Search": ["binary_search", "binarysearch"],
    "Bubble Sort": ["bubble_sort", "bubblesort"],
    "Selection Sort": ["selection_sort", "selectionsort"],
    "Insertion Sort": ["insertion_sort", "insertionsort"],
    "Merge Sort": ["merge_sort", "mergesort"],
    "Quick Sort": ["quick_sort", "quicksort"],
    "Breadth-First Search": ["breadth_first_search", "breadthfirstsearch", "bfs"],
    "Depth-First Search": ["depth_first_search", "depthfirstsearch", "dfs"],
    "Dijkstra's": ["dijkstra"],
    "A* Search": ["a_star_search", "a_star", "astar"],
}

ALLOWED_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"}
EXCLUDED_PARTS = {"test", "tests", "docs", "doc", "examples", "example", "benchmarks", "benchmark", "notebooks", ".github"}


def _request(url: str, token: str | None = None) -> bytes:
    headers = {"User-Agent": "AlgoLens-Research-Corpus/1.0", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def _repository_metadata(repo: str, token: str | None) -> dict:
    return json.loads(_request(f"https://api.github.com/repos/{repo}", token).decode("utf-8"))


def _label_from_path(path: str) -> str | None:
    normalized = path.lower().replace("-", "_")
    for label, aliases in ALGORITHM_PATTERNS.items():
        for alias in aliases:
            if alias in {"bfs", "dfs"}:
                if re.search(rf"(^|[/_.]){alias}([/_.]|$)", normalized):
                    return label
            elif alias in normalized:
                return label
    return None


def _eligible_path(path: str) -> bool:
    parts = [part.lower() for part in path.split("/")]
    if not path.lower().endswith(".py"):
        return False
    if any(part in EXCLUDED_PARTS for part in parts):
        return False
    if path.rsplit("/", 1)[-1].startswith("test_"):
        return False
    return True


def _source_rows(repo: str, branch: str, license_id: str, archive: bytes) -> list[dict]:
    rows = []
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        for member in zipped.infolist():
            if member.is_dir() or member.file_size > 100_000:
                continue
            parts = member.filename.split("/", 1)
            if len(parts) != 2:
                continue
            relative_path = parts[1]
            if not _eligible_path(relative_path):
                continue
            algorithm = _label_from_path(relative_path)
            if algorithm is None:
                continue
            try:
                code = zipped.read(member).decode("utf-8")
                compile(code, relative_path, "exec")
            except (UnicodeDecodeError, SyntaxError, KeyError):
                continue
            if len(code.strip()) < 40:
                continue
            source_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{relative_path}"
            rows.append({
                "sample_id": f"{repo}:{relative_path}",
                "algorithm": algorithm,
                "code": code,
                "source_url": source_url,
                "repository": repo,
                "license": license_id,
                "file_path": relative_path,
                "label_source": "repository_path",
            })
    return rows


def build_corpus(token: str | None = None) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    if DATASET_PATH.exists():
        existing = pd.read_csv(DATASET_PATH).fillna("")
        for column in ["file_path", "label_source"]:
            if column not in existing.columns:
                existing[column] = "legacy_curated"
        rows.extend(existing.to_dict("records"))
    source_records = []
    for config in REPOSITORIES:
        repo = config["name"]
        metadata = _repository_metadata(repo, token)
        license_info = metadata.get("license") or {}
        license_id = license_info.get("spdx_id")
        if license_id not in ALLOWED_LICENSES or license_id != config["expected_license"]:
            source_records.append({"repository": repo, "status": "skipped", "license": license_id or "unknown", "reason": "License was not verified against the expected permissive license."})
            continue
        branch = metadata["default_branch"]
        archive_url = f"https://codeload.github.com/{repo}/zip/refs/heads/{branch}"
        archive = _request(archive_url, token)
        repo_rows = _source_rows(repo, branch, license_id, archive)
        rows.extend(repo_rows)
        source_records.append({"repository": repo, "status": "included", "license": license_id, "branch": branch, "samples_collected": len(repo_rows), "source_url": f"https://github.com/{repo}"})
    if not rows:
        raise RuntimeError("No source examples were collected. Check network access and the configured repositories.")
    df = pd.DataFrame(rows)
    for column in ["sample_id", "algorithm", "code", "source_url", "repository", "license", "file_path", "label_source"]:
        if column not in df.columns:
            df[column] = ""
    df = df.dropna(subset=["code", "algorithm"]).copy()
    df["code"] = df["code"].astype(str)
    df["algorithm"] = df["algorithm"].astype(str)
    df = df[df["algorithm"].isin(ALGORITHM_PATTERNS)].copy()
    df = df.drop_duplicates(subset=["source_url", "algorithm"])
    df = df.drop_duplicates(subset=["code", "algorithm"])
    df = df.sort_values(["algorithm", "repository", "sample_id"]).reset_index(drop=True)
    df["sample_id"] = [f"sample_{index:05d}" for index in range(1, len(df) + 1)]
    df.to_csv(DATASET_PATH, index=False)
    summary = df.groupby(["algorithm", "repository"]).size().unstack(fill_value=0)
    source_lines = [
        "# AlgoLens source-code corpus",
        "",
        "The corpus is assembled from public Python repositories. Collection checks each repository's SPDX license metadata against an explicit permissive-license allowlist, records the source URL for every sample, and labels samples from algorithm-specific source paths. The path-derived labels should be reviewed before making research claims.",
        "",
        "## Collection results",
        "",
        f"- Total deduplicated source files: {len(df)}",
        f"- Algorithms represented: {df['algorithm'].nunique()} of {len(ALGORITHM_PATTERNS)}",
        f"- Repositories represented: {df['repository'].nunique()}",
        "",
        "## Repository status",
        "",
    ]
    for record in source_records:
        source_lines.append(f"- {record['repository']}: {record['status']}; license: {record['license']}; samples: {record.get('samples_collected', 0)}; {record.get('reason', record.get('source_url', ''))}")
    source_lines.extend(["", "## Samples by algorithm and repository", "", "\n".join(["| Algorithm | " + " | ".join(summary.columns.astype(str)) + " |", "|---|" + "|".join(["---"] * len(summary.columns)) + "|"] + ["| " + str(index) + " | " + " | ".join(str(value) for value in row) + " |" for index, row in summary.iterrows()]), "", "## Labeling and provenance", "", "Each row in `algorithm_samples.csv` includes the repository, original raw source URL, SPDX license identifier, source path, and labeling method. Files are selected by explicit algorithm-related path or filename patterns. Duplicate source URLs and identical code/label pairs are removed. Test, documentation, example, and benchmark folders are excluded.", "", "## Important interpretation", "", "This is a source-derived corpus, not a pre-labeled academic benchmark. A path-based label is a useful starting point, but it is not proof that every file implements only the named algorithm. Review samples before using them in a publication or claiming a verified dataset size. The training script reports repository-held-out metrics only when the corpus supports that split."])
    SOURCES_PATH.write_text("\n".join(source_lines), encoding="utf-8")
    return df


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", default=None)
    args = parser.parse_args()
    import os
    token = args.token or os.environ.get("GITHUB_TOKEN")
    try:
        df = build_corpus(token)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError, RuntimeError) as error:
        raise SystemExit(f"Corpus collection failed: {error}") from error
    print(f"Collected {len(df)} deduplicated source files across {df['algorithm'].nunique()} algorithms and {df['repository'].nunique()} repositories.")
    print(df.groupby("algorithm").size().to_string())


if __name__ == "__main__":
    main()
