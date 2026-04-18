from django.db import models
from pgvector.django import VectorField


class Recipe(models.Model):

    title = models.TextField()
    ingredients = models.TextField()
    directions = models.TextField()
    link = models.URLField(max_length=255, blank=True, default="")
    source = models.TextField(blank=True, default="")
    ner = models.JSONField(default=list)
    tokens = models.JSONField(default=list)
    # Vector field for semantic search (this dataset uses 300-d food2vec embeddings)
    embedding = VectorField(dimensions=300, null=True, blank=True)
