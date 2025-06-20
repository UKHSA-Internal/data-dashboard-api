HEADLINE_COLUMNS_FIELD: str = """
Add up to {} number column components within this row. 
The columns are ordered from left to right, top to bottom respectively. 
So by moving 1 column component above the other, that component will be rendered in the column left of the other. 
"""

HEADLINE_COLUMNS_IN_CHART_CARD: str = """
Add up to {} headline or trend number column components within this space.
Note that these figures will be displayed within the card, and above the chart itself.
"""
CHART_CARD_ROW: str = """
Here you can add 1 or 2 columns to contain a particular chart card.
If you add the 1 column, then the chart card will spread across the available width.
If you add 2 columns, then the cards will be split across 2 columns within the available width.
"""

CHART_ROW_CARD_COLUMN_WIDTH_THREE: str = """
Here you can add chart cards to a section and the layout will change based on the number of cards added.
A single card will expand to take up half the row. When 2 or 3 cards are added they will share the width
of a row equally, creating either a 2 or 3 column layout.
"""

NUMBERS_ROW_FIELD: str = """
Here you can add up to {} rows within this column component.
Each row can be used to add a number block. 
This can be a headline number, a trend number or a percentage number.
If you only add 1 row, then that block will be rendered on the upper half of the column.
And the bottom row of the column will remain empty.
"""

CHART_BLOCK_FIELD: str = """
Add the plots required for your chart. 
Within each plot, you will be required to add a set of fields which will be used to fetch the supporting data 
for that plot.
"""

TOPIC_PAGE_FIELD: str = """
The related topic page you want to link to. Eg: `COVID-19`
"""

INDEX_PAGE_FIELD: str = """
The related index page you want to link to. Eg: `Respiratory viruses` or `Outbreaks`
"""

HEADLINE_BLOCK_FIELD: str = """
This component will display a key headline number type metric.
You can also optionally add a body of text to accompany that headline number.
E.g. "Patients admitted"
"""
TREND_BLOCK_FIELD: str = """
This component will display a trend number type metric.
This will display an arrow pointing in the direction of the metric change 
as well as colouring of the block to indicate the context of the change.
You can also optionally add a body of text to accompany that headline number.
E.g. "Last 7 days"
"""
PERCENTAGE_BLOCK_FIELD: str = """
This component will display a percentage number type metric.
This will display the value of the metric appended with a % character.
You can also optionally add a body of text to accompany this percentage number.
E.g. "Virus tests positivity".
"""

TOP_HEADLINE_BLOCK_FIELD: str = """
This will display a key headline number type metric as the top half of this column component.
"""
BOTTOM_HEADLINE_BLOCK_FIELD: str = """
This will display a key headline number type metric as the bottom half of this column component.
"""

SINGLE_HEADLINE_COMPONENT: str = """
This component will be displayed as a single headline number type metric on the top half of the column.
The bottom half of this column component will be left empty.
"""
HEADLINE_AND_TREND_COMPONENT: str = """
This component will be displayed with a headline number type metric on the top half of the column.
And a trend type metric will be shown on the bottom half of the column component.
"""
DUAL_HEADLINE_COMPONENT: str = """
This component will be displayed with a headline number type metric on the top half of the column.
And another headline number type metric will be shown on the bottom half of the column component.
"""

TEXT_CARD: str = """
This section of text will comprise this card. 
Note that this card will span the length of the available page width if sufficient text content is provided.
"""
BODY_FIELD: str = "The section of text which will accommodate this block."
BODY_FIELD_ABOVE_BLOCK: str = f"""
{BODY_FIELD} Note that this text will be placed above the main content of the block.
"""
HEADING_BLOCK: str = """
The text you add here will be used as the heading for this section. 
"""

CONTENT_ROW_CARDS: str = """
Here you can add any number of content row cards for this section.
Note that these cards will be displayed across the available width.
"""


TOPIC_FIELD: str = "The name of the topic to pull data e.g. COVID-19."
METRIC_FIELD: str = """
The name of the metric to pull data for e.g. "COVID-19_deaths_ONSByDay".
"""
STRATUM_FIELD: str = """
The smallest subgroup a piece of data can be broken down into.
For example, this could be broken down by ethnicity or testing pillar.
If nothing is provided, then no filtering will be applied for this field.
"""
GEOGRAPHY_FIELD: str = """
The name of the geography associated with this particular piece of data.
If nothing is provided, then no filtering will be applied for this field.
"""
GEOGRAPHY_TYPE_FIELD: str = """
The type of geographical categorisation to apply any data filtering to.
If nothing is provided, then no filtering will be applied for this field.
"""

TREND_METRIC_FIELD: str = """
The name of the trend type metric to pull data e.g. "COVID-19_headline_ONSdeaths_7daychange". 
Note that only 'change' type metrics are available for selection for this field type.
"""
TREND_PERCENTAGE_METRIC_FIELD: str = """
The name of the accompanying percentage trend type metric to pull data 
e.g. "COVID-19_headline_ONSdeaths_7daypercentchange". 
Note that only 'percent' type metrics are available for selection for this field type.
"""
CHART_TYPE_FIELD: str = """
The name of the type of chart which you want to create e.g. bar
"""
DATE_FROM_FIELD: str = """
The date from which to begin the supporting plot data. 
Note that if nothing is provided, a default of 1 year ago from the current date will be applied.
"""
DATE_TO_FIELD: str = """
The date to which to end the supporting plot data. 
Note that if nothing is provided, a default of the current date will be applied.
"""
SEX_FIELD: str = """
The gender to filter for, if any.
The only options available are `M`, `F` and `ALL`.
By default, no filtering will be applied to the underlying query if no selection is made.
"""
AGE_FIELD: str = """
The age band to filter for, if any.
By default, no filtering will be applied to the underlying query if no selection is made.
"""

LABEL_FIELD: str = """
The label to assign on the legend for this individual plot.
E.g. `15 to 44 years old`
"""
LINE_COLOUR_FIELD: str = """
The colour to apply to this individual line plot. The colours conform to the GDS specification.
Currently, only the `line_multi_coloured` chart type supports different line colours.
For all other chart types, this field will be ignored.
Note that if nothing is provided, a default of "BLACK" will be applied.
E.g. `GREEN`
"""
LINE_TYPE_FIELD: str = """
The line type to apply to this individual line plot.
Currently, only the `line_multi_coloured` chart type supports different line types.
For all other chart types, this field will be ignored.
Note that if nothing is provided, a default of "SOLID" will be applied.
E.g. `DASH`
"""
SHOW_TOOLTIPS_ON_CHARTS_FIELD: str = """
This is a switch to show tooltips on hover within the chart.
Defaults to False.
"""

TITLE_FIELD: str = """
The title to display for this component. 
Note that this will be shown in the hex colour #505A5F
"""
SUB_TITLE_FIELD: str = """
The sub title to display for this component.
"""

OPTIONAL_CHART_ABOUT_FIELD: str = """
An optional body of text to accompany this block. This text will be displayed in the about content of the chart.
"""

OPTIONAL_BODY_FIELD: str = """
An optional body of text to accompany this block. This text will be displayed below the chart title.
"""

OPTIONAL_RELATED_LINK: str = """
Provide optional URLs that can provide further contextual information for the data displayed in the chart.
"""

RELATED_LINK_TEXT: str = """
The Text that will be displayed for the URL.
"""

RELATED_LINK_URL: str = """
The URL that the user will be navigated to when clicked.
An optional body of text to accompany this block. This text will be displayed below the chart title.
"""

REQUIRED_BODY_FIELD: str = """
A required body of text to accompany this block.
"""

PAGE_DESCRIPTION_FIELD: str = """
An optional body of text which will be rendered at the top of the page. 
This text will be displayed after the title of the page and before any of the main content.
"""

CHART_X_AXIS: str = """
An optional choice of what to display along the x-axis of the chart.
If nothing is provided, `dates` will be used by default.
Dates are used by default
"""

CHART_X_AXIS_TITLE: str = """
An optional title to display along the x-axis of the chart.
If nothing is provided, then no title will be displayed.
"""

REQUIRED_CHART_X_AXIS_TITLE: str = """
A required title to display along the x-axis of the chart.
"""

CHART_Y_AXIS_TITLE: str = """
An optional title to display along the y-axis of the chart.
If nothing is provided, then no title will be displayed.
"""

REQUIRED_CHART_X_AXIS: str = """
A required choice of what to display along the x-axis of the chart.
"""

CHART_Y_AXIS: str = """
An optional choice of what to display along the y-axis of the chart.
If nothing is provided, `metric value` will be used by default.
"""

CHART_Y_AXIS_MINIMUM_VALUE: str = """
This field allows you to set the first value in the chart's y-axis range. Please
note that a value provided here, which is higher than the lowest value in the data will
be overridden and the value from the dataset will be used.
"""

CHART_Y_AXIS_MAXIMUM_VALUE: str = """
This field allows you to set the last value in the chart's y-axis range. Please
note that a value provided here, which is lower than the highest value in the data will
be overridden and the value from the dataset will be used. 
"""

REQUIRED_CHART_Y_AXIS: str = """
A required choice of what to display along the y-axis of the chart.
"""

USE_SMOOTH_LINES: str = """
If set to true, draws the plot as a spline line, resulting in smooth curves between data points.
If set to false, draws the plot as a linear line, 
resulting in linear point-to-point lines being drawn between data points.
This is only applicable to line-type charts.
"""

USE_MARKERS: str = """
If set to true, markers are drawn on each individual data point.
If set to false, markers are not drawn at all.
This is only applicable to line-type charts.
"""

CODE_EXAMPLE: str = """
A required section that can be used to add code examples to a composite page type.
"""

BUTTON_TYPE_GDS: str = """
A required choice of the button type to be used, the options include `Primary`, `Secondary`.
These align with GDS guidelines.
"""

BUTTON_ICON: str = """
An optional choice of icon to add to a button, defaults to none.
"""

CODE_SNIPPET: str = """
A code snippet to demonstrate the example. Please note that HTML type content is not permitted.
"""

GLOBAL_BANNER_TITLE: str = """
The title to associate with the banner. This must be provided.
"""

GLOBAL_BANNER_BODY: str = """
A body of text to be displayed by the banner. There is a limit of 255 characters for this field.
"""

GLOBAL_BANNER_TYPE: str = """
The type to associate with the banner. Defaults to `Information`.
"""

GLOBAL_BANNER_IS_ACTIVE: str = """
Whether to activate this banner across every page in the dashboard. 
Multiple banners can be active across the dashboard.
Note: Warning banners are prioritised across the dashboard and will be displayed above information banners.
"""

TAG_MANAGER_EVENT_ID_FIELD: str = """
The ID to associate with this component. 
This allows for tracking of events when users interact with this component.
Note that changing this multiple times will result in the recording of different groups of events.
"""


RELATED_LINKS_LAYOUT_FIELD: str = """
This dictates where the related links for this page will be positioned.
"""

SHOW_PAGINATION_FIELD: str = """
This is used to determine whether to render pagination controls or not.
"""
PAGINATION_SIZE_FIELD: str = """
This is used to control the default pagination size used if there are associated children pages.
"""

WHA_ALERT_CHOICE: str = """
This is used to select the current weather health alert type Eg: Heat or Cold alert season.
"""

PAGE_LINK_TITLE: str = """
This is the title of the page you're linking to Eg. COVID-19
"""

PAGE_LINK_SUB_TITLE: str = """
This is an optional short description of the page you're linking to.
"""

HEADLINE_DATE_PREFIX: str = """
This is the accompanying text for headline column dates Eg: `Up to` 27 Oct 2024 
"""

CHART_DATE_PREFIX: str = """
This is the accompanying text for chart dates Eg: `Up to and including` 21 Oct 2024
"""

CHART_TIMESERIES_FILTER: str = """
This option enables timeseries filter for this chart.
The timeseries filter allows a user to change the timeseries range for example between
1m, 3m, 6m, 1y etc.
"""

ANNOUNCEMENT_BANNER_TITLE: str = """
The title to associate with the announcement. This must be provided.
"""

ANNOUNCEMENT_BANNER_BODY: str = """
A body of text to be displayed by the announcement. There is a limit of 255 characters for this field.
"""

ANNOUNCEMENT_BANNER_TYPE: str = """
The type to associate with the announcement. Defaults to `Information`.
"""

ANNOUNCEMENT_BANNER_IS_ACTIVE: str = """
Whether to activate this banner only on this individual page. 
Note that multiple page banners can be active on one page. Consider 
carefully if you need multiple announcements to be active at once as
this can have an impact on user experience of the dashboard page.
"""
