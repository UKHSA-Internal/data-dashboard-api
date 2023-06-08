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
LABEL_FIELD: str = """
The label to assign on the legend for this individual plot.
E.g. `15 to 44 years old`
"""
HEADLINE_METRIC_VALUE_FIELD_HELP_TEXT: str = """
The associated value of the headline metric which was queried for. E.g. `new_cases_7days_change`
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
DATE_TO_FIELD: str = """
The date to which to end analysing the data to. 
If nothing is provided, a default of **the current date** will be applied.
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
FILE_DOWNLOAD_FORMAT: str = """
The format you want the data downloaded in. 
This can be either `json` or `csv`
"""
CHARTS_RESPONSE_HELP_TEXT: str = """
The specified chart in the requested format e.g. svg
"""
CHART_WIDTH: str = """
The width in pixels that you want to chart to be (default = 435 pixels)
"""
CHART_HEIGHT: str = """
The height in pixels that you want to chart to be (default = 220 pixels)
"""
TABLES_RESPONSE_DATE_HELP_TEXT: str = """
The dates for the specified plots in a tabular format
"""
TABLES_RESPONSE_HELP_TEXT: str = """
The specified plots in a tabular format
"""
CHART_X_AXIS: str = """
The metric to use along the X Axis of the chart
"""
CHART_Y_AXIS: str = """
The metric to use along the Y Axis of the chart
"""
ENCODED_CHARTS_RESPONSE_HELP_TEXT: str = """
The specified chart in the requested format e.g. svg URI encoded
"""
ENCODED_CHARTS_LAST_UPDATED_HELP_TEXT: str = """
The date that the chart data goes up to
"""
