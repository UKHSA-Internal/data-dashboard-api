from unittest import mock

import pytest

from caching.private_api.crawler import PrivateAPICrawler
from caching.private_api.crawler.dynamic_block_crawler import DynamicContentBlockCrawler


@pytest.fixture
def dynamic_content_block_crawler_with_mocked_internal_api_client() -> (
    DynamicContentBlockCrawler
):
    return DynamicContentBlockCrawler(internal_api_client=mock.Mock())


@pytest.fixture
def private_api_crawler_with_mocked_internal_api_client() -> PrivateAPICrawler:
    return PrivateAPICrawler(internal_api_client=mock.MagicMock())


@pytest.fixture
def example_dummy_chart_row_cards() -> list[dict[str, str | list[dict]]]:
    return [
        {
            "type": "chart_row_card",
            "value": {
                "columns": [
                    {
                        "type": "chart_card",
                        "value": "",
                    },
                    {
                        "type": "chart_card",
                        "value": "",
                    },
                ]
            },
        }
    ]


@pytest.fixture
def example_chart_row_column() -> list[dict[str, str | list[dict]]]:
    return [
        {
            "type": "chart_card",
            "value": {"title": "title text one", "body": "body text one", "chart": []},
        },
        {
            "type": "chart_card",
            "value": {"title": "title text two", "body": "body text two", "chart": []},
        },
    ]
