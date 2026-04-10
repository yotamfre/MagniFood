import json
from pathlib import Path
from typing import Any

import numpy as np
from food2vec.semantic_nutrition import Estimator


def _normalize_ingredient_list(ingredients: list[str]) -> str:
	cleaned = [str(x).strip().lower() for x in ingredients if str(x).strip()]
	return "; ".join(cleaned)


def _load_vector_set(vector_set_path: str) -> list[dict[str, Any]]:
	"""Load newline-delimited JSON recipe vectors from disk."""
	path = Path(vector_set_path)
	if not path.exists():
		raise FileNotFoundError(f"Vector set not found: {vector_set_path}")

	records: list[dict[str, Any]] = []
	with path.open("r", encoding="utf-8") as f:
		for line_number, line in enumerate(f, start=1):
			text = line.strip()
			if not text:
				continue
			try:
				rec = json.loads(text)
			except json.JSONDecodeError as exc:
				raise ValueError(f"Invalid JSON on line {line_number} in {vector_set_path}") from exc

			if "embedding" not in rec:
				continue
			records.append(rec)

	if not records:
		raise ValueError(f"No valid records with embeddings found in {vector_set_path}")
	return records


def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
	"""Compute cosine similarity of one vector against all rows in a matrix."""
	query_norm = np.linalg.norm(query_vec)
	matrix_norms = np.linalg.norm(matrix, axis=1)
	denom = query_norm * matrix_norms
	# Avoid division by zero when vectors are empty or invalid.
	denom = np.where(denom == 0, 1e-12, denom)
	return (matrix @ query_vec) / denom


def rank_recipes_by_ingredients(
	query_ingredients: list[str],
	vector_set_path: str,
	k: int,
) -> list[dict[str, Any]]:
	"""
	Rank recipes by semantic similarity to user-provided ingredients.

	Args:
		query_ingredients: List of ingredient strings from user input.
		vector_set_path: Path to JSONL vector set produced by semantic_vec.ipynb.
		k: Number of top recipes to return.

	Returns:
		Ranked list of recipe dictionaries with similarity score.
	"""
	if not query_ingredients:
		raise ValueError("query_ingredients must contain at least one ingredient string")
	if k <= 0:
		raise ValueError("k must be a positive integer")

	records = _load_vector_set(vector_set_path)

	query_text = _normalize_ingredient_list(query_ingredients)
	estimator = Estimator()
	query_embedding = np.asarray(estimator.embed(query_text), dtype=float)

	embeddings = np.asarray([rec["embedding"] for rec in records], dtype=float)
	similarities = _cosine_similarity(query_embedding, embeddings)

	top_k = min(k, len(records))
	top_indices = np.argsort(-similarities)[:top_k]

	ranked: list[dict[str, Any]] = []
	for rank, idx in enumerate(top_indices, start=1):
		rec = records[int(idx)]
		ranked.append(
			{
				"rank": rank,
				"similarity": float(similarities[int(idx)]),
				"recipe_id": rec.get("recipe_id"),
				"title": rec.get("title"),
				"ingredient_text": rec.get("ingredient_text"),
				"directions": rec.get("directions"),
				"link": rec.get("link"),
				"source": rec.get("source"),
			}
		)

	return ranked

