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
        self.bm25 = BM25Okapi(self.corpus)

    def search_bm25(self, query, k=20):
        query = normalize_text(query) # normalize
        query_tokens = query.split() # tokenize
        query_scores = self.bm25.get_scores(query_tokens) # process with bm25

        top_indices = np.argsort(query_scores)[-k:][::-1]

        results = []
        for rank_num, i in enumerate(top_indices, start=1):
            results.append({
                "rank": rank_num,
                "recipe_id": i,  
                "bm25_score": query_scores[i], 
                "title": self.records[i]["title"], 
                "ingredient_text": self.records[i]["ingredients"],
                "directions": self.records[i]["directions"],
                "link": self.records[i]["link"],
                "source": self.records[i]["source"]
            })
        
        return results # top k results

# if __name__ == "__main__":
#     bm25_eng = BM25Search("data/BM25_data.jsonl", limit=1000000)
#     results = bm25_eng.search_bm25("brown sugar vanilla milk")
#     for result in results:
#         print(f"#{result['rank']} - {result['title']} ({result['bm25_score']:.3f})", flush=True)