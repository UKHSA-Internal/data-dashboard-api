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
    (
        "extreme_event",
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
    (
        "infectious_disease",
        "chemical_exposure",
        "Lead",
        "lead_headline_percentByDeprivationLatest",
        "headline",
    ),  # Invalid parent theme
    (
        "climate_and_environment",
        "seasonal_environmental",
        "heat-or-sunstroke",
        "heat-or-sunburn_syndromic_emergencyDepartment_averageRolling7Day",
        "syndromic",
    ),  # Invalid topic name
]
