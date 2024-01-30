"""
This file contains the custom QuerySet and Manager classes associated with the `Stratum` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

from django.db import models


class StratumQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `StratumManager`"""

    def get_all_names(self) -> models.QuerySet:
        """Gets all available stratum names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual stratum names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<StratumQuerySet ['0_4', '0_5']>`

        """
        return self.all().values_list("name", flat=True).order_by("name")


class StratumManager(models.Manager):
    """Custom model manager class for the `Stratum` model."""

    def get_queryset(self) -> StratumQuerySet:
        return StratumQuerySet(model=self.model, using=self.db)

    def get_all_names(self) -> StratumQuerySet:
        """Gets all available stratum names as a flat list queryset.

        Returns:
            QuerySet: A queryset of the individual stratum names
                ordered in descending ordering starting from A -> Z:
                Examples:
                    `<StratumQuerySet ['0_4', '0_5']>`

        """
        return self.get_queryset().get_all_names()
