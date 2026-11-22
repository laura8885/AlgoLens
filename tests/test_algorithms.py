import unittest

from src.algorithms import array_search_trace, graph_trace, sorting_trace, SAMPLE_GRAPH


class AlgorithmTraceTests(unittest.TestCase):
    def test_sorting_algorithms_finish_sorted(self):
        values = [7, 2, 9, 1, 5, 2]
        for name in ["Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort", "Quick Sort"]:
            with self.subTest(name=name):
                trace = sorting_trace(name, values)
                self.assertEqual(trace[-1]["array"], sorted(values))

    def test_linear_search_finds_target(self):
        trace = array_search_trace("Linear Search", [4, 8, 2, 9], 2)
        self.assertEqual(trace[-1]["found"], [2])

    def test_binary_search_finds_target(self):
        trace = array_search_trace("Binary Search", [4, 8, 2, 9], 8)
        self.assertEqual(trace[-1]["found"], [2])

    def test_graph_algorithms_find_a_path(self):
        for name in ["Breadth-First Search", "Depth-First Search", "Dijkstra's", "A* Search"]:
            with self.subTest(name=name):
                trace = graph_trace(name, SAMPLE_GRAPH, "A", "F")
                self.assertTrue(trace[-1]["path"])
                self.assertEqual(trace[-1]["path"][0], "A")
                self.assertEqual(trace[-1]["path"][-1], "F")


if __name__ == "__main__":
    unittest.main()
