"""
This file contains the custom QuerySet and Manager classes associated with the `Topic` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""
from django.db import models


class TopicQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `TopicManager`"""

    def get_all_names(self) -> models.QuerySet:
        return self.all().values_list("name", flat=True)


class TopicManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> TopicQuerySet:
        return TopicQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> TopicQuerySet:
        return self.get_queryset().get_all_names()
