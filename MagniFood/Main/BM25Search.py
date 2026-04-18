from rank_bm25 import BM25Okapi
import numpy as np
import json
import re

def normalize_text(text):
    text = text.lower() # lowercase
    text = re.sub(r"[^\w\s]", " ", text) # replace punctuation symbols with " "
    text = re.sub(r"\s+", " ", text) # remove trailing whitespaces
    return text

def load_bm25_data(path, limit = None):
    records = []
    with open(path, "r", encoding="utf-8") as bm25_f:
        for idx, recipe in enumerate(bm25_f):
            if limit is not None and idx >= limit: # limit in case of overwhelming data length
                break
            recipe = recipe.strip()
            if not recipe:
                continue
            records.append(json.loads(recipe)) # json to dict
    return records

class BM25Search:
    def __init__(self):
        from Main.models import Recipe
        self.records = list(Recipe.objects.values("id", "title", "ingredients", "directions", "link", "source", "tokens"))
        self.corpus = [record["tokens"] for record in self.records]
        self.bm25 = BM25Okapi(self.corpus) if self.corpus else None

    @staticmethod
    def search_records_bm25(records, query, k=20):
        if not records:
            return []

        query = normalize_text(query)
        query_tokens = query.split()
        if not query_tokens:
            return []

        corpus = []
        normalized_records = []
        for rec in records:
            tokens = rec.get("tokens")
            if not isinstance(tokens, list):
                tokens = []
            tokens = [str(token).strip().lower() for token in tokens if str(token).strip()]
            if not tokens:
                # Fallback tokenization when tokens are missing for some rows.
                tokens = normalize_text(str(rec.get("ingredients") or "")).split()
            corpus.append(tokens)
            normalized_records.append(rec)

        if not corpus:
            return []

        bm25 = BM25Okapi(corpus)
        query_scores = bm25.get_scores(query_tokens)

        top_n = min(max(1, k), len(normalized_records))
        top_indices = np.argsort(query_scores)[-top_n:][::-1]

        results = []
        for rank_num, i in enumerate(top_indices, start=1):
            rec = normalized_records[i]
            results.append({
                "rank": rank_num,
                "recipe_id": rec.get("id"),
                "bm25_score": float(query_scores[i]),
                "title": rec.get("title", ""),
                "ingredient_text": rec.get("ingredients", ""),
                "directions": rec.get("directions", ""),
                "link": rec.get("link", ""),
                "source": rec.get("source", ""),
            })

        return results

    def search_bm25(self, query, k=20):
        if not self.records or self.bm25 is None:
            return []
        return BM25Search.search_records_bm25(self.records, query, k=k)

# if __name__ == "__main__":
#     bm25_eng = BM25Search("data/BM25_data.jsonl", limit=1000000)
#     results = bm25_eng.search_bm25("brown sugar vanilla milk")
#     for result in results:
#         print(f"#{result['rank']} - {result['title']} ({result['bm25_score']:.3f})", flush=True)