import datetime
from http import HTTPStatus
from urllib.parse import unquote_plus
from unittest import mock

import pytest
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.api.enums import AppMode
from metrics.api.views.charts.single_category_charts import ChartsView
from metrics.data.models.core_models import CoreTimeSeries
from metrics.interfaces.data_classification.access import DataClassificationInterface
from tests.factories.metrics.time_series import CoreTimeSeriesFactory

DEFAULT_WATERMARK_LABEL = "OFFICIAL-SENSITIVE"


class TestChartsView:
    @staticmethod
    def _build_valid_payload_for_existing_timeseries(
        core_timeseries: CoreTimeSeries,
    ) -> dict[str, object]:
        return {
            "file_format": "png",
            "plots": [
                {
                    "topic": core_timeseries.metric.metric_group.topic.name,
                    "metric": core_timeseries.metric.name,
                    "chart_type": "bar",
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly_for_v2(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/charts/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)

        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        path = "/api/charts/v2"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_returns_correct_response_for_v2(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/charts/v2/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)

        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        path = "/api/charts/v2/"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK != HTTPStatus.UNAUTHORIZED

        # Check that the headers on the response indicate a `png` image being returned
        assert response.headers["Content-Type"] == "image/png"

    def test_cms_admin_mode_uses_is_authenticated_permission(self):
        """
        Given the application is running in CMS admin mode
        When `ChartsView.get_permissions()` is called
        Then the view requires Django authenticated access
        """

        with mock.patch(
            "metrics.api.views.charts.single_category_charts.config.APP_MODE",
            AppMode.CMS_ADMIN.value,
        ):
            permissions_list = ChartsView().get_permissions()

        assert len(permissions_list) == 1
        assert isinstance(permissions_list[0], permissions.IsAuthenticated)

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly_for_v3(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/charts/v3` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        valid_payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        valid_payload["file_format"] = "svg"
        path = "/api/charts/v3"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )
        assert response.status_code == HTTPStatus.OK
        response_data = response.data
        latest_date = max(
            core_timeseries.date for core_timeseries in core_timeseries_example
        )
        assert response_data["last_updated"] == str(latest_date)

    @pytest.mark.django_db
    def test_returns_correct_response_for_v3_age_based_chart(self):
        """
        Given a valid payload to create an age-based chart
        When the `POST /api/charts/v3/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        And the `last_updated` field is returned with the correct value
        """
        # Given
        client = APIClient()
        core_timeseries_records = [
            CoreTimeSeriesFactory.create_record(
                metric_name="COVID-19_deaths_ONSByDay", age_name="65-84", metric_value=1
            ),
            CoreTimeSeriesFactory.create_record(
                metric_name="COVID-19_deaths_ONSByDay", age_name="06-17", metric_value=2
            ),
            CoreTimeSeriesFactory.create_record(
                metric_name="COVID-19_deaths_ONSByDay", age_name="85+", metric_value=3
            ),
            CoreTimeSeriesFactory.create_record(
                metric_name="COVID-19_deaths_ONSByDay", age_name="18-64", metric_value=4
            ),
            CoreTimeSeriesFactory.create_record(
                metric_name="COVID-19_deaths_ONSByDay", age_name="all", metric_value=5
            ),
        ]

        valid_payload = {
            "file_format": "svg",
            "x_axis": "age",
            "plots": [
                {
                    "topic": "COVID-19",
                    "metric": "COVID-19_deaths_ONSByDay",
                    "chart_type": "bar",
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }
        path = "/api/charts/v3/"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.OK != HTTPStatus.UNAUTHORIZED

        # Check that the headers on the response indicate a json response is being returned
        assert response.headers["Content-Type"] == "application/json"

        # Check that the "last_updated" is returned correctly for the age-based chart
        response_data = response.data
        latest_date = max(
            core_timeseries.date for core_timeseries in core_timeseries_records
        )
        assert response_data["last_updated"] == str(latest_date)

    @pytest.mark.django_db
    @pytest.mark.parametrize("endpoint", ["/api/charts/v2/", "/api/charts/v3/"])
    def test_returns_bad_request_response_when_queried_data_does_not_exist(
        self,
        endpoint: str,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a payload for which there is no corresponding data
        When the `POST /api/charts/v3/` endpoint is hit
        Then the response is an HTTP 400 BAD REQUEST
        """
        # Given
        client = APIClient()
        client.force_authenticate(user=admin_user)
        # Note that the authentication is only needed for the v2 endpoint
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": core_timeseries_example[0].metric.topic.name,
                    "metric": core_timeseries_example[0].metric.name,
                    "chart_type": "bar",
                    "age": "non-existent-age",
                }
            ],
        }
        path = endpoint

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST

    @pytest.mark.django_db
    def test_v2_defaults_data_classification_to_official_sensitive_when_not_public(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a v2 chart request with `is_public=False` and no `data_classification`
        When the endpoint is called
        Then the generated chart params contain the default data classification
        """

        client = APIClient()
        client.force_authenticate(user=admin_user)

        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["is_public"] = False

        with mock.patch(
            "metrics.api.views.charts.single_category_charts.access.generate_chart_as_file",
            return_value=b"png-bytes",
        ) as spy_generate_chart_as_file:
            response: Response = client.post(
                path="/api/charts/v2/",
                data=payload,
                format="json",
            )

        assert response.status_code == HTTPStatus.OK
        chart_request_params = spy_generate_chart_as_file.call_args.kwargs[
            "chart_request_params"
        ]
        assert chart_request_params.is_public is False
        assert (
            chart_request_params.data_classification
            == DataClassificationInterface.DEFAULT
        )

    @pytest.mark.django_db
    def test_v2_preserves_explicit_data_classification_when_not_public(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a v2 chart request with `is_public=False` and an explicit classification
        When the endpoint is called
        Then the explicit data classification is used for chart generation
        """

        client = APIClient()
        client.force_authenticate(user=admin_user)

        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["is_public"] = False
        payload["data_classification"] = "SECRET"

        with mock.patch(
            "metrics.api.views.charts.single_category_charts.access.generate_chart_as_file",
            return_value=b"png-bytes",
        ) as spy_generate_chart_as_file:
            response: Response = client.post(
                path="/api/charts/v2/",
                data=payload,
                format="json",
            )

        assert response.status_code == HTTPStatus.OK
        chart_request_params = spy_generate_chart_as_file.call_args.kwargs[
            "chart_request_params"
        ]
        assert chart_request_params.is_public is False
        assert chart_request_params.data_classification == "SECRET"

    @pytest.mark.django_db
    def test_v2_svg_response_contains_watermark_for_non_public_chart(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a v2 request for an SVG chart with `is_public=False`
        When the endpoint returns the generated chart
        Then the SVG output contains the default watermark text
        """

        client = APIClient()
        client.force_authenticate(user=admin_user)

        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["file_format"] = "svg"
        payload["is_public"] = False

        response: Response = client.post(
            path="/api/charts/v2/",
            data=payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK
        assert response.headers["Content-Type"].startswith("image/svg")

        svg_bytes = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        svg_text = svg_bytes.decode("utf-8", errors="ignore")

        assert "<svg" in svg_text
        assert DEFAULT_WATERMARK_LABEL in svg_text

    @pytest.mark.django_db
    def test_v2_svg_response_formats_explicit_official_sensitive_value_as_label(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a v2 SVG chart request with the canonical value `official_sensitive`
        When the endpoint renders the chart
        Then the SVG watermark uses the explicit label `OFFICIAL-SENSITIVE`
        """

        client = APIClient()
        client.force_authenticate(user=admin_user)

        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["file_format"] = "svg"
        payload["is_public"] = False
        payload["data_classification"] = "official_sensitive"

        response: Response = client.post(
            path="/api/charts/v2/",
            data=payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

        svg_bytes = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        svg_text = svg_bytes.decode("utf-8", errors="ignore")

        assert DEFAULT_WATERMARK_LABEL in svg_text
        assert "official_sensitive" not in svg_text

    @pytest.mark.django_db
    def test_v2_svg_response_defaults_unknown_data_classification_to_default_label(
        self,
        core_timeseries_example: list[CoreTimeSeries],
        admin_user: User,
    ):
        """
        Given a v2 non-public SVG chart request with an unknown data classification
        When the endpoint renders the chart
        Then the watermark falls back to the default label
        """

        client = APIClient()
        client.force_authenticate(user=admin_user)

        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["file_format"] = "svg"
        payload["is_public"] = False
        payload["data_classification"] = "not-a-valid-classification"

        response: Response = client.post(
            path="/api/charts/v2/",
            data=payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

        svg_bytes = (
            b"".join(response.streaming_content)
            if hasattr(response, "streaming_content")
            else response.content
        )
        svg_text = svg_bytes.decode("utf-8", errors="ignore")

        assert DataClassificationInterface.DEFAULT in svg_text
        assert "not-a-valid-classification" not in svg_text

    @pytest.mark.django_db
    def test_v3_encoded_response_contains_default_watermark_label_for_non_public_chart(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a v3 non-public chart request without an explicit classification
        When the endpoint returns the encoded chart response
        Then both the encoded SVG and interactive figure contain the display label watermark
        """

        client = APIClient()
        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["file_format"] = "svg"
        payload["is_public"] = False

        response: Response = client.post(
            path="/api/charts/v3/",
            data=payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

        decoded_chart = unquote_plus(response.data["chart"])
        annotations = response.data["figure"]["layout"].get("annotations", [])
        annotation_texts = [annotation.get("text") for annotation in annotations]

        assert DEFAULT_WATERMARK_LABEL in decoded_chart
        assert DEFAULT_WATERMARK_LABEL in annotation_texts

    @pytest.mark.django_db
    def test_v3_encoded_response_formats_explicit_official_sensitive_value_as_label(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a v3 non-public chart request with the enum-style value `official_sensitive`
        When the endpoint returns the encoded chart response
        Then the watermark is rendered as the display label rather than the raw value
        """

        client = APIClient()
        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["file_format"] = "svg"
        payload["is_public"] = False
        payload["data_classification"] = "official_sensitive"

        response: Response = client.post(
            path="/api/charts/v3/",
            data=payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

        decoded_chart = unquote_plus(response.data["chart"])
        annotations = response.data["figure"]["layout"].get("annotations", [])
        annotation_texts = [annotation.get("text") for annotation in annotations]

        assert DEFAULT_WATERMARK_LABEL in decoded_chart
        assert DEFAULT_WATERMARK_LABEL in annotation_texts
        assert "official_sensitive" not in decoded_chart

    @pytest.mark.django_db
    def test_v3_encoded_response_defaults_unknown_data_classification_to_default_label(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a v3 non-public chart request with an unknown data classification
        When the endpoint returns the encoded chart response
        Then the watermark falls back to the default label
        """

        client = APIClient()
        payload = self._build_valid_payload_for_existing_timeseries(
            core_timeseries=core_timeseries_example[0]
        )
        payload["file_format"] = "svg"
        payload["is_public"] = False
        payload["data_classification"] = "not-a-valid-classification"

        response: Response = client.post(
            path="/api/charts/v3/",
            data=payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

        decoded_chart = unquote_plus(response.data["chart"])
        annotations = response.data["figure"]["layout"].get("annotations", [])
        annotation_texts = [annotation.get("text") for annotation in annotations]

        assert DataClassificationInterface.DEFAULT in decoded_chart
        assert DataClassificationInterface.DEFAULT in annotation_texts
        assert "not-a-valid-classification" not in decoded_chart
