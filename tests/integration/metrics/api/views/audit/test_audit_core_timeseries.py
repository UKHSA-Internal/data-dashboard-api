import datetime
from unittest import mock
from http import HTTPStatus
from django.test import RequestFactory

import pytest

from rest_framework.response import Response
from django.urls import reverse
from rest_framework.test import APIClient

from metrics.api.views.audit.serializers import AuditCoreTimeseriesSerializer
from metrics.api.views.audit import AuditCoreTimeseriesViewSet

from metrics.data.models.core_models import CoreTimeSeries
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestAuditCoreTimeSeriesViewSet:
    @property
    def path(self) -> str:
        return "/api/audit/v1/core-timeseries"

    @pytest.mark.django_db
    def test_list_returns_correct_response_data(self):
        """
        Given there are a number of records in the database for two different metrics
        When a request is made to the `AuditCoreHeadline` endpoint
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
        current_date = (datetime.datetime.now()).strftime("%Y-%m-%d")

        core_timeseries_records = [
            CoreTimeSeriesFactory.create_record(metric_value=1),
            CoreTimeSeriesFactory.create_record(metric_value=2),
            CoreTimeSeriesFactory.create_record(
                metric_name=metric,
                metric_value=metric_value,
                date=current_date,
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
        assert response.data["results"][0]["metric_value"] == f"{metric_value:.4f}"

    @pytest.mark.django_db
    def test_list_returns_records_including_records_under_embargo(self):
        """
        Given two records, one of which is under embargo
        When the list endpoint is called
        Then both records are returned by the `AuditCoreHeadline` endpoint
        """
        # Given
        client = APIClient()
        metric = "COVID-19_cases_casesByDay"
        geography_type = "Nation"
        geography = "England"
        stratum = "default"
        sex = "all"
        age = "all"
        current_date = (datetime.datetime.now()).strftime("%Y-%m-%d")
        past_date = (datetime.datetime.now() - datetime.timedelta(days=2)).strftime(
            "%Y-%m-%d"
        )

        future_embargo = datetime.datetime.now() + datetime.timedelta(days=1)

        core_timeseries_records = [
            CoreTimeSeriesFactory.create_record(metric_value=1, date=past_date),
            CoreTimeSeriesFactory.create_record(
                metric_value=2, embargo=future_embargo, date=current_date
            ),
        ]

        # When
        path = (
            f"{self.path}/{metric}/{geography_type}/{geography}/{stratum}/{sex}/{age}"
        )
        response: Response = client.get(path)

        # Then
        assert len(response.data["results"]) == len(core_timeseries_records)
