REQUEST_PAYLOAD_EXAMPLE = {
    "file_format": "svg",
    "chart_height": 300,
    "chart_width": 900,
    "x_axis_title": "Coverage %",
    "y_axis_title": "Vaccination type",
    "y_axis_minimum_value": None,
    "y_axis_maximum_value": None,
    "target_threshold": 95,
    "target_threshold_label": "95% target",
    "chart_parameters": {
        "x_axis": "geography",
        "y_axis": "metric",
        "theme": "immunisation",
        "sub_theme": "childhood-vaccines",
        "date_from": "2021-01-31",
        "date_to": "2021-12-31",
        "age": "all",
        "sex": "all",
        "stratum": "default"
    },
    "subplots": [
        {
            "subplot_title": "6-in-1 (12 months)",
            "subplot_parameters": {
                "topic": "6-in-1",
                "metric": "6-in-1_coverage_coverageByYear",
                "stratum": "12m"
            },
            "plots": [
                {
                    "label": "England",
                    "geography": "England",
                    "geography_type": "Nation",
                    "line_colour": "COLOUR_1_DARK_BLUE"
                },
                {
                    "label": "North East",
                    "geography": "North East",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_2_TURQUOISE"
                },
                {
                    "label": "Darlington",
                    "geography": "Darlington",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_3_DARK_PINK"
                }
            ]
        },
        {
            "subplot_title": "6-in-1 (24 months)",
            "subplot_parameters": {
                "topic": "6-in-1",
                "metric": "6-in-1_coverage_coverageByYear",
                "stratum": "24m"
            },
            "plots": [
                {
                    "label": "England",
                    "geography": "England",
                    "geography_type": "Nation",
                    "line_colour": "COLOUR_1_DARK_BLUE"
                },
                {
                    "label": "North East",
                    "geography": "North East",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_2_TURQUOISE"
                },
                {
                    "label": "Darlington",
                    "geography": "Darlington",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_3_DARK_PINK"
                }
            ]
        },
        {
            "subplot_title": "MMR1 (24 months)",
            "subplot_parameters": {
                "topic": "MMR1",
                "metric": "MMR1_coverage_coverageByYear",
                "stratum": "24m"
            },
            "plots": [
                {
                    "label": "England",
                    "geography": "England",
                    "geography_type": "Nation",
                    "line_colour": "COLOUR_1_DARK_BLUE"
                },
                {
                    "label": "North East",
                    "geography": "North East",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_2_TURQUOISE"
                },
                {
                    "label": "Darlington",
                    "geography": "Darlington",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_3_DARK_PINK"
                }
            ]
        },
        {
            "subplot_title": "MMR1 (5 years)",
            "subplot_parameters": {
                "topic": "MMR1",
                "metric": "MMR1_coverage_coverageByYear",
                "stratum": "5y"
            },
            "plots": [
                {
                    "label": "England",
                    "geography": "England",
                    "geography_type": "Nation",
                    "line_colour": "COLOUR_1_DARK_BLUE"
                },
                {
                    "label": "North East",
                    "geography": "North East",
                    "geography_type": "Region",
                    "line_colour": "COLOUR_2_TURQUOISE"
                },
                {
                    "label": "Darlington",
                    "geography": "Darlington",
                    "geography_type": "Upper Tier Local Authority",
                    "line_colour": "COLOUR_3_DARK_PINK"
                }
            ]
        }
    ]
}
