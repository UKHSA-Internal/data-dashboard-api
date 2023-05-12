import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from cms.common.models import CommonPage
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
        home_page_response_template = open_example_page_response("respiratory_viruses")
        assert response_data["title"] == home_page_response_template["title"]
        assert (
            response_data["page_description"]
            == home_page_response_template["page_description"]
        )
        assert response_data["body"] == home_page_response_template["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = home_page_response_template["related_links"]

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
        coronavirus_page_response_template = open_example_page_response("coronavirus")
        assert response_data["title"] == coronavirus_page_response_template["title"]
        assert (
            response_data["page_description"]
            == coronavirus_page_response_template["page_description"]
        )
        assert response_data["body"] == coronavirus_page_response_template["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = coronavirus_page_response_template[
            "related_links"
        ]

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
        influenza_page_response_template = open_example_page_response("influenza")
        assert response_data["title"] == influenza_page_response_template["title"]
        assert (
            response_data["page_description"]
            == influenza_page_response_template["page_description"]
        )
        assert response_data["body"] == influenza_page_response_template["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = influenza_page_response_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_other_respiratory_viruses_page(
        self,
        authenticated_api_client: APIClient,
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `other_respiratory_viruses` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        other_respiratory_viruses_page = TopicPage.objects.get(
            slug="other-respiratory-viruses"
        )

        # When
        response = authenticated_api_client.get(
            path=f"/api/pages/{other_respiratory_viruses_page.id}/"
        )

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        other_respiratory_viruses_page_template = open_example_page_response(
            "other_respiratory_viruses"
        )
        assert (
            response_data["title"] == other_respiratory_viruses_page_template["title"]
        )
        assert (
            response_data["page_description"]
            == other_respiratory_viruses_page_template["page_description"]
        )
        assert response_data["body"] == other_respiratory_viruses_page_template["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = other_respiratory_viruses_page_template[
            "related_links"
        ]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_about_page(
        self,
        authenticated_api_client: APIClient,
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `about` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        about_page = CommonPage.objects.get(slug="about")

        # When
        response = authenticated_api_client.get(path=f"/api/pages/{about_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        about_page_template = open_example_page_response("about")
        assert response_data["title"] == about_page_template["title"]
        assert response_data["body"] == about_page_template["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = about_page_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]

    @pytest.mark.django_db
    def test_command_builds_site_with_correct_whats_new_page(
        self,
        authenticated_api_client: APIClient,
    ):
        """
        Given a CMS site which has been created via the `build_cms_site` management command
        And the ID of the `whats_new` page
        When a GET request is made to `/api/pages/{}` detail endpoint
        Then the response contains the expected data
        """
        # Given
        call_command("build_cms_site")
        whats_new_page = CommonPage.objects.get(slug="what-s-new")

        # When
        response = authenticated_api_client.get(path=f"/api/pages/{whats_new_page.id}/")

        # Then
        response_data = response.data

        # Compare the response from the endpoint to the template used to build the page
        whats_new_page_template = open_example_page_response("whats_new")
        assert response_data["title"] == whats_new_page_template["title"]
        assert response_data["body"] == whats_new_page_template["body"]

        # Check that the related links have been populated correctly
        related_links_from_response = response_data["related_links"]
        assert len(related_links_from_response) == 5

        related_links_from_template = whats_new_page_template["related_links"]

        for index, related_link in enumerate(related_links_from_response):
            assert related_link["title"] == related_links_from_template[index]["title"]
            assert related_link["url"] == related_links_from_template[index]["url"]
            assert related_link["body"] == related_links_from_template[index]["body"]
