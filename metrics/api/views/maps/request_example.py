REQUEST_PAYLOAD_EXAMPLE = {
    "date_from": "2023-01-01",
    "date_to": "2023-12-31",
    "parameters": {
        "theme": "immunisation",
        "sub_theme": "childhood-vaccines",
        "topic": "6-in-1",
        "metric": "6-in-1_coverage_coverageByYear",
        "stratum": "12m",
        "age": "all",
        "sex": "all",
        "geography_type": "Upper Tier Local Authority",
        "geographies": [],
        # An empty `geographies` array means return all
        # geographies associated with the given `geography_type`
    },
    "accompanying_points": [
        {
            "label_prefix": "Country level of coverage: ",
            "label_suffix": "%",
            "parameters": {
                "geography_type": "Nation",
                # This configuration will extend the `parameters`
                # object and inject the corresponding related `Nation`
                # associated with each UTLA given above
            },
        },
        {
            "label_prefix": "Region level of coverage: ",
            "label_suffix": "%",
            "parameters": {
                "geography_type": "Region",
                # This configuration will extend the `parameters`
                # object and inject the corresponding related `Region`
                # associated with each UTLA given above
            },
        },
    ],
}
