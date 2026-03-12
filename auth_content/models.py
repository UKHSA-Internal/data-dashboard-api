from django.db import models

# Create your models here.
from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet


class AuthFeature(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
    ]

    def __str__(self):
        return self.title