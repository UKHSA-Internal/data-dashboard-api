"""Integration tests for butterfly charts.

Notes:
    Butterfly charts are served by the dual-category endpoints.
    A butterfly chart payload describes the axes as they are drawn on
    the chart: the horizontal (x) axis holds the metric values and the
    vertical (y) axis holds the primary category (eg. age), with the
    requested `primary_field_values` making up the y-axis categories
    and the 2 requested `segments` making up either side of the chart.

    The dual-category tables and downloads endpoints are not butterfly
    specific, they always carry the primary category on `x_axis`,
    so the equivalent tabular payloads are built by
    `_build_tabular_payload()`, which swaps the axes back over.
"""

import datetime
import json
from http import HTTPStatus
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.test import APIClient

from ingestion.file_ingestion import data_ingester
from metrics.api.settings import ROOT_LEVEL_BASE_DIR
from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.charts.butterfly.generation import (
    InvalidButterflyChartSegmentsError,
)
from metrics.domain.charts.colour_scheme import RGBAChartLineColours
from tests.factories.metrics.headline import CoreHeadlineFactory

CHARTS_PATH = "/api/charts/dual-category/v1"
TABLES_PATH = "/api/tables/dual-category/v1/"
DOWNLOADS_PATH = "/api/downloads/dual-category/v1"

SOURCE_DATA_DIR = Path(ROOT_LEVEL_BASE_DIR) / "source_data"

# A butterfly chart draws 1 trace per side of the chart
EXPECTED_BUTTERFLY_SIDES_COUNT = 2

HEADLINE_METRIC = "COVID-19_headline_positivity_latest"
PRIMARY_FIELD_VALUES = ["00-04", "05-11"]
# Age values are cast to human-readable display names by the tables interface
DISPLAYED_PRIMARY_FIELD_VALUES = ["00 - 04", "05 - 11"]

MEASLES_METRIC = "measles_cases_casesByOnsetWeek"
MEASLES_PRIMARY_FIELD_VALUES = ["00-01", "05-10"]

LEAD_METRIC = "lead_headline_casesByAgeSex"
# All 4 available age bands are used (rather than just 2) so that these
# tests exercise the real "age/sex pyramid" use case, where the y-axis
# (primary field) is expected to support many values, mirrored on
# either side of the chart by sex (the segments).
LEAD_PRIMARY_FIELD_VALUES = ["00-01", "01-04", "05-11", "12-15"]
# Age values are cast to human-readable display names by the tables interface
LEAD_DISPLAYED_PRIMARY_FIELD_VALUES = ["00 - 01", "01 - 04", "05 - 11", "12 - 15"]


def _ingest_source_file(*, filename: str) -> None:
    """Ingests the given `source_data` file via the production `data_ingester()` path."""
    filepath = SOURCE_DATA_DIR / filename
    with open(filepath) as file:
        data = json.load(file)

    data_ingester(data=data, filename=filename)


def _build_tabular_payload(*, chart_payload: dict) -> dict:
    """Recasts the given butterfly chart payload for the tables/downloads endpoints.

    Notes:
        The dual-category tables and downloads endpoints always carry
        the primary category (eg. age) on `x_axis` and the metric
        values on `y_axis`, which is the opposite way round to the
        butterfly chart payload. The axes and their titles are
        therefore swapped over here.

    Args:
        chart_payload: The butterfly chart payload to recast.

    Returns:
        The equivalent payload for the tables/downloads endpoints.

    """
    payload = {**chart_payload}
    payload["x_axis"], payload["y_axis"] = payload["y_axis"], payload["x_axis"]
    payload["x_axis_title"], payload["y_axis_title"] = (
        payload["y_axis_title"],
        payload["x_axis_title"],
    )
    return payload


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


def _ingest_measles_source_file(*, age: str, stratum: str) -> None:
    _ingest_source_file(
        filename=(
            f"measles_cases_casesByOnsetWeek_CTRY_E92000001_{age}_all_{stratum}.json"
        )
    )


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


def _ingest_lead_source_file(*, age: str, sex: str) -> None:
    _ingest_source_file(
        filename=f"lead_headline_casesByAgeSex_CTRY_E92000001_{age}_{sex}_default.json"
    )


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


@pytest.mark.django_db
class TestButterflyChartsView:
    @property
    def path(self) -> str:
        return CHARTS_PATH

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

    def test_mirrors_each_segment_on_either_side_of_the_chart(
        self,
        admin_user: User,
    ):
        """
        Given a valid payload to create a headline butterfly chart
        When the `POST /api/charts/dual-category/v1` endpoint is hit
        Then the chart is drawn with 1 trace per requested segment,
            plotted against the primary field values,
            with the first requested segment mirrored
            onto the left hand side of the chart
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _create_headline_records()

        # When
        response: Response = client.post(
            path=self.path,
            data=_build_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        left_hand_side, right_hand_side = response.data["figure"]["data"]

        # The requested segment labels are used for each side of the chart
        assert left_hand_side["name"] == "Male"
        assert right_hand_side["name"] == "Female"

        # The primary field values make up the categories of the y-axis
        assert left_hand_side["y"] == PRIMARY_FIELD_VALUES
        assert right_hand_side["y"] == PRIMARY_FIELD_VALUES

        # The 1st requested segment is drawn on the left hand side,
        # by negating its values, whilst the absolute values
        # are retained on the `customdata` for the hover text
        assert left_hand_side["x"] == [-100.0, -200.0]
        assert left_hand_side["customdata"] == [100.0, 200.0]
        assert right_hand_side["x"] == [100.0, 200.0]
        assert right_hand_side["customdata"] == [100.0, 200.0]

        # The requested colour is applied to each side of the chart
        assert (
            left_hand_side["marker"]["color"]
            == RGBAChartLineColours.COLOUR_1_DARK_BLUE.stringified
        )
        assert (
            right_hand_side["marker"]["color"]
            == RGBAChartLineColours.COLOUR_4_ORANGE.stringified
        )

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
        return TABLES_PATH

    def test_groups_values_by_primary_field_value_with_segment_labels(self):
        """
        Given a valid butterfly table payload
        When the dual-category tables endpoint is called
        Then the response groups values by primary field value with segment labels
        """
        # Given
        client = APIClient()
        _create_headline_records()
        payload = _build_tabular_payload(chart_payload=_build_butterfly_payload())

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
        return DOWNLOADS_PATH

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
        payload = _build_tabular_payload(chart_payload=_build_butterfly_payload())
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
    exercise the butterfly chart endpoint against that
    timeseries data.
    """

    @property
    def path(self) -> str:
        return CHARTS_PATH

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

    def test_draws_one_bar_per_primary_field_value_for_each_segment(
        self,
        admin_user: User,
    ):
        """
        Given real measles source data ingested via `data_ingester()`
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a valid butterfly chart payload
        Then the chart is drawn with 1 trace per requested segment,
            each holding 1 value per primary field value,
            with the first requested segment mirrored
            onto the left hand side of the chart
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        _ingest_measles_butterfly_source_data()

        # When
        response: Response = client.post(
            path=self.path,
            data=_build_measles_butterfly_payload(),
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK
        left_hand_side, right_hand_side = response.data["figure"]["data"]

        assert left_hand_side["name"] == "Active"
        assert right_hand_side["name"] == "Recovered"

        # Each side holds a single bar per primary field value,
        # even though the underlying metric is sourced from timeseries data
        assert left_hand_side["y"] == MEASLES_PRIMARY_FIELD_VALUES
        assert right_hand_side["y"] == MEASLES_PRIMARY_FIELD_VALUES

        # The 1st requested segment is mirrored onto the left hand side
        assert left_hand_side["x"] == [-value for value in left_hand_side["customdata"]]
        assert right_hand_side["x"] == right_hand_side["customdata"]

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

    def test_raises_error_when_only_one_segment_returns_data(
        self,
        admin_user: User,
    ):
        """
        Given real measles source data ingested for only one
            of the two requested secondary field values (strata)
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a butterfly chart payload requesting both strata
        Then an `InvalidButterflyChartSegmentsError` is raised,
            since a butterfly chart cannot be drawn
            without data for both sides of the chart
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        # Only ingest the "active" stratum data, omitting "recovered"
        for age in MEASLES_PRIMARY_FIELD_VALUES:
            _ingest_measles_source_file(age=age, stratum="active")

        # When / Then
        with pytest.raises(InvalidButterflyChartSegmentsError):
            client.post(
                path=self.path,
                data=_build_measles_butterfly_payload(),
                format="json",
            )


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
        return CHARTS_PATH

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
        traces = response.data["figure"]["data"]
        # The chart is drawn across exactly 2 sides, 1 per sex segment
        assert len(traces) == EXPECTED_BUTTERFLY_SIDES_COUNT
        left_hand_side, right_hand_side = traces
        assert [trace["name"] for trace in traces] == ["Male", "Female"]

        # Every age band is carried on the y-axis as its own category,
        # in the order it was requested, on both sides of the chart
        assert left_hand_side["y"] == LEAD_PRIMARY_FIELD_VALUES
        assert right_hand_side["y"] == LEAD_PRIMARY_FIELD_VALUES

        # 1 bar is drawn per age band, per side of the chart
        assert len(left_hand_side["x"]) == len(LEAD_PRIMARY_FIELD_VALUES)
        assert len(right_hand_side["x"]) == len(LEAD_PRIMARY_FIELD_VALUES)

        # The male bars are mirrored onto the left hand side,
        # whilst the female bars are drawn on the right hand side
        assert all(value < 0 for value in left_hand_side["x"])
        assert all(value > 0 for value in right_hand_side["x"])

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

    def test_raises_error_when_only_one_segment_returns_data(
        self,
        admin_user: User,
    ):
        """
        Given real lead source data ingested for only one
            of the two requested segments (sexes)
        When the `POST /api/charts/dual-category/v1` endpoint is hit
            with a butterfly chart payload requesting both sexes
        Then an `InvalidButterflyChartSegmentsError` is raised,
            since a butterfly chart cannot be drawn
            without data for both sides of the chart
        """
        client = APIClient()
        client.force_authenticate(user=admin_user)
        # Only ingest the "Male" segment data, omitting "Female"
        for age in LEAD_PRIMARY_FIELD_VALUES:
            _ingest_lead_source_file(age=age, sex="Male")

        with pytest.raises(InvalidButterflyChartSegmentsError):
            client.post(
                path=self.path,
                data=_build_lead_butterfly_payload(),
                format="json",
            )


@pytest.mark.django_db
class TestButterflyTablesViewWithRealLeadSourceData:
    @property
    def path(self) -> str:
        return TABLES_PATH

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
        payload = _build_tabular_payload(chart_payload=_build_lead_butterfly_payload())

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
        return DOWNLOADS_PATH

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
        payload = _build_tabular_payload(chart_payload=_build_lead_butterfly_payload())
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
