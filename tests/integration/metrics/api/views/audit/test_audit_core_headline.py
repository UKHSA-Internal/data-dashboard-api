from unittest import mock
from http import HTTPStatus
from django.test import RequestFactory

import pytest

from rest_framework.response import Response
from django.urls import reverse
from rest_framework.test import APIClient

from metrics.api.views.audit.serializers import AuditAPITimeSeriesSerializer
from metrics.api.views.audit import AuditAPITimeSeriesViewSet


class TestAuditCoreHeadline:
    @property
    def path(self) -> str:
        return "/api/audit/v1/core-headline"

    @pytest.mark.django_db
    def test_list_returns_correct_response(self):
        """
        Given a valid request to the `audit` endpoint
        When the `GET /api/audit/v1/core-headline` endpoint is hit.
        Then the expected response is returned.
        """
        # Given
        client = APIClient()
        metric = "COVID-19_headline_ONSdeaths_7DayChange"
        geography_type = "Nation"
        geography = "England"
        stratum = "default"
        sex = "all"
        age = "all"

        # When
        path = (
            f"{self.path}/{metric}/{geography_type}/{geography}/{age}/{sex}/{stratum}"
        )
        response: Response = client.get(path)

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == "application/json"
