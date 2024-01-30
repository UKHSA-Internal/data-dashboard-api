from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import GeographyType
from tests.factories.metrics.geography_type import GeographyTypeFactory
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestGeographyTypesViewSet:
    @property
    def path(self) -> str:
        return "/api/geographies/v1/types/"

    @pytest.mark.django_db
    def test_list_view_returns_correct_response(self):
        """
        Given a number of `GeographyType` records in the database
        When a GET request is made to the list
            `/api/geographies/v1/types/` endpoint
        Then the ID and the name of each `GeographyType` record
            are listed in the response
        """
        # Given
        client = APIClient()
        geography_type_names = ["Nation", "Lower Tier Local Authority"]
        geography_types = [
            GeographyType.objects.create(name=geography_type_name)
            for geography_type_name in geography_type_names
        ]

        # When
        response: Response = client.get(path=self.path)

        # Then
        assert response.status_code == HTTPStatus.OK
        for geography_type in geography_types:
            expected_data_for_geography_type = {
                "id": geography_type.id,
                "name": geography_type.name,
            }
            assert expected_data_for_geography_type in response.data

    @pytest.mark.django_db
    def test_detail_view_returns_correct_response(self):
        """
        Given a `GeographyType` record in the database
        And a number of associated `Geography` records
        When a GET request is made to the detail
            `/api/geographies/v1/types/{id}` endpoint
        Then the ID and the name of each `Geography` record
            associated with the requested `GeographyType`
            are listed in the response
        """
        # Given
        client = APIClient()
        geography_names = ["London", "Leeds"]
        geography_type = GeographyTypeFactory.create(
            name="Lower Tier Local",
            with_geographies__geography_names=geography_names,
        )

        # When
        path = f"{self.path}{geography_type.id}/"
        response: Response = client.get(path=path)

        # Then
        assert response.status_code == HTTPStatus.OK
        returned_associated_geographies = response.data["geographies"]

        for associated_geography in geography_type.geographies.all():
            expected_geography_detail_data = {
                "id": associated_geography.id,
                "name": associated_geography.name,
            }
            assert expected_geography_detail_data in returned_associated_geographies


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
