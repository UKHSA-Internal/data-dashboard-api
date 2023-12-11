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
