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





