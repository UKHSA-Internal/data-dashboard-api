from unittest import mock

from caching.frontend.crawler import FrontEndCrawler
from caching.frontend.handlers import crawl_front_end


class TestCrawlFrontEnd:
    @mock.patch.object(FrontEndCrawler, "process_all_pages")
    def test_delegates_call_to_frontend_crawler(
        self, spy_process_all_pages: mock.MagicMock, monkeypatch
    ):
        """
        Given a `FRONTEND_URL` environment variable
        When `crawl_front_end()` is called
        Then `process_all_pages()` is called from an instance of `FrontEndCrawler`
        """
        # Given / When
        monkeypatch.setenv("FRONTEND_URL", "fake-url")
        crawl_front_end()

        # Then
        spy_process_all_pages.assert_called_once()
