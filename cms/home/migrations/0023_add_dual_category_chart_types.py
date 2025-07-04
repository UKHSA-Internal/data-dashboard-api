# Generated by Django 5.2.3 on 2025-06-19 14:26

import cms.dynamic_content.cards
import cms.metrics_interface.field_choices_callables
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0022_add_single_page_announcements"),
    ]

    operations = [
        migrations.AlterField(
            model_name="landingpage",
            name="body",
            field=wagtail.fields.StreamField(
                [("section", 75)],
                block_lookup={
                    0: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nThe text you add here will be used as the heading for this section. \n",
                            "required": True,
                        },
                    ),
                    1: (
                        "cms.dynamic_content.blocks.PageLinkChooserBlock",
                        (),
                        {
                            "help_text": "\nThe related index page you want to link to. Eg: `Respiratory viruses` or `Outbreaks`\n",
                            "page_type": ["composite.CompositePage"],
                            "required": False,
                        },
                    ),
                    2: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {
                            "features": ["h2", "h3", "h4", "bold", "ul", "link"],
                            "help_text": "\nThis section of text will comprise this card. \nNote that this card will span the length of the available page width if sufficient text content is provided.\n",
                        },
                    ),
                    3: ("wagtail.blocks.StructBlock", [[("body", 2)]], {}),
                    4: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nThe title to display for this component. \nNote that this will be shown in the hex colour #505A5F\n",
                            "required": True,
                        },
                    ),
                    5: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nAn optional body of text to accompany this block. This text will be displayed below the chart title.\n",
                            "label": "Subtitle",
                            "required": False,
                        },
                    ),
                    6: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "default": "",
                            "help_text": "\nAn optional body of text to accompany this block. This text will be displayed in the about content of the chart.\n",
                            "required": False,
                        },
                    ),
                    7: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "\nThe Text that will be displayed for the URL.\n",
                            "required": True,
                        },
                    ),
                    8: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "\nThe URL that the user will be navigated to when clicked.\nAn optional body of text to accompany this block. This text will be displayed below the chart title.\n",
                            "required": True,
                        },
                    ),
                    9: (
                        "wagtail.blocks.StructBlock",
                        [[("link_display_text", 7), ("link", 8)]],
                        {},
                    ),
                    10: (
                        "wagtail.blocks.StreamBlock",
                        [[("related_link", 9)]],
                        {
                            "help_text": "\nProvide optional URLs that can provide further contextual information for the data displayed in the chart.\n",
                            "required": False,
                        },
                    ),
                    11: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "\nThe ID to associate with this component. \nThis allows for tracking of events when users interact with this component.\nNote that changing this multiple times will result in the recording of different groups of events.\n",
                            "label": "Tag manager event ID",
                            "required": False,
                        },
                    ),
                    12: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_possible_axis_choices,
                            "help_text": "\nAn optional choice of what to display along the x-axis of the chart.\nIf nothing is provided, `dates` will be used by default.\nDates are used by default\n",
                            "required": False,
                        },
                    ),
                    13: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "default": "",
                            "help_text": "\nAn optional title to display along the x-axis of the chart.\nIf nothing is provided, then no title will be displayed.\n",
                            "required": False,
                        },
                    ),
                    14: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_possible_axis_choices,
                            "help_text": "\nAn optional choice of what to display along the y-axis of the chart.\nIf nothing is provided, `metric value` will be used by default.\n",
                            "required": False,
                        },
                    ),
                    15: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "default": "",
                            "help_text": "\nAn optional title to display along the y-axis of the chart.\nIf nothing is provided, then no title will be displayed.\n",
                            "required": False,
                        },
                    ),
                    16: (
                        "wagtail.blocks.DecimalBlock",
                        (),
                        {
                            "default": 0,
                            "help_text": "\nThis field allows you to set the first value in the chart's y-axis range. Please\nnote that a value provided here, which is higher than the lowest value in the data will\nbe overridden and the value from the dataset will be used.\n",
                            "required": False,
                        },
                    ),
                    17: (
                        "wagtail.blocks.DecimalBlock",
                        (),
                        {
                            "help_text": "\nThis field allows you to set the last value in the chart's y-axis range. Please\nnote that a value provided here, which is lower than the highest value in the data will\nbe overridden and the value from the dataset will be used. \n",
                            "required": False,
                        },
                    ),
                    18: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": "\nThis is a switch to show tooltips on hover within the chart.\nDefaults to False.\n",
                            "required": False,
                        },
                    ),
                    19: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "default": "Up to and including",
                            "help_text": "\nThis is the accompanying text for chart dates Eg: `Up to and including` 21 Oct 2024\n",
                            "required": True,
                        },
                    ),
                    20: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": "\nThis option enables timeseries filter for this chart.\nThe timeseries filter allows a user to change the timeseries range for example between\n1m, 3m, 6m, 1y etc.\n",
                            "required": False,
                        },
                    ),
                    21: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_topic_names,
                            "help_text": "The name of the topic to pull data e.g. COVID-19.",
                        },
                    ),
                    22: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_timeseries_metric_names,
                            "help_text": '\nThe name of the metric to pull data for e.g. "COVID-19_deaths_ONSByDay".\n',
                        },
                    ),
                    23: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_geography_names,
                            "help_text": "\nThe name of the geography associated with this particular piece of data.\nIf nothing is provided, then no filtering will be applied for this field.\n",
                        },
                    ),
                    24: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_geography_type_names,
                            "help_text": "\nThe type of geographical categorisation to apply any data filtering to.\nIf nothing is provided, then no filtering will be applied for this field.\n",
                        },
                    ),
                    25: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_sex_names,
                            "help_text": "\nThe gender to filter for, if any.\nThe only options available are `M`, `F` and `ALL`.\nBy default, no filtering will be applied to the underlying query if no selection is made.\n",
                        },
                    ),
                    26: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_age_names,
                            "help_text": "\nThe age band to filter for, if any.\nBy default, no filtering will be applied to the underlying query if no selection is made.\n",
                        },
                    ),
                    27: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_stratum_names,
                            "help_text": "\nThe smallest subgroup a piece of data can be broken down into.\nFor example, this could be broken down by ethnicity or testing pillar.\nIf nothing is provided, then no filtering will be applied for this field.\n",
                        },
                    ),
                    28: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_chart_types,
                            "help_text": "\nThe name of the type of chart which you want to create e.g. bar\n",
                        },
                    ),
                    29: (
                        "wagtail.blocks.DateBlock",
                        (),
                        {
                            "help_text": "\nThe date from which to begin the supporting plot data. \nNote that if nothing is provided, a default of 1 year ago from the current date will be applied.\n",
                            "required": False,
                        },
                    ),
                    30: (
                        "wagtail.blocks.DateBlock",
                        (),
                        {
                            "help_text": "\nThe date to which to end the supporting plot data. \nNote that if nothing is provided, a default of the current date will be applied.\n",
                            "required": False,
                        },
                    ),
                    31: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nThe label to assign on the legend for this individual plot.\nE.g. `15 to 44 years old`\n",
                            "required": False,
                        },
                    ),
                    32: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_colours,
                            "help_text": '\nThe colour to apply to this individual line plot. The colours conform to the GDS specification.\nCurrently, only the `line_multi_coloured` chart type supports different line colours.\nFor all other chart types, this field will be ignored.\nNote that if nothing is provided, a default of "BLACK" will be applied.\nE.g. `GREEN`\n',
                        },
                    ),
                    33: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_chart_line_types,
                            "help_text": '\nThe line type to apply to this individual line plot.\nCurrently, only the `line_multi_coloured` chart type supports different line types.\nFor all other chart types, this field will be ignored.\nNote that if nothing is provided, a default of "SOLID" will be applied.\nE.g. `DASH`\n',
                            "required": False,
                        },
                    ),
                    34: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": "\nIf set to true, markers are drawn on each individual data point.\nIf set to false, markers are not drawn at all.\nThis is only applicable to line-type charts.\n",
                            "required": False,
                        },
                    ),
                    35: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": True,
                            "help_text": "\nIf set to true, draws the plot as a spline line, resulting in smooth curves between data points.\nIf set to false, draws the plot as a linear line, \nresulting in linear point-to-point lines being drawn between data points.\nThis is only applicable to line-type charts.\n",
                            "required": False,
                        },
                    ),
                    36: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("topic", 21),
                                ("metric", 22),
                                ("geography", 23),
                                ("geography_type", 24),
                                ("sex", 25),
                                ("age", 26),
                                ("stratum", 27),
                                ("chart_type", 28),
                                ("date_from", 29),
                                ("date_to", 30),
                                ("label", 31),
                                ("line_colour", 32),
                                ("line_type", 33),
                                ("use_markers", 34),
                                ("use_smooth_lines", 35),
                            ]
                        ],
                        {},
                    ),
                    37: (
                        "wagtail.blocks.StreamBlock",
                        [[("plot", 36)]],
                        {
                            "help_text": "\nAdd the plots required for your chart. \nWithin each plot, you will be required to add a set of fields which will be used to fetch the supporting data \nfor that plot.\n"
                        },
                    ),
                    38: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 4),
                                ("body", 5),
                                ("about", 6),
                                ("related_links", 10),
                                ("tag_manager_event_id", 11),
                                ("x_axis", 12),
                                ("x_axis_title", 13),
                                ("y_axis", 14),
                                ("y_axis_title", 15),
                                ("y_axis_minimum_value", 16),
                                ("y_axis_maximum_value", 17),
                                ("show_tooltips", 18),
                                ("date_prefix", 19),
                                ("show_timeseries_filter", 20),
                                ("chart", 37),
                            ]
                        ],
                        {},
                    ),
                    39: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_possible_axis_choices,
                            "help_text": "\nA required choice of what to display along the x-axis of the chart.\n",
                        },
                    ),
                    40: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_headline_metric_names,
                            "help_text": '\nThe name of the metric to pull data for e.g. "COVID-19_deaths_ONSByDay".\n',
                        },
                    ),
                    41: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_headline_chart_types,
                            "help_text": "\nThe name of the type of chart which you want to create e.g. bar\n",
                        },
                    ),
                    42: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("topic", 21),
                                ("metric", 40),
                                ("geography", 23),
                                ("geography_type", 24),
                                ("sex", 25),
                                ("age", 26),
                                ("stratum", 27),
                                ("chart_type", 41),
                                ("line_colour", 32),
                                ("label", 31),
                            ]
                        ],
                        {},
                    ),
                    43: (
                        "wagtail.blocks.StreamBlock",
                        [[("plot", 42)]],
                        {
                            "help_texts": "\nAdd the plots required for your chart. \nWithin each plot, you will be required to add a set of fields which will be used to fetch the supporting data \nfor that plot.\n"
                        },
                    ),
                    44: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 4),
                                ("body", 5),
                                ("about", 6),
                                ("related_links", 10),
                                ("tag_manager_event_id", 11),
                                ("x_axis", 39),
                                ("x_axis_title", 13),
                                ("y_axis", 14),
                                ("y_axis_title", 15),
                                ("y_axis_minimum_value", 16),
                                ("y_axis_maximum_value", 17),
                                ("show_tooltips", 18),
                                ("date_prefix", 19),
                                ("show_timeseries_filter", 20),
                                ("chart", 43),
                            ]
                        ],
                        {},
                    ),
                    45: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nAn optional body of text to accompany this block. This text will be displayed in the about content of the chart.\n",
                            "required": False,
                        },
                    ),
                    46: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_unique_metric_names,
                            "help_text": '\nThe name of the metric to pull data for e.g. "COVID-19_deaths_ONSByDay".\n',
                        },
                    ),
                    47: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nAn optional body of text to accompany this block. This text will be displayed below the chart title.\n",
                            "required": False,
                        },
                    ),
                    48: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("topic", 21),
                                ("metric", 46),
                                ("geography", 23),
                                ("geography_type", 24),
                                ("sex", 25),
                                ("age", 26),
                                ("stratum", 27),
                                ("body", 47),
                            ]
                        ],
                        {
                            "help_text": '\nThis component will display a key headline number type metric.\nYou can also optionally add a body of text to accompany that headline number.\nE.g. "Patients admitted"\n'
                        },
                    ),
                    49: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_unique_change_type_metric_names,
                            "help_text": "\nThe name of the trend type metric to pull data e.g. \"COVID-19_headline_ONSdeaths_7daychange\". \nNote that only 'change' type metrics are available for selection for this field type.\n",
                        },
                    ),
                    50: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_all_unique_percent_change_type_names,
                            "help_text": "\nThe name of the accompanying percentage trend type metric to pull data \ne.g. \"COVID-19_headline_ONSdeaths_7daypercentchange\". \nNote that only 'percent' type metrics are available for selection for this field type.\n",
                        },
                    ),
                    51: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("topic", 21),
                                ("metric", 49),
                                ("geography", 23),
                                ("geography_type", 24),
                                ("sex", 25),
                                ("age", 26),
                                ("stratum", 27),
                                ("body", 47),
                                ("percentage_metric", 50),
                            ]
                        ],
                        {
                            "help_text": '\nThis component will display a trend number type metric.\nThis will display an arrow pointing in the direction of the metric change \nas well as colouring of the block to indicate the context of the change.\nYou can also optionally add a body of text to accompany that headline number.\nE.g. "Last 7 days"\n'
                        },
                    ),
                    52: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("topic", 21),
                                ("metric", 46),
                                ("geography", 23),
                                ("geography_type", 24),
                                ("sex", 25),
                                ("age", 26),
                                ("stratum", 27),
                                ("body", 47),
                            ]
                        ],
                        {
                            "help_text": '\nThis component will display a percentage number type metric.\nThis will display the value of the metric appended with a % character.\nYou can also optionally add a body of text to accompany this percentage number.\nE.g. "Virus tests positivity".\n'
                        },
                    ),
                    53: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("headline_number", 48),
                                ("trend_number", 51),
                                ("percentage_number", 52),
                            ]
                        ],
                        {
                            "help_text": "\nAdd up to 2 headline or trend number column components within this space.\nNote that these figures will be displayed within the card, and above the chart itself.\n",
                            "max_num": 2,
                            "min_num": 0,
                            "required": False,
                        },
                    ),
                    54: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 4),
                                ("body", 5),
                                ("about", 45),
                                ("related_links", 10),
                                ("tag_manager_event_id", 11),
                                ("x_axis", 12),
                                ("x_axis_title", 13),
                                ("y_axis", 14),
                                ("y_axis_title", 15),
                                ("y_axis_minimum_value", 16),
                                ("y_axis_maximum_value", 17),
                                ("show_tooltips", 18),
                                ("date_prefix", 19),
                                ("show_timeseries_filter", 20),
                                ("chart", 37),
                                ("headline_number_columns", 53),
                            ]
                        ],
                        {},
                    ),
                    55: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "\nThe sub title to display for this component.\n",
                            "required": False,
                        },
                    ),
                    56: (
                        "cms.dynamic_content.blocks.PageLinkChooserBlock",
                        (),
                        {
                            "help_text": "\nThe related topic page you want to link to. Eg: `COVID-19`\n",
                            "page_type": ["topic.TopicPage"],
                            "required": True,
                        },
                    ),
                    57: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_possible_axis_choices,
                            "help_text": "\nA required choice of what to display along the x-axis of the chart.\n",
                            "ready_only": True,
                        },
                    ),
                    58: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_possible_axis_choices,
                            "help_text": "\nA required choice of what to display along the y-axis of the chart.\n",
                        },
                    ),
                    59: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.metrics_interface.field_choices_callables.get_simplified_chart_types
                        },
                    ),
                    60: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": "\nIf set to true, draws the plot as a spline line, resulting in smooth curves between data points.\nIf set to false, draws the plot as a linear line, \nresulting in linear point-to-point lines being drawn between data points.\nThis is only applicable to line-type charts.\n",
                            "required": False,
                        },
                    ),
                    61: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("topic", 21),
                                ("metric", 22),
                                ("geography", 23),
                                ("geography_type", 24),
                                ("sex", 25),
                                ("age", 26),
                                ("stratum", 27),
                                ("chart_type", 59),
                                ("date_from", 29),
                                ("date_to", 30),
                                ("use_smooth_lines", 60),
                            ]
                        ],
                        {},
                    ),
                    62: (
                        "wagtail.blocks.StreamBlock",
                        [[("plot", 61)]],
                        {
                            "help_text": "\nAdd the plots required for your chart. \nWithin each plot, you will be required to add a set of fields which will be used to fetch the supporting data \nfor that plot.\n",
                            "max_num": 1,
                            "required": True,
                        },
                    ),
                    63: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 4),
                                ("sub_title", 55),
                                ("tag_manager_event_id", 11),
                                ("topic_page", 56),
                                ("x_axis", 57),
                                ("x_axis_title", 13),
                                ("y_axis", 58),
                                ("y_axis_title", 15),
                                ("y_axis_minimum_value", 16),
                                ("y_axis_maximum_value", 17),
                                ("chart", 62),
                            ]
                        ],
                        {},
                    ),
                    64: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("chart_card", 38),
                                ("headline_chart_card", 44),
                                ("chart_with_headline_and_trend_card", 54),
                                ("simplified_chart_with_link", 63),
                            ]
                        ],
                        {
                            "help_text": "\nHere you can add chart cards to a section and the layout will change based on the number of cards added.\nA single card will expand to take up half the row. When 2 or 3 cards are added they will share the width\nof a row equally, creating either a 2 or 3 column layout.\n",
                            "min_num": 1,
                        },
                    ),
                    65: ("wagtail.blocks.StructBlock", [[("cards", 64)]], {}),
                    66: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "default": "Up to",
                            "help_text": "\nThis is the accompanying text for headline column dates Eg: `Up to` 27 Oct 2024 \n",
                            "required": True,
                        },
                    ),
                    67: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("headline_number", 48),
                                ("trend_number", 51),
                                ("percentage_number", 52),
                            ]
                        ],
                        {
                            "help_text": "\nHere you can add up to 2 rows within this column component.\nEach row can be used to add a number block. \nThis can be a headline number, a trend number or a percentage number.\nIf you only add 1 row, then that block will be rendered on the upper half of the column.\nAnd the bottom row of the column will remain empty.\n",
                            "max_num": 2,
                            "min_num": 1,
                            "required": True,
                        },
                    ),
                    68: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 4), ("date_prefix", 66), ("rows", 67)]],
                        {},
                    ),
                    69: (
                        "wagtail.blocks.StreamBlock",
                        [[("column", 68)]],
                        {
                            "help_text": "\nAdd up to 5 number column components within this row. \nThe columns are ordered from left to right, top to bottom respectively. \nSo by moving 1 column component above the other, that component will be rendered in the column left of the other. \n",
                            "max_num": 5,
                            "min_num": 1,
                        },
                    ),
                    70: ("wagtail.blocks.StructBlock", [[("columns", 69)]], {}),
                    71: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {
                            "help_text": "\nThe sub title to display for this component.\n",
                            "required": True,
                        },
                    ),
                    72: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": cms.dynamic_content.cards.WHAlerts.get_alerts,
                            "help_text": "\nThis is used to select the current weather health alert type Eg: Heat or Cold alert season.\n",
                        },
                    ),
                    73: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 4), ("sub_title", 71), ("alert_type", 72)]],
                        {},
                    ),
                    74: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("text_card", 3),
                                ("chart_card_section", 65),
                                ("headline_numbers_row_card", 70),
                                ("weather_health_alert_card", 73),
                            ]
                        ],
                        {
                            "help_text": "\nHere you can add any number of content row cards for this section.\nNote that these cards will be displayed across the available width.\n"
                        },
                    ),
                    75: (
                        "wagtail.blocks.StructBlock",
                        [[("heading", 0), ("page_link", 1), ("content", 74)]],
                        {},
                    ),
                },
            ),
        ),
    ]
