from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from ingestion.data_transfer_models.validation.geography_code import (
    UNITED_KINGDOM_GEOGRAPHY_CODE,
)
from tests.factories.metrics.geography import GeographyFactory
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestGeographiesDeprecatedView:
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
            in descending alphabetical order
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
            geography_code="E09000004",
        )
        arun = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name="COVID-19",
            geography_type_name=ltla,
            geography_name="Arun",
            geography_code="E07000224",
        )
        hackney = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=ltla,
            geography_name="Hackney",
            geography_code="E09000012",
        )
        england = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=nation,
            geography_name="England",
            geography_code="E92000001",
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=ltla,
            geography_name="Leeds",
            geography_code="E08000035",
        )

        # When
        path = f"{self.path}/{topic}"
        response: Response = client.get(path=path)

        # Then
        # Geographies are returned in descending alphabetical order
        expected_results = [
            {
                "geography_type": ltla,
                "geographies": [
                    {
                        "name": arun.geography.name,
                        "geography_code": arun.geography.geography_code,
                        "relationships": None,
                    },
                    {
                        "name": bexley.geography.name,
                        "geography_code": bexley.geography.geography_code,
                        "relationships": None,
                    },
                    {
                        "name": hackney.geography.name,
                        "geography_code": hackney.geography.geography_code,
                        "relationships": None,
                    },
                ],
            },
            {
                "geography_type": nation,
                "geographies": [
                    {
                        "name": england.geography.name,
                        "geography_code": england.geography.geography_code,
                        "relationships": [
                            {
                                "geography_type": "United Kingdom",
                                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
                                "name": "United Kingdom",
                            }
                        ],
                    }
                ],
            },
        ]
        assert response.status_code == HTTPStatus.OK
        assert response.data == expected_results


class TestGeographiesView:
    @property
    def path(self) -> str:
        return "/api/geographies/v3"

    @pytest.mark.django_db
    def test_get_returns_correct_results_for_topic(self):
        """
        Given a `topic` and a number of `CoreTimeSeries` records
        When a GET request is made to the
            `/api/geographies/v3/?topic={topic}` endpoint
        Then the returned results contain the correct geographies
            in descending alphabetical order
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
            geography_code="E09000004",
        )
        arun = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name="COVID-19",
            geography_type_name=ltla,
            geography_name="Arun",
            geography_code="E07000224",
        )
        hackney = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=ltla,
            geography_name="Hackney",
            geography_code="E09000012",
        )
        england = CoreTimeSeriesFactory.create_record(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name=topic,
            geography_type_name=nation,
            geography_name="England",
            geography_code="E92000001",
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=ltla,
            geography_name="Leeds",
            geography_code="E08000035",
        )

        # When
        query_params = {"topic": topic}
        response: Response = client.get(path=self.path, query_params=query_params)

        # Then
        # Geographies are returned in descending alphabetical order
        expected_results = [
            {
                "geography_type": ltla,
                "geographies": [
                    {
                        "name": arun.geography.name,
                        "geography_code": arun.geography.geography_code,
                        "relationships": None,
                    },
                    {
                        "name": bexley.geography.name,
                        "geography_code": bexley.geography.geography_code,
                        "relationships": None,
                    },
                    {
                        "name": hackney.geography.name,
                        "geography_code": hackney.geography.geography_code,
                        "relationships": None,
                    },
                ],
            },
            {
                "geography_type": nation,
                "geographies": [
                    {
                        "name": england.geography.name,
                        "geography_code": england.geography.geography_code,
                        "relationships": [
                            {
                                "geography_type": "United Kingdom",
                                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
                                "name": "United Kingdom",
                            }
                        ],
                    }
                ],
            },
        ]
        assert response.status_code == HTTPStatus.OK
        assert response.data == expected_results

    @pytest.mark.django_db
    def test_get_returns_correct_results_for_geography_type(self):
        """
        Given a `geography_type` and a number of `Geography` records
        When a GET request is made to the
            `/api/geographies/v3/?geography_type={geography_type}` endpoint
        Then the returned results contain the correct geographies
            in descending alphabetical order for the given geography type
        """
        # Given
        client = APIClient()
        ltla = "Lower Tier Local Authority"

        bexley = GeographyFactory.create_with_geography_type(
            name="Bexley", geography_code="E09000004", geography_type=ltla
        )
        arun = GeographyFactory.create_with_geography_type(
            name="Arun", geography_code="E07000224", geography_type=ltla
        )
        hackney = GeographyFactory.create_with_geography_type(
            name="Hackney", geography_code="E09000012", geography_type=ltla
        )
        GeographyFactory.create_with_geography_type(
            name="England", geography_code="E92000001", geography_type="Nation"
        )

        # When
        query_params = {"geography_type": ltla}
        response: Response = client.get(path=self.path, query_params=query_params)

        # Then
        # Geographies are returned in descending alphabetical order
        assert response.status_code == HTTPStatus.OK
        response_data = response.data
        assert len(response_data) == 1

        result = response_data[0]
        assert result["geography_type"] == ltla

        assert result["geographies"][0]["name"] == arun.name
        assert result["geographies"][0]["geography_code"] == arun.geography_code

        assert result["geographies"][1]["name"] == bexley.name
        assert result["geographies"][1]["geography_code"] == bexley.geography_code

        assert result["geographies"][2]["name"] == hackney.name
        assert result["geographies"][2]["geography_code"] == hackney.geography_code

        assert len(result["geographies"]) == 3
