import pytest

from cms.error.models import ErrorPage


class TestErrorPageManager:
    @pytest.mark.django_db
    def test_get_live_pages(self):
        """
        Given 2 `ErrorPage` records of which only 1 is live
        When `get_live_pages()` is called from the `ErrorPageManager`
        Then the correct `ErrorPage` record is returned
        """
        # Given
        live_page = ErrorPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            body="ghi",
            live=True,
            seo_title="ABC",
        )
        unpublished_page = ErrorPage.objects.create(
            path="def",
            depth=1,
            title="def",
            body="ghi",
            live=False,
            seo_title="DEF",
        )

        # When
        retrieved_live_pages = ErrorPage.objects.get_live_pages()

        # Then
        assert live_page in retrieved_live_pages
        assert unpublished_page not in retrieved_live_pages
