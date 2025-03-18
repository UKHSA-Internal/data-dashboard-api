INVALID_PARAMETERS = [
    (
        "extreme_event",
        "respiratory",
        "COVID-19",
        "COVID-19_deaths_ONSByWeek",
        "deaths",
    ),  # Invalid metric group
    (
        "infectious_disease",
        "vectors",
        "ticks",
        "ticks_counts_countByYear",
        "counts",
    ),  # Invalid parent theme
    (
        "extreme_event",
        "invasive_bacterial_infections",
        "iGAS",
        "iGAS_cases_rateByMonth",
        "cases",
    ),  # Invalid parent theme
    (
        "infectious_disease",
        "respiratory",
        "Scarlet-fever",
        "scarlet-fever_syndromic_consultationRateByWeek",
        "syndromic",
    ),  # Invalid child theme
    (
        "infectious_disease",
        "bloodborne",
        "Scarlet-fever",
        "hepatitis-c_cases_prevalenceByYearEstimate",
        "prevention",
    ),  # Invalid child Topic
]
