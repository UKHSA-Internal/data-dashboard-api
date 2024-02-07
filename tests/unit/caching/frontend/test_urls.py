from unittest import mock

import pytest

from caching.frontend.urls import FrontEndURLBuilder

FAKE_BASE_URL = "https://fake-base-url.com"


class TestFrontEndURLBuilder:
    def test_build_url_for_topic_page(self):
        """
        Given a slug for a topic page
        When `build_url_for_topic_page()` is called from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        topic_page_slug = "influenza"
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)

        # When
        topic_page_url: str = frontend_url_builder.build_url_for_topic_page(
            slug=topic_page_slug
        )

        # Then
        assert topic_page_url == f"{base_url}/topics/{topic_page_slug}"

    def test_build_url_for_common_page(self):
        """
        Given a slug for a common page
        When `build_url_for_common_page()` is called from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        common_page_slug = "about"
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)

        # When
        common_page_url: str = frontend_url_builder.build_url_for_common_page(
            slug=common_page_slug
        )

        # Then
        assert common_page_url == f"{base_url}/{common_page_slug}"

    def test_build_url_for_home_page(self):
        """
        Given a base URL
        When `build_url_for_home_page()` is called from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)

        # When
        home_page_url: str = frontend_url_builder.build_url_for_home_page()

        # Then
        assert home_page_url == base_url

    def test_build_url_for_whats_new_parent_page(self):
        """
        Given a base URL
        When `build_url_for_whats_new_parent_page()` is called
            from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)

        # When
        whats_new_parent_page_url: str = (
            frontend_url_builder.build_url_for_whats_new_parent_page()
        )

        # Then
        assert whats_new_parent_page_url == f"{base_url}/whats-new"

    def test_build_url_for_whats_new_child_entry(self):
        """
        Given a slug for a what's new child entry
        When `build_url_for_whats_new_child_entry()` is called
            from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)
        whats_new_child_entry_slug = "issue-with-vaccination-data"

        # When
        whats_new_child_entry_url: str = (
            frontend_url_builder.build_url_for_whats_new_child_entry(
                slug=whats_new_child_entry_slug
            )
        )

        # Then
        assert (
            whats_new_child_entry_url
            == f"{base_url}/whats-new/{whats_new_child_entry_slug}"
        )

    def test_build_url_for_feedback_confirmation_page(self):
        """
        Given a base URL
        When `build_url_for_feedback_confirmation_page()` is called
            from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)

        # When
        feedback_confirmation_page_url: str = (
            frontend_url_builder.build_url_for_feedback_confirmation_page()
        )

        # Then
        assert feedback_confirmation_page_url == f"{base_url}/feedback/confirmation"

    def test_build_url_for_metrics_documentation_parent_page(self):
        """
        Given a base URL
        When `build_url_for_metrics_documentation_parent_page()` is called
            from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)

        # When
        metrics_documentation_parent_page_url: str = (
            frontend_url_builder.build_url_for_metrics_documentation_parent_page()
        )

        # Then
        assert (
            metrics_documentation_parent_page_url == f"{base_url}/metrics-documentation"
        )

    def test_build_url_for_metrics_documentation_child_entry(self):
        """
        Given a slug for a metrics documentation child entry
        When `build_url_for_metrics_documentation_child_entry()` is called
            from an instance of `FrontEndURLBuilder`
        Then the correct URL will be returned
        """
        # Given
        base_url = FAKE_BASE_URL
        frontend_url_builder = FrontEndURLBuilder(base_url=base_url)
        metrics_documentation_child_entry_slug = "covid-19_cases_raterollingmean"

        # When
        metrics_documentation_child_entry_url: str = (
            frontend_url_builder.build_url_for_metrics_documentation_child_entry(
                slug=metrics_documentation_child_entry_slug
            )
        )

        # Then
        assert (
            metrics_documentation_child_entry_url
            == f"{base_url}/metrics-documentation/{metrics_documentation_child_entry_slug}"
        )

    @pytest.mark.parametrize(
        "input_geography_type, input_geography_name, expected_geography_type, expected_geography_name",
        (
            ["Nation", "England", "Nation", "England"],
            [
                "Lower Tier Local Authority",
                "London",
                "Lower+Tier+Local+Authority",
                "London",
            ],
            [
                "Lower Tier Local Authority",
                "Cheshire West and Chester",
                "Lower+Tier+Local+Authority",
                "Cheshire+West+and+Chester",
            ],
            [
                "Lower Tier Local Authority",
                "Bristol, City of",
                "Lower+Tier+Local+Authority",
                "Bristol%2C+City+of",
            ],
            [
                "Lower Tier Local Authority",
                "St. Helens",
                "Lower+Tier+Local+Authority",
                "St.+Helens",
            ],
            [
                "Lower Tier Local Authority",
                "Stoke-on-Trent",
                "Lower+Tier+Local+Authority",
                "Stoke-on-Trent",
            ],
        ),
    )
    def test_build_query_params_for_area_selector_page(
        self,
        input_geography_type: str,
        input_geography_name: str,
        expected_geography_type: str,
        expected_geography_name: str,
    ):
        """
        Given the names of a geography and geography type
        When `build_query_params_for_area_selector_page()` is called
            from an instance of the `FrontEndURLBuilder`
        Then a dict is returned which represents the query parameters
        """
        # Given
        frontend_url_builder = FrontEndURLBuilder(base_url=mock.Mock())

        # When
        params: dict[str, str] = (
            frontend_url_builder.build_query_params_for_area_selector_page(
                geography_type_name=input_geography_type,
                geography_name=input_geography_name,
            )
        )

        # Then
        expected_params = {
            "areaType": expected_geography_type,
            "areaName": expected_geography_name,
        }
        assert params == expected_params
