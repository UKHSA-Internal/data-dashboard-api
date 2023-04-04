"""
This file contains the custom QuerySet and Manager classes associated with the `APITimeSeries` model.

Note that the application layer should only call into the `Manager` class.
The application should not interact directly with the `QuerySet` class.
"""

import logging

from django.db import models

logger = logging.getLogger(__name__)


class APITimeSeriesQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `APITimeSeriesManager`"""


class APITimeSeriesManager(models.Manager):
    """Custom model manager class for the `APITimeSeries` model."""

    def get_queryset(self) -> APITimeSeriesQuerySet:
        return APITimeSeriesQuerySet(model=self.model, using=self.db)
