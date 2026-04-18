# MagniFood Database Setup Guide

## 1. Update your `.env` file

Replace the placeholder password in `.env` with your actual Neon password:

```
DATABASE_URL=postgresql://neondb_owner:YOUR_ACTUAL_PASSWORD@ep-rough-bread-amx54a00.c-5.us-east-1.aws.neon.tech/neondb?sslmode=require
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `pgvector` - PostgreSQL vector extension support
- `django-pgvector` - Django ORM integration for vectors
- `python-dotenv` - Load environment variables from `.env`

## 3. Enable pgvector Extension in Neon

In your Neon project dashboard or via psql:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Or run this Django management command (after migrations):
```bash
python manage.py shell
>>> from django.db import connection
>>> with connection.cursor() as cursor:
>>>     cursor.execute('CREATE EXTENSION IF NOT EXISTS vector')
>>> exit()
```

## 4. Create and Run Migrations

```bash
# Generate migrations for the new embedding field
python manage.py makemigrations

# Apply migrations to Neon database
python manage.py migrate
```

## 5. Load Recipe Data

Once your data is ready in the `data/` folder, you can load it:

```bash
python manage.py load_recipes  # Update this command in management/commands/load_recipes.py
```

## 6. Update Your Data Loading Script

The Recipe model now has:
- **embedding** (VectorField): Store 1536-dimensional vector embeddings from your vectorized recipe data
- Other fields: title, ingredients, directions, link, source, ner, tokens

When loading data from `data/recipes_data_reduced.csv` and `data/recipe_vectors_reduced.jsonl`:

```python
from django.db import models
from Main.models import Recipe

# Example: loading with vectors
recipe = Recipe.objects.create(
    title="...",
    ingredients="...",
    directions="...",
    link="...",
    source="...",
    ner=[...],
    tokens=[...],
    embedding=[0.1, 0.2, 0.3, ...]  # 1536-dimensional vector
)
```

## 7. Testing the Connection

```bash
python manage.py shell
>>> from Main.models import Recipe
>>> Recipe.objects.all().count()  # Should return 0 initially
```

## 8. Vector Search Queries

You can now perform vector similarity searches:

```python
from django.db.models import F
from pgvector.django import L2Distance, MaxInnerProduct, CosineDistance
from Main.models import Recipe

# L2 distance (Euclidean)
Recipe.objects.all().annotate(
    distance=L2Distance('embedding', [0.1, 0.2, ...])
).order_by('distance')[:5]

# Cosine similarity
Recipe.objects.all().annotate(
    distance=CosineDistance('embedding', [0.1, 0.2, ...])
).order_by('distance')[:5]

# Max inner product
Recipe.objects.all().annotate(
    similarity=MaxInnerProduct('embedding', [0.1, 0.2, ...])
).order_by('-similarity')[:5]
```

## 9. Environment Setup Checklist

- [ ] Update `.env` with actual Neon password
- [ ] Run `pip install -r requirements.txt`
- [ ] Enable pgvector extension in Neon
- [ ] Run `python manage.py migrate`
- [ ] Test database connection with Django shell
- [ ] Load recipe data with embedding vectors

## Troubleshooting

**Connection refused?**
- Verify your Neon password is correct
- Check internet connection
- Ensure SSL mode is enabled (`?sslmode=require`)

**pgvector extension not found?**
- Ensure you're using Neon's PostgreSQL (has pgvector available)
- Run the CREATE EXTENSION command

**Vector dimension mismatch?**
- The embedding field is configured for 1536 dimensions
- Adjust if your embeddings are different size

