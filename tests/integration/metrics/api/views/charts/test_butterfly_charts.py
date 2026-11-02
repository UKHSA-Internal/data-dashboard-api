import datetime
import json
import re
import urllib.parse
from http import HTTPStatus
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.test import APIClient

from ingestion.file_ingestion import data_ingester
from metrics.api.settings import ROOT_LEVEL_BASE_DIR
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from tests.factories.metrics.headline import CoreHeadlineFactory

HEADLINE_METRIC = "COVID-19_headline_positivity_latest"
PRIMARY_FIELD_VALUES = ["00-04", "05-11"]
# Age values are cast to human-readable display names by the plots interface
DISPLAYED_PRIMARY_FIELD_VALUES = ["00 - 04", "05 - 11"]

MEASLES_METRIC = "measles_cases_casesByOnsetWeek"
MEASLES_SOURCE_DATA_DIR = Path(ROOT_LEVEL_BASE_DIR) / "source_data"
MEASLES_PRIMARY_FIELD_VALUES = ["00-01", "05-10"]
# Age values are cast to human-readable display names by the plots interface
MEASLES_DISPLAYED_PRIMARY_FIELD_VALUES = ["00 - 01", "05 - 10"]


def _ingest_measles_source_file(*, age: str, stratum: str) -> None:
    """Ingests one of the real `source_data/measles_cases_casesByOnsetWeek_*`
    files via the production `data_ingester()` path.
    """
    filename = (
        f"measles_cases_casesByOnsetWeek_CTRY_E92000001_{age}_all_{stratum}.json"
    )
    filepath = MEASLES_SOURCE_DATA_DIR / filename
    with open(filepath) as file:
        data = json.load(file)

    data_ingester(data=data, filename=filename)


def _ingest_measles_butterfly_source_data() -> None:
    for age in MEASLES_PRIMARY_FIELD_VALUES:
        for stratum in ("active", "recovered"):
            _ingest_measles_source_file(age=age, stratum=stratum)


def _build_measles_butterfly_payload() -> dict:
    return {
        "file_format": "svg",
        "chart_height": 260,
        "chart_width": 515,
        "x_axis": "metric",
        "y_axis": "age",
        "x_axis_title": "Cases",
        "y_axis_title": "Age group",
        "y_axis_minimum_value": None,
        "y_axis_maximum_value": None,
        "chart_type": "butterfly",
        "primary_field_values": MEASLES_PRIMARY_FIELD_VALUES,
        "secondary_category": "stratum",
        "legend_title": "Stratum",
        "static_fields": {
            "theme": "infectious_disease",
            "sub_theme": "vaccine_preventable",
            "topic": "Measles",
            "metric": MEASLES_METRIC,
            "stratum": "default",
            "age": "all",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "date_from": None,
            "date_to": None,
        },
        "segments": [
            {
                "secondary_field_value": "active",
                "colour": RGBAChartLineColours.COLOUR_1_DARK_BLUE.name,
                "label": "Active",
            },
            {
                "secondary_field_value": "recovered",
                "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                "label": "Recovered",
            },
        ],
    }


LEAD_METRIC = "lead_headline_casesByAgeSex"
# All 4 available age bands are used (rather than just 2) so that these
# tests exercise the real "age/sex pyramid" use case, where the y-axis
# (primary field) is expected to support many values, mirrored on
# either side of the chart by sex (the segments).
LEAD_PRIMARY_FIELD_VALUES = ["00-01", "01-04", "05-11", "12-15"]
# Age values are cast to human-readable display names by the plots interface
LEAD_DISPLAYED_PRIMARY_FIELD_VALUES = ["00 - 01", "01 - 04", "05 - 11", "12 - 15"]


def _ingest_lead_source_file(*, age: str, sex: str) -> None:
    """Ingests one of the real `source_data/lead_headline_casesByAgeSex_*`
    files via the production `data_ingester()` path.
    """
    filename = f"lead_headline_casesByAgeSex_CTRY_E92000001_{age}_{sex}_default.json"
    filepath = MEASLES_SOURCE_DATA_DIR / filename
    with open(filepath) as file:
        data = json.load(file)

    data_ingester(data=data, filename=filename)


def _ingest_lead_butterfly_source_data() -> None:
    for age in LEAD_PRIMARY_FIELD_VALUES:
        for sex in ("Male", "Female"):
            _ingest_lead_source_file(age=age, sex=sex)


def _build_lead_butterfly_payload() -> dict:
    return {
        "file_format": "svg",
        "chart_height": 260,
        "chart_width": 515,
        "x_axis": "metric",
        "y_axis": "age",
        "x_axis_title": "Cases",
        "y_axis_title": "Age group",
        "y_axis_minimum_value": None,
        "y_axis_maximum_value": None,
        "chart_type": "butterfly",
        "primary_field_values": LEAD_PRIMARY_FIELD_VALUES,
        "secondary_category": "sex",
        "legend_title": "Sex",
        "static_fields": {
            "theme": "climate_and_environment",
            "sub_theme": "chemical_exposure",
            "topic": "Lead",
            "metric": LEAD_METRIC,
            "stratum": "default",
            "age": "all",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "date_from": None,
            "date_to": None,
        },
        "segments": [
            {
                "secondary_field_value": "m",
                "colour": RGBAChartLineColours.COLOUR_1_DARK_BLUE.name,
                "label": "Male",
            },
            {
                "secondary_field_value": "f",
                "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                "label": "Female",
            },
        ],
    }


LYME_METRIC = "lyme_cases_infectionRateByYear"
# Lyme only varies along the `sex` field in the available source data
# (`age` is fixed to "all" and `stratum` is fixed to "default" across
# every file), so the two sides of the butterfly chart (the segments)
# are male/female, matching the "Lyme disease - male/female" dataset
# described for this feature. Since there is no second field in the
# source data to split across the y-axis, the same `stratum` value is
# deliberately requested twice as the two primary field values.
LYME_PRIMARY_FIELD_VALUES = ["default", "default"]


def _ingest_lyme_source_file(*, sex: str) -> None:
    """Ingests one of the real `source_data/lyme_cases_infectionRateByYear_*`
    files via the production `data_ingester()` path.
    """
    filename = f"lyme_cases_infectionRateByYear_CTRY_E92000001_all_{sex}_default.json"
    filepath = MEASLES_SOURCE_DATA_DIR / filename
    with open(filepath) as file:
        data = json.load(file)

    data_ingester(data=data, filename=filename)


def _ingest_lyme_butterfly_source_data() -> None:
    for sex in ("male", "female"):
        _ingest_lyme_source_file(sex=sex)


def _build_lyme_butterfly_payload() -> dict:
    return {
        "file_format": "svg",
        "chart_height": 260,
        "chart_width": 515,
        "x_axis": "metric",
        "y_axis": "stratum",
        "x_axis_title": "Infection rate",
        "y_axis_title": "Stratum",
        "y_axis_minimum_value": None,
        "y_axis_maximum_value": None,
        "chart_type": "butterfly",
        "primary_field_values": LYME_PRIMARY_FIELD_VALUES,
        "secondary_category": "sex",
        "legend_title": "Sex",
        "static_fields": {
            "theme": "infectious_disease",
            "sub_theme": "vector_borne",
            "topic": "lyme",
            "metric": LYME_METRIC,
            "stratum": "default",
            "age": "all",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "date_from": None,
            "date_to": None,
        },
        "segments": [
            {
                "secondary_field_value": "m",
                "colour": RGBAChartLineColours.COLOUR_1_DARK_BLUE.name,
                "label": "Male",
            },
            {
                "secondary_field_value": "f",
                "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                "label": "Female",
            },
        ],
    }


def _build_butterfly_payload() -> dict:
    return {
        "file_format": "svg",
        "chart_height": 260,
        "chart_width": 515,
        "x_axis": "metric",
        "y_axis": "age",
        "x_axis_title": "Cases",
        "y_axis_title": "Age group",
        "y_axis_minimum_value": None,
        "y_axis_maximum_value": None,
        "chart_type": "butterfly",
        "primary_field_values": PRIMARY_FIELD_VALUES,
        "secondary_category": "sex",
        "legend_title": "Sex",
        "static_fields": {
            "theme": "infectious_disease",
            "sub_theme": "respiratory",
            "topic": "COVID-19",
            "metric": HEADLINE_METRIC,
            "stratum": "default",
            "age": "all",
            "geography": "England",
            "geography_type": "Nation",
            "sex": "all",
            "date_from": None,
            "date_to": None,
        },
        "segments": [
            {
                "secondary_field_value": "m",
                "colour": RGBAChartLineColours.COLOUR_1_DARK_BLUE.name,
                "label": "Male",
            },
            {
                "secondary_field_value": "f",
                "colour": RGBAChartLineColours.COLOUR_4_ORANGE.name,
                "label": "Female",
            },
        ],
    }


def _create_headline_records() -> None:
    for index, age in enumerate(PRIMARY_FIELD_VALUES):
        for sex in ("m", "f"):
            CoreHeadlineFactory.create_record(
                metric_value=100 * (index + 1),
                metric=HEADLINE_METRIC,
                age=age,
                sex=sex,
                stratum="default",
                period_end=datetime.date(2023, 1, 7),
            )


@pytest.mark.django_db
class TestButterflyChartsView:
    @property
    def path(self) -> str:
        return "/api/charts/dual-category/v1"

    @pytest.mark.parametrize(
        "query_params,response_header",
        [
            ({}, "application/json"),
            ({"preview": True}, "image/svg"),
        ],
    )
    def test_returns_correct_response_for_headline_butterfly_chart(
        self,
        query_params: dict[str, bool],
        response_header: str,
        admin_user: User,
    ):
        """
        Given a valid payload to create a headline butterfly chart
        When the `POST /api/charts/dual-category/v1` endpoint is hit
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _create_headline_records()

        # When
        response: Response = client.post(
            path=self.path,
            query_params=query_params,
            data=_build_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == response_header

    def test_returns_bad_request_when_segment_count_is_not_two(
        self,
        admin_user: User,
    ):
        """
        Given a butterfly chart payload which contains more than 2 segments
        When the `POST /api/charts/dual-category/v1` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _create_headline_records()
        invalid_payload = _build_butterfly_payload()
        invalid_payload["segments"].append(
            {
                "secondary_field_value": "all",
                "colour": RGBAChartLineColours.COLOUR_2_TURQUOISE.name,
                "label": "All",
            }
        )

        # When
        response: Response = client.post(
            path=self.path,
            data=invalid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
class TestButterflyTablesView:
    @property
    def path(self) -> str:
        return "/api/tables/dual-category/v1/"

    def test_groups_values_by_primary_field_value_with_segment_labels(self):
        """
        Given a valid butterfly table payload
        When the dual-category tables endpoint is called
        Then the response groups values by primary field value with segment labels
        """
        # Given
        client = APIClient()
        _create_headline_records()
        payload = _build_butterfly_payload()

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK
        assert [row["reference"] for row in response.data] == (
            DISPLAYED_PRIMARY_FIELD_VALUES
        )
        assert [value["label"] for value in response.data[0]["values"]] == [
            "Male",
            "Female",
        ]


@pytest.mark.django_db
class TestButterflyDownloadsView:
    @property
    def path(self) -> str:
        return "/api/downloads/dual-category/v1"

    @pytest.mark.parametrize("file_format", ["csv", "json"])
    def test_returns_download_for_both_file_formats(self, file_format: str):
        """
        Given a valid butterfly download payload
        When the dual-category downloads endpoint is called
        Then an HTTP 200 OK response is returned containing the plot data
        """
        # Given
        client = APIClient()
        _create_headline_records()
        payload = _build_butterfly_payload()
        payload["file_format"] = file_format

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK

        content = response.getvalue().decode()
        if file_format == "json":
            assert len(json.loads(content)) > 0
        else:
            assert HEADLINE_METRIC in content


@pytest.mark.django_db
class TestButterflyChartsViewWithRealMeaslesSourceData:
    """Integration tests which ingest the real
    `source_data/measles_cases_casesByOnsetWeek_*` files
    via the production `data_ingester()` path, and then
    exercise the butterfly chart endpoint against that data.
    """

    @property
    def path(self) -> str:
        return "/api/charts/dual-category/v1"

    @pytest.mark.parametrize(
        "query_params,response_header",
        [
            ({}, "application/json"),
            ({"preview": True}, "image/svg"),
        ],
    )
    def test_returns_correct_response_for_measles_butterfly_chart(
        self,
        query_params: dict[str, bool],
        response_header: str,
        admin_user: User,
    ):
        """
        Given real measles `casesByOnsetWeek` source data
            ingested via `data_ingester()`
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a valid butterfly chart payload
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_measles_butterfly_source_data()
        assert CoreTimeSeries.objects.filter(metric__name=MEASLES_METRIC).exists()

        # When
        response: Response = client.post(
            path=self.path,
            query_params=query_params,
            data=_build_measles_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == response_header

    def test_returns_bad_request_when_segment_count_is_not_two_for_measles_data(
        self,
        admin_user: User,
    ):
        """
        Given real measles source data ingested via `data_ingester()`
            and a butterfly chart payload with more than 2 segments
        When the `POST /api/charts/dual-category/v1` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_measles_butterfly_source_data()
        invalid_payload = _build_measles_butterfly_payload()
        invalid_payload["segments"].append(
            {
                "secondary_field_value": "all",
                "colour": RGBAChartLineColours.COLOUR_2_TURQUOISE.name,
                "label": "All",
            }
        )

        # When
        response: Response = client.post(
            path=self.path,
            data=invalid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_returns_not_found_when_primary_field_value_has_no_data_for_segment(
        self,
        admin_user: User,
    ):
        """
        Given real measles source data ingested for only one
            of the two requested secondary field values (strata)
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a butterfly chart payload requesting both strata
        Then an HTTP 400 BAD REQUEST response is returned
            since data cannot be found for one of the segments
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        # Only ingest the "active" stratum data, omitting "recovered"
        for age in MEASLES_PRIMARY_FIELD_VALUES:
            _ingest_measles_source_file(age=age, stratum="active")

        # When
        response: Response = client.post(
            path=self.path,
            data=_build_measles_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
class TestButterflyTablesViewWithRealMeaslesSourceData:
    @property
    def path(self) -> str:
        return "/api/tables/dual-category/v1/"

    def test_groups_values_by_primary_field_value_with_segment_labels(self):
        """
        Given real measles source data ingested via `data_ingester()`
            and a valid butterfly table payload
        When the dual-category tables endpoint is called
        Then the response groups values by primary field value
            with segment labels
        """
        # Given
        client = APIClient()
        _ingest_measles_butterfly_source_data()
        payload = _build_measles_butterfly_payload()

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK
        assert [row["reference"] for row in response.data] == (
            MEASLES_DISPLAYED_PRIMARY_FIELD_VALUES
        )
        assert [value["label"] for value in response.data[0]["values"]] == [
            "Active",
            "Recovered",
        ]


@pytest.mark.django_db
class TestButterflyDownloadsViewWithRealMeaslesSourceData:
    @property
    def path(self) -> str:
        return "/api/downloads/dual-category/v1"

    @pytest.mark.parametrize("file_format", ["csv", "json"])
    def test_returns_download_for_both_file_formats(self, file_format: str):
        """
        Given real measles source data ingested via `data_ingester()`
            and a valid butterfly download payload
        When the dual-category downloads endpoint is called
        Then an HTTP 200 OK response is returned containing the plot data
        """
        # Given
        client = APIClient()
        _ingest_measles_butterfly_source_data()
        payload = _build_measles_butterfly_payload()
        payload["file_format"] = file_format

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK

        content = response.getvalue().decode()
        if file_format == "json":
            assert len(json.loads(content)) > 0
        else:
            assert MEASLES_METRIC in content


@pytest.mark.django_db
class TestButterflyChartsViewWithRealLeadSourceData:
    """Integration tests which ingest the real
    `source_data/lead_headline_casesByAgeSex_*` files
    via the production `data_ingester()` path, and then
    exercise the butterfly chart endpoint against that
    headline data (dataset: "Lead - age/sex").
    """

    @property
    def path(self) -> str:
        return "/api/charts/dual-category/v1"

    @pytest.mark.parametrize(
        "query_params,response_header",
        [
            ({}, "application/json"),
            ({"preview": True}, "image/svg"),
        ],
    )
    def test_returns_correct_response_for_lead_butterfly_chart(
        self,
        query_params: dict[str, bool],
        response_header: str,
        admin_user: User,
    ):
        """
        Given real lead `casesByAgeSex` headline source data
            ingested via `data_ingester()`
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a valid butterfly chart payload
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_lead_butterfly_source_data()

        # When
        response: Response = client.post(
            path=self.path,
            query_params=query_params,
            data=_build_lead_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == response_header

    def test_renders_all_age_bands_mirrored_across_exactly_two_sides(
        self,
        admin_user: User,
    ):
        """
        Given real lead `casesByAgeSex` headline source data ingested
            for all 4 age bands via `data_ingester()`
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a valid butterfly chart payload
        Then the rendered chart is a true "pyramid" style butterfly chart:
            the y-axis (primary field) carries every one of the 4 age
            bands, mirrored across exactly 2 sides (the sex segments)
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_lead_butterfly_source_data()

        # When
        response: Response = client.post(
            path=self.path,
            data=_build_lead_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        svg = urllib.parse.unquote_plus(response.data["chart"])
        # Every age band label appears on the y-axis as its own category
        for displayed_age in LEAD_DISPLAYED_PRIMARY_FIELD_VALUES:
            assert displayed_age in svg
        # Plotly renders every bar trace within a single `<g class="point">`
        # group, so the bar count is asserted via the rendered `<path>`
        # elements: 1 per age band, per side (mirrored for each sex)
        points_group = re.search(
            r'<g class="point".*?</g>',
            svg,
            re.DOTALL,
        )
        assert points_group is not None
        bar_count = points_group.group().count("<path")
        assert bar_count == len(LEAD_PRIMARY_FIELD_VALUES) * 2

    def test_returns_bad_request_when_segment_count_is_not_two_for_lead_data(
        self,
        admin_user: User,
    ):
        """
        Given real lead source data ingested via `data_ingester()`
            and a butterfly chart payload with more than 2 segments
        When the `POST /api/charts/dual-category/v1` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_lead_butterfly_source_data()
        invalid_payload = _build_lead_butterfly_payload()
        invalid_payload["segments"].append(
            {
                "secondary_field_value": "all",
                "colour": RGBAChartLineColours.COLOUR_2_TURQUOISE.name,
                "label": "All",
            }
        )

        # When
        response: Response = client.post(
            path=self.path,
            data=invalid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_returns_not_found_when_primary_field_value_has_no_data_for_segment(
        self,
        admin_user: User,
    ):
        """
        Given real lead source data ingested for only one
            of the two requested segments (sexes)
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a butterfly chart payload requesting both sexes
        Then an HTTP 400 BAD REQUEST response is returned
            since data cannot be found for one of the segments
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        # Only ingest the "Male" segment data, omitting "Female"
        for age in LEAD_PRIMARY_FIELD_VALUES:
            _ingest_lead_source_file(age=age, sex="Male")

        # When
        response: Response = client.post(
            path=self.path,
            data=_build_lead_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
class TestButterflyTablesViewWithRealLeadSourceData:
    @property
    def path(self) -> str:
        return "/api/tables/dual-category/v1/"

    def test_groups_values_by_primary_field_value_with_segment_labels(self):
        """
        Given real lead source data ingested via `data_ingester()`
            and a valid butterfly table payload
        When the dual-category tables endpoint is called
        Then the response groups values by primary field value
            with segment labels
        """
        # Given
        client = APIClient()
        _ingest_lead_butterfly_source_data()
        payload = _build_lead_butterfly_payload()

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK
        assert [row["reference"] for row in response.data] == (
            LEAD_DISPLAYED_PRIMARY_FIELD_VALUES
        )
        assert [value["label"] for value in response.data[0]["values"]] == [
            "Male",
            "Female",
        ]


@pytest.mark.django_db
class TestButterflyDownloadsViewWithRealLeadSourceData:
    @property
    def path(self) -> str:
        return "/api/downloads/dual-category/v1"

    @pytest.mark.parametrize("file_format", ["csv", "json"])
    def test_returns_download_for_both_file_formats(self, file_format: str):
        """
        Given real lead source data ingested via `data_ingester()`
            and a valid butterfly download payload
        When the dual-category downloads endpoint is called
        Then an HTTP 200 OK response is returned containing the plot data
        """
        # Given
        client = APIClient()
        _ingest_lead_butterfly_source_data()
        payload = _build_lead_butterfly_payload()
        payload["file_format"] = file_format

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK

        content = response.getvalue().decode()
        if file_format == "json":
            assert len(json.loads(content)) > 0
        else:
            assert LEAD_METRIC in content


@pytest.mark.django_db
class TestButterflyChartsViewWithRealLymeSourceData:
    """Integration tests which ingest the real
    `source_data/lyme_cases_infectionRateByYear_*` files
    via the production `data_ingester()` path, and then
    exercise the butterfly chart endpoint against that
    timeseries data (dataset: "Lyme disease - male/female").

    Notes:
        Unlike the lead/measles source data, the available Lyme
        source files only vary along the `sex` field (`age` and
        `stratum` are fixed across every file). The male/female
        sides of the butterfly chart are therefore modelled as the
        segments, with the same `stratum` value requested twice as
        the two primary (y-axis) field values, since there is no
        second field in the source data to split the y-axis on.
    """

    @property
    def path(self) -> str:
        return "/api/charts/dual-category/v1"

    @pytest.mark.parametrize(
        "query_params,response_header",
        [
            ({}, "application/json"),
            ({"preview": True}, "image/svg"),
        ],
    )
    def test_returns_correct_response_for_lyme_butterfly_chart(
        self,
        query_params: dict[str, bool],
        response_header: str,
        admin_user: User,
    ):
        """
        Given real lyme `infectionRateByYear` timeseries source data
            ingested via `data_ingester()`
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a valid butterfly chart payload
        Then an HTTP 200 OK response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_lyme_butterfly_source_data()
        assert CoreTimeSeries.objects.filter(metric__name=LYME_METRIC).exists()

        # When
        response: Response = client.post(
            path=self.path,
            query_params=query_params,
            data=_build_lyme_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"] == response_header

    def test_returns_bad_request_when_segment_count_is_not_two_for_lyme_data(
        self,
        admin_user: User,
    ):
        """
        Given real lyme source data ingested via `data_ingester()`
            and a butterfly chart payload with more than 2 segments
        When the `POST /api/charts/dual-category/v1` endpoint is hit
        Then an HTTP 400 BAD REQUEST response is returned
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_lyme_butterfly_source_data()
        invalid_payload = _build_lyme_butterfly_payload()
        invalid_payload["segments"].append(
            {
                "secondary_field_value": "all",
                "colour": RGBAChartLineColours.COLOUR_2_TURQUOISE.name,
                "label": "All",
            }
        )

        # When
        response: Response = client.post(
            path=self.path,
            data=invalid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_returns_bad_request_when_segments_resolve_to_a_single_group(
        self,
        admin_user: User,
    ):
        """
        Given real lyme source data ingested for only one sex
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a butterfly chart payload requesting both male and
            female segments
        Then an HTTP 400 BAD REQUEST response is returned
            since data cannot be found for the missing segment
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        # Only ingest the "male" sex data, omitting "female"
        _ingest_lyme_source_file(sex="male")

        # When
        response: Response = client.post(
            path=self.path,
            data=_build_lyme_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.django_db
class TestButterflyTablesViewWithRealLymeSourceData:
    @property
    def path(self) -> str:
        return "/api/tables/dual-category/v1/"

    def test_groups_values_by_segment_labels(self):
        """
        Given real lyme source data ingested via `data_ingester()`
            and a valid butterfly table payload
        When the dual-category tables endpoint is called
        Then the response includes a single row, since both requested
            primary field values resolve to the same "default" stratum,
            with the male/female segment labels
        """
        # Given
        client = APIClient()
        _ingest_lyme_butterfly_source_data()
        payload = _build_lyme_butterfly_payload()

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK
        # Both primary field values are "default", so they collapse into 1 row
        assert len(response.data) == 1
        assert response.data[0]["reference"] == "default"
        assert [value["label"] for value in response.data[0]["values"]] == [
            "Male",
            "Female",
        ]


@pytest.mark.django_db
class TestButterflyDownloadsViewWithRealLymeSourceData:
    @property
    def path(self) -> str:
        return "/api/downloads/dual-category/v1"

    @pytest.mark.parametrize("file_format", ["csv", "json"])
    def test_returns_download_for_both_file_formats(self, file_format: str):
        """
        Given real lyme source data ingested via `data_ingester()`
            and a valid butterfly download payload
        When the dual-category downloads endpoint is called
        Then an HTTP 200 OK response is returned containing the plot data
        """
        # Given
        client = APIClient()
        _ingest_lyme_butterfly_source_data()
        payload = _build_lyme_butterfly_payload()
        payload["file_format"] = file_format

        # When
        response: Response = client.post(path=self.path, data=payload, format="json")

        # Then
        assert response.status_code == HTTPStatus.OK

        content = response.getvalue().decode()
        if file_format == "json":
            assert len(json.loads(content)) > 0
        else:
            assert LYME_METRIC in content
