from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.crawler import Crawler
from caching.handlers import (
    _crawl_all_pages,
    check_cache_for_all_pages,
    collect_all_pages,
    force_cache_refresh_for_all_pages,
)
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory
from tests.fakes.managers.cms.common_page_manager import FakeCommonPageManager
from tests.fakes.managers.cms.home_page_manager import FakeHomePageManager
from tests.fakes.managers.cms.topic_page_manager import FakeTopicPageManager

MODULE_PATH = "caching.handlers"


class TestCollectAllPages:
    def test_all_pages_collected(self):
        """
        Given a `HomePage` with a slug of "dashboard"
        And a number of live `TopicPages` and a `CommonPage`
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

        # Published `CommonPage` which should be collected
        published_about_page = FakeCommonPageFactory.build_blank_page(
            slug="about", live=True
        )
        fake_common_page_manager = FakeCommonPageManager(pages=[published_about_page])

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
            common_page_manager=fake_common_page_manager,
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert published_influenza_page in collected_pages
        assert published_about_page in collected_pages

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
            common_page_manager=FakeCommonPageManager(pages=[]),
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
            common_page_manager=FakeCommonPageManager(pages=[]),
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert unpublished_page not in collected_pages


class TestCrawlAllPages:
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_delegates_calls_successfully(self, spy_collect_all_pages: mock.MagicMock):
        """
        Given a mocked `Crawler` object
        When `_crawl_all_pages()` is called
        Then calls are delegated to `collect_all_pages()`
        And to the `process_pages()` method on the `Crawler` object

        Patches:
            `spy_collect_all_pages`: To isolate the collected pages
                and pass to the assertion on `spy_crawl_pages`
        """
        # Given
        spy_crawler = mock.Mock()

        # When
        _crawl_all_pages(crawler=spy_crawler)

        # Then
        # Check that all pages are collected
        spy_collect_all_pages.assert_called_once()
        collected_pages = spy_collect_all_pages.return_value

        # And then those pages are passed to be processed
        spy_crawler.process_pages.assert_called_once_with(pages=collected_pages)

    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_correct_logs_are_made(
        self,
        mocked_collect_all_pages: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given no pages to be cached
        When `_crawl_all_pages()` is called
        Then the correct log statements are made

        Patches:
            `mocked_collect_all_pages`: To simulate no collected pages
                in order to avoid any unnecessary side effects
        """
        # Given
        mocked_crawler = mock.Mock()
        mocked_collect_all_pages.return_value = []

        # When
        _crawl_all_pages(crawler=mocked_crawler)

        # Then
        assert "Commencing refresh of cache" in caplog.text
        assert "Finished refreshing of cache" in caplog.text


class TestCheckCacheForAllPages:
    @mock.patch(f"{MODULE_PATH}._crawl_all_pages")
    @mock.patch.object(Crawler, "create_crawler_for_cache_checking_only")
    def test_delegates_calls_successfully(
        self,
        spy_create_crawler_for_cache_checking_only: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
    ):
        """
        Given no input
        When `check_cache_for_all_pages()` is called
        Then the correct crawler is passed to `_crawl_all_pages()`

        Patches:
            `spy_create_crawler_for_cache_checking_only`: To assert that
                the correct crawler is initialized i.e. the one
                which can be used purely for checking purposes
            `spy_crawl_all_pages`: For the main assertion
        """
        # Given / When
        check_cache_for_all_pages()

        # Then
        spy_create_crawler_for_cache_checking_only.assert_called_once()
        expected_crawler = spy_create_crawler_for_cache_checking_only.return_value
        spy_crawl_all_pages.assert_called_once_with(crawler=expected_crawler)


class TestHydrateCacheForAllPages:
    @mock.patch(f"{MODULE_PATH}._crawl_all_pages")
    @mock.patch.object(Crawler, "create_crawler_for_force_cache_refresh")
    def test_delegates_calls_successfully(
        self,
        spy_create_crawler_for_force_cache_refresh: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
    ):
        """
        Given no input
        When `force_cache_refresh_for_all_pages()` is called
        Then the correct crawler is passed to `_crawl_all_pages()`

        Patches:
            `spy_create_crawler_for_force_cache_refresh`: To assert that
                the correct crawler is initialized i.e. the one
                which can be used to forcibly refresh the cache
            `spy_crawl_all_pages`: For the main assertion
        """
        # Given / When
        force_cache_refresh_for_all_pages()

        # Then
        spy_create_crawler_for_force_cache_refresh.assert_called_once()
        expected_crawler = spy_create_crawler_for_force_cache_refresh.return_value
        spy_crawl_all_pages.assert_called_once_with(crawler=expected_crawler)
