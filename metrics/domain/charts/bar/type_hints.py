from typing import Dict, Union

from metrics.domain.charts.bar import colour_scheme

AXIS_ARGS = Dict[
    str,
    Union[
        bool,
        str,
        Dict[str, Union[str, int, colour_scheme.RGBAColours]],
    ],
]

LAYOUT_ARGS = Dict[
    str,
    Union[
        colour_scheme.RGBAColours,
        Dict[str, int],
        bool,
        Dict[str, Union[str, float, int]],
        str,
        int,
        AXIS_ARGS,
    ],
]
