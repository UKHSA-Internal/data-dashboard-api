from django.db import models

from django.db import models
from wagtail.admin.panels import FieldPanel

from validation.enums.geographies_enums import GeographyType
from validation.enums.theme_and_topic_enums import ChildTheme, ParentTheme, Topic


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

    print(theme_mapping)
    return theme_mapping


def get_sub_theme_child_map():
    """Returns an object of all parent to child mappings
    e.g.
    {
        infectious_disease: [vaccine_preventable, respiratory ....],
        extreme_event: [weather_alert, mortality_report...]
        ...
    }

    """

    sub_theme_mapping = {}
    for topic in Topic:
        print("item: ", topic.value)

        # It has been assumed for now that validation and ingestion will catch if any parent name are not used in ChildTheme
        sub_theme_mapping[topic.name.lower(
        )] = Topic[topic.name].return_tuple_list()

    print(sub_theme_mapping)

    return sub_theme_mapping


def get_geography_type_geographies_map():
    """Returns an object of all parent to child mappings
    e.g.
    {
        infectious_disease: [vaccine_preventable, respiratory ....],
        extreme_event: [weather_alert, mortality_report...]
        ...
    }

    """

    geographies_mapping = {}
    for geographyType in GeographyType:
        # It has been assumed for now that validation and ingestion will catch if any parent name are not used in ChildTheme
        geographies_mapping[geographyType.value] = [
            geographyType.name].return_tuple_list()

    print(geographies_mapping)
    geographies_mapping = {}
    return geographies_mapping


class PermissionSet(models.Model):
    theme = models.CharField(
        choices=[(e.value, e.name.replace("_", " ").title())
                 for e in ParentTheme]
    )
    sub_theme = models.CharField(max_length=255, choices=[])
    topic = models.CharField(max_length=255, choices=[])
    metric = models.CharField(max_length=255, choices=[])
    geography_type = models.CharField(max_length=255, choices=[(
        e.value, e.value.replace("_", " ")) for e in GeographyType])
    geography = models.CharField(max_length=255, choices=[])

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
