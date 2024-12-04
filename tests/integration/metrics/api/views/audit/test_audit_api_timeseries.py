import datetime
from unittest import mock
from http import HTTPStatus
from django.test import RequestFactory

import pytest

from rest_framework.response import Response
from django.urls import reverse
from rest_framework.test import APIClient

from metrics.api.views.audit.serializers import AuditAPITimeSeriesSerializer
from metrics.api.views.audit import AuditAPITimeSeriesViewSet

from metrics.data.models.api_models import APITimeSeries
from tests.factories.metrics.api_models.time_series import APITimeSeriesFactory


class TestAuditAPITimeSeriesViewSet:

    @property
    def path(self) -> str:
        return "/api/audit/v1/api-timeseries"

    @pytest.mark.django_db
    def test_list_returns_correct_response_data(self):
        """
        Given there are a number of records in the database for two different metrics
        When a request is made to the `audit/v1/api-timeseries` endpoint
        Then the correct record is returned.
        """
        # Given
        client = APIClient()
        metric = "COVID-19_deaths_ONSByDay"
        geography_type = "Nation"
        geography = "England"
        stratum = "default"
        sex = "all"
        age = "all"
        metric_value = 3

        api_timeseries_records = [
            APITimeSeriesFactory.create_record(metric_value=1),
            APITimeSeriesFactory.create_record(metric_value=2),
            APITimeSeriesFactory.create_record(
                metric_name=metric,
                metric_value=metric_value,
            ),
        ]

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
        assert response.data["results"][0]["metric_value"] == float(metric_value)

    @pytest.mark.django_db
    def test_list_returns_records_including_records_under_embargo(self):
        """
        Given two records, one of which is still under embargo
        When the list endpoint is called
        Then both records are returned by the `AuditAPITimeseries` endpoint
        """
        # Given
        client = APIClient()
        metric = "COVID-19_cases_casesByDay"
        geography_type = "Nation"
        geography = "England"
        stratum = "default"
        sex = "all"
        age = "all"

        future_embargo = datetime.datetime.now() + datetime.timedelta(days=1)

        api_timeseries_records = [
            APITimeSeriesFactory.create_record(metric_value=1, embargo=future_embargo),
            APITimeSeriesFactory.create_record(metric_value=2),
        ]

        # When
        path = (
            f"{self.path}/{metric}/{geography_type}/{geography}/{stratum}/{sex}/{age}"
        )
        response: Response = client.get(path)

        # Then
        assert len(response.data["results"]) == len(api_timeseries_records)