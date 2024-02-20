from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestGeographiesView:
    @property
    def path(self) -> str:
        return "/api/geographies/v2"

    @pytest.mark.django_db
    def test_get_returns_correct_results(self):
        """
        Given a `topic` and a number of `CoreTimeSeries` records
        When a GET request is made to the
            `/api/geographies/v2/{topic}` endpoint
        Then the returned results contain the correct geographies
        """
        # Given
        client = APIClient()
        ltla = "Lower Tier Local Authority"
        nation = "Nation"
        topic = "COVID-19"

        bexley = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=ltla,
            geography_name="Bexley",
        )
        hackney = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=ltla,
            geography_name="Hackney",
        )
        england = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=nation,
            geography_name="England",
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=ltla,
            geography_name="Leeds",
        )

        # When
        path = f"{self.path}/{topic}"
        response: Response = client.get(path=path)

        # Then
        expected_results = [
            {
                "geography_type": ltla,
                "geographies": [
                    {"name": bexley.geography.name},
                    {"name": hackney.geography.name},
                ],
            },
            {
                "geography_type": nation,
                "geographies": [{"name": england.geography.name}],
            },
        ]
        assert response.status_code == HTTPStatus.OK
        assert response.data == expected_results
