from rank_bm25 import BM25Okapi
import pandas as pd
import numpy as np
import time
import re
import ast

def normalize_text(text):
    text = text.lower() # lowercase
    text = re.sub(r"[^\w\s]", " ", text) # replace punctuation symbols with " "
    text = re.sub(r"\s+", " ", text) # remove trailing whitespaces
    return text

def normalize_ner_list(ner_list): # normalize an ner list
    normed = []
    for ner in ner_list:
        ner = ner.strip()
        if ner: # if can get words
            normed.append(normalize_text(ner)) # append it
    return normed

def load_bm25_data(path, limit = None):
    df = pd.read_csv(path)
    if limit is not None:
        df = df.iloc[:limit]

    records = []
    for _, row in df.iterrows():
        try:
            ner_list = ast.literal_eval(row["NER"])
        except Exception:
            ner_list = []

        ner_norm = normalize_ner_list(ner_list)
        tokens = " ".join(ner_norm).split()
        records.append({                
            "title": row.get("title", ""),
            "ingredients": row.get("ingredients", ""),
            "directions": row.get("directions", ""),
            "link": row.get("link", ""),
            "source": row.get("source", ""),
            "tokens": tokens        
        })

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

if __name__ == "__main__":
    # build once for convenience
    print("loading data") # debug
    t0 = time.time()
    records = load_bm25_data("data/recipes_data.csv", limit = 500000)
    print(f"loaded {len(records)} records in {time.time() - t0:.2f} sec") # debug
    t1 = time.time()
    corpus = [record["tokens"] for record in records]
    print(f"corpus built in {time.time() - t1:.2f} sec") # debug
    t2 = time.time()
    bm25 = BM25Okapi(corpus)
    print(f"bm25 built in {time.time() - t2:.2f} sec\n") # debug

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