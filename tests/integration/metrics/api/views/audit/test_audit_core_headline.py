import datetime
from unittest import mock
from decimal import Decimal
from http import HTTPStatus
from django.test import RequestFactory

import pytest

from rest_framework.response import Response
from django.urls import reverse
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreHeadline
from tests.factories.metrics.headline import CoreHeadlineFactory


class TestAuditCoreHeadline:
    @property
    def path(self) -> str:
        return "/api/audit/v1/core-headline"

    @pytest.mark.django_db
    def test_list_returns_correct_response_data(self):
        """
        Given there are a number of records in the database for two different metrics
        When a request is made to the `AuditCoreTimeseries` endpoint
        Then the correct record is returned.
        """
        # Given
        client = APIClient()
        metric = "COVID-19_headline_7DayOccupiedBedsChange"
        geography_type = "Nation"
        geography = "England"
        stratum = "default"
        sex = "all"
        age = "all"
        metric_value = 3

        CoreHeadlineFactory.create_record(metric_value=1)
        CoreHeadlineFactory.create_record(metric_value=2)
        CoreHeadlineFactory.create_record(
            metric=metric,
            metric_value=3,
        )

        # When
        path = (
            f"{self.path}/{metric}/{geography_type}/{geography}/{stratum}/{sex}/{age}"
        )
        response: Response = client.get(path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"

        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["metric"] == metric
        assert response.data["results"][0]["metric_value"] == f"{metric_value}.0000"

    @pytest.mark.django_db
    def test_list_returns_records_including_records_under_embargo(self):
        """
        Given two records, one of which is still under embargo
        When the list endpoint is called
        Then both records are returned by the `AuditCoreTimeseries` endpoint
        """
        # Given
        client = APIClient()
        metric = "COVID-19_headline_positivity_latest"
        geography_type = "Nation"
        geography = "England"
        stratum = "default"
        sex = "all"
        age = "all"
        metric_value = 1

        future_embargo = datetime.datetime.now() + datetime.timedelta(days=1)

        core_headline_records = [
            CoreHeadlineFactory.create_record(
                metric_value=metric_value, embargo=future_embargo
            ),
            CoreHeadlineFactory.create_record(metric_value=2),
        ]

        # When
        path = (
            f"{self.path}/{metric}/{geography_type}/{geography}/{stratum}/{sex}/{age}"
        )
        response: Response = client.get(path)

        # Then
        assert len(response.data["results"]) == len(core_headline_records)
