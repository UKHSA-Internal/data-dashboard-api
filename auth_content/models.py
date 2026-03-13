from django.db import models

from django.db import models
from wagtail.admin.panels import FieldPanel

from validation.enums.theme_and_topic_enums import ChildTheme, ParentTheme

def get_theme_child_map():
    """Returns an object of all parent to child mappings
    e.g.
    {
        infectious_disease: [vaccine_preventable, respiratory ....],
        extreme_event: [weather_alert, mortality_report...]
        ...
    }

    """

    theme_mapping = {}
    for parent in ParentTheme:
        # It has been assumed for now that validation and ingestion will catch if any parent name are not used in ChildTheme
        theme_mapping[parent.value] = ChildTheme[parent.name].return_tuple_list()

    return theme_mapping

class PermissionSet(models.Model):
    theme = models.CharField(
        choices=[(e.value, e.name.replace("_", " ").title()) for e in ParentTheme]
    )
    sub_theme = models.CharField(max_length=255, choices=[])
    topic = models.CharField(max_length=255)
    metric = models.CharField(max_length=255)
    geography_type = models.CharField(max_length=255)
    geography = models.CharField(max_length=255)

    
    panels = [
        FieldPanel("theme"),
        FieldPanel("sub_theme"),
        FieldPanel("topic"),
        FieldPanel("metric"),
        FieldPanel("geography_type"),
        FieldPanel("geography"),
    ]
    
    def __str__(self):
        return self.theme
