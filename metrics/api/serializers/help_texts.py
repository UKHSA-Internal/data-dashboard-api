TOPIC_FIELD: str = "The name of the topic being queried for. E.g. `COVID-19`"
METRIC_FIELD: str = "The name of the metric being queried for. E.g. `{}`"
STRATUM_FIELD: str = """
The smallest subgroup a metric can be broken down into. E.g. `0_4` for the age band 0 - 4 years old.
"""
GEOGRAPHY_FIELD: str = """
The geography constraints to apply any data filtering to.
E.g. `London`
"""
GEOGRAPHY_TYPE_FIELD: str = """
The type of geographical categorisation to apply any data filtering to.
E.g. `Nation`
"""
TREND_METRIC_NAME_FIELD: str = """
The name of the main change type metric being queried for. E.g. `new_cases_7days_change`
"""
TREND_METRIC_VALUE_FIELD: str = """
The associated value of the main change type metric which was queried for. E.g. `10`
"""

TREND_PERCENTAGE_METRIC_NAME_FIELD: str = """
The name of the percentage change type metric being queried for. E.g. `new_cases_7days_change_percentage`
"""
TREND_PERCENTAGE_METRIC_VALUE_FIELD: str = """
The associated value of the percentage change type metric being queried for. E.g. `3.2` would be considered as +3.2%
"""
DATE_FROM_FIELD: str = """
The date from which to begin analysing data from. 
If nothing is provided, a default of **1 year ago from the current date** will be applied.
"""
CHART_TYPE_FIELD: str = """The type of chart to create this individual plot with."""
DIRECTION_FIELD: str = """
The direction in which the trend is represented as. 
This can be one of the following `up`, `neutral` or `down`.
"""
COLOUR_FIELD: str = """
The colour in which the trend is represented as. 
This can be one of the following `green`, `neutral` or `red`.
"""
CHART_FILE_FORMAT_FIELD: str = """
The file format to render the chart in. 
This can be one of the following `svg`, `png`, `jpg` or `jpeg`.
"""
DOWNLOAD_FORMAT: str = """
The format you want the data downloaded in. 
This can be either `json` or `csv`
"""
