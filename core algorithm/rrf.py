def RRF(list1: list[str], list2: list[str], k: int) -> list[str]:
    scores = {}

    for i, doc in enumerate(list1):
        scores[doc] = scores.get(doc, 0) + (1 / (k + (i+1)))
    for i, doc in enumerate(list2):
        scores[doc] = scores.get(doc, 0) + (1 / (k + (i+1)))
    
    return sorted(scores, key=lambda d: scores[d], reverse=True)
                                        


list1 = ["A", "B", "C", "D", "E"]
list2 = ["B", "A", "E", "D", "C"]

print(RRF(list1, list2, 60))

