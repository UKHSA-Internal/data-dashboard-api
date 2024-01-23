import pytest

from cms.composite.models import CompositePage


class TestCompositePageManager:
    @pytest.mark.django_db
    def test_get_live_pages(self):
        """
        Given 2 `CompositePage` records of which only 1 is live
        When `get_live_pages()` is called from the `CompositePageManager`
        Then the correct `CompositePage` record is returned.
        """
        # Given
        live_page = CompositePage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            date_posted="2024-01-01",
            live=True,
        )
        unpublished_page = CompositePage.objects.create(
            path="def",
            depth=1,
            title="def",
            date_posted="2024-01-01",
            live=False,
        )

        # When
        retrieved_live_pages = CompositePage.objects.get_live_pages()

        # Then
        assert live_page in retrieved_live_pages
        assert unpublished_page not in retrieved_live_pages
