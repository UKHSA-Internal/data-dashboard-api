import datetime
from collections import OrderedDict
from http import HTTPStatus
from typing import List, Tuple

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from metrics.data.models.api_models import APITimeSeries


class TestPublicAPINestedLinkViews:
    @property
    def path(self) -> str:
        return "/api/public/timeseries/"

    @property
    def test_server_base_name(self) -> str:
        return "http://testserver"

    @property
    def api_base_path(self) -> str:
        return f"{self.test_server_base_name}{self.path}"

    @staticmethod
    def _setup_api_time_series(
        **kwargs,
    ) -> APITimeSeries:
        day = kwargs.pop("day", 1)
        return APITimeSeries.objects.create(
            metric_value=123,
            epiweek=1,
            year=2023,
            dt=datetime.date(year=2023, month=1, day=day),
            **kwargs,
        )

    @staticmethod
    def _build_expected_response_fields(
        theme_name: str,
        sub_theme_name: str,
        topic_name: str,
        geography_type_name: str,
        geography_name: str,
        metric_name: str,
    ) -> List[Tuple[str, str, str, str]]:
        return [
            (
                "name",
                "link",
                theme_name,
                f"themes/{theme_name}",
            ),
            (
                "information",
                "sub_themes",
                "",
                f"themes/{theme_name}/sub_themes/",
            ),
            (
                "name",
                "link",
                sub_theme_name,
                f"themes/{theme_name}/sub_themes/{sub_theme_name}",
            ),
            (
                "information",
                "topics",
                "",
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics",
            ),
            (
                "name",
                "link",
                topic_name,
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}",
            ),
            (
                "information",
                "geography_types",
                "",
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types",
            ),
            (
                "name",
                "link",
                geography_type_name,
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types/{geography_type_name}",
            ),
            (
                "information",
                "geographies",
                "",
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types/{geography_type_name}/geographies",
            ),
            (
                "name",
                "link",
                geography_name,
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types/{geography_type_name}/geographies/{geography_name}",
            ),
            (
                "information",
                "metrics",
                "",
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types/{geography_type_name}/geographies/{geography_name}/metrics",
            ),
            (
                "name",
                "link",
                metric_name,
                f"themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types/{geography_type_name}/geographies/{geography_name}/metrics/{metric_name}",
            ),
        ]

    @pytest.mark.django_db
    def test_returns_correct_links_to_subsequent_views(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a valid request and a number of matching `APITimeSeries` records
        When the `GET /api/public/timeseries/` API is used
        Then the response contains links which will direct the caller to the subsequent views
        """
        # Given
        theme_name = "infectious_disease"
        sub_theme_name = "respiratory"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"
        metric_name = "new_cases_daily"

        self._setup_api_time_series(
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            geography_type=geography_type_name,
            geography=geography_name,
            metric=metric_name,
        )

        # When
        expected_response_fields: List[
            Tuple[str, str, str, str]
        ] = self._build_expected_response_fields(
            theme_name=theme_name,
            sub_theme_name=sub_theme_name,
            topic_name=topic_name,
            geography_type_name=geography_type_name,
            geography_name=geography_name,
            metric_name=metric_name,
        )

        path = f"{self.path}themes/"
        for (
            metadata_field,
            link_field,
            expected_metadata_field_value,
            expected_link_field_value,
        ) in expected_response_fields:
            response: Response = authenticated_api_client.get(path=path, format="json")
            assert response.status_code == HTTPStatus.OK
            response_data: OrderedDict = response.data

            # Then
            # Check that the metadata field matches up to expected value
            # For example, the `name` of 1 of the items in the `themes` list view
            # should be equal to the `theme_name` which in this case is `infectious_disease`.
            metadata_field_from_response: str = response_data[0][metadata_field]
            assert metadata_field_from_response == expected_metadata_field_value

            # Check that the link field matches up to expected value
            link_field_from_response: str = response_data[0][link_field]
            assert (
                link_field_from_response
                == f"{self.api_base_path}{expected_link_field_value}"
            )

            # Point the next request to the link field provided by the previous response
            path = link_field_from_response

    @pytest.mark.django_db
    def test_returns_correct_data_at_final_view(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a set of `APITimeSeries` records
        And a list of parameters to filter for a subset of those records
        When the final public API endpoint is hit
        Then the response contains the correct filtered `APITimeSeries` records
        And the response is paginated as expected
        """
        # Given
        theme_name = "infectious_disease"
        sub_theme_name = "respiratory"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"
        metric_name = "new_cases_daily"

        other_topic_name = "Influenza"
        other_metric_name = "weekly_positivity"

        expected_matching_time_series_count: int = 7

        # Records to be filtered for
        for i in range(expected_matching_time_series_count):
            self._setup_api_time_series(
                theme=theme_name,
                sub_theme=sub_theme_name,
                topic=topic_name,
                geography_type=geography_type_name,
                geography=geography_name,
                metric=metric_name,
                day=i + 1,
            )

        # Records to be filtered out
        for i in range(10):
            self._setup_api_time_series(
                theme=theme_name,
                sub_theme=sub_theme_name,
                topic=other_topic_name,
                geography_type=geography_type_name,
                geography=geography_name,
                metric=other_metric_name,
                day=i + 1,
            )

        # When
        path = f"{self.path}themes/{theme_name}/sub_themes/{sub_theme_name}/topics/{topic_name}/geography_types/{geography_type_name}/geographies/{geography_name}/metrics/{metric_name}"
        response: Response = authenticated_api_client.get(path=path, format="json")

        # Then
        # Check that the filtering has been applied correctly
        # And that only the requested time series records are returned
        response_data: OrderedDict = response.data
        assert response_data["count"] == expected_matching_time_series_count

        # Check that API returns a link to the next page of the paginated data
        assert response_data["next"] == f"{self.test_server_base_name}{path}?page=2"
        assert response_data["previous"] is None

        # Check that by default, the page size is returned as 5
        assert len(response_data["results"]) == 5

        # Check that the results match the expected records
        # which were to be filtered for
        for result in response_data["results"]:
            assert result["theme"] == theme_name
            assert result["sub_theme"] == sub_theme_name
            assert result["geography_type"] == geography_type_name
            assert result["geography"] == geography_name
            assert result["topic"] == topic_name != other_topic_name
            assert result["metric"] == metric_name != other_metric_name
