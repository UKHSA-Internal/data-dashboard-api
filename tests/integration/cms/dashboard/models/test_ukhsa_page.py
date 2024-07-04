from rest_framework.test import APIClient
from wagtail.models import Site, Page
import pytest

from cms.dashboard.management.commands.build_cms_site import _create_topic_page
from cms.home.models import HomePage


class TestUKHSAPage:
    @pytest.mark.django_db
    def test_get_url_parts_returns_correct_url(self):
        """
        Given a page and child page which belongs to that page
        And a `Site` with a hostname
        When the GET `pages/` list endpoint is hit
        Then the correct URLs are returned in the response
        """
        # Given
        hostname = "my-prefix.dev.ukhsa-dashboard.data.gov.uk"
        root_page = HomePage(title="UKHSA dashboard root", slug="ukhsa-dashboard-root")
        wagtail_root_page = Page.get_first_root_node()
        wagtail_root_page.add_child(instance=root_page)
        wagtail_root_page.save_revision().publish()
        Site.objects.all().delete()
        Site.objects.create(
            hostname=hostname,
            port=443,
            site_name="dashboard",
            root_page=root_page,
            is_default_site=True,
        )

        parent_page = _create_topic_page(name="covid_19", parent_page=root_page)
        child_page = _create_topic_page(name="influenza", parent_page=parent_page)
        api_client = APIClient()

        # When
        response = api_client.get(path="/api/pages/")

        # Then
        response_data = response.data
        expected_base_url = f"https://{hostname}"
        assert (
            response_data["items"][1]["meta"]["html_url"]
            == f"{expected_base_url}/{parent_page.slug}/"
        )
        assert (
            response_data["items"][2]["meta"]["html_url"]
            == f"{expected_base_url}/{parent_page.slug}/{child_page.slug}/"
        )
