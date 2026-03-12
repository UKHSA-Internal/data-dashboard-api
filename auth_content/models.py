from django.db import models

# Create your models here.
from django.db import models
from wagtail.admin.panels import FieldPanel

from validation.enums.theme_and_topic_enums import ChildTheme, ParentTheme


class PermissionSet(models.Model):
    theme = models.CharField(
        choices=[(e.value, e.name.replace("_", " ").title()) for e in ParentTheme]
    )
    sub_theme = models.CharField(
        choices=ChildTheme["INFECTIOUS_DISEASE"].return_tuple_list()
    )
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