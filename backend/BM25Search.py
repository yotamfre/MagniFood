from rank_bm25 import BM25Okapi
import numpy as np
import time
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

def run_bm25(query, bm25, records, k):
    query = normalize_text(query) # normalize
    tokens = query.split() # tokenize
    scores = bm25.get_scores(tokens) # process with bm25

    top_indices = np.argsort(scores)[-k:][::-1]

    results = []
    for rank_num, i in enumerate(top_indices, start=1):
        results.append({
            "rank": rank_num,
            "recipe_id": i,  
            "bm25_score": scores[i], 
            "title": records[i]["title"], 
            "ingredient_text": records[i]["ingredients"],
            "directions": records[i]["directions"],
            "link": records[i]["link"],
            "source": records[i]["source"]
        })
    
    return results # top k results

# build once for convenience
# records = load_bm25_data("data/BM25_data.jsonl", limit = 500000)
# corpus = [record["tokens"] for record in records]
# bm25 = BM25Okapi(corpus)

if __name__ == "__main__":
    # build once for convenience
    print("loading data")
    t0 = time.time()
    records = load_bm25_data("data/BM25_data.jsonl", limit = 500000)
    print(f"loaded {len(records)} records in {time.time() - t0:.2f} sec")
    t1 = time.time()
    corpus = [record["tokens"] for record in records]
    print(f"corpus built in {time.time() - t1:.2f} sec")
    t2 = time.time()
    bm25 = BM25Okapi(corpus)
    print(f"bm25 built in {time.time() - t2:.2f} sec\n")

    # testing different queries
    query = "brown sugar vanilla milk"
    t3 = time.time()
    results = run_bm25(query, bm25, records, k = 5)
    print(f"query 1 results in {time.time() - t3:.2f} sec")
    print(f"top 5 results for: {query}")
    for result in results:
        print(f"#{result['rank']} - score: {result['bm25_score']} - {result['title']}")

    query = "chicken broth salt sugar"
    t4 = time.time()
    results = run_bm25(query, bm25, records, k = 5)
    print(f"query 2 results in {time.time() - t4:.2f} sec")
    print(f"top 5 results for: {query}")
    for result in results:
        print(f"#{result['rank']} - score: {result['bm25_score']} - {result['title']}")

    query = "goat chickpea thyme"
    t5 = time.time()
    results = run_bm25(query, bm25, records, k = 5)
    print(f"query 3 results in {time.time() - t5:.2f} sec")
    print(f"top 5 results for: {query}")
    for result in results:
        print(f"#{result['rank']} - score: {result['bm25_score']} - {result['title']}")

    query = "yogurt honey orange"
    t6 = time.time()
    results = run_bm25(query, bm25, records, k = 5)
    print(f"query 4 results in {time.time() - t6:.2f} sec")
    print(f"top 5 results for: {query}")
    for result in results:
        print(f"#{result['rank']} - score: {result['bm25_score']} - {result['title']}")

    query = "tomato basil mozarella olive oil"
    t7 = time.time()
    results = run_bm25(query, bm25, records, k = 5)
    print(f"query 5 results in {time.time() - t7:.2f} sec")
    print(f"top 5 results for: {query}")
    for result in results:
        print(f"#{result['rank']} - score: {result['bm25_score']} - {result['title']}")