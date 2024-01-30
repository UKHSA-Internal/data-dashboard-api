from unittest import mock

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.area_selector.orchestration import (
    AreaSelectorOrchestrator,
)
from caching.private_api.crawler.geographies_crawler import (
    GeographyData,
    GeographyTypeData,
)
from cms.topic.models import TopicPage

MODULE_PATH = "caching.private_api.crawler.area_selector.orchestration"


class TestAreaSelectorOrchestrator:
    @mock.patch.object(
        AreaSelectorOrchestrator, "parallel_process_all_geography_combinations_for_page"
    )
    @mock.patch.object(AreaSelectorOrchestrator, "get_geography_combinations_for_page")
    def test_process_pages(
        self,
        mocked_get_geography_combinations_for_page: mock.MagicMock,
        spy_parallel_process_all_geography_combinations_for_page: mock.MagicMock,
    ):
        """
        Given a list of mocked `Page` instances
        And a list of enriched `GeographyData` models
        When `process_pages()` is called
            from an instance of the `AreaSelectorOrchestrator`
        Then the `parallel_process_all_geography_combinations_for_page()`
            method is called with the correct args

        Patches:
            `mocked_get_geography_combinations_for_page`: To patch the enriched
                `GeographyData` models into place without having to hit
                the geographies API
            `spy_parallel_process_all_geography_combinations_for_page`: For the
                main assertion of checking the page and geography combos
                are provided

        """
        # Given
        mocked_pages = [mock.Mock()] * 3
        geography_combinations = [
            GeographyData(name="England", geography_type_name="Nation"),
            GeographyData(
                name="City of London", geography_type_name="Lower Tier Local Authority"
            ),
        ]
        mocked_get_geography_combinations_for_page.return_value = geography_combinations
        area_selector_orchestrator = AreaSelectorOrchestrator(
            geographies_api_crawler=mock.Mock()
        )

        # When
        area_selector_orchestrator.process_pages(pages=mocked_pages)

        # Then
        expected_calls = [
            mock.call(page=mocked_page, geography_combinations=geography_combinations)
            for mocked_page in mocked_pages
        ]
        spy_parallel_process_all_geography_combinations_for_page.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch(f"{MODULE_PATH}.call_with_star_map_multiprocessing")
    def test_parallel_process_all_geography_combinations_for_page_delegates_call(
        self, spy_call_with_star_map_multiprocessing: mock.MagicMock
    ):
        """
        Given an iterable of enriched `GeographyData` models
        And a mocked `Page` model of a specific ID
        When `parallel_process_all_geography_combinations_for_page()` is called
            from the `AreaSelectorOrchestrator` class
        Then the call is delegated to `call_with_star_map_multiprocessing()`
            with the correct arguments

        Patches:
            `spy_call_with_star_map_multiprocessing`: For the main assertion
                of checking the parallel processing is kicked off
                for the geography/page combinations

        """
        # Given
        geography_data_combinations = [
            GeographyData(
                name="Croydon", geography_type_name="Lower Tier Local Authority"
            ),
            GeographyData(name="England", geography_type_name="Nation"),
        ]
        page_id = 123
        mocked_page = mock.Mock(id=page_id)

        # When
        AreaSelectorOrchestrator.parallel_process_all_geography_combinations_for_page(
            geography_combinations=geography_data_combinations, page=mocked_page
        )

        # Then
        zipped_args = [
            (geography_data, page_id) for geography_data in geography_data_combinations
        ]
        spy_call_with_star_map_multiprocessing.assert_called_once_with(
            func=AreaSelectorOrchestrator.process_geography_page_combination,
            items=zipped_args,
        )

    @mock.patch.object(TopicPage, "objects")
    @mock.patch.object(PrivateAPICrawler, "create_crawler_for_force_cache_refresh")
    def test_process_geography_page_combination(
        self,
        mocked_create_crawler_for_force_cache_refresh: mock.MagicMock,
        spy_topic_page_manager: mock.MagicMock,
    ):
        """
        Given an ID of a `Page` and an enriched `GeographyData` model
        When `process_geography_page_combination()` is called
            from the `AreaSelectorOrchestrator` class
        Then the `Page` model is retrieved and passed to
            the `process_all_sections_in_page`
            from a `PrivateAPICrawler` instance
            along with the `GeographyData` model

        Patches:
            `spy_topic_page_manager`: To check the page ID
                is used to retrieve the `TopicPage` model
            `mocked_create_crawler_for_force_cache_refresh`: To
                isolate the `PrivateAPICrawler` so that the
                returned mock object can be spied on further
                i.e. to check the main `process_all_sections_in_page()` call

        """
        # Given
        page_id = 1
        geography_data = GeographyData(
            name="Croydon", geography_type_name="Lower Tier Local Authority"
        )

        # When
        AreaSelectorOrchestrator.process_geography_page_combination(
            geography_data=geography_data, page_id=page_id
        )

        # Then
        spy_topic_page_manager.get.assert_called_once_with(id=page_id)
        page_model = spy_topic_page_manager.get.return_value

        spy_private_api_crawler = (
            mocked_create_crawler_for_force_cache_refresh.return_value
        )
        spy_private_api_crawler.process_all_sections_in_page(
            page=page_model, geography_data=geography_data
        )

    def test_get_geography_combinations_for_page(self):
        """
        Given a topic and mocked return `GeographyTypeData` models
        When `get_geography_combinations_for_page()` is called
            from an instance of the `AreaSelectorOrchestrator`
        Then the correct list of `GeographyData` models are returned
        """
        # Given
        ltha = "Lower Tier Local Authority"
        spy_geographies_api_crawler = mock.Mock()
        geography_type_data_models = [
            GeographyTypeData(
                name=ltha, geography_names=["Bexley", "Hackney", "Tower Hamlets"]
            )
        ]
        spy_geographies_api_crawler.hit_list_endpoint_for_topic.return_value = (
            geography_type_data_models
        )

        topic = "COVID-19"
        mocked_page = mock.Mock(selected_topics={topic})
        area_selector_orchestrator = AreaSelectorOrchestrator(
            geographies_api_crawler=spy_geographies_api_crawler
        )

        # When
        geography_combinations: list[GeographyData] = (
            area_selector_orchestrator.get_geography_combinations_for_page(
                page=mocked_page
            )
        )

        # Then
        # Check the `GeographiesAPICrawler` is used correctly to
        # fetch the correct geographies for the given topic
        spy_geographies_api_crawler.hit_list_endpoint_for_topic.assert_called_once_with(
            topic=topic
        )

        # Check the returned `GeographyData` models are correct
        assert len(geography_combinations) == 3
        assert geography_combinations[0].geography_type_name
        assert geography_combinations[0].name == "Bexley"

        assert geography_combinations[1].geography_type_name
        assert geography_combinations[1].name == "Hackney"

        assert geography_combinations[2].geography_type_name
        assert geography_combinations[2].name == "Tower Hamlets"
