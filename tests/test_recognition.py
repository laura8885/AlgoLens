import io
import keyword
import tokenize
import unittest

import pandas as pd

from src.recognition import DATASET_PATH, analyze_code, estimate_complexity


class RecognitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = pd.read_csv(DATASET_PATH)

    def rename_identifiers(self, code):
        tokens = []
        replacements = {}
        previous = ""
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            if token.type == tokenize.NAME and not keyword.iskeyword(token.string) and previous != ".":
                replacements.setdefault(token.string, f"identifier_{len(replacements)}")
                token = token._replace(string=replacements[token.string])
            tokens.append(token)
            previous = token.string
        return tokenize.untokenize(tokens)

    def test_reference_examples_match_their_curated_labels(self):
        for row in self.dataset.itertuples():
            with self.subTest(sample=row.sample_id):
                self.assertEqual(analyze_code(row.code)["prediction"], row.algorithm)

    def test_identifier_renaming_does_not_change_reference_predictions(self):
        for row in self.dataset.itertuples():
            with self.subTest(sample=row.sample_id):
                renamed = self.rename_identifiers(row.code)
                self.assertEqual(analyze_code(renamed)["prediction"], row.algorithm)

    def test_algorithm_name_in_function_and_docstring_is_not_used(self):
        code = "\"\"\"Bubble Sort implementation\"\"\"\ndef bubble_sort(bubble, target):\n    for i in range(len(bubble) - 1):\n        min_index = i\n        for j in range(i + 1, len(bubble)):\n            if bubble[j] < bubble[min_index]:\n                min_index = j\n        if min_index != i:\n            bubble[i], bubble[min_index] = bubble[min_index], bubble[i]\n    return bubble\n"
        self.assertEqual(analyze_code(code)["prediction"], "Selection Sort")

    def test_all_samples_have_source_attribution(self):
        self.assertTrue(self.dataset["source_url"].str.startswith("https://raw.githubusercontent.com/").all())
        self.assertTrue(self.dataset["license"].eq("MIT").all())

    def test_complexity_estimate_for_pasted_binary_search(self):
        code = """def locate(data, value):
    left, right = 0, len(data) - 1
    while left <= right:
        middle = (left + right) // 2
        if data[middle] == value:
            return middle
        if data[middle] < value:
            left = middle + 1
        else:
            right = middle - 1
    return -1
"""
        estimate = estimate_complexity(code, "Binary Search")
        self.assertEqual(estimate["best"], "O(1)")
        self.assertEqual(estimate["average"], "O(log n)")
        self.assertEqual(estimate["worst"], "O(log n)")

    def test_complexity_estimate_detects_bubble_sort_early_exit(self):
        code = """def arrange(data):
    for i in range(len(data)):
        changed = False
        for j in range(len(data) - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                changed = True
        if not changed:
            break
    return data
"""
        estimate = estimate_complexity(code, "Bubble Sort")
        self.assertEqual(estimate["best"], "O(n)")
        self.assertEqual(estimate["average"], "O(n²)")
        self.assertEqual(estimate["worst"], "O(n²)")


if __name__ == "__main__":
    unittest.main()
