import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


# Make backend/ importable when running this file directly.
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))


# Allow tests to run even if food2vec is not installed by providing a stub module.
try:
    import VectorSearch as vs
except ModuleNotFoundError as exc:
    if exc.name != "food2vec":
        raise

    food2vec_module = types.ModuleType("food2vec")
    semantic_module = types.ModuleType("food2vec.semantic_nutrition")

    class _StubEstimator:
        def embed(self, _text: str):
            return [0.0, 0.0]

    semantic_module.Estimator = _StubEstimator
    food2vec_module.semantic_nutrition = semantic_module

    sys.modules["food2vec"] = food2vec_module
    sys.modules["food2vec.semantic_nutrition"] = semantic_module

    import VectorSearch as vs


class DummyEstimator:
    def embed(self, text: str):
        # Deterministic vectors for predictable ranking behavior in tests.
        mapping = {
            "chicken; garlic": [1.0, 0.0],
            "tomato; basil": [0.2, 0.8],
            "beef; soy sauce": [0.0, 1.0],
            "chicken; salt": [0.95, 0.05],
        }
        return mapping.get(text, [0.1, 0.1])


class TestVectorSearch(unittest.TestCase):
    log_stream = sys.stdout

    def _log(self, message: str):
        print(message, file=self.log_stream)

    def _print_ranked(self, title: str, ranked: list[dict]):
        self._log(f"\n{title}")
        for row in ranked:
            self._log(
                f"  rank={row['rank']} recipe_id={row['recipe_id']} "
                f"title={row['title']} sim={row['similarity']:.4f}"
            )

    def _build_large_test_records(self) -> list[dict]:
        records: list[dict] = [
            {
                "recipe_id": 1,
                "title": "Chicken Plate",
                "ingredient_text": "chicken; garlic",
                "directions": "Cook chicken",
                "link": "https://example.com/chicken",
                "source": "unit-test",
                "embedding": [1.0, 0.0],
            },
            {
                "recipe_id": 2,
                "title": "Tomato Plate",
                "ingredient_text": "tomato; basil",
                "directions": "Mix tomato",
                "link": "https://example.com/tomato",
                "source": "unit-test",
                "embedding": [0.0, 1.0],
            },
            {
                "recipe_id": 3,
                "title": "Beef Plate",
                "ingredient_text": "beef; soy sauce",
                "directions": "Cook beef",
                "link": "https://example.com/beef",
                "source": "unit-test",
                "embedding": [-1.0, 0.0],
            },
        ]

        # Add additional recipes so top-20 output is meaningful.
        for i in range(4, 36):
            if i % 3 == 0:
                embedding = [0.9 - (i * 0.01), 0.1 + (i * 0.005)]
                family = "chicken-family"
            elif i % 3 == 1:
                embedding = [0.1 + (i * 0.003), 0.9 - (i * 0.01)]
                family = "tomato-family"
            else:
                embedding = [-0.9 + (i * 0.01), 0.05]
                family = "beef-family"

            records.append(
                {
                    "recipe_id": i,
                    "title": f"Recipe {i} ({family})",
                    "ingredient_text": f"ingredient-{i}",
                    "directions": "Test directions",
                    "link": f"https://example.com/{i}",
                    "source": "unit-test",
                    "embedding": embedding,
                }
            )

        return records

    def _write_jsonl(self, records: list[dict]) -> str:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        with tmp as f:
            for rec in records:
                f.write(json.dumps(rec) + "\n")
        return tmp.name

    def test_normalize_ingredient_list(self):
        actual = vs._normalize_ingredient_list([" Chicken ", "", "Garlic", "  "])
        self.assertEqual(actual, "chicken; garlic")

    def test_load_vector_set_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            vs._load_vector_set("this_file_should_not_exist_12345.jsonl")

    def test_load_vector_set_invalid_json_raises(self):
        tmp = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8")
        with tmp as f:
            f.write("{not-valid-json}\n")

        with self.assertRaises(ValueError):
            vs._load_vector_set(tmp.name)

    def test_rank_recipes_returns_expected_top_order(self):
        records = self._build_large_test_records()
        vector_path = self._write_jsonl(records)

        query_scenarios = [
            {
                "name": "chicken-query",
                "query": ["Chicken", "Garlic"],
                "expected_recipe_id": 1,
            },
            {
                "name": "tomato-query",
                "query": ["Tomato", "Basil"],
                "expected_recipe_id": 2,
            },
            {
                "name": "beef-query",
                "query": ["Beef", "Soy Sauce"],
                "expected_recipe_id": 3,
            },
        ]

        with patch.object(vs, "Estimator", DummyEstimator):
            for scenario in query_scenarios:
                ranked = vs.rank_recipes_by_ingredients(
                    query_ingredients=scenario["query"],
                    vector_set_path=vector_path,
                    k=20,
                )

                self._print_ranked(
                    f"Top 20 ranking for {scenario['name']}: {'; '.join(scenario['query']).lower()}",
                    ranked,
                )

                self.assertEqual(len(ranked), 20)
                self.assertEqual(ranked[0]["recipe_id"], scenario["expected_recipe_id"])

                for i in range(len(ranked) - 1):
                    self.assertGreaterEqual(ranked[i]["similarity"], ranked[i + 1]["similarity"])

                # Quality guardrail: top should be noticeably above rank 20.
                similarity_gap = ranked[0]["similarity"] - ranked[-1]["similarity"]
                self._log(f"  similarity gap (rank1 - rank20): {similarity_gap:.4f}")
                self.assertGreater(similarity_gap, 0.4)

    def test_rank_recipes_invalid_inputs_raise(self):
        records = [
            {
                "recipe_id": 1,
                "title": "Chicken Plate",
                "ingredient_text": "chicken; garlic",
                "embedding": [1.0, 0.0],
            }
        ]
        vector_path = self._write_jsonl(records)

        with self.assertRaises(ValueError):
            vs.rank_recipes_by_ingredients([], vector_path, 1)

        with self.assertRaises(ValueError):
            vs.rank_recipes_by_ingredients(["chicken"], vector_path, 0)


if __name__ == "__main__":
    log_path = CURRENT_DIR / "test_vector_search_log.txt"
    with log_path.open("w", encoding="utf-8") as log_file:
        TestVectorSearch.log_stream = log_file
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestVectorSearch)
        runner = unittest.TextTestRunner(stream=log_file, verbosity=2)
        result = runner.run(suite)
        log_file.write(f"\nLog written to: {log_path}\n")

    raise SystemExit(0 if result.wasSuccessful() else 1)
