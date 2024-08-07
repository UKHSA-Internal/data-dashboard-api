# Headline specific help text
PERIOD_START = """
Start of the period for which this figure is being provided.
"""
PERIOD_END = """
End of the period for which this figure is being provided.
"""
METRIC_HEADLINE: str = """
The name of the metric e.g. `COVID-19_headline_ONSdeaths_7daychange`
"""

# Common help texts
REFRESH_DATE = """
The date which this piece of data was last updated.
"""
EMBARGO = """
The point in time at which the data is released from embargo and made available.
"""
GEOGRAPHY: str = """
The name of the geography associated with the metric e.g. `London`
"""
STRATUM = """
Smallest subgroup a metric can be broken down into (e.g. ethnicity, testing pillar) excluding age and sex.
If a metric cannot be further broken down into strata, the value for stratum will be 'default'
"""
AGE = """
Age band of patients.
"""
SEX = """
Sex of patients.
"""

# Timeseries specific fields
IN_REPORTING_DELAY_PERIOD = """
Whether the record falls within the current reporting delay period. 
If true, then the value is subject to change in a subsequent retrospective update.
"""
