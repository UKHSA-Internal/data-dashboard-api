REQUEST_PAYLOAD_EXAMPLE = {
    "file_format": "svg",
    "chart_height": 300,
    "chart_width": 900,
    "x_axis_title": "coverage %",
    "y_axis_title": "vaccination type",
    "y_axis_minimum_value": None,
    "y_axis_maximum_value": None,
    "chart_parameters": {
        "x_axis": "geography",
        "y_axis": "metric",
        "theme": "immunisation",
        "sub_theme": "childhood-vaccines",
        "date_from": "2021-01-31",
        "date_to": "2021-12-31",
        "age": "all",
        "sex": "all",
        "stratum": "test",
    },
    "subplots": [
        {
            "subplot_title": "MMR1 (UTLA)",
            "subplot_parameters": {
                "topic": "MMR1",
                "metric": "MMR1_coverage_coverageByYear",
                "stratum": "24m",
            },
            "plots": [
                {
                    "label": "Country",
                    "geography": "Darlington",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_1_DARK_BLUE",
                    "stratum": "24m",
                },
                {
                    "label": "Region",
                    "geography": "Hartlepool",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_2_TURQUOISE",
                    "stratum": "24m",
                },
                {
                    "label": "Local Authority",
                    "geography": "Stockton-on-Tees",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_3_DARK_PINK",
                    "stratum": "24m",
                },
            ],
        },
        {
            "subplot_title": "MMR1 (Region)",
            "subplot_parameters": {
                "topic": "MMR1",
                "metric": "MMR1_coverage_coverageByYear",
                "stratum": "24m",
            },
            "plots": [
                {
                    "label": "Country",
                    "geography": "North West",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_1_DARK_BLUE",
                    "stratum": "24m",
                },
                {
                    "label": "Region",
                    "geography": "West Midlands",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_2_TURQUOISE",
                    "stratum": "24m",
                },
                {
                    "label": "Local Authority",
                    "geography": "London",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_3_DARK_PINK",
                    "stratum": "24m",
                },
            ],
        },
    ],
}
