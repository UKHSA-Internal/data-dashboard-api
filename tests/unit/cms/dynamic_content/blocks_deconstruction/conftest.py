import pytest

from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE


@pytest.fixture
def example_headline_cms_block(
    example_headline_number_block: dict[str, str],
) -> dict[str, str | dict[str, str]]:
    return {
        "type": "headline_number",
        "value": example_headline_number_block,
        "id": "eff08341-7bfa-4a3b-b013-527e7b954ce8",
    }


@pytest.fixture
def example_headline_number_row_cards():
    return [
        {
            "type": "headline_numbers_row_card",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "title": "Cases",
                            "rows": [
                                {
                                    "type": "headline_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_cases_7DayTotals",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "Weekly",
                                    },
                                    "id": "eff08341-7bfa-4a3b-b013-527e7b954ce8",
                                },
                                {
                                    "type": "trend_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_cases_7DayChange",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "7 days",
                                        "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                                    },
                                    "id": "a57a4ad5-6b52-45a6-acfd-2fe208cb5617",
                                },
                            ],
                        },
                        "id": "ff081d2a-e235-4bc2-9b09-220f8fe20494",
                    },
                    {
                        "type": "column",
                        "value": {
                            "title": "Testing",
                            "rows": [
                                {
                                    "type": "percentage_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_positivity_latest",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "Virus tests positivity",
                                    },
                                    "id": "36746bcd-1dce-4e5e-81f8-60c8b9994540",
                                }
                            ],
                        },
                        "id": "1e3bf214-88e4-4cf4-9b78-3ad7eabb2eaa",
                    },
                ]
            },
            "id": "e285caf4-ae79-4c76-bcb7-426d6e66cb8a",
        }
    ]


@pytest.fixture
def example_section_with_headline_card_and_chart_card() -> CMS_COMPONENT_BLOCK_TYPE:
    return {
        "type": "section",
        "value": {
            "heading": "COVID-19",
            "content": [
                {
                    "type": "headline_numbers_row_card",
                    "value": {
                        "columns": [
                            {
                                "type": "column",
                                "value": {
                                    "title": "Cases",
                                    "rows": [
                                        {
                                            "type": "headline_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_cases_7DayTotals",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "Weekly",
                                            },
                                            "id": "eff08341-7bfa-4a3b-b013-527e7b954ce8",
                                        }
                                    ],
                                },
                                "id": "ff081d2a-e235-4bc2-9b09-220f8fe20494",
                            },
                        ]
                    },
                    "id": "e285caf4-ae79-4c76-bcb7-426d6e66cb8a",
                },
                {
                    "type": "chart_row_card",
                    "value": {
                        "columns": [
                            {
                                "type": "chart_with_headline_and_trend_card",
                                "value": {
                                    "title": "Cases",
                                    "body": "Positive COVID-19 cases reported in England (7-day rolling average)",
                                    "x_axis": "",
                                    "y_axis": "",
                                    "chart": [
                                        {
                                            "type": "plot",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_cases_countRollingMean",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "chart_type": "line_with_shaded_section",
                                                "date_from": None,
                                                "date_to": None,
                                                "label": "",
                                                "line_colour": "",
                                                "line_type": "",
                                            },
                                            "id": "b0ead98b-4102-48f6-b94e-ff7bcffe1dc4",
                                        }
                                    ],
                                    "headline_number_columns": [
                                        {
                                            "type": "headline_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_cases_7DayTotals",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "7 days",
                                            },
                                            "id": "95b24a05-a015-42ed-b258-51c7ccaedbcd",
                                        },
                                    ],
                                },
                                "id": "d9b86415-9734-46be-952a-56182f0c40be",
                            },
                            {
                                "type": "chart_with_headline_and_trend_card",
                                "value": {
                                    "title": "Deaths",
                                    "body": "Deaths with COVID-19 on the death certificate in England (7-day rolling average)",
                                    "x_axis": "",
                                    "y_axis": "",
                                    "chart": [
                                        {
                                            "type": "plot",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_deaths_ONSRollingMean",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "chart_type": "line_with_shaded_section",
                                                "date_from": None,
                                                "date_to": None,
                                                "label": "",
                                                "line_colour": "",
                                                "line_type": "",
                                            },
                                            "id": "d3b521d8-a6bb-4960-9db9-864c3d362976",
                                        }
                                    ],
                                    "headline_number_columns": [],
                                },
                                "id": "c18703a1-9b01-417f-8fd8-3e4db35865e5",
                            },
                        ]
                    },
                    "id": "a5acbd6c-f9b7-4d36-86f4-005c2d46debc",
                },
            ],
        },
        "id": "1f53f495-e8d1-45a3-bd34-5d27878c20fc",
    }


@pytest.fixture
def example_section_with_headline_chart_and_text_cards() -> CMS_COMPONENT_BLOCK_TYPE:
    return {
        "type": "section",
        "value": {
            "heading": "COVID-19",
            "content": [
                {
                    "type": "text_card",
                    "value": {
                        "body": '<p data-block-key="6du8j">Summary of COVID-19 data. For more detailed data, go to the <a id="5" linktype="page">COVID-19 page</a>.</p>'
                    },
                    "id": "6a399089-6e24-4010-a484-a12745d38872",
                },
                {
                    "type": "headline_numbers_row_card",
                    "value": {
                        "columns": [
                            {
                                "type": "column",
                                "value": {
                                    "title": "Cases",
                                    "rows": [
                                        {
                                            "type": "headline_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_cases_7DayTotals",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "Weekly",
                                            },
                                            "id": "eff08341-7bfa-4a3b-b013-527e7b954ce8",
                                        },
                                        {
                                            "type": "trend_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_cases_7DayChange",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "7 days",
                                                "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                                            },
                                            "id": "a57a4ad5-6b52-45a6-acfd-2fe208cb5617",
                                        },
                                    ],
                                },
                                "id": "ff081d2a-e235-4bc2-9b09-220f8fe20494",
                            },
                            {
                                "type": "column",
                                "value": {
                                    "title": "Testing",
                                    "rows": [
                                        {
                                            "type": "percentage_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_positivity_latest",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "Virus tests positivity",
                                            },
                                            "id": "36746bcd-1dce-4e5e-81f8-60c8b9994540",
                                        }
                                    ],
                                },
                                "id": "1e3bf214-88e4-4cf4-9b78-3ad7eabb2eaa",
                            },
                        ]
                    },
                    "id": "e285caf4-ae79-4c76-bcb7-426d6e66cb8a",
                },
                {
                    "type": "chart_row_card",
                    "value": {
                        "columns": [
                            {
                                "type": "chart_with_headline_and_trend_card",
                                "value": {
                                    "title": "Cases",
                                    "body": "Positive COVID-19 cases reported in England (7-day rolling average)",
                                    "x_axis": "",
                                    "y_axis": "",
                                    "chart": [
                                        {
                                            "type": "plot",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_cases_countRollingMean",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "chart_type": "line_with_shaded_section",
                                                "date_from": None,
                                                "date_to": None,
                                                "label": "",
                                                "line_colour": "",
                                                "line_type": "",
                                            },
                                            "id": "b0ead98b-4102-48f6-b94e-ff7bcffe1dc4",
                                        }
                                    ],
                                    "headline_number_columns": [
                                        {
                                            "type": "headline_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_cases_7DayTotals",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "7 days",
                                            },
                                            "id": "95b24a05-a015-42ed-b258-51c7ccaedbcd",
                                        },
                                        {
                                            "type": "trend_number",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_headline_cases_7DayChange",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "body": "",
                                                "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                                            },
                                            "id": "8c42a86e-f675-41d0-a65a-633c20ac98e3",
                                        },
                                    ],
                                },
                                "id": "d9b86415-9734-46be-952a-56182f0c40be",
                            },
                            {
                                "type": "chart_with_headline_and_trend_card",
                                "value": {
                                    "title": "Deaths",
                                    "body": "Deaths with COVID-19 on the death certificate in England (7-day rolling average)",
                                    "x_axis": "",
                                    "y_axis": "",
                                    "chart": [
                                        {
                                            "type": "plot",
                                            "value": {
                                                "topic": "COVID-19",
                                                "metric": "COVID-19_deaths_ONSRollingMean",
                                                "geography": "England",
                                                "geography_type": "Nation",
                                                "sex": "all",
                                                "age": "all",
                                                "stratum": "default",
                                                "chart_type": "line_with_shaded_section",
                                                "date_from": None,
                                                "date_to": None,
                                                "label": "",
                                                "line_colour": "",
                                                "line_type": "",
                                            },
                                            "id": "d3b521d8-a6bb-4960-9db9-864c3d362976",
                                        }
                                    ],
                                    "headline_number_columns": [],
                                },
                                "id": "c18703a1-9b01-417f-8fd8-3e4db35865e5",
                            },
                        ]
                    },
                    "id": "a5acbd6c-f9b7-4d36-86f4-005c2d46debc",
                },
            ],
        },
        "id": "1f53f495-e8d1-45a3-bd34-5d27878c20fc",
    }


@pytest.fixture
def example_section_with_global_filter() -> CMS_COMPONENT_BLOCK_TYPE:
    return {
        "type": "section",
        "value": {
            "heading": "Filter childhood vaccination data",
            "content": [
                {
                    "type": "global_filter_card",
                    "value": {
                        "time_range": {
                            "title": "Year selection",
                            "time_periods": [
                                {
                                    "type": "time_period",
                                    "value": {
                                        "label": "2022-2023",
                                        "date_from": "2022-04-01",
                                        "date_to": "2023-03-31",
                                    },
                                    "id": "24fec754-d7e8-42f8-8c8b-7c191ada6e8d",
                                },
                                {
                                    "type": "time_period",
                                    "value": {
                                        "label": "2023-2024",
                                        "date_from": "2023-04-01",
                                        "date_to": "2024-03-31",
                                    },
                                    "id": "cbfb7958-bcb1-4036-881e-0a2fbec79db5",
                                },
                                {
                                    "type": "time_period",
                                    "value": {
                                        "label": "2024-2025",
                                        "date_from": "2024-04-01",
                                        "date_to": "2025-03-31",
                                    },
                                    "id": "72ab2c6a-5116-42b9-9f15-25aacd12c467",
                                },
                            ],
                        },
                        "rows": [
                            {
                                "type": "row",
                                "value": {
                                    "title": "Area",
                                    "filters": [
                                        {
                                            "type": "geography_filters",
                                            "value": {
                                                "geography_types": [
                                                    {
                                                        "type": "geography_filter",
                                                        "value": {
                                                            "label": "Country",
                                                            "colour": "COLOUR_1_DARK_BLUE",
                                                            "geography_type": "Nation",
                                                        },
                                                        "id": "5ed27d55-ffaa-4a8d-8b93-8f20d186265d",
                                                    },
                                                    {
                                                        "type": "geography_filter",
                                                        "value": {
                                                            "label": "Region",
                                                            "colour": "COLOUR_2_TURQUOISE",
                                                            "geography_type": "Lower Tier Local Authority",
                                                        },
                                                        "id": "87c30c92-c9bd-46cd-89eb-6468e46e7b5b",
                                                    },
                                                    {
                                                        "type": "geography_filter",
                                                        "value": {
                                                            "label": "Local Authority",
                                                            "colour": "COLOUR_3_DARK_PINK",
                                                            "geography_type": "Upper Tier Local Authority",
                                                        },
                                                        "id": "b531fee6-149d-429d-8de6-90bf27f4f9e6",
                                                    },
                                                ]
                                            },
                                            "id": "2cb36d1b-6f38-4a92-bc8d-d54fa22fbdf2",
                                        }
                                    ],
                                },
                                "id": "64c0fc3f-f2db-48a5-b8cf-9ee43c31b11e",
                            },
                            {
                                "type": "row",
                                "value": {
                                    "title": "Vaccination and coverage",
                                    "filters": [
                                        {
                                            "type": "data_filters",
                                            "value": {
                                                "label": "Select vaccination",
                                                "data_filters": [
                                                    {
                                                        "type": "data_filter",
                                                        "value": {
                                                            "label": "MMR1 (2 years)",
                                                            "colour": "COLOUR_1_DARK_BLUE",
                                                            "parameters": {
                                                                "theme": {
                                                                    "label": "",
                                                                    "value": "immunisation",
                                                                },
                                                                "sub_theme": {
                                                                    "label": "",
                                                                    "value": "childhood-vaccines",
                                                                },
                                                                "topic": {
                                                                    "label": "",
                                                                    "value": "MMR1",
                                                                },
                                                                "stratum": {
                                                                    "label": "2 years",
                                                                    "value": "24m",
                                                                },
                                                                "metric": {
                                                                    "label": "",
                                                                    "value": "MMR1_coverage_coverageByYear",
                                                                },
                                                                "age": {
                                                                    "label": "",
                                                                    "value": "all",
                                                                },
                                                                "sex": {
                                                                    "label": "",
                                                                    "value": "all",
                                                                },
                                                            },
                                                            "accompanying_points": [
                                                                {
                                                                    "type": "accompanying_point",
                                                                    "value": {
                                                                        "label_prefix": "Country level of coverage",
                                                                        "label_suffix": "%",
                                                                        "parameters": [],
                                                                    },
                                                                    "id": "ab8e4f2f-d62b-411c-adff-8a9bb0aa8ac7",
                                                                }
                                                            ],
                                                        },
                                                        "id": "119e270f-2759-44a0-969a-1651407a109a",
                                                    },
                                                    {
                                                        "type": "data_filter",
                                                        "value": {
                                                            "label": "MMR1 (5 years)",
                                                            "colour": "COLOUR_2_TURQUOISE",
                                                            "parameters": {
                                                                "theme": {
                                                                    "label": "",
                                                                    "value": "immunisation",
                                                                },
                                                                "sub_theme": {
                                                                    "label": "",
                                                                    "value": "childhood-vaccines",
                                                                },
                                                                "topic": {
                                                                    "label": "",
                                                                    "value": "MMR1",
                                                                },
                                                                "stratum": {
                                                                    "label": "5 years",
                                                                    "value": "5y",
                                                                },
                                                                "metric": {
                                                                    "label": "",
                                                                    "value": "MMR1_coverage_coverageByYear",
                                                                },
                                                                "age": {
                                                                    "label": "",
                                                                    "value": "all",
                                                                },
                                                                "sex": {
                                                                    "label": "",
                                                                    "value": "all",
                                                                },
                                                            },
                                                            "accompanying_points": [
                                                                {
                                                                    "type": "accompanying_point",
                                                                    "value": {
                                                                        "label_prefix": "Country level of coverage",
                                                                        "label_suffix": "%",
                                                                        "parameters": [],
                                                                    },
                                                                    "id": "2bc2d44e-7425-4ce8-a703-e6269936ec39",
                                                                }
                                                            ],
                                                        },
                                                        "id": "01627419-571a-4ea7-ba9a-c77cf354d582",
                                                    },
                                                ],
                                                "categories_to_group_by": [
                                                    {
                                                        "type": "category",
                                                        "value": {
                                                            "data_category": "stratum"
                                                        },
                                                        "id": "85acdaf0-540c-49e2-9210-7e6370c574eb",
                                                    },
                                                    {
                                                        "type": "category",
                                                        "value": {
                                                            "data_category": "topic"
                                                        },
                                                        "id": "76fcdb38-db17-4580-8bf0-48bca2881b4a",
                                                    },
                                                ],
                                            },
                                            "id": "8c0e75e3-4399-45f8-b9f2-944ce631960e",
                                        },
                                        {
                                            "type": "threshold_filters",
                                            "value": {
                                                "thresholds": [
                                                    {
                                                        "type": "threshold",
                                                        "value": {
                                                            "label": "Under 80%",
                                                            "colour": "COLOUR_1_DARK_BLUE",
                                                            "boundary_minimum_value": "0",
                                                            "boundary_maximum_value": "80",
                                                        },
                                                        "id": "9019a648-901c-4801-9d3e-d3b95242a58e",
                                                    },
                                                    {
                                                        "type": "threshold",
                                                        "value": {
                                                            "label": "80-85%",
                                                            "colour": "COLOUR_2_TURQUOISE",
                                                            "boundary_minimum_value": "81",
                                                            "boundary_maximum_value": "85",
                                                        },
                                                        "id": "9137b412-ef3a-4d39-8662-1096ba1c3b99",
                                                    },
                                                    {
                                                        "type": "threshold",
                                                        "value": {
                                                            "label": "85-90%",
                                                            "colour": "COLOUR_3_DARK_PINK",
                                                            "boundary_minimum_value": "86",
                                                            "boundary_maximum_value": "90",
                                                        },
                                                        "id": "38cd3f76-46ed-41d9-a7a2-9a41510c0b2d",
                                                    },
                                                    {
                                                        "type": "threshold",
                                                        "value": {
                                                            "label": "90-95%",
                                                            "colour": "COLOUR_4_ORANGE",
                                                            "boundary_minimum_value": "91",
                                                            "boundary_maximum_value": "95",
                                                        },
                                                        "id": "3584882d-ce37-4d57-abcb-ac0d71133dc5",
                                                    },
                                                    {
                                                        "type": "threshold",
                                                        "value": {
                                                            "label": "Over 95%",
                                                            "colour": "COLOUR_5_DARK_GREY",
                                                            "boundary_minimum_value": "96",
                                                            "boundary_maximum_value": "100",
                                                        },
                                                        "id": "d8583ba3-259f-49f0-be86-eaa670198c25",
                                                    },
                                                ]
                                            },
                                            "id": "b029909f-588d-4a13-90db-7e08e7e20f3d",
                                        },
                                    ],
                                },
                                "id": "854569f8-0cd0-4fbf-bf21-b8eadeb613cb",
                            },
                        ],
                    },
                    "id": "da1c5477-4e98-4686-8fa2-2af05d50a701",
                }
            ],
        },
        "id": "364790e5-adca-408c-a76e-ecfdbe485b58",
    }


@pytest.fixture
def example_chart_blocks() -> list[CMS_COMPONENT_BLOCK_TYPE]:
    return [
        {
            "title": "Cases",
            "body": "Positive COVID-19 cases reported in England (7-day rolling average)",
            "x_axis": "",
            "y_axis": "",
            "chart": [
                {
                    "type": "plot",
                    "value": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_cases_countRollingMean",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "chart_type": "line_with_shaded_section",
                        "date_from": None,
                        "date_to": None,
                        "label": "",
                        "line_colour": "",
                        "line_type": "",
                    },
                    "id": "b0ead98b-4102-48f6-b94e-ff7bcffe1dc4",
                }
            ],
            "headline_number_columns": [
                {
                    "type": "headline_number",
                    "value": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_headline_cases_7DayTotals",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "body": "7 days",
                    },
                    "id": "95b24a05-a015-42ed-b258-51c7ccaedbcd",
                },
                {
                    "type": "trend_number",
                    "value": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_headline_cases_7DayChange",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "body": "",
                        "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                    },
                    "id": "8c42a86e-f675-41d0-a65a-633c20ac98e3",
                },
            ],
        },
        {
            "title": "Deaths",
            "body": "Deaths with COVID-19 on the death certificate in England (7-day rolling average)",
            "x_axis": "",
            "y_axis": "",
            "chart": [
                {
                    "type": "plot",
                    "value": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_deaths_ONSRollingMean",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "chart_type": "line_with_shaded_section",
                        "date_from": None,
                        "date_to": None,
                        "label": "",
                        "line_colour": "",
                        "line_type": "",
                    },
                    "id": "d3b521d8-a6bb-4960-9db9-864c3d362976",
                }
            ],
            "headline_number_columns": [
                {
                    "type": "headline_number",
                    "value": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "body": "7 days",
                    },
                    "id": "10c92d4c-bdb1-4bcc-a8a5-d0063dcee095",
                },
                {
                    "type": "trend_number",
                    "value": {
                        "topic": "COVID-19",
                        "metric": "COVID-19_headline_ONSdeaths_7DayChange",
                        "geography": "England",
                        "geography_type": "Nation",
                        "sex": "all",
                        "age": "all",
                        "stratum": "default",
                        "body": "",
                        "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
                    },
                    "id": "41ce6c59-99fe-486a-8225-341a306cc395",
                },
            ],
        },
    ]


@pytest.fixture
def example_chart_row_cards():
    return [
        {
            "type": "chart_row_card",
            "value": {
                "columns": [
                    {
                        "type": "chart_with_headline_and_trend_card",
                        "value": {
                            "title": "Cases",
                            "body": "Positive COVID-19 cases reported in England (7-day rolling average)",
                            "x_axis": "",
                            "y_axis": "",
                            "chart": [
                                {
                                    "type": "plot",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_cases_countRollingMean",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "chart_type": "line_with_shaded_section",
                                        "date_from": None,
                                        "date_to": None,
                                        "label": "",
                                        "line_colour": "",
                                        "line_type": "",
                                    },
                                    "id": "b0ead98b-4102-48f6-b94e-ff7bcffe1dc4",
                                }
                            ],
                            "headline_number_columns": [
                                {
                                    "type": "headline_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_cases_7DayTotals",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "7 days",
                                    },
                                    "id": "95b24a05-a015-42ed-b258-51c7ccaedbcd",
                                },
                                {
                                    "type": "trend_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_cases_7DayChange",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "",
                                        "percentage_metric": "COVID-19_headline_cases_7DayPercentChange",
                                    },
                                    "id": "8c42a86e-f675-41d0-a65a-633c20ac98e3",
                                },
                            ],
                        },
                        "id": "d9b86415-9734-46be-952a-56182f0c40be",
                    },
                    {
                        "type": "chart_with_headline_and_trend_card",
                        "value": {
                            "title": "Deaths",
                            "body": "Deaths with COVID-19 on the death certificate in England (7-day rolling average)",
                            "x_axis": "",
                            "y_axis": "",
                            "chart": [
                                {
                                    "type": "plot",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_deaths_ONSRollingMean",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "chart_type": "line_with_shaded_section",
                                        "date_from": None,
                                        "date_to": None,
                                        "label": "",
                                        "line_colour": "",
                                        "line_type": "",
                                    },
                                    "id": "d3b521d8-a6bb-4960-9db9-864c3d362976",
                                }
                            ],
                            "headline_number_columns": [
                                {
                                    "type": "headline_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_ONSdeaths_7DayTotals",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "7 days",
                                    },
                                    "id": "10c92d4c-bdb1-4bcc-a8a5-d0063dcee095",
                                },
                                {
                                    "type": "trend_number",
                                    "value": {
                                        "topic": "COVID-19",
                                        "metric": "COVID-19_headline_ONSdeaths_7DayChange",
                                        "geography": "England",
                                        "geography_type": "Nation",
                                        "sex": "all",
                                        "age": "all",
                                        "stratum": "default",
                                        "body": "",
                                        "percentage_metric": "COVID-19_headline_ONSdeaths_7DayPercentChange",
                                    },
                                    "id": "41ce6c59-99fe-486a-8225-341a306cc395",
                                },
                            ],
                        },
                        "id": "c18703a1-9b01-417f-8fd8-3e4db35865e5",
                    },
                ]
            },
            "id": "a5acbd6c-f9b7-4d36-86f4-005c2d46debc",
        }
    ]
