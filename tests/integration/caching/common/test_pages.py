import pytest
from django.utils import timezone
from wagtail.models import Page

from caching.common.pages import collect_viewable_pages
from cms.topic.models import TopicPage


def _create_topic_page(*, title: str, slug: str, **kwargs) -> TopicPage:
    page = TopicPage(
        title=title,
        page_description="test",
        slug=slug,
        seo_title=slug,
        **kwargs,
    )
    home_page = Page.objects.get(id=2)
    home_page.add_child(instance=page)
    page.last_published_at = timezone.now()
    page.save(update_fields=["last_published_at"])
    return page


def _build_permission_sets(
    *, has_global_access: bool = False, permission_sets: list[dict] | None = None
) -> dict:
    return {
        "permission_sets": permission_sets or [],
        "summary": {
            "has_global_access": has_global_access,
            "total_permission_sets": len(permission_sets or []),
        },
    }


class TestCollectViewablePages:
    @pytest.fixture
    def public_topic_page(self) -> TopicPage:
        return _create_topic_page(
            title="Public topic page",
            slug="public-topic-page",
            is_public=True,
        )

    @pytest.fixture
    def non_public_topic_page(self) -> TopicPage:
        return _create_topic_page(
            title="Non-public topic page",
            slug="non-public-topic-page",
            is_public=False,
            page_theme="1",
            page_sub_theme="2",
            page_topic="3",
            page_classification="official_sensitive",
        )

    @pytest.mark.django_db
    def test_only_public_pages_are_collected_for_anonymous_users(
        self, public_topic_page: TopicPage, non_public_topic_page: TopicPage
    ):
        """
        Given a live public page and a live non-public page
        When `collect_viewable_pages()` is called without any permission sets
        Then only the public page is returned
        """
        # Given / When
        collected_pages = collect_viewable_pages()

        # Then
        assert public_topic_page in collected_pages
        assert non_public_topic_page not in collected_pages

    @pytest.mark.django_db
    def test_all_pages_are_collected_for_users_with_global_access(
        self, public_topic_page: TopicPage, non_public_topic_page: TopicPage
    ):
        """
        Given a live public page and a live non-public page
        When `collect_viewable_pages()` is called
            with permission sets which have global access
        Then both pages are returned
        """
        # Given
        permission_sets = _build_permission_sets(has_global_access=True)

        # When
        collected_pages = collect_viewable_pages(permission_sets=permission_sets)

        # Then
        assert public_topic_page in collected_pages
        assert non_public_topic_page in collected_pages

    @pytest.mark.django_db
    def test_permitted_non_public_pages_are_collected(
        self, public_topic_page: TopicPage, non_public_topic_page: TopicPage
    ):
        """
        Given a live public page and a live non-public page
        When `collect_viewable_pages()` is called
            with permission sets which allow for that non-public page
        Then both pages are returned
        """
        # Given
        permission_sets = _build_permission_sets(
            permission_sets=[
                {
                    "theme": {"id": non_public_topic_page.page_theme},
                    "sub_theme": {"id": non_public_topic_page.page_sub_theme},
                    "topic": {"id": non_public_topic_page.page_topic},
                }
            ]
        )

        # When
        collected_pages = collect_viewable_pages(permission_sets=permission_sets)

        # Then
        assert public_topic_page in collected_pages
        assert non_public_topic_page in collected_pages

    @pytest.mark.django_db
    def test_non_permitted_non_public_pages_are_not_collected(
        self, public_topic_page: TopicPage, non_public_topic_page: TopicPage
    ):
        """
        Given a live public page and a live non-public page
        When `collect_viewable_pages()` is called
            with permission sets which do not allow for that non-public page
        Then only the public page is returned
        """
        # Given
        permission_sets = _build_permission_sets(
            permission_sets=[
                {
                    "theme": {"id": "999"},
                    "sub_theme": {"id": "999"},
                    "topic": {"id": "999"},
                }
            ]
        )

        # When
        collected_pages = collect_viewable_pages(permission_sets=permission_sets)

        # Then
        assert public_topic_page in collected_pages
        assert non_public_topic_page not in collected_pages
