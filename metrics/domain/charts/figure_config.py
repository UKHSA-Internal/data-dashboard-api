"""Build the three responsive Plotly overrides for interactive charts.

The base ``figure`` remains the source used for static and non-JavaScript output.
The configurations built here contain only the trace and layout attributes the
frontend needs to apply for the selected responsive mode.
"""

import copy
import re
from collections.abc import Mapping
from typing import Any

from metrics.domain.charts.chart_settings.single_category import (
    COMPACT_X_AXIS_NTICKS,
    FULL_WIDTH_X_AXIS_NTICKS,
)
from metrics.domain.charts.chart_settings.subplot_chart_settings import (
    ROTATED_SUBPLOT_AXIS_TITLE_ANNOTATION_CONFIG,
    ROTATED_SUBPLOT_LEGEND_CONFIG,
    ROTATED_SUBPLOT_MARGIN_CONFIG,
)

AXIS_KEY_PATTERN = re.compile(r"^xaxis(?P<suffix>\d*)$")
PATH_COORDINATE_PATTERN = re.compile(
    r"(?P<command>[ML])\s+"
    r"(?P<x>-?(?:\d+(?:\.\d*)?|\.\d+))\s+"
    r"(?P<y>-?(?:\d+(?:\.\d*)?|\.\d+))"
)
HOVER_AXIS_PATTERN = re.compile(r"%\{(?P<axis>[xy])(?P<remainder>[^}]*)\}")

COMPACT_CHART_BASE_HEIGHT = 200
COMPACT_CHART_HEIGHT_PER_BAR = 25
MINIMUM_COMPACT_CHART_HEIGHT = 400

DOMAIN_COORDINATE_COUNT = 2

AXIS_POSITION_PROPERTIES = {
    "anchor",
    "domain",
    "overlaying",
    "position",
    "side",
}
X_ANCHOR_TO_Y_ANCHOR = {
    "auto": "auto",
    "left": "bottom",
    "center": "middle",
    "right": "top",
}
Y_ANCHOR_TO_X_ANCHOR = {
    "auto": "auto",
    "bottom": "left",
    "middle": "center",
    "top": "right",
}


def _swap_axis_reference(reference: Any) -> Any:
    if not isinstance(reference, str):
        return reference
    if reference.startswith("x"):
        return f"y{reference[1:]}"
    if reference.startswith("y"):
        return f"x{reference[1:]}"
    return reference


def _swap_hovertemplate(template: Any) -> Any:
    if not isinstance(template, str):
        return template

    return HOVER_AXIS_PATTERN.sub(
        lambda match: (
            f"%{{{'y' if match.group('axis') == 'x' else 'x'}"
            f"{match.group('remainder')}}}"
        ),
        template,
    )


def _build_trace_override(trace: Mapping[str, Any], *, rotate: bool) -> dict:
    """Return the responsive attributes for one Plotly trace."""
    override: dict[str, Any] = {}

    for attribute in ("x", "y", "hovertemplate", "error_x", "error_y"):
        if attribute in trace:
            override[attribute] = copy.deepcopy(trace[attribute])

    if trace.get("type") == "bar":
        override["orientation"] = trace.get("orientation", "v")

    if not rotate or trace.get("type") != "bar":
        return override

    override["x"] = copy.deepcopy(trace.get("y"))
    override["y"] = copy.deepcopy(trace.get("x"))
    override["orientation"] = "h"

    if "hovertemplate" in trace:
        override["hovertemplate"] = _swap_hovertemplate(trace["hovertemplate"])

    if "error_y" in trace:
        override["error_x"] = copy.deepcopy(trace["error_y"])
        override["error_y"] = {"visible": False}

    return override


def _axis_for_rotated_position(
    *, source_axis: Mapping[str, Any], destination_axis: Mapping[str, Any]
) -> dict:
    """Move semantic axis settings while retaining the destination position.

    Plotly subplot axes contain positional properties such as ``domain`` and
    ``anchor``. Those describe where the destination axis lives and must not be
    copied from the opposite axis.
    """
    rotated_axis = copy.deepcopy(source_axis)

    for property_name in AXIS_POSITION_PROPERTIES:
        if property_name in destination_axis:
            rotated_axis[property_name] = copy.deepcopy(destination_axis[property_name])
        else:
            rotated_axis.pop(property_name, None)

    for reference_property in ("matches", "scaleanchor"):
        if reference_property in source_axis:
            rotated_axis[reference_property] = _swap_axis_reference(
                source_axis[reference_property]
            )
        else:
            rotated_axis.pop(reference_property, None)

    return rotated_axis


def _axis_pairs(layout: Mapping[str, Any]):
    for key, x_axis in layout.items():
        match = AXIS_KEY_PATTERN.match(key)
        if match is None or not isinstance(x_axis, Mapping):
            continue

        suffix = match.group("suffix")
        y_axis_key = f"yaxis{suffix}"
        y_axis = layout.get(y_axis_key)
        if isinstance(y_axis, Mapping):
            yield key, y_axis_key, x_axis, y_axis


def _transpose_domain(domain: Any) -> Any:
    """Turn a left-to-right subplot domain into a top-to-bottom domain"""
    if (
        not isinstance(domain, (list, tuple))
        or len(domain) != DOMAIN_COORDINATE_COUNT
    ):
        return domain

    start, end = domain
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
        return domain

    return [1 - end, 1 - start]


def _position_rotated_subplot_grid(
    *,
    axis_pairs: list[tuple[str, str, Mapping[str, Any], Mapping[str, Any]]],
    rotated_layout: dict[str, Any],
) -> None:
    """Transpose a one-row subplot grid into one column while preserving order."""
    if not axis_pairs:
        return

    first_x_key = axis_pairs[0][0]
    last_x_key = axis_pairs[-1][0]
    primary_x_axis = rotated_layout[first_x_key]
    primary_title = copy.deepcopy(primary_x_axis.get("title"))
    primary_tick_length = primary_x_axis.get("ticklen", 5)

    for x_key, y_key, source_x_axis, source_y_axis in axis_pairs:
        rotated_x_axis = rotated_layout[x_key]
        rotated_y_axis = rotated_layout[y_key]

        rotated_x_axis["domain"] = copy.deepcopy(source_y_axis.get("domain", [0, 1]))
        rotated_x_axis["showticklabels"] = False
        rotated_x_axis["ticklen"] = 0
        rotated_x_axis["automargin"] = True
        rotated_x_axis.pop("title", None)

        source_x_domain = source_x_axis.get("domain")
        transposed_domain = _transpose_domain(source_x_domain)
        if transposed_domain is not None:
            rotated_y_axis["domain"] = copy.deepcopy(transposed_domain)
        rotated_y_axis["automargin"] = True

    bottom_x_axis = rotated_layout[last_x_key]
    bottom_x_axis["showticklabels"] = True
    bottom_x_axis["ticklen"] = primary_tick_length
    if primary_title is not None:
        bottom_x_axis["title"] = primary_title


def _position_rotated_subplot_annotations(annotations: list[dict]) -> None:
    """Keep the shared categorical-axis title close to a tall subplot grid."""
    for annotation in annotations:
        if (
            annotation.get("xref") == "paper"
            and annotation.get("yref") == "paper"
            and annotation.get("textangle")
            == ROTATED_SUBPLOT_AXIS_TITLE_ANNOTATION_CONFIG["textangle"]
        ):
            annotation.update(
                copy.deepcopy(ROTATED_SUBPLOT_AXIS_TITLE_ANNOTATION_CONFIG)
            )


def _rotate_shape(shape: Mapping[str, Any]) -> dict:
    rotated_shape = copy.deepcopy(shape)

    for x_attribute, y_attribute in (("x0", "y0"), ("x1", "y1")):
        original_x = copy.deepcopy(shape.get(x_attribute))
        original_y = copy.deepcopy(shape.get(y_attribute))
        if y_attribute in shape:
            rotated_shape[x_attribute] = original_y
        else:
            rotated_shape.pop(x_attribute, None)
        if x_attribute in shape:
            rotated_shape[y_attribute] = original_x
        else:
            rotated_shape.pop(y_attribute, None)

    if "xref" in shape or "yref" in shape:
        rotated_shape["xref"] = _swap_axis_reference(shape.get("yref", "y"))
        rotated_shape["yref"] = _swap_axis_reference(shape.get("xref", "x"))

    if shape.get("type") == "path" and isinstance(shape.get("path"), str):
        rotated_shape["path"] = PATH_COORDINATE_PATTERN.sub(
            lambda match: (
                f"{match.group('command')} {match.group('y')} {match.group('x')}"
            ),
            shape["path"],
        )

    return rotated_shape


def _rotate_annotation(annotation: Mapping[str, Any]) -> dict:
    rotated_annotation = copy.deepcopy(annotation)
    xref = annotation.get("xref", "x")
    yref = annotation.get("yref", "y")

    # Watermarks and similar paper-positioned annotations are not tied to an
    # axis. Axis-title annotations have anchors and do need rotating.
    is_unpositioned_paper_annotation = (
        xref == "paper"
        and yref == "paper"
        and "xanchor" not in annotation
        and "yanchor" not in annotation
    )
    if is_unpositioned_paper_annotation:
        return rotated_annotation

    if "x" in annotation or "y" in annotation:
        rotated_annotation["x"] = copy.deepcopy(annotation.get("y"))
        rotated_annotation["y"] = copy.deepcopy(annotation.get("x"))

    rotated_annotation["xref"] = _swap_axis_reference(yref)
    rotated_annotation["yref"] = _swap_axis_reference(xref)

    if "xanchor" in annotation or "yanchor" in annotation:
        rotated_annotation["xanchor"] = Y_ANCHOR_TO_X_ANCHOR.get(
            annotation.get("yanchor", "auto"), "auto"
        )
        rotated_annotation["yanchor"] = X_ANCHOR_TO_Y_ANCHOR.get(
            annotation.get("xanchor", "auto"), "auto"
        )

    if xref == "paper" and yref == "paper":
        rotated_annotation["textangle"] = annotation.get("textangle", 0) - 90

    return rotated_annotation


def _build_layout_configs(
    layout: Mapping[str, Any], *, rotate_compact: bool, rotate_subplot_grid: bool,
) -> tuple[dict, dict, dict]:
    full_layout: dict[str, Any] = {}
    compact_layout: dict[str, Any] = {}
    compact_rotated_layout: dict[str, Any] = {}

    axis_pairs = list(_axis_pairs(layout))

    for x_key, y_key, x_axis, y_axis in axis_pairs:
        full_x_axis = copy.deepcopy(x_axis)
        full_y_axis = copy.deepcopy(y_axis)
        compact_x_axis = copy.deepcopy(x_axis)
        compact_y_axis = copy.deepcopy(y_axis)

        should_limit_x_axis_ticks = x_key == "xaxis" and "nticks" in x_axis

        if should_limit_x_axis_ticks:
            full_x_axis["nticks"] = FULL_WIDTH_X_AXIS_NTICKS
            compact_x_axis["nticks"] = COMPACT_X_AXIS_NTICKS

        if rotate_compact:
            compact_rotated_x_axis = _axis_for_rotated_position(
                source_axis=y_axis,
                destination_axis=x_axis,
            )
            compact_rotated_y_axis = _axis_for_rotated_position(
                source_axis=x_axis,
                destination_axis=y_axis,
            )
        else:
            compact_rotated_x_axis = copy.deepcopy(compact_x_axis)
            compact_rotated_y_axis = copy.deepcopy(compact_y_axis)

        full_layout[x_key] = full_x_axis
        full_layout[y_key] = full_y_axis
        compact_layout[x_key] = compact_x_axis
        compact_layout[y_key] = compact_y_axis
        compact_rotated_layout[x_key] = compact_rotated_x_axis
        compact_rotated_layout[y_key] = compact_rotated_y_axis

    if rotate_compact and rotate_subplot_grid:
        _position_rotated_subplot_grid(
            axis_pairs=axis_pairs,
            rotated_layout=compact_rotated_layout,
        )

    shapes = layout.get("shapes")
    if isinstance(shapes, (list, tuple)):
        full_layout["shapes"] = copy.deepcopy(shapes)
        compact_layout["shapes"] = copy.deepcopy(shapes)
        compact_rotated_layout["shapes"] = (
            [_rotate_shape(shape) for shape in shapes]
            if rotate_compact
            else copy.deepcopy(shapes)
        )

    annotations = layout.get("annotations")
    if isinstance(annotations, (list, tuple)):
        full_layout["annotations"] = copy.deepcopy(annotations)
        compact_layout["annotations"] = copy.deepcopy(annotations)
        compact_rotated_annotations = (
            [_rotate_annotation(annotation) for annotation in annotations]
            if rotate_compact
            else copy.deepcopy(annotations)
        )
        if rotate_compact and rotate_subplot_grid:
            _position_rotated_subplot_annotations(compact_rotated_annotations)
        compact_rotated_layout["annotations"] = compact_rotated_annotations

    if rotate_compact and rotate_subplot_grid:
        legend = copy.deepcopy(layout.get("legend", {}))
        legend.update(copy.deepcopy(ROTATED_SUBPLOT_LEGEND_CONFIG))
        compact_rotated_layout["legend"] = legend
        compact_rotated_layout["margin"] = copy.deepcopy(
            ROTATED_SUBPLOT_MARGIN_CONFIG
        )

    return full_layout, compact_layout, compact_rotated_layout


def _count_bar_categories(traces: list | tuple) -> int:
    """Count distinct category positions without double-counting stacked traces."""
    categories: list[tuple[Any, Any]] = []

    for trace in traces:
        if not isinstance(trace, Mapping) or trace.get("type") != "bar":
            continue

        x_values = trace.get("x", [])
        if not isinstance(x_values, (list, tuple)):
            continue

        x_axis_reference = trace.get("x", [])
        for category in x_values:
            category_position = (x_axis_reference, category)
            if category_position not in categories:
                categories.append(category_position)

    return len(categories)


def _calculate_compact_bar_chart_height(traces: list | tuple) -> int:
    number_of_bars = _count_bar_categories(traces)
    calculated_height = (
        COMPACT_CHART_BASE_HEIGHT + number_of_bars * COMPACT_CHART_HEIGHT_PER_BAR
    )
    return max(MINIMUM_COMPACT_CHART_HEIGHT, calculated_height)


def build_figure_config(
    *,
    figure: Any,
    rotate_compact: bool = False,
    rotate_subplot_grid: bool = False,
) -> dict[str, dict[str, Any]]:
    """Build full, compact and compact-rotated Plotly overrides."""
    if not isinstance(figure, Mapping):
        figure = {}

    traces = figure.get("data", [])
    if not isinstance(traces, (list, tuple)):
        traces = []

    layout = figure.get("layout", {})
    if not isinstance(layout, Mapping):
        layout = {}

    full_data = [
        _build_trace_override(trace, rotate=False)
        for trace in traces
        if isinstance(trace, Mapping)
    ]
    compact_data = [
        _build_trace_override(trace, rotate=False)
        for trace in traces
        if isinstance(trace, Mapping)
    ]
    compact_rotated_data = (
        [
            _build_trace_override(trace, rotate=True)
            for trace in traces
            if isinstance(trace, Mapping)
        ]
        if rotate_compact
        else copy.deepcopy(compact_data)
    )
    full_layout, compact_layout, compact_rotated_layout = _build_layout_configs(
        layout,
        rotate_compact=rotate_compact,
        rotate_subplot_grid=rotate_subplot_grid,
    )

    if rotate_compact:
        compact_rotated_layout["height"] = _calculate_compact_bar_chart_height(traces)

    return {
        "full": {"data": full_data, "layout": full_layout},
        "compact": {"data": compact_data, "layout": compact_layout},
        "compact_rotated": {
            "data": compact_rotated_data,
            "layout": compact_rotated_layout,
        },
    }
