import datetime
from decimal import Decimal

from rest_framework.response import Response
from rest_framework.test import APIClient
from tests.factories.metrics.time_series import CoreTimeSeriesFactory
import pytest


class TestMapsView:
    @property
    def path(self) -> str:
        return "/api/maps/v1"

    @property
    def covid_19(self) -> str:
        return "COVID-19"

    @property
    def ltla(self) -> str:
        return "Lower Tier Local Authority"

    @property
    def covid_19_cases_metric(self) -> str:
        return "COVID-19_cases_countRollingMean"

    @pytest.mark.django_db
    def test_returns_correct_data_when_geographies_not_specified(self):
        """
        Given a number of `CoreTimeSeries` records
        When a POST request is made to the `api/maps/v1` endpoint
        And the `geographies` are not specified
        Then the correct data is returned
            for all geographies within the given `geography_type`
        """
        # Given
        client = APIClient()
        earlier_date = datetime.date(year=2025, month=1, day=1)
        latest_date = datetime.date(year=2025, month=12, day=31)

        bexley = CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=self.ltla,
            geography_name="Bexley",
            geography_code="E09000004",
            metric_value=1,
            date=latest_date,
        )
        arun = CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=self.ltla,
            geography_name="Arun",
            geography_code="E07000224",
            metric_value=2,
            date=earlier_date,
        )
        hackney = CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=self.ltla,
            geography_name="Hackney",
            geography_code="E09000012",
            metric_value=3,
            date=earlier_date,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name="Nation",
            geography_name="England",
            geography_code="E92000001",
            metric_value=4,
            date=datetime.date(year=2025, month=1, day=1),
        )
        # An unrelated record which will be returned as a null case
        missing_geography_record = CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=self.ltla,
            geography_name="Reigate and Banstead",
            geography_code="E07000211",
            metric_value=5,
        )

        payload = {
            "date_from": "2020-01-01",
            "date_to": "2025-12-31",
            "parameters": {
                "theme": "infectious_disease",
                "sub_theme": "respiratory",
                "topic": self.covid_19,
                "metric": self.covid_19_cases_metric,
                "stratum": "default",
                "age": "all",
                "sex": "all",
                "geography_type": self.ltla,
                "geographies": [],
                # When no `geographies` are specified,
                # Then all geographies under the given `geography_type`
                # should be returned
            },
            "accompanying_points": [
                {
                    "label_prefix": "Rate of cases in England: ",
                    "label_suffix": "",
                    "parameters": {
                        "metric": self.covid_19_cases_metric,
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
                "geography_code": arun.geography.geography_code,
                "geography_type": self.ltla,
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
                "geography_code": bexley.geography.geography_code,
                "geography_type": self.ltla,
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
                "geography_code": hackney.geography.geography_code,
                "geography_type": self.ltla,
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
            {
                "geography_code": missing_geography_record.geography.geography_code,
                "geography_type": self.ltla,
                "geography": missing_geography_record.geography.name,
                "metric_value": None,
                "accompanying_points": None,
            },
        ]

        assert response.data == {
            "data": expected_data,
            "latest_date": latest_date,
        }

    @pytest.mark.django_db
    def test_returns_correct_data_when_geographies_are_specified(self):
        """
        Given a number of `CoreTimeSeries` records
        When a POST request is made to the `api/maps/v1` endpoint
        And the `geographies` are specified
        Then the correct data is returned
            for each of the requested geographies
        """
        # Given
        client = APIClient()
        date_stamp = datetime.date(year=2020, month=1, day=1)

        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=self.ltla,
            geography_name="Bexley",
            geography_code="E09000004",
            metric_value=1,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=self.ltla,
            geography_name="Arun",
            geography_code="E07000224",
            metric_value=2,
            date=date_stamp,
        )
        hackney = CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=self.ltla,
            geography_name="Hackney",
            geography_code="E09000012",
            metric_value=3,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name="Nation",
            geography_name="England",
            geography_code="E92000001",
            metric_value=4,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=self.ltla,
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
                "topic": self.covid_19,
                "metric": self.covid_19_cases_metric,
                "stratum": "default",
                "age": "all",
                "sex": "all",
                "geography_type": self.ltla,
                "geographies": [
                    hackney.geography.name,
                    # Only Hackney is being requested
                ],
            },
            "accompanying_points": [
                {
                    "label_prefix": "Rate of cases in England: ",
                    "label_suffix": "",
                    "parameters": {
                        "metric": self.covid_19_cases_metric,
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
                "geography_code": hackney.geography.geography_code,
                "geography_type": self.ltla,
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
            "latest_date": date_stamp,
        }

    @pytest.mark.django_db
    def test_returns_correct_data_for_related_geography_linked_accompanying_points(
        self,
    ):
        """
        Given a number of `CoreTimeSeries` records
        When a POST request is made to the `api/maps/v1` endpoint
        And the `accompanying_points` reference a related geography
        Then the correct data is returned
            for each of the requested geographies
        """
        # Given
        client = APIClient()
        utla = "Upper Tier Local Authority"
        date_stamp = datetime.date(year=2020, month=1, day=1)

        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=utla,
            geography_name="Hackney",
            geography_code="E09000012",
            metric_value=3,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name="Region",
            geography_name="London",
            geography_code="E12000007",
            metric_value=7,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name="Nation",
            geography_name="England",
            geography_code="E92000001",
            metric_value=4,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name=self.covid_19_cases_metric,
            topic_name=self.covid_19,
            geography_type_name=utla,
            geography_name="Leeds",
            geography_code="E08000035",
            metric_value=9,
            date=date_stamp,
        )
        CoreTimeSeriesFactory.create_record(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            geography_type_name=utla,
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
                "topic": self.covid_19,
                "metric": self.covid_19_cases_metric,
                "stratum": "default",
                "age": "all",
                "sex": "all",
                "geography_type": utla,
                "geographies": [],
            },
            "accompanying_points": [
                {
                    "label_prefix": "Region rate of cases: ",
                    "label_suffix": "",
                    "parameters": {
                        "geography_type": "Region",
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
                "geography": "Hackney",
                "geography_code": "E09000012",
                "geography_type": "Upper Tier Local Authority",
                "metric_value": Decimal("3.0000"),
                "accompanying_points": [
                    {
                        "label_prefix": "Region rate of cases:",
                        "label_suffix": "",
                        "metric_value": Decimal("7.0000"),
                    }
                    # For the geography of `Hackney` the corresponding
                    # `Region` of `London` has data that we should get back
                ],
            },
            {
                "accompanying_points": [
                    {
                        "label_prefix": "Region rate of cases:",
                        "label_suffix": "",
                        "metric_value": None,
                    }
                ],
                # For the geography of `Leeds` the corresponding
                # `Region` of `Yorkshire and The Humber` doesn't have any data
                # so it should return None
                "geography": "Leeds",
                "geography_code": "E08000035",
                "geography_type": "Upper Tier Local Authority",
                "metric_value": Decimal("9.0000"),
            },
        ]

        assert response.data == {
            "data": expected_data,
            "latest_date": date_stamp,
        }
