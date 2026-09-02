from http import HTTPStatus
import os
import pytest

from rest_framework.test import RequestsClient


@pytest.mark.django_db
class TestSearchAPIView:

    @property
    def path(self) -> str:
        return "/api/public/search/v1"

    @property
    def target_domain(self) -> str:
        return os.environ.get("PUBLIC_API_TEST_DOMAIN", "http://testserver")

    def test_search_finds_topics_only(self, topics, other_pages):
        """
        Given a string that matches all topic pages
        When the API is called with that query and a limit of 5
        Then the results will include only topic pages
        """

        # Given
        limit = len(topics)
        search = "topic"  # All topics have a title with topic in them
        query = f"search={search}&limit={limit}"

        # When
        client = RequestsClient()
        url = f"{self.target_domain}{self.path}?{query}"
        response: Response = client.get(url)

        # Then
        assert response.status_code == HTTPStatus.OK
        response_data: list[dict] = response.json()
        assert limit == len(response_data)
        for page in topics:
            target = {"title": page.title, "slug": page.slug}
            assert response_data.index(target) > -1

    def test_search_finds_topics_and_pages(self, topics, other_pages):
        """
        Given a string that matches 2 topic page
        When the API is called with that query and no limit
        Then the results will include the matching topic pages and others with the topics first
        """

        # Given
        search = "rare"  # All topics have a title, only even ones have rare in it
        query = f"search={search}"
        expected_results = [t for t in topics if "rare" in t.title]

        # When
        client = RequestsClient()
        url = f"{self.target_domain}{self.path}?{query}"
        response: Response = client.get(url)

        # Then
        assert response.status_code == HTTPStatus.OK
        response_data: list[dict] = response.json()
        assert len(expected_results) == len(response_data)
        for page in expected_results:
            target = {"title": page.title, "slug": page.slug}
            assert response_data.index(target) > -1

    def test_search_doesnt_find_unpublish_pages(self, topics, other_pages):
        """
        Given a string that matches 2 topic page
        When the API is called with that query and no limit
        Then the results will include the matching topic pages and others with the topics first
        """

        # Given
        search = "rare"  # All topics have a title, only even ones have rare in it
        query = f"search={search}"
        expected_results = [t for t in topics if "rare" in t.title]

        # When
        client = RequestsClient()
        url = f"{self.target_domain}{self.path}?{query}"
        response: Response = client.get(url)

        # Then
        assert response.status_code == HTTPStatus.OK
        response_data: list[dict] = response.json()
        assert len(expected_results) == len(response_data)
        for page in expected_results:
            target = {"title": page.title, "slug": page.slug}
            assert response_data.index(target) > -1
