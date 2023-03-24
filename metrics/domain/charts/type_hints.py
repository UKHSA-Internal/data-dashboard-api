from typing import Dict, List, Tuple, Union

from metrics.domain.charts.line_with_shaded_section import colour_scheme

AXIS_ARGS = Dict[
    str, Union[bool, str, Dict[str, Union[str, int, colour_scheme.RGBAColours]]]
]

LAYOUT_ARGS = Dict[
    str, Union[colour_scheme.RGBAColours, Dict[str, int], bool, int, AXIS_ARGS]
]

COLOUR_PAIR = Tuple[colour_scheme.RGBAColours, colour_scheme.RGBAColours]
