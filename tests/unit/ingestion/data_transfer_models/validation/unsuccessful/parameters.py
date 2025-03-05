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
        "respiratory",
        "lower-respiratory-tract-infection",
        "upper-respiratory-tract-infection_syndromic_GPInHours_rateByDay",
        "syndromic",
    ),  # Invalid topic <-> metric combination
    (
        "extreme_event",
        "contact",
        "mpox-clade-1b",
        "mpox-clade-1b_cases_countByWeek",
        "cases",
    ),  # Invalid theme
]
