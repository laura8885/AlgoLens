from __future__ import annotations

import ast
import copy
import json
import re
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
DATASET_PATH = DATA_DIR / "algorithm_samples.csv"
MODEL_PATH = MODEL_DIR / "classifier.joblib"

LABELS = [
    "Linear Search", "Binary Search", "Bubble Sort", "Selection Sort",
    "Insertion Sort", "Merge Sort", "Quick Sort", "Breadth-First Search",
    "Depth-First Search", "Dijkstra's", "A* Search",
]


def _clean_tree(tree: ast.AST) -> ast.AST:
    class Cleaner(ast.NodeTransformer):
        def visit_Module(self, node):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            self.generic_visit(node)
            return node

        def visit_ClassDef(self, node):
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            self.generic_visit(node)
            return node

        def visit_FunctionDef(self, node):
            node.name = "FUNCTION"
            node.decorator_list = []
            node.returns = None
            node.type_comment = None
            if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
            self.generic_visit(node)
            return node

        def visit_AsyncFunctionDef(self, node):
            return self.visit_FunctionDef(node)

        def visit_Name(self, node):
            node.id = "VAR"
            node.ctx = node.ctx
            return node

        def visit_arg(self, node):
            node.arg = "ARG"
            node.annotation = None
            return node

        def visit_Attribute(self, node):
            self.generic_visit(node)
            if node.attr not in {"append", "extend", "pop", "popleft", "heappop", "heappush", "put", "get", "add", "update", "items", "keys", "values", "sort", "reverse"}:
                node.attr = "ATTR"
            return node

        def visit_Constant(self, node):
            if isinstance(node.value, (int, float, complex)):
                node.value = 1
            elif isinstance(node.value, str):
                node.value = "STR"
            return node

    return Cleaner().visit(tree)


def _tree_tokens(tree: ast.AST) -> str:
    cleaned = _clean_tree(ast.fix_missing_locations(copy.deepcopy(tree)))
    tokens = []
    for node in ast.walk(cleaned):
        tokens.append(type(node).__name__)
        if isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
                             ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
                             ast.And, ast.Or, ast.In, ast.NotIn, ast.Is, ast.IsNot)):
            tokens.append(type(node).__name__.upper())
        if isinstance(node, ast.Attribute) and node.attr != "ATTR":
            tokens.append("API_" + node.attr.upper())
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"len", "range", "enumerate", "sorted", "reversed", "set", "list", "min", "max", "abs", "float", "int"}:
            tokens.append("BUILTIN_" + node.func.id.upper())
    return " ".join(tokens)


def _structural_profile(tree: ast.AST) -> dict[str, int]:
    nodes = list(ast.walk(tree))
    counts = {name: sum(isinstance(n, getattr(ast, name)) for n in nodes) for name in [
        "For", "While", "If", "IfExp", "Compare", "Call", "Subscript", "ListComp",
        "DictComp", "SetComp", "Lambda", "Return", "Assign", "AugAssign", "FunctionDef",
        "BinOp", "BoolOp", "Tuple", "List", "Set", "Dict", "Try", "With",
    ]}
    names = [n.id for n in nodes if isinstance(n, ast.Name)]
    attrs = [n.attr for n in nodes if isinstance(n, ast.Attribute)]
    calls = []
    for node in nodes:
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)
    funcs = [n for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    recursive = 0
    for fn in funcs:
        recursive += sum(1 for n in ast.walk(fn) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == fn.name)
    counts["RecursiveCalls"] = recursive
    counts["HeapCalls"] = calls.count("heappop") + calls.count("heappush")
    counts["StackCalls"] = sum(1 for n in nodes if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pop" and not n.args)
    counts["PopFrontCalls"] = sum(1 for n in nodes if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "pop" and n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == 0)
    counts["QueueCalls"] = calls.count("popleft") + calls.count("put") + calls.count("get") + counts["PopFrontCalls"]
    counts["AppendCalls"] = calls.count("append")
    counts["SetCalls"] = calls.count("set")
    counts["RangeCalls"] = calls.count("range")
    counts["LenCalls"] = calls.count("len")
    counts["SliceNodes"] = sum(isinstance(n, ast.Slice) for n in nodes)
    counts["FloorDiv"] = sum(isinstance(n, ast.FloorDiv) for n in nodes)
    counts["AddOps"] = sum(isinstance(n, ast.Add) for n in nodes)
    counts["EqualityOps"] = sum(isinstance(n, ast.Eq) for n in nodes)
    counts["OrderingOps"] = sum(isinstance(n, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)) for n in nodes)
    counts["SubscriptStores"] = sum(isinstance(n, ast.Subscript) and isinstance(n.ctx, ast.Store) for n in nodes)
    counts["Comprehensions"] = counts["ListComp"] + counts["DictComp"] + counts["SetComp"]
    counts["PopLeftCalls"] = calls.count("popleft")
    counts["HeapPushCalls"] = calls.count("heappush")
    counts["HeapPopCalls"] = calls.count("heappop")
    counts["PopCalls"] = calls.count("pop")
    counts["SortCalls"] = calls.count("sort")
    counts["ReverseCalls"] = calls.count("reverse")
    counts["PriorityQueuePattern"] = int(calls.count("sort") > 0 and calls.count("reverse") > 0 and calls.count("pop") > 0)
    counts["AppendCalls"] = calls.count("append")
    counts["HasDequeImport"] = int(any(isinstance(n, ast.ImportFrom) and n.module == "collections" for n in nodes))
    counts["HasHeapqImport"] = int(any(isinstance(n, ast.Import) and any(a.name == "heapq" for a in n.names) for n in nodes) or any(isinstance(n, ast.ImportFrom) and n.module == "heapq" for n in nodes))
    counts["HasHeuristicPattern"] = int(any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add) and (isinstance(n.left, (ast.Subscript, ast.Call)) or isinstance(n.right, (ast.Subscript, ast.Call))) for n in nodes))
    counts["AdjacentIndexOps"] = sum(1 for n in nodes if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.BinOp) and isinstance(n.slice.op, (ast.Add, ast.Sub)))
    counts["TupleSubscriptAssignments"] = sum(1 for n in nodes if isinstance(n, ast.Assign) and any(isinstance(t, ast.Tuple) and any(isinstance(e, ast.Subscript) for e in t.elts) for t in n.targets))
    counts["HasNestedLoop"] = int(any(isinstance(n, (ast.For, ast.While)) and any(isinstance(x, (ast.For, ast.While)) for x in ast.walk(n) if x is not n) for n in nodes))
    counts["HasCompareAndSubscript"] = int(counts["Compare"] > 0 and counts["Subscript"] > 0)
    return counts


def _heuristic_scores(profile: dict[str, int]) -> dict[str, float]:
    p = profile
    s = {label: 0.0 for label in LABELS}
    s["Linear Search"] = 1.0 * p["For"] + 1.0 * p["EqualityOps"] + 0.7 * min(p["Subscript"], 3) + 1.4 * p["RecursiveCalls"] - 1.5 * p["FloorDiv"] - 1.2 * p["SliceNodes"] - 1.2 * p["Comprehensions"] - 1.0 * p["PriorityQueuePattern"]
    s["Binary Search"] = 1.7 * p["While"] + 2.4 * p["FloorDiv"] + 1.0 * p["OrderingOps"] + 0.5 * min(p["Subscript"], 4) - 1.2 * p["PriorityQueuePattern"]
    s["Bubble Sort"] = 1.8 * p["HasNestedLoop"] + 1.4 * p["AdjacentIndexOps"] + 1.0 * p["OrderingOps"] + 0.8 * p["TupleSubscriptAssignments"]
    s["Selection Sort"] = 2.0 * p["HasNestedLoop"] + 1.3 * p["OrderingOps"] + 0.8 * p["TupleSubscriptAssignments"] + 0.6 * p["If"] - 0.8 * p["AdjacentIndexOps"]
    s["Insertion Sort"] = 1.8 * p["While"] + 1.2 * p["SubscriptStores"] + 0.7 * p["OrderingOps"] + 0.7 * p["AdjacentIndexOps"]
    s["Merge Sort"] = 2.0 * p["RecursiveCalls"] + 1.5 * p["SliceNodes"] + 0.8 * p["List"] + 0.6 * p["ExtendCalls"] if "ExtendCalls" in p else 2.0 * p["RecursiveCalls"] + 1.5 * p["SliceNodes"] + 0.8 * p["List"]
    s["Quick Sort"] = 1.7 * p["RecursiveCalls"] + 1.5 * p["Comprehensions"] + 1.2 * p["If"] + 0.5 * p["OrderingOps"]
    s["Breadth-First Search"] = 1.7 * p["QueueCalls"] + 1.0 * p["PopLeftCalls"] + 0.8 * p["AppendCalls"] + 0.6 * p["SetCalls"]
    s["Depth-First Search"] = 1.8 * p["StackCalls"] + 0.8 * p["AppendCalls"] + 0.7 * p["SetCalls"] + 0.6 * p["RecursiveCalls"]
    s["Dijkstra's"] = 2.0 * p["HeapCalls"] + 1.4 * p["HeapPushCalls"] + 1.1 * p["AddOps"] + 0.8 * p["OrderingOps"]
    s["A* Search"] = 1.8 * p["HeapCalls"] + 1.2 * p["HeapPushCalls"] + 4.0 * p["HasHeuristicPattern"] + 1.0 * p["AddOps"] + 1.2 * p["PriorityQueuePattern"] + 0.3 * min(p["Subscript"], 12) + 0.5 * p["HasNestedLoop"]
    return s


def _extract(code: str) -> tuple[str, dict[str, int]]:
    tree = ast.parse(code)
    return _tree_tokens(tree), _structural_profile(tree)


def make_features() -> FeatureUnion:
    return FeatureUnion([
        ("ast", TfidfVectorizer(analyzer="word", token_pattern=r"(?u)\b\w+\b", ngram_range=(1, 3), sublinear_tf=True)),
        ("shape", TfidfVectorizer(analyzer="char", ngram_range=(2, 5), sublinear_tf=True)),
    ])


def load_dataset() -> pd.DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"The source-code corpus is missing: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    required = {"code", "algorithm", "source_url", "repository", "license"}
    if not required.issubset(df.columns):
        raise ValueError(f"Dataset is missing required columns: {sorted(required - set(df.columns))}")
    return df.dropna(subset=["code", "algorithm"])


def train() -> dict:
    DATA_DIR.mkdir(exist_ok=True)
    MODEL_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)
    df = load_dataset()
    extracted = [_extract(code) for code in df.code]
    df = df.copy()
    df["ast_features"] = [item[0] for item in extracted]
    feature_text = [f"{ast_text} STRUCTURE " + " ".join(f"{key}_{value}" for key, value in profile.items()) for ast_text, profile in extracted]
    vectorizer = make_features()
    X = vectorizer.fit_transform(feature_text)
    classifier = LinearSVC(C=0.8, class_weight="balanced", random_state=42)
    classifier.fit(X, df.algorithm)
    model = {
        "vectorizer": vectorizer,
        "classifier": classifier,
        "labels": sorted(df.algorithm.unique()),
        "version": "3.0-ast-structure",
        "training_samples": len(df),
        "training_sources": sorted(df.repository.unique()),
    }
    joblib.dump(model, MODEL_PATH)
    metrics = {
        "dataset_size": int(len(df)),
        "classes": sorted(df.algorithm.unique()),
        "examples_per_class": {str(k): int(v) for k, v in df.algorithm.value_counts().items()},
        "training_sources": sorted(df.repository.unique()),
        "feature_method": "Identifier-normalized Python AST node/operator/API patterns plus structural counts; comments and docstrings are excluded.",
        "classifier": "LinearSVC trained on the full curated source corpus.",
        "evaluation": "No held-out accuracy is reported. The available source corpus is a small curated reference set, not a sufficiently large independent benchmark. A repository-held-out evaluation is required before making generalization claims.",
        "limitations": "The model is a code-pattern classifier, not a formal program verifier. It may confuse algorithms with similar control flow, and it may return an uncertain match for unsupported or hybrid code.",
    }
    (RESULTS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def load_model():
    if not MODEL_PATH.exists():
        train()
    model = joblib.load(MODEL_PATH)
    if model.get("version") != "3.0-ast-structure":
        train()
        model = joblib.load(MODEL_PATH)
    return model


def analyze_code(code: str) -> dict:
    tree = ast.parse(code)
    ast_text = _tree_tokens(tree)
    profile = _structural_profile(tree)
    feature_text = f"{ast_text} STRUCTURE " + " ".join(f"{key}_{value}" for key, value in profile.items())
    model = load_model()
    features = model["vectorizer"].transform([feature_text])
    raw_scores = model["classifier"].decision_function(features)[0]
    labels = model["classifier"].classes_
    ml_scores = {str(label): float(score) for label, score in zip(labels, raw_scores)}
    structural = _heuristic_scores(profile)
    ml_min, ml_max = min(ml_scores.values()), max(ml_scores.values())
    ml_range = ml_max - ml_min or 1.0
    normalized_ml = {label: (ml_scores.get(label, ml_min) - ml_min) / ml_range for label in LABELS}
    heuristic_max = max(structural.values()) or 1.0
    normalized_rules = {label: structural[label] / heuristic_max for label in LABELS}
    combined = {label: 0.42 * normalized_ml[label] + 0.58 * normalized_rules[label] for label in LABELS}
    ranked = sorted(combined.items(), key=lambda item: item[1], reverse=True)
    evidence = []
    if profile["FloorDiv"] and profile["While"]:
        evidence.append("Midpoint-style division inside a loop")
    if profile["HasNestedLoop"] and profile["SubscriptStores"]:
        evidence.append("Nested iteration with indexed writes")
    if profile["RecursiveCalls"]:
        evidence.append("Recursive self-calls")
    if profile["SliceNodes"]:
        evidence.append("Sequence slicing")
    if profile["QueueCalls"]:
        evidence.append("FIFO queue operations")
    if profile["StackCalls"]:
        evidence.append("Stack-style pop operations")
    if profile["HeapCalls"]:
        evidence.append("Priority-queue / heap operations")
    if profile["AddOps"] and profile["HeapCalls"]:
        evidence.append("Accumulated path-cost arithmetic")
    if profile["HasHeuristicPattern"]:
        evidence.append("Estimated cost combined with accumulated cost")
    if profile["Comprehensions"]:
        evidence.append("Comprehension-based construction")
    return {
        "prediction": ranked[0][0],
        "ranking": ranked,
        "evidence": evidence,
        "profile": profile,
        "confidence_note": "Ranking scores are relative model/rule scores, not calibrated probabilities.",
    }


def predict(code: str) -> tuple[str, list[tuple[str, float]]]:
    result = analyze_code(code)
    return result["prediction"], result["ranking"]


if __name__ == "__main__":
    print(json.dumps(train(), indent=2))


def estimate_complexity(code: str, algorithm: str) -> dict[str, str]:
    tree = ast.parse(code)
    loops = [node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))]
    nested_loops = any(
        any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(loop) if child is not loop)
        for loop in loops
    )
    has_break = any(isinstance(node, ast.Break) for node in ast.walk(tree))
    has_heap = any(
        isinstance(node, ast.Call) and (
            isinstance(node.func, ast.Name) and node.func.id in {"heappush", "heappop"}
            or isinstance(node.func, ast.Attribute) and node.func.attr in {"heappush", "heappop"}
        )
        for node in ast.walk(tree)
    )
    if algorithm == "Linear Search":
        values = ("O(1)", "O(n)", "O(n)")
        note = "The scan can stop at the first matching element; otherwise it may inspect every element."
    elif algorithm == "Binary Search":
        values = ("O(1)", "O(log n)", "O(log n)")
        note = "The midpoint comparison halves the remaining sorted search interval on each iteration."
    elif algorithm == "Bubble Sort":
        best = "O(n)" if has_break else "O(n²)"
        values = (best, "O(n²)", "O(n²)")
        note = "The best case is linear only when the implementation detects an already sorted array and exits early."
    elif algorithm == "Selection Sort":
        values = ("O(n²)", "O(n²)", "O(n²)")
        note = "It scans the unsorted suffix to select each next minimum, regardless of initial order."
    elif algorithm == "Insertion Sort":
        values = ("O(n)" if nested_loops else "O(n²)", "O(n²)", "O(n²)")
        note = "A sorted input requires only one comparison per item; reverse order causes repeated shifts."
    elif algorithm == "Merge Sort":
        values = ("O(n log n)", "O(n log n)", "O(n log n)")
        note = "The implementation divides the input recursively and merges each level in linear time."
    elif algorithm == "Quick Sort":
        values = ("O(n log n)", "O(n log n)", "O(n²)")
        note = "Balanced partitions give n log n behavior; repeatedly unbalanced partitions lead to quadratic time."
    elif algorithm in {"Breadth-First Search", "Depth-First Search"}:
        values = ("O(V + E)", "O(V + E)", "O(V + E)")
        note = "Assumes an adjacency-list graph and visits each reachable vertex and edge at most a constant number of times."
    elif algorithm == "Dijkstra's":
        values = (("O((V + E) log V)" if has_heap else "O(V²)"),) * 3
        note = "The estimate depends on the priority-queue implementation; a binary heap gives the stated heap-based bound."
    elif algorithm == "A* Search":
        values = ("Heuristic-dependent", "Heuristic-dependent", "O(b^d)")
        note = "A* depends on the heuristic and graph. In the worst case it may explore exponentially many states; b is branching factor and d is solution depth."
    else:
        values = ("Not available", "Not available", "Not available")
        note = "No complexity estimate is available for this prediction."
    if len(loops) > 1 and not nested_loops and algorithm in {"Linear Search", "Binary Search"}:
        note += " The snippet also contains multiple loops, so review helper routines when interpreting this estimate."
    return {"best": values[0], "average": values[1], "worst": values[2], "note": note}
