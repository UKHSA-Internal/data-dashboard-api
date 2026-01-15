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
    (
        "infectious_disease",
        "chemical_exposure",
        "mpox-clade-2b",
        "mpox-clade-2b_cases_countByMonth",
        "cases",
    ),  # Invalid child_theme
    (
        "infectious_disease",
        "bloodborne",
        "Hepatitis-C",
        "hepatitis-b_vaccinations_coverageOf3DosesTargetWHO",
        "vaccinations",
    ),  # Invalid topic of `Hepatitis-C` instead of `Hepatitis-B`
    (
        "climate_and_environment",
        "respiratory",
        "Scarlet-fever",
        "impact-of-cold",
        "impact-of-cold_syndromic_emergencyDepartment_averageRolling7Day",
        "syndromic",
    ),  # Invalid child_theme
    (
        "infectious_disease",
        "antimicrobial_resistance",
        "carbapenamase-producing-organisms",
        "carbapenamase-producing-organisms_cases_allSitesRateByMonth",
        "syndromic",
    ), # Invalid metric group
]
