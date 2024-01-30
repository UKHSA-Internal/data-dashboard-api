from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.handlers import (
    check_cache_for_all_pages,
    collect_all_pages,
    crawl_all_pages,
    extract_area_selectable_pages,
    force_cache_refresh_for_all_pages,
    get_all_downloads,
)
from caching.private_api.management import CacheManagement
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory
from tests.fakes.factories.cms.whats_new_child_entry_factory import (
    FakeWhatsNewChildEntryFactory,
)
from tests.fakes.factories.cms.whats_new_parent_page_factory import (
    FakeWhatsNewParentPageFactory,
)
from tests.fakes.managers.cms.common_page_manager import FakeCommonPageManager
from tests.fakes.managers.cms.home_page_manager import FakeHomePageManager
from tests.fakes.managers.cms.topic_page_manager import FakeTopicPageManager
from tests.fakes.managers.cms.whats_new_child_entry_manager import (
    FakeWhatsNewChildEntryManager,
)
from tests.fakes.managers.cms.whats_new_parent_page_manager import (
    FakeWhatsNewParentPageManager,
)

MODULE_PATH = "caching.private_api.handlers"


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
            whats_new_parent_page_manager=FakeWhatsNewParentPageManager(pages=[]),
            whats_new_child_entry_manager=FakeWhatsNewChildEntryManager(pages=[]),
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert published_influenza_page in collected_pages
        assert published_about_page in collected_pages

    def test_all_whats_new_type_pages_collected(self):
        """
        Given a `WhatsNewParentPage` and `WhatsNewChildEntry`
        When `collect_all_pages()` is called
        Then the correct pages are returned
        """
        # Given
        # Published `WhatsNewParentPage` which should be collected
        published_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template(
                live=True,
            )
        )
        fake_whats_new_parent_page_manager = FakeWhatsNewParentPageManager(
            pages=[published_whats_new_parent_page]
        )
        # Published `WhatsNewChildEntry` which should be collected
        published_whats_new_child_entry = (
            FakeWhatsNewChildEntryFactory.build_page_from_template(
                live=True,
            )
        )
        # Unpublished `WhatsNewChildEntry` which should not be collected
        unpublished_whats_new_child_entry = (
            FakeWhatsNewChildEntryFactory.build_page_from_template(
                live=False,
            )
        )
        fake_whats_new_child_entry_manager = FakeWhatsNewChildEntryManager(
            pages=[published_whats_new_child_entry, unpublished_whats_new_child_entry]
        )

        # When
        collected_pages = collect_all_pages(
            home_page_manager=FakeHomePageManager(pages=[]),
            topic_page_manager=FakeTopicPageManager(pages=[]),
            common_page_manager=FakeCommonPageManager(pages=[]),
            whats_new_child_entry_manager=fake_whats_new_child_entry_manager,
            whats_new_parent_page_manager=fake_whats_new_parent_page_manager,
        )

        # Then
        assert published_whats_new_parent_page in collected_pages
        assert published_whats_new_child_entry in collected_pages
        assert unpublished_whats_new_child_entry not in collected_pages

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
            whats_new_parent_page_manager=FakeWhatsNewParentPageManager(pages=[]),
            whats_new_child_entry_manager=FakeWhatsNewChildEntryManager(pages=[]),
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
            whats_new_parent_page_manager=FakeWhatsNewParentPageManager(pages=[]),
            whats_new_child_entry_manager=FakeWhatsNewChildEntryManager(pages=[]),
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert unpublished_page not in collected_pages


class TestExtractAreaSelectablePages:
    def test_returns_for_topic_pages_only(self):
        """
        Given a list of pages of different types
            including a `TopicPage` which is valid for the area selector
        When `extract_area_selectable_pages()` is called
        Then only the valid `TopicPage` model is returned
        """
        # Given
        valid_topic_page = FakeTopicPageFactory.build_covid_19_page_from_template()
        valid_topic_page.enable_area_selector = True

        # The topic page was not selected so should be excluded
        unselected_topic_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )
        unselected_topic_page.enable_area_selector = False

        # Although the build other viruses page was selected
        # It contains more than 1 topic and therefore is not included
        invalid_topic_page = (
            FakeTopicPageFactory.build_other_respiratory_viruses_page_from_template()
        )
        invalid_topic_page.enable_area_selector = True

        # Other page types do not implement the `is_valid_for_area_selector`
        # property and therefore should return False by default
        # and will be excluded
        other_pages = [
            FakeHomePageFactory.build_blank_page(slug="dashboard"),
            FakeWhatsNewParentPageFactory.build_page_from_template(live=True),
        ]
        all_pages = other_pages + [
            valid_topic_page,
            unselected_topic_page,
            invalid_topic_page,
        ]

        # When
        area_selectable_pages = extract_area_selectable_pages(all_pages=all_pages)

        # Then
        assert area_selectable_pages == [valid_topic_page]


class TestCrawlAllPages:
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_delegates_calls_successfully(self, spy_collect_all_pages: mock.MagicMock):
        """
        Given a mocked `Crawler` object
        When `crawl_all_pages()` is called
        Then calls are delegated to `collect_all_pages()`
        And to the `process_pages()` method on the `Crawler` object

        Patches:
            `spy_collect_all_pages`: To isolate the collected pages
                and pass to the assertion on `spy_crawl_pages`
        """
        # Given
        spy_crawler = mock.Mock()

        # When
        crawl_all_pages(
            private_api_crawler=spy_crawler, area_selector_orchestrator=mock.Mock()
        )

        # Then
        # Check that all pages are collected
        spy_collect_all_pages.assert_called_once()
        collected_pages = spy_collect_all_pages.return_value

        # And then those pages are passed to be processed
        spy_crawler.process_pages.assert_called_once_with(pages=collected_pages)

    @mock.patch(f"{MODULE_PATH}.extract_area_selectable_pages")
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_delegates_calls_successfully_when_area_selector_is_activated(
        self,
        spy_collect_all_pages: mock.MagicMock,
        spy_extract_area_selectable_pages: mock.MagicMock,
        monkeypatch,
    ):
        """
        Given a mocked `Crawler` object
        When `crawl_all_pages()` is called
        Then calls are delegated to `collect_all_pages()`
        And to the `process_pages()` method on the `Crawler` object
        And to the `process_pages()` method on the `AreaSelectorOrchestrator` object

        Patches:
            `spy_collect_all_pages`: To isolate the collected pages
                and pass to the assertion on `spy_crawl_pages`
            `spy_extract_area_selectable_pages`: To extract the
                topic pages which are deemed suitable
                from the previously retrieved pages

        """
        # Given
        spy_private_api_crawler = mock.Mock()
        spy_area_selector_orchestrator = mock.Mock()
        monkeypatch.setenv(name="ENABLE_AREA_SELECTOR", value=True)

        # When
        crawl_all_pages(
            private_api_crawler=spy_private_api_crawler,
            area_selector_orchestrator=spy_area_selector_orchestrator,
        )

        # Then
        # Check that all pages are collected
        spy_collect_all_pages.assert_called_once()
        all_collected_pages = spy_collect_all_pages.return_value
        # And then those pages are passed to be processed
        spy_private_api_crawler.process_pages.assert_called_once_with(
            pages=all_collected_pages
        )

        # Check that the topic pages are extracted
        spy_extract_area_selectable_pages.assert_called_once_with(
            all_pages=all_collected_pages
        )
        # And then those topic pages are passed to the `AreaSelectorOrchestrator`
        spy_area_selector_orchestrator.process_pages.assert_called_once_with(
            pages=spy_extract_area_selectable_pages.return_value
        )

    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_correct_logs_are_made(
        self,
        mocked_collect_all_pages: mock.MagicMock,
        caplog: LogCaptureFixture,
    ):
        """
        Given no pages to be cached
        When `crawl_all_pages()` is called
        Then the correct log statements are made

        Patches:
            `mocked_collect_all_pages`: To simulate no collected pages
                in order to avoid any unnecessary side effects
        """
        # Given
        mocked_crawler = mock.Mock()
        mocked_collect_all_pages.return_value = []

        # When
        crawl_all_pages(
            private_api_crawler=mocked_crawler, area_selector_orchestrator=mock.Mock()
        )

        # Then
        assert "Commencing refresh of cache" in caplog.text
        assert "Finished refreshing of cache" in caplog.text


class TestCheckCacheForAllPages:
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_cache_checking_only")
    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    def test_delegates_calls_successfully(
        self,
        spy_area_selector_orchestrator_class: mock.MagicMock,
        spy_create_crawler_for_cache_checking_only: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
    ):
        """
        Given no input
        When `check_cache_for_all_pages()` is called
        Then the correct crawler is passed to `crawl_all_pages()`

        Patches:
            `spy_create_crawler_for_cache_checking_only`: To assert that
                the correct crawler is initialized i.e. the one
                which can be used purely for checking purposes
            `spy_crawl_all_pages`: For the main assertion
            `spy_area_selector_orchestrator_class`: To check the
                area selector orchestrator is passed to the
                `crawl_all_pages()` function
        """
        # Given / When
        check_cache_for_all_pages()

        # Then
        # Check the `PrivateAPICrawler` is initialized via the correct class constructor method
        spy_create_crawler_for_cache_checking_only.assert_called_once()
        expected_private_crawler = (
            spy_create_crawler_for_cache_checking_only.return_value
        )

        # Check the `AreaSelectorOrchestrator` object is initialized
        spy_area_selector_orchestrator_class.assert_called_once_with(
            geographies_api_crawler=expected_private_crawler.geography_api_crawler
        )
        # Check both the `PrivateAPICrawler` and the `AreaSelectorOrchestrator`
        # are passed to the `crawl_all_pages()` call
        spy_crawl_all_pages.assert_called_once_with(
            private_api_crawler=expected_private_crawler,
            area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
        )


class TestForceCacheRefreshForAllPages:
    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_force_cache_refresh")
    def test_delegates_calls_successfully(
        self,
        spy_create_crawler_for_force_cache_refresh: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
        spy_area_selector_orchestrator_class: mock.MagicMock,
    ):
        """
        Given no input
        When `force_cache_refresh_for_all_pages()` is called
        Then the correct crawler is passed to `crawl_all_pages()`

        Patches:
            `spy_create_crawler_for_force_cache_refresh`: To assert that
                the correct crawler is initialized i.e. the one
                which can be used to forcibly refresh the cache
            `spy_crawl_all_pages`: For the main assertion
            `spy_area_selector_orchestrator_class`: To check the
                area selector orchestrator is passed to the
                `crawl_all_pages()` function
        """
        # Given / When
        force_cache_refresh_for_all_pages()

        # Then
        spy_create_crawler_for_force_cache_refresh.assert_called_once()
        expected_crawler = spy_create_crawler_for_force_cache_refresh.return_value
        spy_crawl_all_pages.assert_called_once_with(
            private_api_crawler=expected_crawler,
            area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
        )

    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_force_cache_refresh")
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    @mock.patch.object(CacheManagement, "clear")
    def test_clears_cache_prior_to_crawler(
        self,
        spy_cache_management_clear: mock.MagicMock,
        spy_area_selector_orchestrator_class: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
        mocked_created_private_api_crawler: mock.MagicMock,
    ):
        """
        Given no input
        When `check_cache_for_all_pages()` is called
        Then `clear()` is called from a `CacheManagement` object
            before the call is made to `crawl_all_pages()`
        """
        # Given
        spy_manager = mock.Mock()
        spy_manager.attach_mock(spy_cache_management_clear, "cache_management_clear")
        spy_manager.attach_mock(spy_crawl_all_pages, "crawl_all_pages")

        # When
        force_cache_refresh_for_all_pages()

        # Then
        # `clear()` should only have been called once from the CacheManagement object
        spy_cache_management_clear.assert_called_once()

        # The cache should flushed before crawling the pages
        expected_calls = [
            mock.call.cache_management_clear(),
            mock.call.crawl_all_pages(
                private_api_crawler=mocked_created_private_api_crawler.return_value,
                area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
            ),
        ]
        spy_manager.assert_has_calls(calls=expected_calls, any_order=False)

        # `crawl_all_pages()` should only have been called once
        spy_crawl_all_pages.assert_called_once()


class TestGetAllDownloads:
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_lazy_loading")
    def test_delegates_calls_correctly(
        self,
        spy_create_crawler_for_lazy_loading: mock.MagicMock,
        spy_collect_all_pages: mock.MagicMock,
    ):
        """
        Given a mocked `Crawler` object and fake_file_format
        When `get_all_downloads()` is called
        Then calls are delegated to `collect_all_pages()` and
            crawler_get_all_downloads() methods.
        """
        # Given
        crawler = spy_create_crawler_for_lazy_loading.return_value
        fake_file_format = "csv"

        # When
        get_all_downloads()

        # Then
        spy_collect_all_pages.assert_called_once()
        expected_pages = spy_collect_all_pages.return_value
        spy_create_crawler_for_lazy_loading.assert_called_once()
        crawler.get_all_downloads.assert_called_once_with(
            pages=expected_pages, file_format=fake_file_format
        )

    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_lazy_loading")
    def test_default_file_format_can_be_changed_to_json(
        self,
        spy_create_crawler_for_lazy_loading: mock.MagicMock,
        spy_collect_all_pages,
    ):
        """
        Given a mocked `Crawler` object
        When `get_all_downloads()` is called passing in a file_format parameter
            set to json.
        Then The file_format parameter set to json.
        """
        # Given
        crawler = spy_create_crawler_for_lazy_loading.return_value
        file_format = "json"

        # Then
        get_all_downloads(file_format=file_format)

        # Then
        collected_pages = spy_collect_all_pages.return_value
        crawler.get_all_downloads.assert_called_once_with(
            pages=collected_pages, file_format=file_format
        )

    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_lazy_loading")
    def test_default_file_format_is_csv(
        self,
        spy_create_crawler_for_lazy_loading: mock.MagicMock,
        spy_collect_all_pages,
    ):
        """
        Given a mocked `Crawler` object.
        When `get_all_downloads()` is called without passing a file_format parameter.
        Then The default file_format parameter is set to csv.
        """
        # Given
        crawler = spy_create_crawler_for_lazy_loading.return_value

        # When
        get_all_downloads()

        # Then crawl.get_all_downloads will have file_format csv
        collected_pages = spy_collect_all_pages.return_value
        crawler.get_all_downloads.assert_called_once_with(
            pages=collected_pages, file_format="csv"
        )
