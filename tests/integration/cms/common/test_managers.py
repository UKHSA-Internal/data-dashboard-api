import pytest

from cms.common.models import CommonPage


class TestCommonPageManager:
    @pytest.mark.django_db
    def test_get_live_pages(self):
        """
        Given 2 `CommonPage` records of which only 1 is live
        When `get_live_pages()` is called from the `CommonPageManager`
        Then the correct `CommonPage` record is returned
        """
        # Given
        live_page = CommonPage.objects.create(
            path="abc",
            depth=1,
            title="abc",
            date_posted="2023-01-01",
            body="ghi",
            live=True,
        )
        unpublished_page = CommonPage.objects.create(
            path="def",
            depth=1,
            title="def",
            date_posted="2023-01-01",
            body="ghi",
            live=False,
        )

        # When
        retrieved_live_pages = CommonPage.objects.get_live_pages()

        # Then
        assert live_page in retrieved_live_pages
        assert unpublished_page not in retrieved_live_pages
