import datetime

import pytest

from cms.topic.models import TopicPage
from django.utils import timezone


class TestTopicPageManager:
    @pytest.mark.django_db
    def test_get_live_pages(self):
        """
        Given 2 `TopicPage` records of which only 1 is live
        When `get_live_pages()` is called from the `TopicPageManager`
        Then the correct `TopicPage` record is returned
        """
        # Given
        live_page = TopicPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            live=True,
            seo_title="ABC",
        )
        unpublished_page = TopicPage.objects.create(
            path="def",
            depth=1,
            title="def",
            live=False,
            seo_title="DEF",
        )

        # When
        retrieved_live_pages = TopicPage.objects.get_live_pages()

        # Then
        assert live_page in retrieved_live_pages
        assert unpublished_page not in retrieved_live_pages
