TOPIC_FIELD: str = "The name of the topic being queried for. E.g. `COVID-19`"
METRIC_FIELD: str = "The name of the metric being queried for. E.g. `{}`"
STRATUM_FIELD: str = """
The smallest subgroup a metric can be broken down into.
Defaults to `default`
"""
AGE_FIELD: str = """
The patient age band to apply any data filtering to
E.g. `0_4`
"""
GEOGRAPHY_FIELD: str = """
The geography constraints to apply any data filtering to.
E.g. `London`
"""
GEOGRAPHY_TYPE_FIELD: str = """
The type of geographical categorisation to apply any data filtering to.
E.g. `Nation`
"""
SEX_FIELD: str = """
The gender to apply data filtering to.
The only options available are `M`, `F` and `ALL`.
By default, `ALL` will be applied to the underlying query.
"""
LABEL_FIELD: str = """
The label to assign on the legend for this individual plot.
E.g. `15 to 44 years old`
"""
HEADLINE_METRIC_VALUE_FIELD: str = """
The associated value of the headline metric which was queried for. E.g. `COVID-19_headline_tests_7DayTotals`
"""
TREND_METRIC_NAME_FIELD: str = """
The name of the main change type metric being queried for. E.g. `COVID-19_headline_ONSdeaths_7DayChange`
"""
TREND_METRIC_VALUE_FIELD: str = """
The associated value of the main change type metric which was queried for. E.g. `10`
"""

TREND_PERCENTAGE_METRIC_NAME_FIELD: str = """
The name of the percentage change type metric being queried for. E.g. `COVID-19_headline_ONSdeaths_7DayPercentChange`
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
ENCODED_CHARTS_FILE_FORMAT_FIELD: str = """
The file format to render the chart in. 
Note this currently only supports `svg`.
"""
FILE_DOWNLOAD_FORMAT: str = """
The format you want the data downloaded in. 
This can be either `json` or `csv`
"""
CHARTS_RESPONSE: str = """
The specified chart in the requested format e.g. svg
"""
CHART_WIDTH: str = """
The width in pixels that you want to chart to be (default = 435 pixels)
"""
CHART_HEIGHT: str = """
The height in pixels that you want to chart to be (default = 220 pixels)
"""
TABLES_RESPONSE_DATE: str = """
The dates for the specified plots in a tabular format
"""
TABLES_RESPONSE: str = """
The specified plots in a tabular format
"""
CHART_X_AXIS: str = """
The metric to use along the X axis of the chart
"""
CHART_X_AXIS_TITLE: str = """
An optional title to display along the X axis of the chart
"""
CHART_Y_AXIS: str = """
The metric to use along the Y Axis of the chart
"""
CHART_Y_AXIS_TITLE: str = """
An optional title to display along the Y axis of the chart
"""
CHART_Y_AXIS_MINIMUM_VALUE: str = """
The value used to start the chart's y_axis Eg: 0 will scale the chart to have a 0 as its lowest value.
"""
CHART_Y_AXIS_MAXIMUM_VALUE: str = """
The value used as the chart's highest y_axis value Eg: providing a higher value than appears in the data will
rescale the chart to that value 
"""
CHART_LEGEND_TITLE: str = """
An optional title to display for the legend.
"""
ENCODED_CHARTS_RESPONSE: str = """
The specified chart in the requested format as a URI encoded string (default format = svg)
"""
ENCODED_CHARTS_LAST_UPDATED: str = """
The date that the chart data goes up to
"""
CHARTS_ALT_TEXT: str = """
The description text which summarizes the chart and the data that it represents.
"""
CHARTS_FIGURE_OUTPUT: str = """
The `plotly` figure object output with overlaid settings specific for interactive charts.
"""
CHART_USE_MARKERS: str = """
Boolean switch to decide whether to draw markers on individual data points.
"""
CHART_USE_SMOOTH_LINES: str = """
Boolean switch to decide whether to draw splines on individual data points.
If set to false, linear point-to-point lines will be drawn between points.
"""

CONFIDENCE_INTERVALS: str = """
Boolean switch to decide whether to draw confidence intervals if provided
"""
