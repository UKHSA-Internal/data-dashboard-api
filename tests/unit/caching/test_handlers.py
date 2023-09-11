from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.crawler import Crawler
from caching.handlers import collect_all_pages, crawl_pages, refresh_cache_for_all_pages
from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory
from tests.fakes.managers.cms.home_page_manager import FakeHomePageManager
from tests.fakes.managers.cms.topic_page_manager import FakeTopicPageManager

MODULE_PATH = "caching.handlers"


class TestCollectAllPages:
    def test_all_pages_collected(self):
        """
        Given a `HomePage` with a slug of "dashboard"
        And a number of live `TopicPage`
        When `collect_all_pages()` is called
        Then the correct pages are returned
        """
        # Given
        # HomePage of slug "dashboard" which should be collected
        published_home_page = FakeHomePageFactory.build_blank_page(slug="dashboard")
        fake_home_page_manager = FakeHomePageManager(pages=[published_home_page])

        # Published `TopicPages` which should be collected
        published_covid_page = FakeTopicPageFactory.build_covid_19_page_from_template()
        published_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )
        fake_topic_page_manager = FakeTopicPageManager(
            pages=[published_covid_page, published_influenza_page]
        )

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert published_influenza_page in collected_pages

    def test_non_dashboard_home_pages_not_collected(self):
        """
        Given a `HomePage` with a slug which is not "dashboard"
        When `collect_all_pages()` is called
        Then no pages are returned
        """
        # Given
        # HomePage which has a different slug then "dashboard" which should not be collected
        non_dashboard_page = FakeHomePageFactory.build_blank_page(
            slug="respiratory-viruses"
        )
        fake_home_page_manager = FakeHomePageManager(pages=[non_dashboard_page])
        fake_topic_page_manager = FakeTopicPageManager(pages=[])

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
        )

        # Then
        assert non_dashboard_page not in collected_pages

    def test_unpublished_pages_not_collected(self):
        """
        Given a `HomePage` with a slug of "dashboard"
        And an unpublished `TopicPage`
        When `collect_all_pages()` is called
        Then the correct pages are returned
        """
        # Given
        published_home_page = FakeHomePageFactory.build_blank_page(slug="dashboard")
        fake_home_page_manager = FakeHomePageManager(pages=[published_home_page])

        # A mixture of unpublished and live pages
        # Whereby only the live pages should be collected
        unpublished_page = (
            FakeTopicPageFactory.build_other_respiratory_viruses_page_from_template(
                live=False
            )
        )
        published_covid_page = FakeTopicPageFactory.build_covid_19_page_from_template()
        fake_topic_page_manager = FakeTopicPageManager(
            pages=[unpublished_page, published_covid_page]
        )

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert unpublished_page not in collected_pages


class TestCrawlPages:
    def test_delegates_call_to_crawler_for_each_page(self):
        """
        Given a list of mocked pages and a `Crawler`
        When `crawl_pages()` is called
        Then `process_all_sections()`
            is called from the `Crawler` for each page
        """
        # Given
        spy_crawler = mock.Mock()
        mocked_pages = [mock.Mock()] * 3

        # When
        crawl_pages(pages=mocked_pages, crawler=spy_crawler)

        # Then
        expected_calls = [mock.call(page=mocked_page) for mocked_page in mocked_pages]
        spy_crawler.process_all_sections.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch.object(Crawler, "__init__", return_value=None)
    def test_initializes_default_crawler_when_not_provided(
        self, spy_crawler_init: mock.MagicMock
    ):
        """
        Given no provided `Crawler`
        When `crawl_pages()` is called
        Then a `Crawler()` is initialized by default
        """
        # Given
        crawler = None

        # When
        crawl_pages(pages=[], crawler=crawler)

        # Then
        spy_crawler_init.assert_called_once()


class TestRefreshCacheForAllPages:
    @mock.patch(f"{MODULE_PATH}.crawl_pages")
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_delegates_calls_successfully(
        self, spy_collect_all_pages: mock.MagicMock, spy_crawl_pages: mock.MagicMock
    ):
        """
        Given pages to be cached
        When `refresh_cache_for_all_pages()` is called
        Then calls are delegated to `collect_all_pages()` and `crawl_pages()`

        Patches:
            `spy_collect_all_pages`: To isolate the collected pages
                and pass to the assertion on `spy_crawl_pages`
            `spy_crawl_pages`: For the main assertion
                of checking pages are passed to it
        """
        # Given / When
        refresh_cache_for_all_pages()

        # Then
        # Check that all pages are collected
        spy_collect_all_pages.assert_called_once()
        collected_pages = spy_collect_all_pages.return_value

        # And then those pages are passed to be processed
        spy_crawl_pages.assert_called_once_with(pages=collected_pages)

    @mock.patch(f"{MODULE_PATH}.crawl_pages")
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_correct_logs_are_made(
        self,
        mocked_collect_all_pages: mock.MagicMock,
        mocked_crawl_pages: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given no pages to be cached
        When `refresh_cache_for_all_pages()` is called
        Then the correct log statements are made

        Patches:
            `mocked_collect_all_pages`: To simulate no collected pages
                in order to avoid any unnecessary side effects
            `mocked_crawl_pages`: To remove any unnecessary
                side effects from the test
        """
        # Given
        mocked_collect_all_pages.return_value = []

        # When
        refresh_cache_for_all_pages()

        # Then
        assert "Commencing refresh of cache" in caplog.text
        assert "Finished refreshing of cache" in caplog.text
