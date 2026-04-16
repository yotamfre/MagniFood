import json

from django.shortcuts import render

from Main.BM25Search import BM25Search
from Main.VectorSearch import rank_recipes_by_ingredients
from Main.rrf import RRF

# Create your views here.
bm25 = BM25Search()

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
            query = " ".join(submitted_ingredients)

            bm25_results = bm25.search_bm25(query, k=20)
            # vector_results = rank_recipes_by_ingredients(submitted_ingredients, k=20)
            # recipe_results = RRF(bm25_results, vector_results)
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