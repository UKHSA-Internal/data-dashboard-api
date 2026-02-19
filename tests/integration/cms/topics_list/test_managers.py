import pytest

from cms.topics_list.managers import EXPECTED_TOPICS_LIST_PAGE_SLUG
from cms.topics_list.models import TopicsListPage


class TestTopicsListPageManager:
    @pytest.mark.django_db
    def test_get_topics_list_page(self):
        """
        Given 2 `TopicsListPage` records of which one has a slug of `health-topics`
        When `get_topics_list_page()` is called from the `TopicsListPageManager`
        Then the correct `TopicsListPage` record is returned
        """
        # Given
        topics_list_page = TopicsListPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            page_description="abc",
            slug=EXPECTED_TOPICS_LIST_PAGE_SLUG,
            seo_title="ABC",
        )
        invalid_topics_list_page = TopicsListPage.objects.create(
            path="def",
            depth=1,
            title="def",
            page_description="def",
            slug="invalid_slug",
            seo_title="DEF",
        )

        # When
        retreived_topics_list_page = TopicsListPage.objects.get_topics_list_page()

        # Then
        assert (
            retreived_topics_list_page == topics_list_page != invalid_topics_list_page
        )
