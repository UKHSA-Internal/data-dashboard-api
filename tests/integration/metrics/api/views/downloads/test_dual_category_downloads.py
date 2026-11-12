import datetime
from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.core_models import CoreHeadline
from tests.factories.metrics.headline import CoreHeadlineFactory


@pytest.mark.django_db
class TestDualCategoryView:
    @property
    def path(self) -> str:
        return "/api/downloads/dual-category/v1/"

    def test_headline_x_dominant_and_y_dominant_produce_same_result(
        self,
        core_headline_example: CoreHeadline,
        user_global_access,
    ):
        """
        Given two valid dual-category timeseries payload for x and y charts
        The download output should be equal to each other.
        Enough tests cover x dominant dual category chart, this ensures y dominant charts don't differ

        Y dominant payload flips the x/yaxis. X becomes the metric
        Butterfly only supports Headline for now
        """

        # Given
        client = APIClient()
        if not core_headline_example.is_public:
            client.force_authenticate(user=user_global_access, token="token")

        CoreHeadlineFactory.create_record(
            metric_value=123.0000,
            metric=core_headline_example.metric.name,
            theme=core_headline_example.metric.metric_group.topic.sub_theme.theme.name,
            sub_theme=core_headline_example.metric.metric_group.topic.sub_theme.name,
            topic=core_headline_example.metric.metric_group.topic.name,
            geography="England",
            geography_type="Nation",
            geography_code="E92000001",
            age="default",
            stratum="default",
            sex="m",
            refresh_date=core_headline_example.refresh_date,
            period_start=core_headline_example.period_start,
            period_end=core_headline_example.period_end,
        )

        x_payload = {
            "file_format": "csv",
            "x_axis": "age",
            "y_axis": "metric",
            "primary_field_values": [
                "default",
            ],
            "chart_type": "stacked_bar",
            "static_fields": {
                "date_from": "2000-01-01",
                "date_to": datetime.date.today(),
                "metric": core_headline_example.metric.name,
                "topic": core_headline_example.metric.metric_group.topic.name,
                "sub_theme": core_headline_example.metric.metric_group.topic.sub_theme.name,
                "theme": core_headline_example.metric.metric_group.topic.sub_theme.theme.name,
                "geography": core_headline_example.geography.name,
                "geography_type": core_headline_example.geography.geography_type.name,
            },
            "secondary_category": "sex",
            "segments": [
                {
                    "secondary_field_value": "f",
                    "label": "0 to 4 years female",
                },
                {
                    "secondary_field_value": "m",
                    "label": "0 to 4 years male",
                },
            ],
        }

        y_payload = {
            "file_format": "csv",
            "x_axis": "metric",
            "y_axis": "age",
            "primary_field_values": [
                "default",
            ],
            "chart_type": "butterfly",
            "static_fields": {
                "date_from": "2000-01-01",
                "date_to": datetime.date.today(),
                "metric": core_headline_example.metric.name,
                "topic": core_headline_example.metric.metric_group.topic.name,
                "sub_theme": core_headline_example.metric.metric_group.topic.sub_theme.name,
                "theme": core_headline_example.metric.metric_group.topic.sub_theme.theme.name,
                "geography": core_headline_example.geography.name,
                "geography_type": core_headline_example.geography.geography_type.name,
            },
            "secondary_category": "sex",
            "segments": [
                {
                    "secondary_field_value": "f",
                    "label": "0 to 4 years female",
                },
                {
                    "secondary_field_value": "m",
                    "label": "0 to 4 years male",
                },
            ],
        }

        # When
        x_response: Response = client.post(
            path=self.path, data=x_payload, format="json"
        )

        y_response: Response = client.post(
            path=self.path, data=y_payload, format="json"
        )

        assert x_response.status_code == HTTPStatus.OK
        assert y_response.status_code == HTTPStatus.OK

        assert x_response.content == y_response.content
