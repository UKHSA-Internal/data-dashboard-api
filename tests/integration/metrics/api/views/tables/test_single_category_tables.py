import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreTimeSeries, CoreHeadline


class TestTablesView:
    @property
    def path(self) -> str:
        return "/api/tables/v4/"

    @pytest.mark.django_db
    def test_hitting_endpoint_without_appended_forward_slash_redirects_correctly(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/v4` endpoint is hit i.e. without the trailing `/`
        Then the response is still a valid HTTP 200 OK
        """
        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name

        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "bar",
                    "chart_height": 220,
                    "chart_width": 435,
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }
        path = "/api/tables/v4"

        # When
        response: Response = client.post(
            path=path,
            data=valid_payload,
            format="json",
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.django_db
    def test_returns_correct_response_type(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/v4/` endpoint is hit
        Then the response is not an HTTP 401 UNAUTHORIZED
        """
        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "bar",
                    "chart_height": 220,
                    "chart_width": 435,
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        assert response.status_code != HTTPStatus.UNAUTHORIZED
        assert response.status_code == HTTPStatus.OK

        # Check that the headers on the response indicate a json-type reponse is being returned
        assert response.headers["Content-Type"] == "application/json"

    @pytest.mark.django_db
    def test_single_plot_output_is_as_expected(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/v4/` endpoint is hit with a single plot
        Then the response is of the correct format
        """
        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "bar",
                    "chart_height": 220,
                    "chart_width": 435,
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                }
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        expected_response = [
            {
                "reference": "2023-01-02",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2023-01-01",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]
        # We expect the v4 endpoint to return data in descending order
        assert response.data == expected_response

    @pytest.mark.django_db
    def test_multiple_plot_output_is_as_expected(
        self,
        core_timeseries_example: list[CoreTimeSeries],
    ):
        """
        Given a valid payload to create a chart
        When the `POST /api/tables/v4/` endpoint is hit with multiple plots
        Then the response is of the correct format
        """
        # Given
        client = APIClient()
        core_timeseries: CoreTimeSeries = core_timeseries_example[0]
        topic_name: str = core_timeseries.metric.metric_group.topic.name
        metric_name: str = core_timeseries.metric.name
        core_timeseries_example[-1].in_reporting_delay_period = True
        core_timeseries_example[-1].save(update_fields=["in_reporting_delay_period"])
        valid_payload = {
            "file_format": "svg",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "bar",
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                },
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "bar",
                    "label": "plot_label",
                    "date_from": "2000-01-01",
                    "date_to": datetime.date.today(),
                },
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        expected_response = [
            {
                "reference": "2023-01-02",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "123.0000",
                        "in_reporting_delay_period": True,
                    },
                    {
                        "label": "plot_label",
                        "value": "123.0000",
                        "in_reporting_delay_period": True,
                    },
                ],
            },
            {
                "reference": "2023-01-01",
                "values": [
                    {
                        "label": "Plot1",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "plot_label",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]
        # For the v4 tables endpoint, we expect data to be returned in descending order
        # i.e. the recent data points first going down to the latest data points last
        assert response.data == expected_response

    @pytest.mark.django_db
    def test_headline_charts_with_plot_label_uses_plot_label_for_reference(
        self,
        core_headline_example: list[CoreHeadline],
    ):
        """
        Given a valid payload to create a headline chart
        When the `POST /api/tables/v4/` endpoint is hit with
            a plot that includes a plot label
        Then the `reference` field in the response contains the plot label.
        """
        # Given
        client = APIClient()
        core_headline: CoreHeadline = core_headline_example
        topic_name: str = core_headline.metric.metric_group.topic.name
        metric_name: str = core_headline.metric.name
        valid_payload = {
            "file_format": "svg",
            "x_axis": "sex",
            "y_axis": "metric",
            "plots": [
                {
                    "topic": topic_name,
                    "metric": metric_name,
                    "chart_type": "bar",
                    "sex": "f",
                    "label": "female",
                }
            ],
        }

        # When
        response: Response = client.post(
            path=self.path, data=valid_payload, format="json"
        )

        # Then
        expected_response = [
            {
                "reference": "female",
                "values": [
                    {
                        "label": "Amount",
                        "value": "123.0000",
                        "in_reporting_delay_period": False,
                    }
                ],
            }
        ]

        assert response.data == expected_response

    @pytest.mark.django_db
    def test_returns_bad_request_response_when_queried_data_does_not_exist(
        self, core_timeseries_example: list[CoreTimeSeries]
    ):
        """
        Given a payload for which there is no corresponding data
        When the `POST /api/tables/v4/` endpoint is hit
        Then the response is an HTTP 400 BAD REQUEST
        """
        # Given
        client = APIClient()
        valid_payload = {
            "plots": [
                {
                    "topic": core_timeseries_example[0].metric.topic.name,
                    "metric": core_timeseries_example[0].metric.name,
                    "chart_type": "bar",
                    "age": "non-existent-age",
                }
            ],
        }

        # When
        response: Response = client.post(
            path=self.path,
            data=valid_payload,
            format="json",
        )

        # Then
        assert response.status_code == HTTPStatus.BAD_REQUEST
