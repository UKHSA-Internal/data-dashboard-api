import pytest

from caching.common.pages import get_childhood_vaccinations_page
from cms.topic.models import TopicPage


class TestGetChildhoodVaccinationsPage:
    @pytest.mark.django_db
    def test_returns_correct_model(self):
        """
        Given an existing `TopicPage`
            with a slug of "childhood-vaccinations"
        When `get_childhood_vaccinations_page()` is called
        Then the page is returned in a list
        """
        # Given
        childhood_vaccinations_page = TopicPage.objects.create(
            slug="childhood-vaccinations",
            path="abc",
            depth=1,
            title="Childhood Vaccinations",
            seo_title="abc",
        )

        # When
        retrieved_pages: list[TopicPage] = get_childhood_vaccinations_page()

        # Then
        assert childhood_vaccinations_page in retrieved_pages

    @pytest.mark.django_db
    def test_returns_empty_list_when_page_not_available(self):
        """
        Given no existing `TopicPage`
            with a slug of "childhood-vaccinations"
        When `get_childhood_vaccinations_page()` is called
        Then an empty list is returned
        """
        # Given / When
        retrieved_pages: list[TopicPage] = get_childhood_vaccinations_page()

        # Then
        assert not retrieved_pages
