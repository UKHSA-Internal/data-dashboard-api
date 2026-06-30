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

    def get_theme_sub_theme_topic_and_metric_id_by_name(
        self,
        theme_name: str,
        sub_theme_name: str,
        topic_name: str,
        metric_name: str,
    ) -> tuple[int | None, int | None, int | None, int | None]:
        """
        Gets the theme, sub-theme, topic and metric IDs matching the given names.

        This resolves all 4 ids in a single query which also enforces that the
        combination is internally consistent. The metric must belong to the topic,
        which must belong to the given sub-theme and theme. An invalid combination
        (e.g. "respiratory" paired with "MMR1") matches no row, so this returns
        (None, None, None, None) and access is denied.

        Returns:
            A tuple of (theme_id, sub_theme_id, topic_id, metric_id) if the whole
            combination exists, or (None, None, None, None) if it does not.
        """
        record = (
            self.filter(
                sub_theme__theme__name=theme_name,
                sub_theme__name=sub_theme_name,
                name=topic_name,
                metric__name=metric_name,
            )
            .select_related("sub_theme__theme")
            .annotate(matched_metric_id=models.F("metric__id"))
            .first()
        )

        if record:
            return (
                int(record.sub_theme.theme_id),
                int(record.sub_theme_id),
                int(record.id),
                int(record.matched_metric_id),
            )

        return (
            None,
            None,
            None,
            None,
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

    def get_theme_sub_theme_topic_and_metric_id_by_name(
        self,
        theme_name: str,
        sub_theme_name: str,
        topic_name: str,
        metric_name: str,
    ) -> tuple[int | None, int | None, int | None, int | None]:
        """
        Gets the theme, sub-theme, topic and metric IDs matching the given names.

        Resolves all 4 ids in a single query that also validates the
        combination is consistent.

        Returns:
            A tuple of (theme_id, sub_theme_id, topic_id, metric_id) if the whole
            combination exists, or (None, None, None, None) if it does not.
        """
        return self.get_queryset().get_theme_sub_theme_topic_and_metric_id_by_name(
            theme_name, sub_theme_name, topic_name, metric_name
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
