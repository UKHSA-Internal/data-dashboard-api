from typing import Dict, Tuple, Union

from metrics.domain.charts import colour_scheme

AXIS_ARGS = Dict[
    str,
    Union[
        bool,
        str,
        Dict[
            str,
            Union[str, int, colour_scheme.RGBAColours],
        ],
    ],
]

CHART_ARGS = Dict[
    str,
    Union[
        colour_scheme.RGBAColours,
        Dict[str, int],
        bool,
        int,
        Dict[str, Union[str, float, int]],
        AXIS_ARGS,
    ],
]

COLOUR_PAIR = Tuple[colour_scheme.RGBAColours, colour_scheme.RGBAColours]
