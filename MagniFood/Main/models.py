from django.db import models


class Recipe(models.Model):

    title = models.TextField()
    ingredients = models.TextField()
    directions = models.TextField()
    link = models.URLField(max_length=255, blank=True, default="")
    source = models.TextField(blank=True, default="")
    ner = models.JSONField(default=list)
    tokens = models.JSONField(default=list)