from metrics.domain.charts import colour_scheme

AXIS_ARGS = dict[str, bool | str | dict[str, str | int | colour_scheme.RGBAColours]]

CHART_ARGS = dict[
    str,
    colour_scheme.RGBAColours
    | dict[str, int]
    | bool
    | int
    | dict[str, str | float | int]
    | AXIS_ARGS,
]

COLOUR_PAIR = tuple[colour_scheme.RGBAColours, colour_scheme.RGBAColours]


DICT_OF_STR_ONLY = dict[str, str]
