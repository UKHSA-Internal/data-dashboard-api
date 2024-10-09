from unittest import mock
import pytest
import datetime
from django.utils import timezone

from cms.dashboard.models import UKHSAPage
from cms.dynamic_content.blocks import PageLinkChooserBlock
from cms.topic.models import TopicPage


class TestPageChooser:
    @pytest.mark.django_db
    @mock.patch.object(UKHSAPage, "get_url_parts")
    def test_page_chooser_returns_full_url(
        self, mocked_url_parts: tuple[int, str, str]
    ):
        """
        Given a `TopicPage` with a mocked `full_url`
        When the page is chosen via  the `PageChooser` block
        Then the `full_url` is returned from the `get_api_representation()` method.
        """
        # Given
        url_parts = ["http://my-prefix", "/topics/abc"]

        mocked_url_parts.return_value = (1, url_parts[0], url_parts[1])

        date_posted: datetime.datetime = timezone.make_aware(
            value=datetime.datetime(year=2023, month=1, day=1)
        )
        TopicPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            date_posted=date_posted,
            live=True,
            seo_title="ABC",
        )
        page_link_chooser = PageLinkChooserBlock(page_type="topic.TopicPage")
        retrieved_topic_page = TopicPage.objects.get_live_pages().first()

        # When
        api_representation_result = page_link_chooser.get_api_representation(
            value=retrieved_topic_page
        )

        # Then
        assert api_representation_result == f"{url_parts[0]}{url_parts[1]}"
