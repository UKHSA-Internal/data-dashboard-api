from unittest import mock

from caching.private_api.crawler.dynamic_block_crawler import DynamicContentBlockCrawler


class TestProcessAllBlocks:
    @mock.patch.object(DynamicContentBlockCrawler, "process_any_headline_number_block")
    def test_process_all_headline_number_blocks_delegates_call(
        self, spy_process_any_headline_number_block: mock.MagicMock
    ):
        """
        Given a list of mocked headline number blocks
        When `process_all_headline_number_blocks()` is called
            from an instance of the `DynamicContentBlockCrawler`
        Then the call is delegated to
            the `process_any_headline_number_block()` method

        Patches:
            spy_process_any_headline_number_block: For the main assertion

        """
        # Given
        mocked_headline_number_blocks = [mock.Mock()] * 3
        dynamic_content_block_crawler = DynamicContentBlockCrawler(
            internal_api_client=mock.Mock()
        )

        # When
        dynamic_content_block_crawler.process_all_headline_number_blocks(
            headline_number_blocks=mocked_headline_number_blocks
        )

        # Then
        expected_calls = [
            mock.call(headline_number_block=x) for x in mocked_headline_number_blocks
        ]
        spy_process_any_headline_number_block.assert_has_calls(
            calls=expected_calls, any_order=True
        )

    @mock.patch.object(DynamicContentBlockCrawler, "process_chart_block")
    def test_process_all_chart_blocks_delegates_call(
        self, spy_process_chart_block: mock.MagicMock
    ):
        """
        Given a list of mocked chart blocks
        When `process_all_chart_blocks()` is called
            from an instance of the `DynamicContentBlockCrawler`
        Then the call is delegated to
            the `process_chart_block()` method

        Patches:
            spy_process_chart_block: For the main assertion

        """
        # Given
        mocked_chart_blocks = [mock.Mock()] * 3
        dynamic_content_block_crawler = DynamicContentBlockCrawler(
            internal_api_client=mock.Mock()
        )

        # When
        dynamic_content_block_crawler.process_all_chart_blocks(
            chart_blocks=mocked_chart_blocks
        )

        # Then
        expected_calls = [mock.call(chart_block=x) for x in mocked_chart_blocks]
        spy_process_chart_block.assert_has_calls(calls=expected_calls, any_order=True)

    @mock.patch.object(DynamicContentBlockCrawler, "process_global_filter")
    def test_process_all_global_filters_delegates_call(
        self, spy_process_global_filter: mock.MagicMock
    ):
        """
        Given a list of mocked chart blocks
        When `process_all_global_filters()` is called
            from an instance of the `DynamicContentBlockCrawler`
        Then the call is delegated to
            the `process_global_filter()` method

        Patches:
            spy_process_global_filter: For the main assertion

        """
        # Given
        mocked_global_filters = [mock.Mock()] * 3
        dynamic_content_block_crawler = DynamicContentBlockCrawler(
            internal_api_client=mock.Mock()
        )

        # When
        dynamic_content_block_crawler.process_all_global_filters(
            global_filters=mocked_global_filters
        )

        # Then
        expected_calls = [mock.call(global_filter=x) for x in mocked_global_filters]
        spy_process_global_filter.assert_has_calls(calls=expected_calls, any_order=True)
