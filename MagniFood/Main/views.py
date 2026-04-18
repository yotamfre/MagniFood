import json
import os

from django.shortcuts import render
from django.db.models import Q

from Main.BM25Search import BM25Search
from Main.models import Recipe

# Create your views here.


def hybrid_bm25_search(ingredients: list[str], k: int = 20):
    terms = [str(ingredient).strip().lower() for ingredient in ingredients if str(ingredient).strip()]
    if not terms:
        return []

    query = " ".join(terms)
    candidate_limit = int(os.getenv("HYBRID_BM25_CANDIDATE_LIMIT", "5000"))

    filters = Q()
    for term in terms:
        filters |= Q(title__icontains=term)
        filters |= Q(ingredients__icontains=term)
        filters |= Q(ner__icontains=term)

    candidates = list(
        Recipe.objects.filter(filters)
        .values("id", "title", "ingredients", "directions", "link", "source", "tokens", "embedding")[:candidate_limit]
    )

    return BM25Search.search_records_bm25(candidates, query, k=k)


def hybrid_vector_rerank(ingredients: list[str], candidates: list[dict], k: int = 20):
    if not candidates:
        return []

    from Main.VectorSearch import rank_recipes_by_ingredients

    return rank_recipes_by_ingredients(ingredients, k=k, records=candidates)

def home(request):
    submitted_ingredients = []
    recipe_results = []
    show_results = False

    if request.method == "POST":
        show_results = True
        raw_ingredients = request.POST.get("ingredients_json", "[]")
        try:
            parsed_ingredients = json.loads(raw_ingredients)
            if isinstance(parsed_ingredients, list):
                submitted_ingredients = [
                    str(ingredient).strip()
                    for ingredient in parsed_ingredients
                    if str(ingredient).strip()
                ]
        except json.JSONDecodeError:
            submitted_ingredients = []

        # TODO: Insert your recipe query logic here.
        # Use submitted_ingredients as the input list of ingredient strings.
        # Replace this placeholder with the list of recipe dictionaries your
        # search logic returns.
        if submitted_ingredients:
            bm25_results = hybrid_bm25_search(submitted_ingredients, k=20)
            if os.getenv("ENABLE_VECTOR_RERANK", "false").lower() == "true":
                from Main.rrf import RRF

                vector_results = hybrid_vector_rerank(submitted_ingredients, bm25_results, k=20)
                bm25_results = RRF(bm25_results, vector_results)

            recipe_results = [
                {
                    "name": r["title"],
                    "link": "//" + r["link"] if r["link"] and not r["link"].startswith("http") else r["link"],
                    "image": "",
                }
                for r in bm25_results
            ]

    return render(
        request,
        "home.html",
        {
            "submitted_ingredients": submitted_ingredients,
            "recipe_results": recipe_results,
            "show_results": show_results,
        },
    )