import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.visualizations import trace_steps, search_trace


class VisualizationTests(unittest.TestCase):
    def test_bubble_sort_finishes_sorted(self):
        self.assertEqual(trace_steps('bubble_sort', [4, 1, 3, 2])[-1], [1, 2, 3, 4])

    def test_insertion_sort_finishes_sorted(self):
        self.assertEqual(trace_steps('insertion_sort', [4, 1, 3, 2])[-1], [1, 2, 3, 4])

    def test_quick_sort_finishes_sorted(self):
        self.assertEqual(trace_steps('quick_sort', [4, 1, 3, 2])[-1], [1, 2, 3, 4])

    def test_merge_sort_finishes_sorted(self):
        self.assertEqual(trace_steps('merge_sort', [4, 1, 3, 2])[-1], [1, 2, 3, 4])

    def test_binary_search_finds_target(self):
        steps = search_trace('binary_search', [1, 3, 5, 7, 9], 7)
        self.assertTrue(any(found for _, found in steps))

    def test_linear_search_finds_target(self):
        steps = search_trace('linear_search', [9, 3, 7, 1], 7)
        self.assertTrue(any(found for _, found in steps))


if __name__ == '__main__':
    unittest.main()
