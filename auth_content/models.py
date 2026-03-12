from django.db import models

# Create your models here.
from django.db import models
from wagtail.admin.panels import FieldPanel


class PermissionSet(models.Model):
    theme = models.CharField(max_length=255)
    sub_theme = models.CharField(max_length=255)
    topic = models.CharField(max_length=255)
    metric = models.CharField(max_length=255)
    geography_type = models.CharField(max_length=255)
    geography = models.CharField(max_length=255)
    

    panels = [
        FieldPanel('theme'),
        FieldPanel('sub_theme'),
        FieldPanel('topic'),
        FieldPanel('metric'),
        FieldPanel('geography_type'),
        FieldPanel('geography'),
    ]

    def __str__(self):
        return self.title