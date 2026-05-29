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

    def get_name_by_id(self, topic_id: int) -> str | None:
        """
        Gets the topic name which matches the given theme id.

        Args:
            topic_id: The ID of the topic to look up

        Returns:
            The topic name if found, None otherwise

        Examples:
            >>> TopicQuerySet.get_name_by_id(1)
            'COVID-19'
            >>> TopicQuerySet.get_name_by_id(999)
            None
        """
        return self.filter(id=topic_id).values_list("name", flat=True).first()

    def get_id_by_name(
        self, theme_name: str, sub_theme_name: str, topic_name: str
    ) -> tuple[int, int, int]:
        """
        Gets the theme, sub-theme and topic IDs matching the given names.

        Args:
            theme_name: The name of the parent theme
            sub_theme_name: The name of the parent sub-theme
            topic_name: The name of the topic to look up

        Returns:
            A tuple of (theme_id, sub_theme_id, topic_id) if found,
            or the tuple (-2, -2, -2) otherwise
        """
        record = self.filter(
            sub_theme__theme__name=theme_name,
            sub_theme__name=sub_theme_name,
            name=topic_name,
        ).first()

        if record:
            return (
                int(record.sub_theme.theme_id),
                int(record.sub_theme_id),
                int(record.id),
            )

        return (
            -2,
            -2,
            -2,
        )

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

    def get_filtered_unique_names_related_to_sub_theme(
        self, parent_sub_theme_id
    ) -> models.QuerySet:
        """Gets all available topics with id and name fields that are related to the parent sub_theme ID.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': '6-in-1'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return (
            self.filter(sub_theme_id=parent_sub_theme_id)
            .values("id", "name")
            .distinct()
        )

    def get_all_names_and_ids(self) -> models.QuerySet:
        """Gets all available topics with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<QuerySet [{'id': 1, 'name': '6-in-1'}, {'id': 2, 'name': 'respiratory'}, ...]>`
        """
        return self.all().values("id", "name").distinct()


class TopicManager(models.Manager):
    """Custom model manager class for the `Metric` model."""

    def get_queryset(self) -> TopicQuerySet:
        return TopicQuerySet(model=self.model, using=self.db)

    def get_name_by_id(self, topic_id: int) -> str | None:
        """Gets the topic name which matches the given topic id.

        Args:
            topic_id: The ID of the theme to look up

        Returns:
            The topic name if found, None otherwise

        Examples:
            >>> TopicManager.get_name_by_id(1)
            'COVID-19'
            >>> TopicManager.get_name_by_id(999)
            None
        """
        return self.get_queryset().get_name_by_id(topic_id)

    def get_id_by_name(
        self, theme_name: str, sub_theme_name: str, topic_name: str
    ) -> tuple[int, int, int]:
        """Gets the theme, sub-theme and topic IDs matching the given names.

        Args:
            theme_name: The name of the parent theme
            sub_theme_name: The name of the parent sub-theme
            topic_name: The name of the topic to look up

        Returns:
            A tuple of (theme_id, sub_theme_id, topic_id) if found,
            or (-2, -2, -2) if not found.

        Examples:
            >>> TopicManager.get_id_by_name("Infectious disease", "Respiratory", "COVID-19")
            (1, 2, 3)
            >>> TopicManager.get_id_by_name("Unknown", "Unknown", "Unknown")
            (-2, -2, -2)
        """
        return self.get_queryset().get_id_by_name(
            theme_name, sub_theme_name, topic_name
        )

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

    def get_filtered_unique_names_related_to_sub_theme(
        self, parent_sub_theme_id: str
    ) -> TopicQuerySet:
        """Gets all available topics with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<TopicSet [{'id': 1, 'name': '6-in-1'}, {'id': 2, 'name': 'MMR1'}, ...]>`
        """
        return self.get_queryset().get_filtered_unique_names_related_to_sub_theme(
            parent_sub_theme_id=parent_sub_theme_id
        )

    def get_all_names_and_ids(self) -> TopicQuerySet:
        """Gets all available themes with id and name fields.

        Returns:
            QuerySet: A queryset containing dictionaries with id and name:
                Examples:
                    `<TopicQuerySet [{'id': 1, 'name': '6-in-1'}, {'id': 2, 'name': 'MMR1'}, ...]>`
        """
        return self.get_queryset().get_all_names_and_ids()
