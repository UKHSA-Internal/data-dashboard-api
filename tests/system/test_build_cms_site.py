import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from cms.common.models import CommonPage
from cms.composite.models import CompositePage
from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
from cms.feedback.models import FormPage
from cms.home.models import HomePage, UKHSARootPage
from cms.snippets.models import InternalButton
from cms.topic.models import TopicPage
from cms.whats_new.models import WhatsNewParentPage


class TestBuildCMSSite:
    @pytest.mark.django_db
    def test_command_builds_site_with_correct_slugs_and_titles(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        When a GET request is made to `/api/pages/` list endpoint
        Then the response contains the page items
            with the expected slugs and titles assigned to each page
        """
        # Given
        call_command("build_cms_site")
        api_client = APIClient()

        # When
        response = api_client.get(path="/api/pages/")

        # Then
        response_data = response.data
        items = response_data["items"]

        expected_slugs: set[str] = {
            "topics",
            "covid-19",
            "influenza",
            "location-based-data",
            "about",
            "whats-new",
            "whats-coming",
            "cookies",
        }
        created_slugs: set[str] = set(item["meta"]["slug"] for item in items)
        assert expected_slugs.issubset(created_slugs)

        expected_titles: set[str] = {
            "UKHSA data dashboard",
            "COVID-19",
            "Influenza",
            "Location based data",
            "About",
            "What's new",
            "What's coming",
            "Cookies",
        }
        created_titles: set[str] = {item["title"] for item in items}
        assert expected_titles.issubset(created_titles)

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_home_page(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `respiratory-viruses` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        home_page = HomePage.objects.get(slug="topics")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{home_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        home_page_response_template = open_example_page_response(
            page_name="ukhsa_data_dashboard"
        )
        assert response_data["title"] == home_page_response_template["title"]
        assert (
            response_data["page_description"]
            == home_page_response_template["page_description"]
        )
        assert (
            response_data["meta"]["seo_title"]
            == home_page_response_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == home_page_response_template["meta"]["search_description"]
        )

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        related_links_from_template = home_page_response_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "slug", ["covid-19", "influenza", "other-respiratory-viruses"]
    )
    def test_command_builds_site_with_correct_topic_pages(self, slug: str):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the topic page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        topic_page = TopicPage.objects.get(slug=slug)
        parent_home_page = HomePage.objects.get(title="UKHSA data dashboard")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{topic_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        page_name = slug.replace("-", "_")
        topic_page_response_template = open_example_page_response(page_name=page_name)
        assert response_data["title"] == topic_page_response_template["title"]
        assert (
            response_data["page_description"]
            == topic_page_response_template["page_description"]
        )
        assert (
            response_data["meta"]["seo_title"]
            == topic_page_response_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == topic_page_response_template["meta"]["search_description"]
        )
        assert response_data["meta"]["parent"]["id"] == parent_home_page.id
        assert response_data["meta"]["parent"]["title"] == parent_home_page.title

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        related_links_from_template = topic_page_response_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_about_page(self, monkeypatch):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `about` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        domain = "my-prefix.dev.ukhsa-data-dashboard.gov.uk"
        monkeypatch.setenv(name="FRONTEND_URL", value=domain)
        call_command("build_cms_site")

        about_page = CommonPage.objects.get(slug="about")
        parent_page = UKHSARootPage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{about_page.id}/")

        # Then
        response_data = response.data

        # Check the `html_url` has been constructed correctly
        assert response_data["meta"]["html_url"] == f"https://{domain}/about/"

        # Compare the response from the endpoint to the template used to build the page
        about_page_template = open_example_page_response(page_name="about")
        assert response_data["title"] == about_page_template["title"]
        assert response_data["body"] == about_page_template["body"]
        assert (
            response_data["meta"]["seo_title"]
            == about_page_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == about_page_template["meta"]["search_description"]
        )
        assert response_data["meta"]["parent"]["id"] == parent_page.id
        assert response_data["meta"]["parent"]["title"] == parent_page.title

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        related_links_from_template = about_page_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_whats_new_page(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `whats_new` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        whats_new_page = WhatsNewParentPage.objects.get(slug="whats-new")
        parent_home_page = UKHSARootPage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{whats_new_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        whats_new_page_template = open_example_page_response(page_name="whats_new")
        assert response_data["title"] == whats_new_page_template["title"]
        assert response_data["body"] == whats_new_page_template["body"]
        assert (
            response_data["meta"]["seo_title"]
            == whats_new_page_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == whats_new_page_template["meta"]["search_description"]
        )
        assert response_data["meta"]["parent"]["id"] == parent_home_page.id
        assert response_data["meta"]["parent"]["title"] == parent_home_page.title

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        related_links_from_template = whats_new_page_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_bulk_download_page(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `bulkdownloads` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        bulk_downloads = CompositePage.objects.get(slug="bulk-downloads")
        parent_page = UKHSARootPage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{bulk_downloads.id}/")
        response_button_snippet = response.data["body"][1]["value"]
        bulk_downloads_template = open_example_page_response(page_name="bulk_downloads")
        button_snippet = InternalButton.objects.get(text="download (zip)")

        # Then
        assert response.data["title"] == bulk_downloads_template["title"]
        assert (
            response.data["meta"]["seo_title"]
            == bulk_downloads_template["meta"]["seo_title"]
        )
        assert (
            response.data["meta"]["search_description"]
            == bulk_downloads_template["meta"]["search_description"]
        )
        assert response.data["meta"]["parent"]["id"] == parent_page.id
        assert response.data["meta"]["parent"]["title"] == parent_page.title

        assert response.data["body"][0] == bulk_downloads_template["body"][0]
        assert response_button_snippet["text"] == button_snippet.text
        assert response_button_snippet["endpoint"] == button_snippet.endpoint
        assert response_button_snippet["method"] == button_snippet.method
        assert response_button_snippet["button_type"] == button_snippet.button_type

    @pytest.mark.django_db
    def test_command_builds_access_our_data_parent_page(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `CompositePae` page for `Access our data parent.
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        access_our_data_parent_page = CompositePage.objects.get(slug="access-our-data")
        parent_page = UKHSARootPage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{access_our_data_parent_page.id}/")
        access_our_data_parent_page_template = open_example_page_response(
            page_name="access_our_data_parent_page"
        )

        # Then
        assert response.data["title"] == access_our_data_parent_page_template["title"]
        assert (
            response.data["meta"]["seo_title"]
            == access_our_data_parent_page_template["meta"]["seo_title"]
        )
        assert (
            response.data["meta"]["search_description"]
            == access_our_data_parent_page_template["meta"]["search_description"]
        )
        assert response.data["meta"]["parent"]["id"] == parent_page.id
        assert response.data["meta"]["parent"]["title"] == parent_page.title

        assert (
            response.data["body"][0] == access_our_data_parent_page_template["body"][0]
        )

    @pytest.mark.django_db
    def test_command_builds_access_our_data_getting_started(self, monkeypatch):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `CompositePae` page for `Access our data getting started page.
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        domain = "my-prefix.dev.ukhsa-data-dashboard.gov.uk"
        monkeypatch.setenv(name="FRONTEND_URL", value=domain)
        call_command("build_cms_site")

        access_our_data_getting_started_page = CompositePage.objects.get(
            slug="getting-started"
        )
        parent_page = CompositePage.objects.get(title="Access our data")
        api_client = APIClient()

        # When
        response = api_client.get(
            path=f"/api/pages/{access_our_data_getting_started_page.id}/"
        )
        access_our_data_getting_started_page_template = open_example_page_response(
            page_name="access_our_data_getting_started"
        )

        # Then
        response_data = response.data
        # Check the `html_url` has been constructed correctly
        assert (
            response_data["meta"]["html_url"]
            == f"https://{domain}/access-our-data/getting-started/"
        )

        assert (
            response_data["title"]
            == access_our_data_getting_started_page_template["title"]
        )
        assert (
            response_data["meta"]["seo_title"]
            == access_our_data_getting_started_page_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == access_our_data_getting_started_page_template["meta"][
                "search_description"
            ]
        )
        assert response_data["meta"]["parent"]["id"] == parent_page.id
        assert response_data["meta"]["parent"]["title"] == parent_page.title

        assert (
            response_data["body"][0]
            == access_our_data_getting_started_page_template["body"][0]
        )

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_feedback_page(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `feedback` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        feedback_page = FormPage.objects.get(slug="feedback")
        parent_home_page = UKHSARootPage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{feedback_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        feedback_page_template = open_example_page_response(page_name="feedback")
        assert response_data["title"] == feedback_page_template["title"]
        assert response_data["body"] == feedback_page_template["body"]
        assert (
            response_data["meta"]["seo_title"]
            == feedback_page_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == feedback_page_template["meta"]["search_description"]
        )
        assert response_data["meta"]["parent"]["id"] == parent_home_page.id
        assert response_data["meta"]["parent"]["title"] == parent_home_page.title

        assert (
            response_data["confirmation_slug"]
            == feedback_page_template["confirmation_slug"]
        )
        assert (
            response_data["confirmation_panel_title"]
            == feedback_page_template["confirmation_panel_title"]
        )
        assert (
            response_data["confirmation_panel_text"]
            == feedback_page_template["confirmation_panel_text"]
        )
        assert (
            response_data["confirmation_body"]
            == feedback_page_template["confirmation_body"]
        )

        # Check that the form fields have been populated correctly
        form_fields_from_response = response_data["form_fields"]
        form_fields_from_template = feedback_page_template["form_fields"]

        for index, form_field in enumerate(form_fields_from_response):
            assert (
                form_field["clean_name"]
                == form_fields_from_template[index]["clean_name"]
            )
            assert form_field["label"] == form_fields_from_template[index]["label"]
            assert (
                form_field["field_type"]
                == form_fields_from_template[index]["field_type"]
            )
            assert (
                form_field["help_text"] == form_fields_from_template[index]["help_text"]
            )
            assert (
                form_field["required"] == form_fields_from_template[index]["required"]
            )
            assert form_field["choices"] == form_fields_from_template[index]["choices"]
            assert (
                form_field["default_value"]
                == form_fields_from_template[index]["default_value"]
            )

    @pytest.mark.django_db
    def test_command_creates_menu_snippet(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        When a GET request is made to `/api/menus/v1` list endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")

        api_client = APIClient()

        # When
        response = api_client.get(
            path="/api/menus/v1",
            headers={"Cache-Force-Refresh": True},
        )

        # Then
        menu_data = response.data["active_menu"]
        # There should be 7 rows in the menu
        assert len(menu_data) == 7

        def extract_primary_link_info(row_index, column_index) -> dict:
            return menu_data[row_index]["value"]["columns"][column_index]["value"][
                "links"
            ]["primary_link"]

        def extract_secondary_link_info(
            row_index, column_index, secondary_link_index
        ) -> dict:
            return menu_data[row_index]["value"]["columns"][column_index]["value"][
                "links"
            ]["secondary_links"][secondary_link_index]["value"]

        home_page = HomePage.objects.last()
        home_page_data = extract_primary_link_info(row_index=0, column_index=0)
        assert home_page_data["title"] == "Homepage"
        assert home_page_data["page"] == home_page.id
        assert home_page_data["html_url"] == home_page.full_url

        covid_page = TopicPage.objects.get(slug="covid-19")
        covid_page_data = extract_secondary_link_info(
            row_index=0, column_index=0, secondary_link_index=0
        )
        assert covid_page_data["title"] == "COVID-19"
        assert covid_page_data["page"] == covid_page.id
        assert covid_page_data["html_url"] == covid_page.full_url

        flu_page = TopicPage.objects.get(slug="influenza")
        flu_page_data = extract_secondary_link_info(
            row_index=0, column_index=0, secondary_link_index=1
        )
        assert flu_page_data["title"] == "Influenza"
        assert flu_page_data["page"] == flu_page.id
        assert flu_page_data["html_url"] == flu_page.full_url

        other_respiratory_viruses_page = TopicPage.objects.get(
            slug="other-respiratory-viruses"
        )
        other_respiratory_viruses_page_data = extract_secondary_link_info(
            row_index=0, column_index=0, secondary_link_index=2
        )
        assert (
            other_respiratory_viruses_page_data["title"] == "Other respiratory viruses"
        )
        assert (
            other_respiratory_viruses_page_data["page"]
            == other_respiratory_viruses_page.id
        )
        assert (
            other_respiratory_viruses_page_data["html_url"]
            == other_respiratory_viruses_page.full_url
        )

        weather_health_alerts_page = CompositePage.objects.get(
            slug="weather-health-alerts"
        )
        weather_health_alerts_page_data = extract_primary_link_info(
            row_index=1, column_index=0
        )
        assert weather_health_alerts_page_data["title"] == "Weather health alerts"
        assert weather_health_alerts_page_data["page"] == weather_health_alerts_page.id
        assert (
            weather_health_alerts_page_data["html_url"]
            == weather_health_alerts_page.full_url
        )
