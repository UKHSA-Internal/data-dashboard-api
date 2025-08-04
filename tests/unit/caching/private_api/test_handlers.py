from unittest import mock

from _pytest.logging import LogCaptureFixture

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.handlers import (
    crawl_all_pages,
    force_cache_refresh_for_all_pages,
    get_all_downloads,
    force_cache_refresh_for_reserved_namespace,
)
from caching.private_api.management import (
    CacheManagement,
    RESERVED_NAMESPACE_KEY_PREFIX,
)

MODULE_PATH = "caching.private_api.handlers"


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
    def test_delegates_calls_successfully_for_area_selector_orchestrator(
        self,
        spy_collect_all_pages: mock.MagicMock,
        spy_extract_area_selectable_pages: mock.MagicMock,
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


class TestForceCacheRefreshForAllPages:
    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch.object(
        PrivateAPICrawler, "create_crawler_to_force_write_in_non_reserved_namespace"
    )
    def test_delegates_calls_successfully(
        self,
        spy_create_crawler_to_force_write_in_non_reserved_namespace: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
        spy_area_selector_orchestrator_class: mock.MagicMock,
    ):
        """
        Given no input
        When `force_cache_refresh_for_all_pages()` is called
        Then the correct crawler is passed to `crawl_all_pages()`

        Patches:
            `spy_create_crawler_to_force_write_in_non_reserved_namespace`: To assert
                that the correct crawler is initialized i.e. the one
                which can be used to forcibly refresh the cache
            `spy_crawl_all_pages`: For the main assertion
            `spy_area_selector_orchestrator_class`: To check the
                area selector orchestrator is passed to the
                `crawl_all_pages()` function
        """
        # Given
        mocked_cache_management = mock.Mock()

        # When
        force_cache_refresh_for_all_pages(cache_management=mocked_cache_management)

        # Then
        spy_create_crawler_to_force_write_in_non_reserved_namespace.assert_called_once()
        expected_crawler = (
            spy_create_crawler_to_force_write_in_non_reserved_namespace.return_value
        )
        spy_crawl_all_pages.assert_called_once_with(
            private_api_crawler=expected_crawler,
            area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
        )

    @mock.patch.object(
        PrivateAPICrawler, "create_crawler_to_force_write_in_non_reserved_namespace"
    )
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    @mock.patch.object(CacheManagement, "clear_non_reserved_keys")
    def test_clears_non_reserved_keys_cache_prior_to_crawler(
        self,
        spy_cache_management_clear_non_reserved_keys: mock.MagicMock,
        spy_area_selector_orchestrator_class: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
        mocked_create_crawler_to_force_write_in_non_reserved_namespace: mock.MagicMock,
    ):
        """
        Given no input
        When `force_cache_refresh_for_all_pages()` is called
        Then `clear_non_reserved_keys()` is called from a `CacheManagement` object
            before the call is made to `crawl_all_pages()`
        """
        # Given
        spy_manager = mock.Mock()
        spy_manager.attach_mock(
            spy_cache_management_clear_non_reserved_keys,
            "cache_management_clear_non_reserved_keys",
        )
        spy_manager.attach_mock(spy_crawl_all_pages, "crawl_all_pages")

        # When
        force_cache_refresh_for_all_pages()

        # Then
        # `clear_non_reserved_keys()` should only have been called once from the CacheManagement object
        spy_cache_management_clear_non_reserved_keys.assert_called_once()

        # The cache should flushed before crawling the pages
        expected_calls = [
            mock.call.cache_management_clear_non_reserved_keys(),
            mock.call.crawl_all_pages(
                private_api_crawler=mocked_create_crawler_to_force_write_in_non_reserved_namespace.return_value,
                area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
            ),
        ]
        spy_manager.assert_has_calls(calls=expected_calls, any_order=False)

        # `crawl_all_pages()` should only have been called once
        spy_crawl_all_pages.assert_called_once()


class TestForceCacheRefreshForReservedNamespace:
    @mock.patch.object(
        PrivateAPICrawler, "create_crawler_to_force_write_in_reserved_staging_namespace"
    )
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    def test_manages_reserved_keys_cache_operations_in_correct_order(
        self,
        spy_area_selector_orchestrator_class: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
        mocked_create_crawler_to_force_write_in_reserved_staging_namespace: mock.MagicMock,
    ):
        """
        Given no input
        When `force_cache_refresh_for_reserved_namespace()` is called
        Then reserved keys are retrieved before crawling, deleted after crawling,
            and finally the reserved staging keys
            are moved to reserved namespace
        """
        # Given
        mocked_cache_management = mock.Mock()
        expected_original_reserved_keys = [
            f"{RESERVED_NAMESPACE_KEY_PREFIX}-abc",
            f"{RESERVED_NAMESPACE_KEY_PREFIX}-def",
            f"{RESERVED_NAMESPACE_KEY_PREFIX}-123",
        ]
        mocked_cache_management.get_reserved_keys.return_value = (
            expected_original_reserved_keys
        )

        # Set up the spy manager to record the order
        # in which the various calls are made
        spy_manager = mock.Mock()
        spy_manager.attach_mock(
            mocked_cache_management.get_reserved_keys, "get_reserved_keys"
        )
        spy_manager.attach_mock(spy_crawl_all_pages, "crawl_all_pages")
        spy_manager.attach_mock(mocked_cache_management.delete_many, "delete_many")
        spy_manager.attach_mock(
            mocked_cache_management.move_all_reserved_staging_keys_into_reserved_namespace,
            "move_all_reserved_staging_keys_into_reserved_namespace",
        )

        # When
        force_cache_refresh_for_reserved_namespace(
            cache_management=mocked_cache_management
        )

        # Then
        # Check that all operations are called in the correct order
        expected_calls = [
            mock.call.get_reserved_keys(),
            mock.call.crawl_all_pages(
                private_api_crawler=mocked_create_crawler_to_force_write_in_reserved_staging_namespace.return_value,
                area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
            ),
            mock.call.delete_many(keys=expected_original_reserved_keys),
            mock.call.move_all_reserved_staging_keys_into_reserved_namespace(),
        ]
        spy_manager.assert_has_calls(calls=expected_calls, any_order=False)

    @mock.patch(f"{MODULE_PATH}.AreaSelectorOrchestrator")
    @mock.patch(f"{MODULE_PATH}.crawl_all_pages")
    @mock.patch.object(
        PrivateAPICrawler, "create_crawler_to_force_write_in_reserved_staging_namespace"
    )
    def test_delegates_calls_successfully(
        self,
        spy_create_crawler_to_force_write_in_reserved_staging_namespace: mock.MagicMock,
        spy_crawl_all_pages: mock.MagicMock,
        spy_area_selector_orchestrator_class: mock.MagicMock,
    ):
        """
        Given no input
        When `force_cache_refresh_for_reserved_namespace()` is called
        Then the correct crawler is passed to `crawl_all_pages()`

        Patches:
            `spy_create_crawler_to_force_write_in_reserved_staging_namespace`: To assert
                that the correct crawler is initialized i.e. the one
                which can be used to forcibly refresh the reserved namespace cache
            `spy_crawl_all_pages`: For the main assertion
            `spy_area_selector_orchestrator_class`: To check the
                area selector orchestrator is passed to the
                `crawl_all_pages()` function
        """
        # Given
        mocked_cache_management = mock.Mock()

        # When
        force_cache_refresh_for_reserved_namespace(
            cache_management=mocked_cache_management
        )

        # Then
        spy_create_crawler_to_force_write_in_reserved_staging_namespace.assert_called_once()
        expected_crawler = (
            spy_create_crawler_to_force_write_in_reserved_staging_namespace.return_value
        )
        spy_crawl_all_pages.assert_called_once_with(
            private_api_crawler=expected_crawler,
            area_selector_orchestrator=spy_area_selector_orchestrator_class.return_value,
        )
        spy_area_selector_orchestrator_class.assert_called_once_with(
            geographies_api_crawler=expected_crawler.geography_api_crawler
        )


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
