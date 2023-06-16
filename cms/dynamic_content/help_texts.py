HEADLINE_COLUMNS_FIELD_HELP_TEXT: str = """
Add up to {} number column components within this row. 
The columns are ordered from left to right, top to bottom respectively. 
So by moving 1 column component above the other, that component will be rendered in the column left of the other. 
"""

HEADLINE_COLUMNS_IN_CHART_CARD_HELP_TEXT: str = """
Add up to {} headline or trend number column components within this space.
Note that these figures will be displayed within the card, and above the chart itself.
"""
CHART_CARD_ROW_HELP_TEXT: str = """
Here you can add 1 or 2 columns to contain a particular chart card.
If you add the 1 column, then the chart card will spread across the available width.
If you add 2 columns, then the cards will be split across 2 columns within the available width.
"""
NUMBERS_ROW_FIELD_HELP_TEXT: str = """
Here you can add up to {} rows within this column component.
Each row can be used to add a number block. 
This can be a headline number, a trend number or a percentage number.
If you only add 1 row, then that block will be rendered on the upper half of the column.
And the bottom row of the column will remain empty.
"""

CHART_BLOCK_FIELD_HELP_TEXT: str = """
Add the plots required for your chart. 
Within each plot, you will be required to add a set of fields which will be used to fetch the supporting data 
for that plot.
"""

HEADLINE_BLOCK_FIELD_HELP_TEXT: str = """
This component will display a key headline number type metric.
You can also optionally add a body of text to accompany that headline number.
E.g. "Patients admitted"
"""
TREND_BLOCK_FIELD_HELP_TEXT: str = """
This component will display a trend number type metric.
This will display an arrow pointing in the direction of the metric change 
as well as colouring of the block to indicate the context of the change.
You can also optionally add a body of text to accompany that headline number.
E.g. "Last 7 days"
"""
PERCENTAGE_BLOCK_FIELD_HELP_TEXT: str = """
This component will display a percentage number type metric.
This will display the value of the metric appended with a % character.
You can also optionally add a body of text to accompany this percentage number.
E.g. "Virus tests positivity".
"""

TOP_HEADLINE_BLOCK_FIELD_HELP_TEXT: str = """
This will display a key headline number type metric as the top half of this column component.
"""
BOTTOM_HEADLINE_BLOCK_FIELD_HELP_TEXT: str = """
This will display a key headline number type metric as the bottom half of this column component.
"""

SINGLE_HEADLINE_COMPONENT_HELP_TEXT: str = """
This component will be displayed as a single headline number type metric on the top half of the column.
The bottom half of this column component will be left empty.
"""
HEADLINE_AND_TREND_COMPONENT_HELP_TEXT: str = """
This component will be displayed with a headline number type metric on the top half of the column.
And a trend type metric will be shown on the bottom half of the column component.
"""
DUAL_HEADLINE_COMPONENT_HELP_TEXT: str = """
This component will be displayed with a headline number type metric on the top half of the column.
And another headline number type metric will be shown on the bottom half of the column component.
"""

TEXT_CARD_HELP_TEXT: str = """
This section of text will comprise this card. 
Note that this card will span the length of the available page width if sufficient text content is provided.
"""
BODY_FIELD_HELP_TEXT: str = "The section of text which will accommodate this block."
BODY_FIELD_ABOVE_BLOCK_HELP_TEXT: str = f"""
{BODY_FIELD_HELP_TEXT} Note that this text will be placed above the main content of the block.
"""
HEADING_BLOCK_HELP_TEXT: str = """
The text you add here will be used as the heading for this section. 
"""

CONTENT_ROW_CARDS_HELP_TEXT: str = """
Here you can add any number of content row cards for this section.
Note that these cards will be displayed across the available width.
"""


TOPIC_FIELD_HELP_TEXT: str = "The name of the topic to pull data e.g. COVID-19."
METRIC_FIELD_HELP_TEXT: str = """
The name of the metric to pull data e.g. new_cases_daily.
"""
TREND_METRIC_FIELD_HELP_TEXT: str = """
The name of the trend type metric to pull data e.g. "new_cases_7days_change". 
Note that only 'change' type metrics are available for selection for this field type.
"""
TREND_PERCENTAGE_METRIC_FIELD_HELP_TEXT: str = """
The name of the accompanying percentage trend type metric to pull data e.g. "new_cases_7days_change_percentage". 
Note that only 'percent' type metrics are available for selection for this field type.
"""
CHART_TYPE_FIELD_HELP_TEXT: str = """
The name of the type of chart which you want to create e.g. waffle
"""
DATE_FROM_FIELD_HELP_TEXT: str = """
The date from which to begin the supporting chart data. 
Note that if nothing is provided, a default of 1 year ago from the current date will be applied.
"""
DATE_TO_FIELD_HELP_TEXT: str = """
The date to which to end the supporting chart data. 
Note that if nothing is provided, a default of the current date will be applied.
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

TITLE_FIELD_HELP_TEXT: str = """
The title to display for this component. 
Note that this will be shown in the hex colour #505A5F
"""
OPTIONAL_BODY_FIELD_HELP_TEXT: str = """
An optional body of text to accompany this block.
"""

PAGE_DESCRIPTION_FIELD_HELP_TEXT: str = """
An optional body of text which will be rendered at the top of the page. 
This text will be displayed after the title of the page and before any of the main content.
"""

X_AXIS_HELP_TEXT: str = """
An optional choice of what to display along the X Axis of the chart.
Dates are used by default
"""

Y_AXIS_HELP_TEXT: str = """
An optional choice of what to display along the Y Axis of the chart.
The metric values are used by default
"""
