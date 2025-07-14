REQUEST_PAYLOAD_EXAMPLE = {
    "date_from": "2023-10-30",
    "date_to": "2023-10-31",
    "parameters": {
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
        "metric": "COVID-19_deaths_ONSByWeek",
        "stratum": "default",
        "age": "all",
        "sex": "all",
        "geography_type": "Lower Tier Local Authority",
        "geographies": [],
        # An empty `geographies` array means return all
        # geographies associated with the given `geography_type`
    },
    "accompanying_points": [
        {
            "label_prefix": "Rate of cases in England: ",
            "label_suffix": "",
            "parameters": {
                "metric": "COVID-19_cases_rateRollingMean",
                "geography_type": "Nation",
                "geography": "England",
            },
        }
    ],
}
