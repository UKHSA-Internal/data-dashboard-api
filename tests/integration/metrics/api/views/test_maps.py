from decimal import Decimal

from rest_framework.response import Response
from rest_framework.test import APIClient
from tests.factories.metrics.time_series import CoreTimeSeriesFactory
import pytest


class TestMapsView:
    @property
    def path(self) -> str:
        return "/api/maps/v1"

    @pytest.mark.django_db
    def test_returns_correct_data(self):
        """
        Given a number of `CoreTimeSeries` records
        When a POST request is made to the `api/maps/v1` endpoint
        Then the correct data is returned for each requested geography
        """
        # Given
        client = APIClient()

        topic = "COVID-19"
        ltla = "Lower Tier Local Authority"
        metric = "COVID-19_cases_countRollingMean"
        bexley = CoreTimeSeriesFactory.create_record(
            metric_name=metric,
            topic_name=topic,
            geography_type_name=ltla,
            geography_name="Bexley",
            geography_code="E09000004",
            metric_value=1,
        )
        arun = CoreTimeSeriesFactory.create_record(
            metric_name=metric,
            topic_name="COVID-19",
            geography_type_name=ltla,
            geography_name="Arun",
            geography_code="E07000224",
            metric_value=2,
        )
        hackney = CoreTimeSeriesFactory.create_record(
            metric_name=metric,
            topic_name=topic,
            geography_type_name=ltla,
            geography_name="Hackney",
            geography_code="E09000012",
            metric_value=3,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=metric,
            topic_name=topic,
            geography_type_name="Nation",
            geography_name="England",
            geography_code="E92000001",
            metric_value=4,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=ltla,
            geography_name="Leeds",
            geography_code="E08000035",
            metric_value=5,
        )

        payload = {
            "date_from": "2020-01-01",
            "date_to": "2025-12-31",
            "parameters": {
                "theme": "infectious_disease",
                "sub_theme": "respiratory",
                "topic": "COVID-19",
                "metric": metric,
                "stratum": "default",
                "age": "all",
                "sex": "all",
                "geography_type": "Lower Tier Local Authority",
                "geographies": [
                    bexley.geography.name,
                    arun.geography.name,
                    hackney.geography.name,
                ],
            },
            "accompanying_points": [
                {
                    "label_prefix": "Rate of cases in England: ",
                    "label_suffix": "",
                    "parameters": {
                        "metric": metric,
                        "geography_type": "Nation",
                        "geography": "England",
                    },
                }
            ],
        }

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == 200
        expected_data = [
            {
                "geography_code": bexley.geography.geography_code,
                "geography_type": "Lower Tier Local Authority",
                "geography": bexley.geography.name,
                "metric_value": Decimal("1.0000"),
                "accompanying_points": [
                    {
                        "label_prefix": "Rate of cases in England:",
                        "label_suffix": "",
                        "metric_value": Decimal("4.0000"),
                    }
                ],
            },
            {
                "geography_code": arun.geography.geography_code,
                "geography_type": "Lower Tier Local Authority",
                "geography": arun.geography.name,
                "metric_value": Decimal("2.0000"),
                "accompanying_points": [
                    {
                        "label_prefix": "Rate of cases in England:",
                        "label_suffix": "",
                        "metric_value": Decimal("4.0000"),
                    }
                ],
            },
            {
                "geography_code": hackney.geography.geography_code,
                "geography_type": "Lower Tier Local Authority",
                "geography": hackney.geography.name,
                "metric_value": Decimal("3.0000"),
                "accompanying_points": [
                    {
                        "label_prefix": "Rate of cases in England:",
                        "label_suffix": "",
                        "metric_value": Decimal("4.0000"),
                    }
                ],
            },
        ]

        assert response.data == {
            "data": expected_data,
            "latest_date": "2025-01-01",
        }
