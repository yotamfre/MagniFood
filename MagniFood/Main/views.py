import json

from django.shortcuts import render

# Create your views here.

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
        recipe_results = [
            {
                "name": "Creamy Garlic Chicken Pasta",
                "image": "https://images.unsplash.com/photo-1521389508051-d7ffb5dc8f93?auto=format&fit=crop&w=900&q=80",
                "link": "https://example.com/creamy-garlic-chicken-pasta",
            },
            {
                "name": "Herb Roasted Vegetable Bowl",
                "image": "https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=80",
                "link": "https://example.com/herb-roasted-vegetable-bowl",
            },
            {
                "name": "Spicy Tomato Soup",
                "image": "https://images.unsplash.com/photo-1547592180-6c1b8c1f4b9c?auto=format&fit=crop&w=900&q=80",
                "link": "https://example.com/spicy-tomato-soup",
            },
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