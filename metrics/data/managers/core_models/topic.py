"""
This file contains the custom QuerySet and Manager classes associated with the `Topic` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class TopicQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `TopicManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available topic names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`

        """
        return self.all().values_list("name", flat=True)


class TopicManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> TopicQuerySet:
        return TopicQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> TopicQuerySet:
        """Gets all available topic names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`

        """
        return self.get_queryset().get_all_names()

    def does_topic_exist(self, topic) -> bool:
        """Given a topic name, checks this against the existing topic names.

        Returns:
            Bool: True or False based on the provided topic name existing in the db.
        """
        return self.get_queryset().get_all_names().filter(name=topic).exists()
