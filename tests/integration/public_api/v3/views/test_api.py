import datetime
import os
from http import HTTPStatus

import pytest
from requests.models import Response
from rest_framework.test import RequestsClient

from metrics.data.models.api_models import APIHeadline, APITimeSeries
from tests.factories.metrics.api_models.headline import APIHeadlineFactory
from tests.factories.metrics.api_models.time_series import APITimeSeriesFactory


class TestPublicAPIV3:
    @property
    def path(self) -> str:
        return "/api/public/v3"

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
        return APITimeSeriesFactory.create_record(
            metric_value=123,
            epiweek=1,
            year=2023,
            date=datetime.date(year=2023, month=1, day=day),
            is_public=True,
            **kwargs,
        )

    @staticmethod
    def _setup_api_headline(
        **kwargs,
    ) -> APIHeadline:
        day = kwargs.pop("day", 1)
        return APIHeadlineFactory.create_record(
            period_start=datetime.date(year=2023, month=1, day=day),
            period_end=datetime.date(year=2023, month=1, day=day),
            **kwargs,
        )

    @staticmethod
    def _build_expected_response_fields(
        type: str,
        theme: str,
        sub_theme: str,
        topic: str,
        geography_type: str,
        geography: str,
        metric: str,
    ) -> list[tuple[str, str, str, str]]:
        return [
            (
                "name",
                "link",
                theme,
                f"{type}/themes/{theme}",
            ),
            (
                "",
                "sub_themes",
                "",
                f"{type}/themes/{theme}/sub_themes/",
            ),
            (
                "name",
                "link",
                sub_theme,
                f"{type}/themes/{theme}/sub_themes/{sub_theme}",
            ),
            (
                "",
                "topics",
                "",
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics",
            ),
            (
                "name",
                "link",
                topic,
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}",
            ),
            (
                "",
                "geography_types",
                "",
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types",
            ),
            (
                "name",
                "link",
                geography_type,
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types/{geography_type}",
            ),
            (
                "",
                "geographies",
                "",
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types/{geography_type}/geographies",
            ),
            (
                "name",
                "link",
                geography,
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types/{geography_type}/geographies/{geography}",
            ),
            (
                "",
                "metrics",
                "",
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types/{geography_type}/geographies/{geography}/metrics",
            ),
            (
                "name",
                "link",
                metric,
                f"{type}/themes/{theme}/sub_themes/{sub_theme}/topics/{topic}/geography_types/{geography_type}/geographies/{geography}/metrics/{metric}",
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

        theme = "infectious_disease"
        sub_theme = "respiratory"
        topic = "COVID-19"
        geography_type = "Nation"
        geography = "England"
        metric = "COVID-19_deaths_ONSByDay"

        self._setup_api_time_series(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            geography_type=geography_type,
            geography=geography,
            metric=metric,
        )

        self._setup_api_headline(
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
            geography_type=geography_type,
            geography=geography,
            metric=metric,
        )

        # When

        for type in ["timeseries", "headline"]:
            expected_response_fields: list[tuple[str, str, str, str]] = (
                self._build_expected_response_fields(
                    type=type,
                    theme=theme,
                    sub_theme=sub_theme,
                    topic=topic,
                    geography_type=geography_type,
                    geography=geography,
                    metric=metric,
                )
            )
            path = f"{self.path}/{type}"
            # This gets reset at the bottom of the loop to get the next item
            target_url = f"{self.target_domain}{path}/themes/"
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
                # should be equal to the `theme` which in this case is `infectious_disease`.
                # The `information` field has been temporarily removed hence the if statement check is in place below.
                if metadata_field:
                    metadata_field_from_response: str = response_data[0][metadata_field]
                    assert metadata_field_from_response == expected_metadata_field_value
                # Check that the link field matches up to expected value
                link_field_from_response: str = response_data[0][link_field]
                assert (
                    link_field_from_response
                    == f"{self.api_base_path}/{expected_link_field_value}"
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

        theme = "infectious_disease"
        sub_theme = "respiratory"
        topic = "COVID-19"
        geography_type = "Nation"
        geography = "England"
        geography_code = "E92000001"
        metric = "COVID-19_deaths_ONSByDay"
        metric_group = "deaths"
        sex = "ALL"
        age = "ALL"
        in_reporting_delay_period = False

        other_topic = "Influenza"
        other_metric = "Influenza_testing_7daypositivity"

        expected_matching_count: int = 7

        # Records to be filtered for
        for i in range(expected_matching_count):
            self._setup_api_time_series(
                theme=theme,
                sub_theme=sub_theme,
                topic=topic,
                geography_type=geography_type,
                geography=geography,
                geography_code=geography_code,
                metric_group=metric_group,
                metric=metric,
                sex=sex,
                age=age,
                day=i + 1,
                in_reporting_delay_period=in_reporting_delay_period,
            )

            self._setup_api_headline(
                theme=theme,
                sub_theme=sub_theme,
                topic=topic,
                geography_type=geography_type,
                geography=geography,
                geography_code=geography_code,
                metric_group=metric_group,
                metric=metric,
                sex=sex,
                age=age,
                day=i + 1,
            )

        # Records to be filtered out
        for i in range(7, 17):
            self._setup_api_time_series(
                theme=theme,
                sub_theme=sub_theme,
                topic=other_topic,
                geography_type=geography_type,
                geography=geography,
                geography_code=geography_code,
                metric_group=metric_group,
                metric=other_metric,
                sex=sex,
                age=age,
                day=i + 1,
            )

            self._setup_api_headline(
                theme=theme,
                sub_theme=sub_theme,
                topic=other_topic,
                geography_type=geography_type,
                geography=geography,
                geography_code=geography_code,
                metric_group=metric_group,
                metric=other_metric,
                sex=sex,
                age=age,
                day=i + 1,
            )

        for data_type in ["timeseries", "headline"]:
            # When
            target_url = (
                f"{self.target_domain}"
                f"{self.path}/{data_type}/themes/"
                f"{theme}/sub_themes/"
                f"{sub_theme}/topics/"
                f"{topic}/geography_types/"
                f"{geography_type}/geographies/"
                f"{geography}/metrics/"
                f"{metric}"
            )
            response: Response = client.get(target_url)

            # Then
            # Check that the filtering has been applied correctly
            # And that only the requested records are returned
            response_data: list[dict] = response.json()
            assert response_data["count"] == expected_matching_count

            # Check that API returns a link to the next page of the paginated data
            assert response_data["next"] == f"{target_url}?page=2"
            assert response_data["previous"] is None

            # Check that by default, the page size is returned as 5
            assert len(response_data["results"]) == 5

            # Check that the results match the expected records
            # which were to be filtered for
            for result in response_data["results"]:
                assert result["theme"] == theme
                assert result["sub_theme"] == sub_theme
                assert result["geography_type"] == geography_type
                assert result["geography"] == geography
                assert result["geography_code"] == geography_code
                assert result["topic"] == topic != other_topic
                assert result["metric"] == metric != other_metric
                assert result["metric_group"] == metric_group
                assert result["sex"] == sex
                assert result["age"] == age

    # @pytest.mark.django_db
    # def test_returns_correct_data_at_final_view_with_query_parameters(self):
    #     """
    #     Given a set of `APITimeSeries` records
    #     And a list of parameters to filter for a subset of those records
    #     And a number of query parameters
    #     When the final public API endpoint is hit
    #     Then the response contains the correct filtered `APITimeSeries` records
    #     """
    #     # Given
    #     client = RequestsClient()

    #     theme = "infectious_disease"
    #     sub_theme = "respiratory"
    #     topic = "COVID-19"
    #     geography_type = "Nation"
    #     geography = "England"
    #     metric = "COVID-19_deaths_ONSByDay"
    #     age = "15_44"
    #     sex = "F"

    #     other_age = "90+"
    #     other_sex = "M"

    #     expected_matching_time_series_count: int = 2

    #     # Records to be filtered for
    #     for i in range(expected_matching_time_series_count):
    #         self._setup_api_time_series(
    #             theme=theme,
    #             sub_theme=sub_theme,
    #             topic=topic,
    #             geography_type=geography_type,
    #             geography=geography,
    #             metric=metric,
    #             day=i + 1,
    #             age=age,
    #             sex=sex,
    #         )

    #     # Records to be filtered out
    #     for i in range(10):
    #         self._setup_api_time_series(
    #             theme=theme,
    #             sub_theme=sub_theme,
    #             topic=topic,
    #             geography_type=geography_type,
    #             geography=geography,
    #             metric=metric,
    #             age=other_age,
    #             sex=other_sex,
    #             day=i + 1,
    #         )

    #     # When
    #     target_url = (
    #         f"{self.target_domain}"
    #         f"{self.path}"
    #         f"{type}/themes/{theme}/"
    #         f"sub_themes/{sub_theme}/"
    #         f"topics/{topic}/"
    #         f"geography_types/{geography_type}/"
    #         f"geographies/{geography}/"
    #         f"metrics/{metric}"
    #     )
    #     response: Response = client.get(target_url, params={"sex": sex, "age": age})

    #     # Then
    #     # Check that the filtering has been applied correctly
    #     # And that only the requested time series records are returned
    #     response_data: list[dict] = response.json()
    #     assert response_data["count"] == expected_matching_time_series_count

    #     # Check that API returns no paginated links
    #     # as we expect a small enough set of data to fit within the 1-page response
    #     assert response_data["next"] is None
    #     assert response_data["previous"] is None

    #     # Check that the results contain the records within the 1-page response
    #     assert len(response_data["results"]) == expected_matching_time_series_count

    #     # Check that the results match the expected records
    #     # which were to be filtered for
    #     for result in response_data["results"]:
    #         assert result["theme"] == theme
    #         assert result["sub_theme"] == sub_theme
    #         assert result["geography_type"] == geography_type
    #         assert result["geography"] == geography
    #         assert result["topic"] == topic
    #         assert result["metric"] == metric
    #         assert result["sex"] == sex != other_sex
    #         assert result["age"] == age != other_age

    @pytest.mark.django_db
    def test_root_view(self):
        """
        Given no existing `APITimeSeries` records
        When a `GET` request is made to the root of the API
        Then the correct response is returned
        """
        # Given
        client = RequestsClient()
        target_url = self.api_base_path + "/"

        # When
        response: Response = client.get(target_url)

        # Then
        assert response.status_code == 200
        expected_response = {
            "links": {
                "headline/themes": f"{self.api_base_path}/headline/themes/",
                "timeseries/themes": f"{self.api_base_path}/timeseries/themes/",
            }
        }
        assert response.json() == expected_response
