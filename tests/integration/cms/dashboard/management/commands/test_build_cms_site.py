import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from cms.dashboard.management.commands.build_cms_site import open_example_page_response
from cms.home.models import HomePage
from cms.topic.models import TopicPage


class TestBuildCMSSite:
    @pytest.mark.django_db
    def test_command_builds_site_with_correct_slugs_and_titles(
        self, authenticated_api_client: APIClient
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        When a GET request is made to `/api/pages/` list endpoint
        Then the response contains the page items
            with the expected slugs and titles assigned to each page
        """
        # Given
        call_command("build_cms_site")

        # When
        response = authenticated_api_client.get(path="/api/pages/")

        # Then
        response_data = response.data
        items = response_data["items"]

        expected_slugs = [
            "respiratory-viruses",
            "coronavirus",
            "influenza",
            "how-to-use-this-data",
            "maps",
            "about",
        ]
        created_slugs = [item["meta"]["slug"] for item in items]
        for expected_slug in expected_slugs:
            assert expected_slug in created_slugs

        expected_titles = [
            "Respiratory viruses",
            "Coronavirus",
            "Influenza",
            "How to use this data",
            "Maps",
            "About",
            "What's New",
        ]
        created_titles = [item["title"] for item in items]
        for expected_title in expected_titles:
            assert expected_title in created_titles

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_home_page(
        self,
        authenticated_api_client: APIClient,
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `respiratory-viruses` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        home_page = HomePage.objects.get(slug="respiratory-viruses")

        # When
        response = authenticated_api_client.get(path=f"/api/pages/{home_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        example_home_page_response = open_example_page_response("respiratory_viruses")
        assert response_data["title"] == example_home_page_response["title"]
        assert (
            response_data["page_description"]
            == example_home_page_response["page_description"]
        )
        assert response_data["body"] == example_home_page_response["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = example_home_page_response["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_coronavirus_page(
        self,
        authenticated_api_client: APIClient,
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `coronavirus` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        coronavirus_page = TopicPage.objects.get(slug="coronavirus")

        # When
        response = authenticated_api_client.get(
            path=f"/api/pages/{coronavirus_page.id}/"
        )

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        example_coronavirus_page_response = open_example_page_response("coronavirus")
        assert response_data["title"] == example_coronavirus_page_response["title"]
        assert (
            response_data["page_description"]
            == example_coronavirus_page_response["page_description"]
        )
        assert response_data["body"] == example_coronavirus_page_response["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = example_coronavirus_page_response["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_influenza_page(
        self,
        authenticated_api_client: APIClient,
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `influenza` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        influenza_page = TopicPage.objects.get(slug="influenza")

        # When
        response = authenticated_api_client.get(path=f"/api/pages/{influenza_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        example_influenza_page_response = open_example_page_response("influenza")
        assert response_data["title"] == example_influenza_page_response["title"]
        assert (
            response_data["page_description"]
            == example_influenza_page_response["page_description"]
        )
        assert response_data["body"] == example_influenza_page_response["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = example_influenza_page_response["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]
