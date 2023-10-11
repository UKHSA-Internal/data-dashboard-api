import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from cms.common.models import CommonPage
from cms.dashboard.management.commands.build_cms_site import open_example_page_response
from cms.home.models import HomePage
from cms.topic.models import TopicPage


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

        expected_slugs = [
            "dashboard",
            "covid-19",
            "influenza",
            "location-based-data",
            "about",
            "whats-new",
            "whats-coming",
            "cookies",
        ]
        created_slugs = [item["meta"]["slug"] for item in items]
        for expected_slug in expected_slugs:
            assert expected_slug in created_slugs

        expected_titles = [
            "UKHSA data dashboard",
            "COVID-19",
            "Influenza",
            "Location based data",
            "About",
            "What's new",
            "What's coming",
            "Cookies",
        ]
        created_titles = [item["title"] for item in items]
        for expected_title in expected_titles:
            assert expected_title in created_titles

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
        home_page = HomePage.objects.get(slug="dashboard")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{home_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        home_page_response_template = open_example_page_response("ukhsa_data_dashboard")
        assert response_data["title"] == home_page_response_template["title"]
        assert (
            response_data["page_description"]
            == home_page_response_template["page_description"]
        )
        assert response_data["body"] == home_page_response_template["body"]
        assert (
            response_data["meta"]["seo_title"]
            == home_page_response_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == home_page_response_template["meta"]["search_description"]
        )
        assert (
            response_data["meta"]["show_in_menus"]
            == home_page_response_template["meta"]["show_in_menus"]
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
        topic_page_response_template = open_example_page_response(page_name)
        assert response_data["title"] == topic_page_response_template["title"]
        assert (
            response_data["page_description"]
            == topic_page_response_template["page_description"]
        )
        assert response_data["body"] == topic_page_response_template["body"]
        assert (
            response_data["meta"]["seo_title"]
            == topic_page_response_template["meta"]["seo_title"]
        )
        assert (
            response_data["meta"]["search_description"]
            == topic_page_response_template["meta"]["search_description"]
        )
        assert (
            response_data["meta"]["show_in_menus"]
            == topic_page_response_template["meta"]["show_in_menus"]
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
    def test_command_builds_site_with_correct_about_page(self):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `about` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        about_page = CommonPage.objects.get(slug="about")
        parent_home_page = HomePage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{about_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        about_page_template = open_example_page_response("about")
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
        assert (
            response_data["meta"]["show_in_menus"]
            == about_page_template["meta"]["show_in_menus"]
        )
        assert response_data["meta"]["parent"]["id"] == parent_home_page.id
        assert response_data["meta"]["parent"]["title"] == parent_home_page.title

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
        whats_new_page = CommonPage.objects.get(slug="whats-new")
        parent_home_page = HomePage.objects.get(title="UKHSA Dashboard Root")
        api_client = APIClient()

        # When
        response = api_client.get(path=f"/api/pages/{whats_new_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        whats_new_page_template = open_example_page_response("whats_new")
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
        assert (
            response_data["meta"]["show_in_menus"]
            == whats_new_page_template["meta"]["show_in_menus"]
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
