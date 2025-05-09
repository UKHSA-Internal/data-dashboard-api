import datetime
import os
from http import HTTPStatus

import pytest
from requests.models import Response
from rest_framework.test import RequestsClient

from metrics.data.models.api_models import APITimeSeries


class TestPublicAPINestedLinkViewsV2:
    @property
    def path(self) -> str:
        return "/api/public/timeseries/v2/"

    @property
    def target_domain(self) -> str:
        return os.environ.get("PUBLIC_API_TEST_DOMAIN", "http://testserver")

    @property
    def api_base_path(self) -> str:
        return f"{self.target_domain}{self.path}"

    @staticmethod
    def _setup_api_time_series(
        **kwargs,
    ) -> APITimeSeries:
        day = kwargs.pop("day", 1)
        return APITimeSeries.objects.create(
            metric_value=123,
            epiweek=1,
            year=2023,
            date=datetime.date(year=2023, month=1, day=day),
            is_public=True,
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
    ) -> list[tuple[str, str, str, str]]:
        return [
            (
                "name",
                "link",
                theme_name,
                f"themes/{theme_name}",
            ),
            (
                "",
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
                "",
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
                "",
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
                "",
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
                "",
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
    def test_returns_correct_links_to_subsequent_views(self):
        """
        Given a valid request and a number of matching `APITimeSeries` records
        When the `GET /api/public/timeseries/` API is used
        Then the response contains links which will direct the caller to the subsequent views
        """
        # Given
        client = RequestsClient()

        theme_name = "infectious_disease"
        sub_theme_name = "respiratory"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"
        metric_name = "COVID-19_deaths_ONSByDay"

        self._setup_api_time_series(
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            geography_type=geography_type_name,
            geography=geography_name,
            metric=metric_name,
        )

        # When
        expected_response_fields: list[tuple[str, str, str, str]] = (
            self._build_expected_response_fields(
                theme_name=theme_name,
                sub_theme_name=sub_theme_name,
                topic_name=topic_name,
                geography_type_name=geography_type_name,
                geography_name=geography_name,
                metric_name=metric_name,
            )
        )

        path = f"{self.path}themes/"
        target_url = f"{self.target_domain}{path}"

        for (
            metadata_field,
            link_field,
            expected_metadata_field_value,
            expected_link_field_value,
        ) in expected_response_fields:
            response: Response = client.get(target_url)
            assert response.status_code == HTTPStatus.OK
            response_data: list[dict] = response.json()

            # Then
            # Check that the metadata field matches up to expected value
            # For example, the `name` of 1 of the items in the `themes` list view
            # should be equal to the `theme_name` which in this case is `infectious_disease`.
            # The `information` field has been temporarily removed hence the if statement check is in place below.
            if metadata_field:
                metadata_field_from_response: str = response_data[0][metadata_field]
                assert metadata_field_from_response == expected_metadata_field_value

            # Check that the link field matches up to expected value
            link_field_from_response: str = response_data[0][link_field]
            assert (
                link_field_from_response
                == f"{self.api_base_path}{expected_link_field_value}"
            )

            # Point the next request to the link field provided by the previous response
            target_url = link_field_from_response

    @pytest.mark.django_db
    def test_returns_correct_data_at_final_view(self):
        """
        Given a set of `APITimeSeries` records
        And a list of parameters to filter for a subset of those records
        When the final public API endpoint is hit
        Then the response contains the correct filtered `APITimeSeries` records
        And the response is paginated as expected
        """
        # Given
        client = RequestsClient()

        theme_name = "infectious_disease"
        sub_theme_name = "respiratory"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"
        geography_code = "E92000001"
        metric_name = "COVID-19_deaths_ONSByDay"
        metric_group = "deaths"
        sex = "ALL"
        age = "ALL"
        in_reporting_delay_period = False

        other_topic_name = "Influenza"
        other_metric_name = "Influenza_testing_7daypositivity"

        expected_matching_time_series_count: int = 7

        # Records to be filtered for
        for i in range(expected_matching_time_series_count):
            self._setup_api_time_series(
                theme=theme_name,
                sub_theme=sub_theme_name,
                topic=topic_name,
                geography_type=geography_type_name,
                geography=geography_name,
                geography_code=geography_code,
                metric_group=metric_group,
                metric=metric_name,
                sex=sex,
                age=age,
                day=i + 1,
                in_reporting_delay_period=in_reporting_delay_period,
            )

        # Records to be filtered out
        for i in range(10):
            self._setup_api_time_series(
                theme=theme_name,
                sub_theme=sub_theme_name,
                topic=other_topic_name,
                geography_type=geography_type_name,
                geography=geography_name,
                geography_code=geography_code,
                metric_group=metric_group,
                metric=other_metric_name,
                sex=sex,
                age=age,
                day=i + 1,
            )

        # When
        target_url = (
            f"{self.target_domain}"
            f"{self.path}themes/"
            f"{theme_name}/sub_themes/"
            f"{sub_theme_name}/topics/"
            f"{topic_name}/geography_types/"
            f"{geography_type_name}/geographies/"
            f"{geography_name}/metrics/"
            f"{metric_name}"
        )
        response: Response = client.get(target_url)

        # Then
        # Check that the filtering has been applied correctly
        # And that only the requested time series records are returned
        response_data: list[dict] = response.json()
        assert response_data["count"] == expected_matching_time_series_count

        # Check that API returns a link to the next page of the paginated data
        assert response_data["next"] == f"{target_url}?page=2"
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
            assert result["geography_code"] == geography_code
            assert result["topic"] == topic_name != other_topic_name
            assert result["metric"] == metric_name != other_metric_name
            assert result["metric_group"] == metric_group
            assert result["sex"] == sex
            assert result["age"] == age
            assert result["in_reporting_delay_period"] == in_reporting_delay_period

    @pytest.mark.django_db
    def test_returns_correct_data_at_final_view_with_query_parameters(self):
        """
        Given a set of `APITimeSeries` records
        And a list of parameters to filter for a subset of those records
        And a number of query parameters
        When the final public API endpoint is hit
        Then the response contains the correct filtered `APITimeSeries` records
        """
        # Given
        client = RequestsClient()

        theme_name = "infectious_disease"
        sub_theme_name = "respiratory"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"
        metric_name = "COVID-19_deaths_ONSByDay"
        age = "15_44"
        sex = "F"

        other_age = "90+"
        other_sex = "M"

        expected_matching_time_series_count: int = 2

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
                age=age,
                sex=sex,
            )

        # Records to be filtered out
        for i in range(10):
            self._setup_api_time_series(
                theme=theme_name,
                sub_theme=sub_theme_name,
                topic=topic_name,
                geography_type=geography_type_name,
                geography=geography_name,
                metric=metric_name,
                age=other_age,
                sex=other_sex,
                day=i + 1,
            )

        # When
        target_url = (
            f"{self.target_domain}"
            f"{self.path}"
            f"themes/{theme_name}/"
            f"sub_themes/{sub_theme_name}/"
            f"topics/{topic_name}/"
            f"geography_types/{geography_type_name}/"
            f"geographies/{geography_name}/"
            f"metrics/{metric_name}"
        )
        response: Response = client.get(target_url, params={"sex": sex, "age": age})

        # Then
        # Check that the filtering has been applied correctly
        # And that only the requested time series records are returned
        response_data: list[dict] = response.json()
        assert response_data["count"] == expected_matching_time_series_count

        # Check that API returns no paginated links
        # as we expect a small enough set of data to fit within the 1-page response
        assert response_data["next"] is None
        assert response_data["previous"] is None

        # Check that the results contain the records within the 1-page response
        assert len(response_data["results"]) == expected_matching_time_series_count

        # Check that the results match the expected records
        # which were to be filtered for
        for result in response_data["results"]:
            assert result["theme"] == theme_name
            assert result["sub_theme"] == sub_theme_name
            assert result["geography_type"] == geography_type_name
            assert result["geography"] == geography_name
            assert result["topic"] == topic_name
            assert result["metric"] == metric_name
            assert result["sex"] == sex != other_sex
            assert result["age"] == age != other_age

    @pytest.mark.django_db
    def test_root_view(self):
        """
        Given no existing `APITimeSeries` records
        When a `GET` request is made to the root of the API
        Then the correct response is returned
        """
        # Given
        client = RequestsClient()
        target_url = self.api_base_path

        # When
        response: Response = client.get(target_url)

        # Then
        assert response.status_code == 200
        expected_response = {"links": {"themes": f"{self.api_base_path}themes/"}}
        assert response.json() == expected_response
