import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import build_index, evaluate_query, load_documents

class RetrievalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = load_documents()
        cls.index = build_index(cls.docs)
        cls.universe = {d["id"] for d in cls.docs}

    def test_and_intersection(self):
        result = evaluate_query("python AND data", self.index, self.universe)
        self.assertEqual(result, {1})

    def test_or_union(self):
        result = evaluate_query("machine OR java", self.index, self.universe)
        self.assertEqual(result, {3, 5})

    def test_not_complement(self):
        result = evaluate_query("NOT database", self.index, self.universe)
        self.assertEqual(result, self.universe - {4})

    def test_precedence_and_parentheses(self):
        result = evaluate_query("(python OR java) AND NOT web", self.index, self.universe)
        self.assertEqual(result, {5})

    def test_implicit_and(self):
        result = evaluate_query("information retrieval", self.index, self.universe)
        self.assertEqual(result, {9})

    def test_empty_query(self):
        with self.assertRaises(ValueError):
            evaluate_query("", self.index, self.universe)

if __name__ == "__main__":
    unittest.main()
