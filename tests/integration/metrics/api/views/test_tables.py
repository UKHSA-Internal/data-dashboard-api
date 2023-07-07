from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries


class TestTablesView:
    @property
    def path(self) -> str:
        return "/tables/v2/"

    @pytest.mark.parametrize("path", ["/tables/v2", "/api/tables/v2"])
    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /tables/v2` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        path_without_trailing_forward_slash: str = path
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name

        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                    "chart_height": 220,
                    "chart_width": 435,
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=path_without_trailing_forward_slash,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.parametrize("path", ["/tables/v2/", "/api/tables/v2/"])
    @pytest.mark.django_db
    def test_returns_correct_response_type(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /tables/v2/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                    "chart_height": 220,
                    "chart_width": 435,
                }
            ],
        }

        # When
        response: Response = authenticated_api_client.post(
            path=path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate a json-type reponse is being returned
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.parametrize("path", ["/tables/v2/", "/api/tables/v2/"])
    @pytest.mark.django_db
    def test_post_request_without_api_key_is_unauthorized(self, path: str):
        """
        Given an APIClient which is not authenticated
        When the `GET /tables/v2/` endpoint is hit
        Then an HTTP 401 UNAUTHORIZED response is returned
        """
        # Given
        client = APIClient()

        # When
        response: Response = client.post(path=path, data={})

        # Then
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    @pytest.mark.parametrize("path", ["/tables/v2/", "/api/tables/v2/"])
    @pytest.mark.django_db
    def test_single_plot_output_is_as_expected(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /tables/v2/` endpoint is hit with a single plot
        Then the response is of the correct format
        """
        # Given
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                    "chart_height": 220,
                    "chart_width": 435,
                }
            ],
        }

        expected_response = [
            {
                "date": "2023-01-31",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "123.0",
                    },
                ],
            }
        ]

        # When
        response: Response = authenticated_api_client.post(
            path=path, data=valid_payload, format="json"
        )

        # Then
        assert response.data == expected_response

    @pytest.mark.parametrize("path", ["/tables/v2/", "/api/tables/v2/"])
    @pytest.mark.django_db
    def test_multiple_plot_output_is_as_expected(
        self,
        path: str,
        authenticated_api_client: APIClient,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        And an authenticated APIClient
        When the `POST /tables/v2/` endpoint is hit with multiple plots
        Then the response is of the correct format
        """
        # Given
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                },
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "waffle",
                    "label": "plot_label",
                },
            ],
        }

        expected_response = [
            {
                "date": "2023-01-31",
                "values": [
                    {"label": "Plot1", "value": "123.0"},
                    {"label": "plot_label", "value": "123.0"},
                ],
            }
        ]

        # When
        response: Response = authenticated_api_client.post(
            path=path, data=valid_payload, format="json"
        )

        # Then
        assert response.data == expected_response
