import ast
import csv
import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from Main.models import Recipe

def safe_literal_list(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return []
        try:
            parsed = ast.literal_eval(text)
            return parsed if isinstance(parsed, list) else []
        except (ValueError, SyntaxError):
            return []
    return []


def recipe_key(title, link):
    return (str(title or "").strip(), str(link or "").strip())


def stream_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            text = line.strip()
            if not text:
                continue
            try:
                yield json.loads(text)
            except json.JSONDecodeError:
                continue


def resolve_input_path(raw_path):
    path = Path(raw_path)
    if path.is_absolute():
        return path
    # settings.BASE_DIR points to the Django project folder (MagniFood/MagniFood)
    # Data files live one level above, under MagniFood/data.
    return (Path(settings.BASE_DIR).parent / path).resolve()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default="data/recipes_data_reduced.csv",
            help="Path to CSV file with base recipe records",
        )
        parser.add_argument(
            "--bm25",
            type=str,
            default="data/BM25_data.jsonl",
            help="Path to BM25 JSONL file with tokens/doc_text",
        )
        parser.add_argument(
            "--vectors",
            type=str,
            default="data/recipe_vectors_reduced.jsonl",
            help="Path to vectors JSONL file with embeddings",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Batch size for bulk create/update operations",
        )
        parser.add_argument(
            "--keep-existing",
            action="store_true",
            help="Do not delete existing recipes before import; skip CSV inserts and only update BM25/embeddings",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Optional limit on number of CSV rows to import (for testing)",
        )

    def handle(self, *args, **options):
        csv_path = resolve_input_path(options["csv"])
        bm25_path = resolve_input_path(options["bm25"])
        vectors_path = resolve_input_path(options["vectors"])
        batch_size = max(1, int(options["batch_size"]))
        limit = options.get("limit")

        for required_path in (csv_path, bm25_path, vectors_path):
            if not required_path.exists():
                raise FileNotFoundError(f"Missing input file: {required_path}")

        if not options["keep_existing"]:
            deleted_count, _ = Recipe.objects.all().delete()
            self.stdout.write(f"Deleted existing recipes: {deleted_count}")

        created = 0
        if options["keep_existing"]:
            self.stdout.write("Keeping existing base recipes; skipping CSV inserts.")
        else:
            create_batch = []
            with open(csv_path, newline="", encoding="utf-8") as f:
                for idx, row in enumerate(csv.DictReader(f)):
                    if limit is not None and idx >= limit:
                        break

                    ner = [str(x).strip() for x in safe_literal_list(row.get("NER", "[]")) if str(x).strip()]
                    create_batch.append(
                        Recipe(
                            title=str(row.get("title") or ""),
                            ingredients=str(row.get("ingredients") or ""),
                            directions=str(row.get("directions") or ""),
                            link=str(row.get("link") or ""),
                            source=str(row.get("source") or ""),
                            ner=ner,
                            tokens=[],
                            embedding=None,
                        )
                    )

                    if len(create_batch) >= batch_size:
                        Recipe.objects.bulk_create(create_batch, batch_size=batch_size)
                        created += len(create_batch)
                        self.stdout.write(f"Loaded recipes: {created}")
                        create_batch = []

                if create_batch:
                    Recipe.objects.bulk_create(create_batch, batch_size=batch_size)
                    created += len(create_batch)

            self.stdout.write(self.style.SUCCESS(f"Loaded base recipes from CSV: {created}"))

        id_by_key = {
            recipe_key(title, link): recipe_id
            for recipe_id, title, link in Recipe.objects.values_list("id", "title", "link")
        }

        bm25_updates = []
        bm25_updated = 0
        for rec in stream_jsonl(bm25_path):
            rid = id_by_key.get(recipe_key(rec.get("title"), rec.get("link")))
            if rid is None:
                continue

            tokens = rec.get("tokens")
            if not isinstance(tokens, list):
                tokens = []
            tokens = [str(t).strip() for t in tokens if str(t).strip()]

            bm25_updates.append(Recipe(id=rid, tokens=tokens))
            if len(bm25_updates) >= batch_size:
                Recipe.objects.bulk_update(bm25_updates, ["tokens"], batch_size=batch_size)
                bm25_updated += len(bm25_updates)
                self.stdout.write(f"Updated BM25 tokens: {bm25_updated}")
                bm25_updates = []

        if bm25_updates:
            Recipe.objects.bulk_update(bm25_updates, ["tokens"], batch_size=batch_size)
            bm25_updated += len(bm25_updates)

        self.stdout.write(self.style.SUCCESS(f"Updated BM25 tokens: {bm25_updated}"))

        vector_updates = []
        vectors_updated = 0
        for rec in stream_jsonl(vectors_path):
            rid = id_by_key.get(recipe_key(rec.get("title"), rec.get("link")))
            if rid is None:
                continue

            embedding = rec.get("embedding")
            if not isinstance(embedding, list):
                continue

            vector_updates.append(Recipe(id=rid, embedding=embedding))
            if len(vector_updates) >= batch_size:
                Recipe.objects.bulk_update(vector_updates, ["embedding"], batch_size=batch_size)
                vectors_updated += len(vector_updates)
                self.stdout.write(f"Updated vector embeddings: {vectors_updated}")
                vector_updates = []

        if vector_updates:
            Recipe.objects.bulk_update(vector_updates, ["embedding"], batch_size=batch_size)
            vectors_updated += len(vector_updates)

        self.stdout.write(self.style.SUCCESS(f"Updated vector embeddings: {vectors_updated}"))

        total = Recipe.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Import completed. Total recipes in DB: {total}"))
