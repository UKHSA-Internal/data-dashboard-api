from unittest import mock

import pytest

from caching.private_api.crawler import PrivateAPICrawler


@pytest.fixture
def private_api_crawler_with_mocked_internal_api_client() -> PrivateAPICrawler:
    return PrivateAPICrawler(internal_api_client=mock.Mock())


@pytest.fixture
def example_headline_number_block() -> dict[str, str]:
    return {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
        "geography": "Croydon",
        "geography_type": "Upper Tier Local Authority",
        "sex": "all",
        "age": "all",
        "stratum": "default",
        "body": "Last 7 days",
    }


@pytest.fixture
def example_trend_number_block() -> dict[str, str]:
    return {
        "topic": "COVID-19",
        "metric": "COVID-19_headline_ONSdeaths_7DayChange",
        "body": "Last 7 days",
        "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
    }


@pytest.fixture
def example_chart_block() -> dict[str, str | list[dict]]:
    return {
        "title": "Admissions rate by age",
        "body": "Age breakdown of people admitted to hospital.",
        "x_axis": "stratum",
        "y_axis": "metric",
        "chart": [
            {
                "type": "plot",
                "value": {
                    "topic": "COVID-19",
                    "metric": "COVID-19_healthcare_admissionByDay",
                    "chart_type": "bar",
                    "date_from": None,
                    "date_to": None,
                    "stratum": "",
                    "geography": "England",
                    "geography_type": "Nation",
                    "sex": "",
                    "age": "",
                    "label": "Admission rate",
                    "line_colour": "",
                    "line_type": "",
                },
                "id": "791efbf1-8880-4dfa-9f5d-526982ed1539",
            }
        ],
    }


@pytest.fixture
def example_chart_row_cards() -> dict[str, str | list[dict]]:
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
def example_chart_row_column() -> dict[str, str | list[dict]]:
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
