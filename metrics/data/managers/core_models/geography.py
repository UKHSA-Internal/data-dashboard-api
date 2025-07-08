"""
This file contains the custom QuerySet and Manager classes associated with the `Geography` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from typing import Self

from django.db import models


class GeographyQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `GeographyManager`"""

    def get_all_names(self) -> Self:
        """Gets all available geography names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual geography names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<GeographyQuerySet ['England', 'London']>`

        """
        return self.all().values_list("name", flat=True).distinct().order_by("name")

    def get_all_geography_codes_by_geography_type(
        self, geography_type_name: str
    ) -> Self:
        """Gets all available geography codes for the given `geography_type_name`.
        Returns:
            QuerySet: A queryset of the individual geography codes
                which are related to the given geography_type:
                Examples:
                    `<GeographyQuerySet ['E06000001', 'E06000002']>`
        """
        return (
            self.filter(geography_type__name=geography_type_name)
            .values_list("geography_code", flat=True)
            .order_by("geography_code")
        )

    def get_all_geography_names_by_geography_type(
        self,
        geography_type_name: str,
    ) -> Self:
        """Gets all available geography names for the given `geography_type_name`.
        Returns:
            QuerySet: A queryset of the individual geography names
            which are related to the given geography_type:
            Examples:
                `<GeographyQuerySet ['England', 'London']>`
        """
        return (
            self.filter(geography_type__name=geography_type_name)
            .values_list("name", flat=True)
            .order_by("name")
        )

    def get_geography_codes_and_names_by_geography_type(
        self,
        geography_type_name: str,
    ):
        """Gets all available geography codes and names for the given `geography_type_name`

        Args:
            geography_type_name: string representation of `geography_type_name`

        Returns:
            QuerySet: A queryset of the individual geography codes
                which are related to the given geography_type:
                Examples:
                    `<GeographyQuerySet [('E06000001', 'North East'), ('E06000002', 'North West')]>`

        """
        return (
            self.filter(geography_type__name=geography_type_name)
            .values_list("geography_code", "name")
            .order_by("geography_code")
        )

    def get_geographies_by_geography_type(
        self,
        geography_type_name: str,
    ):
        return (
            self.filter(geography_type__name=geography_type_name)
            .values("name", "geography_code")
            .order_by("name")
        )


class GeographyManager(models.Manager):
    """Custom model manager class for the `Geography` model."""

    def get_queryset(self) -> GeographyQuerySet:
        return GeographyQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> GeographyQuerySet:
        """Gets all available deduplicated geography names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual geography names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<GeographyQuerySet ['England', 'London']>`

        """
        return self.get_queryset().get_all_names()

    def get_all_geography_codes_by_geography_type(self, geography_type_name: str):
        """Gets all available geography codes for the given `geography_type_name`.

        Args:
            geography_type_name: string representation of `geography_type_name`

        Returns:
            QuerySet: A queryset of the individual geography codes
                which are related to the given geography_type:
                Examples:
                    `<GeographyQuerySet ['E06000001', 'E06000002']>`

        """
        return self.get_queryset().get_all_geography_codes_by_geography_type(
            geography_type_name=geography_type_name
        )

    def get_all_geography_names_by_geography_type(self, geography_type_name: str):
        """Gets all available geography names for the given `geography_type_name`.

        Args:
            geography_type_name: string representation of `geography_type_name`

        Returns:
            QuerySet: A queryset of the individual geography names
            which are related to the given geography_type:
            Examples:
                `<GeographyQuerySet ['England', 'London']>`
        """
        return self.get_queryset().get_all_geography_names_by_geography_type(
            geography_type_name=geography_type_name
        )

    def get_geography_codes_and_names_by_geography_type(
        self,
        geography_type_name: str,
    ):
        """Gets all available geography codes and names for a give `geography_type`

        Args:
            geography_type_name: string representation of `geography_type_name`

        Returns:
            QuerySet: A queryset of the individual geography codes
                which are related to the given geography_type:
                Examples:
                    `<GeographyQuerySet [('E06000001', 'North East'), ('E06000002', 'North West')]>`

        """
        return self.get_queryset().get_geography_codes_and_names_by_geography_type(
            geography_type_name=geography_type_name
        )

    def get_geographies_by_geography_type(
        self,
        geography_type_name: str,
    ):
        """Gets all available geographies for a given `geography_type`

        Args:
            geography_type_name: The name of the selected geography type

        Returns:
            QuerySet: A queryset of the individual geographies
                which are related to the given geography_type:
                Examples:
                    `<GeographyQuerySet [{"geography_code": "E06000001", "name": "North East"}, ...]>`

        """
        return self.get_queryset().get_geographies_by_geography_type(
            geography_type_name=geography_type_name
        )

    def does_geography_code_exist(
        self, *, geography_code: str, geography_type_name: str
    ) -> bool:
        """Given a `geography_code` it validates this against all geography_codes against
           a given `geography_type`

        Returns:
            Bool: True or False based on provided `geography_code` being in the database.

        """
        return (
            self.get_all_geography_codes_by_geography_type(
                geography_type_name=geography_type_name
            )
            .filter(geography_code=geography_code)
            .exists()
        )
