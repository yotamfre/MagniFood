import ast
import re
import csv

from django.core.management.base import BaseCommand
from Main.models import Recipe

def normalize_text(text):
    text = text.lower() # lowercase
    text = re.sub(r"[^\w\s]", " ", text) # replace punctuation symbols with " "
    text = re.sub(r"\s+", " ", text) # remove any trailing whitespaces
    return text.strip()

def normalize_ner_list(raw): # normalize an ner list
    items = ast.literal_eval(raw) if isinstance(raw, str) else raw
    normed = []
    for ner in items:
        ner = ner.strip()
        if ner: # if can get words
            normed.append(normalize_text(ner)) # append it
    return normed


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str)

    def handle(self, *args, **options):
        Recipe.objects.all().delete()

        batch = []
        with open(options["csv_path"], newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                ner = normalize_ner_list(row.get("NER", "[]"))
                batch.append(
                    Recipe(
                    title=row.get("title", ""),
                    ingredients=row.get("ingredients", ""),
                    directions=row.get("directions", ""),
                    link=row.get("link", ""),
                    source=row.get("source", ""),
                    ner=ner,
                    tokens=" ".join(ner).split(),
                ))

        Recipe.objects.bulk_create(batch)
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(batch)} recipes."))
