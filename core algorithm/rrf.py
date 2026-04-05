def RRF(list1: list[dict], list2: list[dict], k: int = 60) -> list[dict]:
    scores = {}
    records = {}

    for i, doc in enumerate(list1):
        rid = doc["recipe_id"]
        scores[rid] = scores.get(rid, 0) + (1 / (k + (i + 1)))
        records[rid] = doc

    for i, doc in enumerate(list2):
        rid = doc["recipe_id"]
        scores[rid] = scores.get(rid, 0) + (1 / (k + (i + 1)))
        if rid not in records:
            records[rid] = doc

    ranked_ids = sorted(scores, key=lambda rid: scores[rid], reverse=True)

    results = []
    for rank, rid in enumerate(ranked_ids, start=1):
        entry = dict(records[rid])
        entry["rank"] = rank
        entry["rrf_score"] = scores[rid]
        results.append(entry)

    return results

if __name__ == "__main__":
    bm25_ranks = [
        {"recipe_id": 1, "title": "No-Bake Nut Cookies", "bm25_score": 5},
        {"recipe_id": 2, "title": "Jewell Ball'S Chicken", "bm25_score": 4},
        {"recipe_id": 3, "title": "Creamy Corn", "bm25_score": 3},
        {"recipe_id": 4, "title": "Chicken Funny", "bm25_score": 2},
        {"recipe_id": 5, "title": "Reeses Cups(Candy)", "bm25_score": 1}
    ]

    vector_ranks = [
        {"recipe_id": 3, "title": "Creamy Corn", "similarity": 0.9},
        {"recipe_id": 1, "title": "No-Bake Nut Cookies", "similarity": 0.8},
        {"recipe_id": 6, "title": "Cheeseburger Potato Soup", "similarity": 0.7},
        {"recipe_id": 2, "title": "Jewell Ball'S Chicken", "similarity": 0.6},
        {"recipe_id": 7, "title": "Rhubarb Coffee Cake", "similarity": 0.5}
    ]

    fused_ranks = RRF(bm25_ranks, vector_ranks, k = 60)

    for r in fused_ranks:
        print(f"Rank {r['rank']}: {r['title']} - RRF: {r['rrf_score']}")



