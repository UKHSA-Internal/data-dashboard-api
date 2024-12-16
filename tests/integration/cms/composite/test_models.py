import datetime

import pytest
from wagtail.models import Page

from cms.dashboard.management.commands import build_cms_site_helpers


class TestCompositePage:
    @pytest.mark.django_db
    def test_last_updated_at_favours_most_recent_timestamp(self):
        """
        Given a `CompositePage` which acts as an index page
        And a `TopicPage` which is a child of the `CompositePage`
        When `last_updated_at` is called from the parent page
        Then the latest associated timestamp is always returned
            regardless of whether this emanates from the child or the parent
        """
        # Given
        root_page = Page.get_first_root_node()
        parent_page = build_cms_site_helpers.create_composite_page(
            name="access_our_data_parent_page", parent_page=root_page
        )
        # We must refetch the page from the db to get the latest version of the model
        parent_page.refresh_from_db()
        original_parent_published_time = parent_page.last_published_at

        child_page = build_cms_site_helpers.create_topic_page(
            name="influenza", parent_page=parent_page
        )
        child_page.refresh_from_db()

        # When
        parent_page_last_updated_at: datetime.datetime = parent_page.last_updated_at

        # Then
        # The latest_updated_at timestamp of the parent takes the child page
        # since that timestamp is later
        assert (
            parent_page_last_updated_at
            == child_page.last_updated_at
            > original_parent_published_time
        )

        # Republish the parent page to force it
        # to produce the most recent later timestamp
        parent_page.save_revision().publish()

        # The parent page `last_updated_at` now points to the latest revision
        # i.e. the one on the parent page itself
        parent_page.refresh_from_db()
        assert parent_page.last_updated_at > child_page.last_updated_at
