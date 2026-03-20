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

    def get_all_unique_names(self) -> models.QuerySet:
        """Gets all available unique topic names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`
        """
        return self.all().values_list("name", flat=True).distinct().order_by("name")

    def get_by_name(self, name: str) -> "Topic":
        """Gets the `Topic` record which matches the given name.

        Returns:
            The matched `Topic` record name

        Raises:
            `Topic.DoesNotExist`: If the `Topic` record
                cannot be matched to the given `name`.

        """
        return self.get(name=name)

    def get_filtered_unique_names_related_to_sub_theme(self, parent_sub_theme_id) -> models.QuerySet:
        """Gets all available unique sub themes with id and name fields that are related to the parent theme ID.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.filter(sub_theme_id=parent_sub_theme_id).values('id', 'name').distinct()


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

    def get_all_unique_names(self) -> TopicQuerySet:
        """Gets unique topic names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual topic names:
                Examples:
                    `<TopicQuerySet ['COVID-19', 'Influenza']>`
        """
        return self.get_queryset().get_all_unique_names()

    def does_topic_exist(self, *, topic: str) -> bool:
        """Given a topic name, checks this against the existing topic names.

        Returns:
            Bool: True or False based on the provided topic name existing in the db.
        """
        return self.get_all_names().filter(name=topic).exists()

    def get_by_name(self, name: str) -> "Topic":
        """Gets the `Topic` record which matches the given name.

        Returns:
            The matched `Topic` record name

        Raises:
            `Topic.DoesNotExist`: If the `Topic` record
                cannot be matched to the given `name`.

        """
        return self.get_queryset().get_by_name(name=name)

    def get_filtered_unique_names_related_to_sub_theme(self, parent_sub_theme_id: str) -> TopicQuerySet:
        """Gets all available themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': 'infectious_disease'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.get_queryset().get_filtered_unique_names_related_to_sub_theme(parent_sub_theme_id=parent_sub_theme_id)
