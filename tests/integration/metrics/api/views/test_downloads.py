import csv
import datetime
import io
from collections import OrderedDict

from rest_framework.response import Response

from metrics.data.models.core_models import CoreTimeSeries, Geography, CoreHeadline
from metrics.data.models.rbac_models import RBACPermission, RBACGroupPermission
from metrics.api.decorators.auth import RBAC_AUTH_X_HEADER
from tests.factories.metrics.time_series import CoreTimeSeriesFactory
from tests.factories.metrics.headline import CoreHeadlineFactory
from tests.factories.metrics.rbac_models.rbac_permission import RBACPermissionFactory
from tests.factories.metrics.rbac_models.rbac_group_permissions import (
    RBACPermissionGroupFactory,
)
import pytest
from rest_framework.test import APIClient
from http import HTTPStatus
from typing import Callable
import io
import csv


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_payload():
    return {
        "file_format": "json",
        "plots": [
            {
                "metric": "COVID-19_cases_rateRollingMean",
                "topic": "COVID-19",
                "stratum": "default",
                "age": "all",
                "sex": "f",
                "geography": "England",
                "geography_type": "Nation",
                "date_from": "2023-01-01",
                "date_to": "2023-01-15",
            }
        ],
    }


@pytest.fixture
def valid_headline_payload():
    return {
        "file_format": "json",
        "x_axis": "geography",
        "y_axis": "metric",
        "plots": [
            {
                "topic": "COVID-19",
                "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
                "stratum": "default",
                "age": "all",
                "geography": "England",
                "geography_type": "Nation",
                "sex": "all",
                "date_from": None,
                "date_to": None,
            }
        ],
    }


core_timeseries_list = [
    {
        "metric_frequency": "D",
        "theme": "non-communicable",
        "sub_theme": "respiratory",
        "topic": "asthma",
        "geography_type": "Nation",
        "geography": "England",
        "metric": "asthma_syndromic_emergencyDepartment_countsByDay",
        "stratum": "default",
        "sex": "f",
        "age": "all",
        "year": 2023,
        "epiweek": 1,
        "date": "2023-01-15",
        "metric_value": 123.45,
        "in_reporting_delay_period": True,
        "is_public": False,
    },
    {
        "metric_frequency": "D",
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "Nation",
        "geography": "England",
        "metric": "COVID-19_cases_rateRollingMean",
        "stratum": "default",
        "sex": "f",
        "age": "all",
        "year": 2023,
        "epiweek": 1,
        "date": "2023-01-15",
        "metric_value": 123.45,
        "in_reporting_delay_period": True,
        "is_public": False,
    },
    {
        "metric_frequency": "D",
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "Nation",
        "geography": "England",
        "metric": "COVID-19_vaccinations_autumn23_dosesByDay",
        "stratum": "default",
        "sex": "f",
        "age": "all",
        "year": 2023,
        "epiweek": 1,
        "date": "2023-01-15",
        "metric_value": 123.45,
        "in_reporting_delay_period": True,
        "is_public": True,
    },
]


def create_example_api_permissions(permissions: list[dict]) -> list[RBACPermission]:
    _permissions = []
    for permission in permissions:
        record = RBACPermissionFactory.create_record(
            name=permission.get("name", ""),
            theme_name=permission.get("theme", ""),
            sub_theme_name=permission.get("sub_theme", ""),
            topic_name=permission.get("topic", None),
            metric_name=permission.get("metric", None),
            geography_type_name=permission.get("geography_type", None),
            geography_name=permission.get("geography", None),
            stratum_name=permission.get("stratum", None),
            age_name=permission.get("age", None),
        )
        _permissions.append(record)
    return _permissions


def create_example_core_time_series_records() -> list[CoreTimeSeries]:
    core_timeseries_data = []
    for core_timeseries in core_timeseries_list:
        record = CoreTimeSeriesFactory.create_record(
            metric_value=core_timeseries["metric_value"],
            theme_name=core_timeseries["theme"],
            sub_theme_name=core_timeseries["sub_theme"],
            topic_name=core_timeseries["topic"],
            metric_name=core_timeseries["metric"],
            geography_name=core_timeseries["geography"],
            geography_type_name=core_timeseries["geography_type"],
            stratum_name=core_timeseries["stratum"],
            age_name=core_timeseries["age"],
            sex=core_timeseries["sex"],
            year=core_timeseries["year"],
            epiweek=core_timeseries["epiweek"],
            date=core_timeseries["date"],
            in_reporting_delay_period=core_timeseries["in_reporting_delay_period"],
            is_public=core_timeseries["is_public"],
        )
        core_timeseries_data.append(record)
    return core_timeseries_data


def create_example_api_group_records(
    name: str, permissions: list[RBACPermission]
) -> RBACGroupPermission:
    return RBACPermissionGroupFactory.create_record(name=name, permissions=permissions)


class TestDownloadsView:
    core_timeseries_data = {
        "metric_frequency": "D",
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "Nation",
        "geography": "England",
        "metric": "COVID-19_cases_rateRollingMean",
        "stratum": "default",
        "sex": "f",
        "age": "all",
        "year": 2023,
        "epiweek": 1,
        "date": "2023-01-15",
        "metric_value": 123.45,
        "in_reporting_delay_period": True,
        "is_public": True,
    }

    core_headline_data = {
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "geography_type": "",
        "geography": "",
        "metric": "COVID-19_headline_vaccines_spring24Uptake",
        "stratum": "default",
        "sex": "",
        "age": "01-04",
        "metric_value": 123.45,
        "period_start": "2024-01-01 00:00:00",
        "period_end": "2024-02-02 00:00:00",
        "is_public": True,
    }

    def _build_valid_payload(self) -> dict[str, str | list[dict[str, str]]]:
        return {
            "file_format": "csv",
            "plots": [
                {
                    "metric": self.core_timeseries_data["metric"],
                    "topic": self.core_timeseries_data["topic"],
                    "stratum": self.core_timeseries_data["stratum"],
                    "age": self.core_timeseries_data["age"],
                    "sex": self.core_timeseries_data["sex"],
                    "geography": self.core_timeseries_data["geography"],
                    "geography_type": self.core_timeseries_data["geography_type"],
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }

    def _build_valid_headline_payload(self) -> dict[str, str | list[dict[str, str]]]:
        return {
            "file_format": "csv",
            "x_axis": "age",
            "y_axis": "metric",
            "plots": [
                {
                    "metric": self.core_headline_data["metric"],
                    "topic": self.core_headline_data["topic"],
                    "stratum": self.core_headline_data["stratum"],
                    "age": self.core_headline_data["age"],
                    "sex": self.core_headline_data["sex"],
                    "geography": self.core_headline_data["geography"],
                    "geography_type": self.core_headline_data["geography_type"],
                }
            ],
        }

    def _build_valid_auth_payload(self) -> dict[str, str | list[dict[str, str]]]:
        return {
            "file_format": "csv",
            "plots": [
                {
                    "metric": core_timeseries_list[0]["metric"],
                    "topic": core_timeseries_list[0]["topic"],
                    "stratum": core_timeseries_list[0]["stratum"],
                    "age": core_timeseries_list[0]["age"],
                    "sex": core_timeseries_list[0]["sex"],
                    "geography": core_timeseries_list[0]["geography"],
                    "geography_type": core_timeseries_list[0]["geography_type"],
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                },
                {
                    "metric": core_timeseries_list[1]["metric"],
                    "topic": core_timeseries_list[1]["topic"],
                    "stratum": core_timeseries_list[1]["stratum"],
                    "age": core_timeseries_list[1]["age"],
                    "sex": core_timeseries_list[1]["sex"],
                    "geography": core_timeseries_list[1]["geography"],
                    "geography_type": core_timeseries_list[1]["geography_type"],
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                },
                {
                    "metric": core_timeseries_list[2]["metric"],
                    "topic": core_timeseries_list[2]["topic"],
                    "stratum": core_timeseries_list[2]["stratum"],
                    "age": core_timeseries_list[2]["age"],
                    "sex": core_timeseries_list[2]["sex"],
                    "geography": core_timeseries_list[2]["geography"],
                    "geography_type": core_timeseries_list[2]["geography_type"],
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                },
            ],
        }

    def _create_example_core_time_series(self, *, is_public: bool) -> CoreTimeSeries:
        return CoreTimeSeriesFactory.create_record(
            metric_value=self.core_timeseries_data["metric_value"],
            theme_name=self.core_timeseries_data["theme"],
            sub_theme_name=self.core_timeseries_data["sub_theme"],
            topic_name=self.core_timeseries_data["topic"],
            metric_name=self.core_timeseries_data["metric"],
            geography_name=self.core_timeseries_data["geography"],
            geography_type_name=self.core_timeseries_data["geography_type"],
            stratum_name=self.core_timeseries_data["stratum"],
            age_name=self.core_timeseries_data["age"],
            sex=self.core_timeseries_data["sex"],
            year=self.core_timeseries_data["year"],
            epiweek=self.core_timeseries_data["epiweek"],
            date=self.core_timeseries_data["date"],
            in_reporting_delay_period=self.core_timeseries_data[
                "in_reporting_delay_period"
            ],
            is_public=is_public,
        )

    def _create_examples_headline_data(self, is_public: bool) -> CoreHeadline:
        return CoreHeadlineFactory.create_record(
            metric_value=self.core_headline_data["metric_value"],
            theme_name=self.core_headline_data["theme"],
            sub_theme_name=self.core_headline_data["sub_theme"],
            topic_name=self.core_headline_data["topic"],
            metric_name=self.core_headline_data["metric"],
            geography_name=self.core_headline_data["geography"],
            geography_type_name=self.core_headline_data["geography_type"],
            stratum_name=self.core_headline_data["stratum"],
            age_name=self.core_headline_data["age"],
            sex=self.core_headline_data["sex"],
            period_start=self.core_headline_data["period_start"],
            period_end=self.core_headline_data["period_end"],
            is_public=is_public,
        )

    @property
    def path(self) -> str:
        return "/api/downloads/v2/"

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        self._create_example_core_time_series(is_public=True)
        valid_payload = self._build_valid_payload()
        path_without_trailing_forward_slash = "/api/downloads/v2"

        # When
        response: Response = client.post(
            path=path_without_trailing_forward_slash,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_json_download_timeseries_returns_correct_response(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in json format
        """
        # Given
        client = APIClient()
        core_time_series = self._create_example_core_time_series(is_public=True)
        valid_payload = self._build_valid_payload()
        valid_payload["file_format"] = "json"

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert "json" in response.headers["Content-Type"]

        # Check the output itself is as expected
        returned_obj = response.data[0]
        expected_data = OrderedDict(
            [
                ("theme", core_time_series.metric.topic.sub_theme.theme.name),
                ("sub_theme", core_time_series.metric.topic.sub_theme.name),
                ("topic", core_time_series.metric.topic.name),
                ("geography_type", core_time_series.geography.geography_type.name),
                ("geography", core_time_series.geography.name),
                ("metric", core_time_series.metric.name),
                ("age", core_time_series.age.name),
                ("stratum", core_time_series.stratum.name),
                ("sex", core_time_series.sex),
                ("year", core_time_series.year),
                ("date", core_time_series.date),
                ("metric_value", f"{core_time_series.metric_value:.4f}"),
                (
                    "in_reporting_delay_period",
                    core_time_series.in_reporting_delay_period,
                ),
            ]
        )
        assert returned_obj == expected_data

    @pytest.mark.django_db
    def test_json_download_headline_returns_correct_response(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2` endpoint is hit
        Then the response contains the expected output in json format
        """
        # Given
        client = APIClient()
        core_headline_data = self._create_examples_headline_data(is_public=True)
        valid_payload = self._build_valid_headline_payload()
        valid_payload["file_format"] = "json"

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_csv_download_timeseries_returns_correct_response(self):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        client = APIClient()
        core_time_series = self._create_example_core_time_series(is_public=True)
        valid_payload = self._build_valid_payload()

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate csv is being returned
        assert response.headers["Content-Type"] == "text/csv"

        # Check the output itself is as expected
        csv_file = csv.reader(io.StringIO(response.content.decode("utf-8")))
        csv_output = list(csv_file)
        csv_headers = csv_output.pop(0)

        expected_csv_headings = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "year",
            "date",
            "metric_value",
            "in_reporting_delay_period",
        ]
        assert csv_headers == expected_csv_headings

        expected_csv_content = [
            [
                core_time_series.metric.topic.sub_theme.theme.name,
                core_time_series.metric.topic.sub_theme.name,
                core_time_series.metric.topic.name,
                core_time_series.geography.geography_type.name,
                core_time_series.geography.name,
                core_time_series.metric.name,
                core_time_series.sex,
                core_time_series.age.name,
                core_time_series.stratum.name,
                str(core_time_series.year),
                core_time_series.date,
                f"{core_time_series.metric_value:.4f}",
                str(core_time_series.in_reporting_delay_period),
            ]
        ]
        assert csv_output == expected_csv_content

    @pytest.mark.django_db
    def test_csv_download_headline_returns_correct_response(self):
        """
        Given a valid `headline` payload to request a download
        When the `POST /api/downloads/v2` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        client = APIClient()
        core_headline_data = self._create_examples_headline_data(is_public=True)
        valid_payload = self._build_valid_headline_payload()

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate csv is being returned
        assert response.headers["Content-Type"] == "text/csv"

        # Check the output itself is as expected
        csv_file = csv.reader(io.StringIO(response.content.decode("utf-8")))
        csv_output = list(csv_file)
        csv_headers = csv_output.pop(0)

        expected_csv_headings = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "period_start",
            "period_end",
            "metric_value",
            "is_public",
        ]
        assert csv_headers == expected_csv_headings

        expected_csv_content = [
            [
                core_headline_data.metric.topic.sub_theme.theme.name,
                core_headline_data.metric.topic.sub_theme.name,
                core_headline_data.metric.topic.name,
                core_headline_data.geography.geography_type.name,
                core_headline_data.geography.name,
                core_headline_data.metric.name,
                core_headline_data.sex,
                core_headline_data.age.name,
                core_headline_data.stratum.name,
                str(core_headline_data.period_start),
                str(core_headline_data.period_end),
                f"{core_headline_data.metric_value:.4f}",
                "",  # is_public
            ]
        ]
        assert csv_output == expected_csv_content

    @pytest.mark.django_db
    def test_returns_bad_request_response_for_invalid_data(self):
        """
        Given a payload to request a download for non-existent data
        When the `POST /api/downloads/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload()
        valid_payload["plots"][0]["date_from"] = "2000-01-01"
        valid_payload["plots"][0]["date_to"] = "2000-12-31"

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.django_db
    def test_returns_bad_request_response_for_sql_injection_input(self):
        """
        Given a payload containing a SQL injection attack
        When the `POST /api/downloads/v2/` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        And the underlying SQL query is escaped and rendered harmless
        """
        # Given
        client = APIClient()
        self._create_example_core_time_series(is_public=True)

        attack_payload = self._build_valid_payload()
        table_name: str = Geography._meta.db_table
        sql_injection_attack_value = f"'; DELETE FROM {table_name}"  # noqa: S608
        attack_payload["plots"][0]["geography"] = sql_injection_attack_value

        # When
        response: Response = client.post(
            path=self.path,
            data=attack_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert Geography.objects.exists()

    @pytest.mark.django_db
    def test_json_download_timeseries_with_no_permissions_returns_correct_response(
        self, patch_auth_enabled: Callable[[], None]
    ):
        """
        Given a valid payload to request a download that contains non-public data
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response should not return any restricted data
        """
        # Given
        client = APIClient()
        core_time_series = self._create_example_core_time_series(is_public=False)
        valid_payload = self._build_valid_payload()
        valid_payload["file_format"] = "json"

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert "json" in response.headers["Content-Type"]

        # Check the output itself is as expected
        assert len(response.data) == 0

    @pytest.mark.django_db
    def test_json_download_timeseries_with_permissions_returns_correct_response(
        self, patch_auth_enabled: Callable[[], None]
    ):
        """
        Given a valid payload to request a download that contains restricted data
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in json format
        """
        # Given
        client = APIClient()
        core_time_series = self._create_example_core_time_series(is_public=False)
        valid_payload = self._build_valid_payload()
        valid_payload["file_format"] = "json"

        infectious_disease_permission = RBACPermissionFactory.create_record(
            name="infectious_disease_permission",
            theme_name=core_time_series.metric.topic.sub_theme.theme.name,
            sub_theme_name=core_time_series.metric.topic.sub_theme.name,
        )

        permission_name = "administrator"
        administrator = RBACPermissionGroupFactory.create_record(name=permission_name)
        administrator.permissions.set([infectious_disease_permission])
        administrator.save()
        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: administrator.name},
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate json is being returned
        assert "json" in response.headers["Content-Type"]

        # Check the output itself is as expected
        returned_obj = response.data[0]
        expected_data = OrderedDict(
            [
                ("theme", core_time_series.metric.topic.sub_theme.theme.name),
                ("sub_theme", core_time_series.metric.topic.sub_theme.name),
                ("topic", core_time_series.metric.topic.name),
                ("geography_type", core_time_series.geography.geography_type.name),
                ("geography", core_time_series.geography.name),
                ("metric", core_time_series.metric.name),
                ("age", core_time_series.age.name),
                ("stratum", core_time_series.stratum.name),
                ("sex", core_time_series.sex),
                ("year", core_time_series.year),
                ("date", core_time_series.date),
                ("metric_value", f"{core_time_series.metric_value:.4f}"),
                (
                    "in_reporting_delay_period",
                    core_time_series.in_reporting_delay_period,
                ),
            ]
        )
        assert returned_obj == expected_data

    @pytest.mark.django_db
    def test_csv_download_timeseries_with_permissions_returns_correct_response(
        self, patch_auth_enabled: Callable[[], None]
    ):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2/` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        client = APIClient()
        core_time_series = self._create_example_core_time_series(is_public=False)
        valid_payload = self._build_valid_payload()
        infectious_disease_permission = RBACPermissionFactory.create_record(
            name="infectious_disease_permission",
            theme_name=core_time_series.metric.topic.sub_theme.theme.name,
            sub_theme_name=core_time_series.metric.topic.sub_theme.name,
        )

        permission_name = "administrator"
        administrator = RBACPermissionGroupFactory.create_record(name=permission_name)
        administrator.permissions.set([infectious_disease_permission])
        administrator.save()

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: administrator.name},
        )

        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate csv is being returned
        assert response.headers["Content-Type"] == "text/csv"

        # Check the output itself is as expected
        csv_file = csv.reader(io.StringIO(response.content.decode("utf-8")))
        csv_output = list(csv_file)
        csv_headers = csv_output.pop(0)

        expected_csv_headings = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "year",
            "date",
            "metric_value",
            "in_reporting_delay_period",
        ]
        assert csv_headers == expected_csv_headings

        expected_csv_content = [
            [
                core_time_series.metric.topic.sub_theme.theme.name,
                core_time_series.metric.topic.sub_theme.name,
                core_time_series.metric.topic.name,
                core_time_series.geography.geography_type.name,
                core_time_series.geography.name,
                core_time_series.metric.name,
                core_time_series.sex,
                core_time_series.age.name,
                core_time_series.stratum.name,
                str(core_time_series.year),
                core_time_series.date,
                f"{core_time_series.metric_value:.4f}",
                str(core_time_series.in_reporting_delay_period),
            ]
        ]
        assert csv_output == expected_csv_content

    @pytest.mark.django_db
    def test_json_download_headline_with_permissions_returns_correct_response(
        self, patch_auth_enabled: Callable[[], None]
    ):
        """
        Given a valid payload to request a download
        When the `POST /api/downloads/v2` endpoint is hit
        Then the response contains the expected output in json format
        """
        # Given
        client = APIClient()
        core_headline_data = self._create_examples_headline_data(is_public=False)
        valid_payload = self._build_valid_headline_payload()
        valid_payload["file_format"] = "json"
        infectious_disease_permission = RBACPermissionFactory.create_record(
            name="infectious_disease_permission",
            theme_name=core_headline_data.metric.topic.sub_theme.theme.name,
            sub_theme_name=core_headline_data.metric.topic.sub_theme.name,
        )

        permission_name = "administrator"
        administrator = RBACPermissionGroupFactory.create_record(name=permission_name)
        administrator.permissions.set([infectious_disease_permission])
        administrator.save()

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: administrator.name},
        )

        # Then
        expected = [
            {
                "theme": core_headline_data.metric.topic.sub_theme.theme.name,
                "sub_theme": core_headline_data.metric.topic.sub_theme.name,
                "topic": core_headline_data.metric.topic.name,
                "geography_type": core_headline_data.geography.geography_type.name,
                "geography": core_headline_data.geography.name,
                "metric": core_headline_data.metric.name,
                "age": core_headline_data.age.name,
                "stratum": core_headline_data.stratum.name,
                "sex": core_headline_data.sex,
                "period_start": core_headline_data.period_start,
                "period_end": core_headline_data.period_end,
                "metric_value": f"{core_headline_data.metric_value:.4f}",
            }
        ]
        json_response = response.data
        assert response.status_code == HTTPStatus.OK
        assert json_response == expected

    @pytest.mark.django_db
    def test_csv_download_headline_with_permissions_returns_correct_response(
        self, patch_auth_enabled: Callable[[], None]
    ):
        """
        Given a valid `headline` payload to request a download that contains restricted data
        When the `POST /api/downloads/v2` endpoint is hit
        Then the response contains the expected output in csv format
        """
        # Given
        client = APIClient()
        core_headline_data = self._create_examples_headline_data(is_public=False)
        valid_payload = self._build_valid_headline_payload()
        infectious_disease_permission = RBACPermissionFactory.create_record(
            name="infectious_disease_permission",
            theme_name=core_headline_data.metric.topic.sub_theme.theme.name,
            sub_theme_name=core_headline_data.metric.topic.sub_theme.name,
        )

        permission_name = "administrator"
        administrator = RBACPermissionGroupFactory.create_record(name=permission_name)
        administrator.permissions.set([infectious_disease_permission])
        administrator.save()

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: administrator.name},
        )

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
            headers={RBAC_AUTH_X_HEADER: administrator.name},
        )
        # Then
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate csv is being returned
        assert response.headers["Content-Type"] == "text/csv"

        # Check the output itself is as expected
        csv_file = csv.reader(io.StringIO(response.content.decode("utf-8")))
        csv_output = list(csv_file)
        csv_headers = csv_output.pop(0)

        expected_csv_headings = [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "metric",
            "sex",
            "age",
            "stratum",
            "period_start",
            "period_end",
            "metric_value",
            "is_public",
        ]
        assert csv_headers == expected_csv_headings

        expected_csv_content = [
            [
                core_headline_data.metric.topic.sub_theme.theme.name,
                core_headline_data.metric.topic.sub_theme.name,
                core_headline_data.metric.topic.name,
                core_headline_data.geography.geography_type.name,
                core_headline_data.geography.name,
                core_headline_data.metric.name,
                core_headline_data.sex,
                core_headline_data.age.name,
                core_headline_data.stratum.name,
                str(core_headline_data.period_start),
                str(core_headline_data.period_end),
                f"{core_headline_data.metric_value:.4f}",
                "",  # is_public
            ]
        ]
        assert csv_output == expected_csv_content
