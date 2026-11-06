from metrics.domain.charts.chart_settings.single_category import (
    COMPACT_X_AXIS_NTICKS,
    FULL_WIDTH_X_AXIS_NTICKS,
)
from metrics.domain.charts.figure_config import build_figure_config

MINIMUM_EXPECTED_COMPACT_HEIGHT = 400
EXPECTED_NINE_BAR_COMPACT_HEIGHT = 425


class TestBuildFigureConfig:
    def test_builds_three_non_rotated_modes_for_ineligible_chart(self):
        figure = {
            "data": [
                {
                    "type": "scatter",
                    "x": ["2026-01-01"],
                    "y": [10],
                    "hovertemplate": "%{x|%d %b %Y}: %{y:,}",
                }
            ],
            "layout": {
                "xaxis": {"type": "date", "nticks": 5},
                "yaxis": {"title": {"text": "Cases"}},
                "shapes": [{"type": "line", "x0": 0, "x1": 1}],
                "annotations": [{"text": "Latest data"}],
            },
        }

        config = build_figure_config(figure=figure)

        assert config["full"]["layout"]["xaxis"]["nticks"] == (FULL_WIDTH_X_AXIS_NTICKS)
        assert config["compact"]["layout"]["xaxis"]["nticks"] == (COMPACT_X_AXIS_NTICKS)
        assert config["compact_rotated"] == config["compact"]
        assert config["compact"]["data"] == config["full"]["data"]

    def test_keeps_compact_unrotated_and_rotates_compact_rotated(self):
        figure = {
            "data": [
                {
                    "type": "bar",
                    "x": [f"Category {index}" for index in range(7)],
                    "y": list(range(7)),
                    "hovertemplate": "%{x}: %{y:.1f}",
                    "error_y": {"array": [2] * 7, "visible": True},
                }
            ],
            "layout": {
                "xaxis": {
                    "title": {
                        "text": "Category",
                        "font": {"family": "Arial", "color": "#0b0c0c"},
                    }
                },
                "yaxis": {"title": {"text": "Percentage"}},
                "margin": {"l": 0, "r": 0, "b": 0, "t": 0},
                "shapes": [
                    {
                        "type": "line",
                        "x0": 0,
                        "x1": 1,
                        "y0": 90,
                        "y1": 90,
                        "xref": "paper",
                        "yref": "y",
                    }
                ],
            },
        }

        config = build_figure_config(figure=figure, rotate_compact=True)

        assert config["compact"]["data"] == config["full"]["data"]
        assert config["compact"]["data"][0]["orientation"] == "v"
        assert config["compact"]["layout"]["xaxis"]["title"]["text"] == ("Category")

        rotated_trace = config["compact_rotated"]["data"][0]
        assert rotated_trace["x"] == list(range(7))
        assert rotated_trace["y"] == [f"Category {index}" for index in range(7)]
        assert rotated_trace["orientation"] == "h"
        assert rotated_trace["hovertemplate"] == "%{y}: %{x:.1f}"
        assert rotated_trace["error_x"] == {
            "array": [2] * 7,
            "visible": True,
        }
        assert rotated_trace["error_y"] == {"visible": False}

        rotated_layout = config["compact_rotated"]["layout"]
        assert rotated_layout["xaxis"]["title"]["text"] == "Percentage"
        assert "title" not in rotated_layout["yaxis"]
        assert rotated_layout["yaxis"]["tickmode"] == "array"
        assert rotated_layout["yaxis"]["tickvals"] == [
            f"Category {index}" for index in range(7)
        ]
        assert rotated_layout["yaxis"]["ticktext"] == [
            f"Category {index}" for index in range(7)
        ]
        assert rotated_layout["yaxis"]["tickangle"] == 0
        assert rotated_layout["yaxis"]["autorange"] == "reversed"
        assert rotated_layout["annotations"] == [
            {
                "text": "Category",
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": 1.05,
                "xanchor": "center",
                "yanchor": "bottom",
                "showarrow": False,
                "align": "left",
                "textangle": 0,
                "font": {"family": "Arial", "color": "#0b0c0c", "size": 14},
            }
        ]
        assert rotated_layout["margin"] == {"l": 0, "r": 0, "b": 0, "t": 50}
        assert rotated_layout["height"] == MINIMUM_EXPECTED_COMPACT_HEIGHT
        assert rotated_layout["shapes"] == [
            {
                "type": "line",
                "x0": 90,
                "x1": 90,
                "y0": 0,
                "y1": 1,
                "xref": "x",
                "yref": "paper",
            }
        ]

    def test_sizes_rotated_height_by_distinct_stacked_bar_categories(self):
        categories = [f"Category {index}" for index in range(9)]
        config = build_figure_config(
            figure={
                "data": [
                    {"type": "bar", "x": categories, "y": list(range(9))},
                    {"type": "bar", "x": categories, "y": list(range(9))},
                ],
                "layout": {},
            },
            rotate_compact=True,
        )

        assert config["compact_rotated"]["layout"]["height"] == (
            EXPECTED_NINE_BAR_COMPACT_HEIGHT
        )
        assert "height" not in config["compact"]["layout"]

    @staticmethod
    def _build_bar_figure(*, stacked: bool) -> dict:
        legend = {
            "orientation": "h",
            "x": 0.5,
            "xanchor": "center",
            "y": 1,
            "yanchor": "bottom",
        }
        layout = {
            "legend": legend,
            "xaxis": {},
            "yaxis": {},
        }
        if stacked:
            layout["barmode"] = "stack"

        return {
            "data": [
                {"type": "bar", "name": "First", "x": ["A"], "y": [10]},
                {"type": "bar", "name": "Second", "x": ["A"], "y": [20]},
            ],
            "layout": layout,
        }

    def test_leaves_legend_order_unset_for_non_rotated_stacked_bar_chart(self):
        figure = self._build_bar_figure(stacked=True)

        config = build_figure_config(figure=figure)

        for mode in ("full", "compact", "compact_rotated"):
            assert "legend" not in config[mode]["layout"]
        assert "traceorder" not in figure["layout"]["legend"]

    def test_uses_bottom_legend_with_normal_order_for_rotated_stacked_bar_chart(self):
        figure = self._build_bar_figure(stacked=True)

        config = build_figure_config(figure=figure, rotate_compact=True)

        assert config["compact_rotated"]["layout"]["legend"] == {
            **figure["layout"]["legend"],
            "y": -0.2,
            "yanchor": "top",
            "traceorder": "normal",
        }
        assert "legend" not in config["full"]["layout"]
        assert "legend" not in config["compact"]["layout"]
        assert "traceorder" not in figure["layout"]["legend"]

    def test_leaves_legend_order_unset_for_non_rotated_non_stacked_bar_chart(self):
        figure = self._build_bar_figure(stacked=False)

        config = build_figure_config(figure=figure)

        for mode in ("full", "compact", "compact_rotated"):
            assert "legend" not in config[mode]["layout"]
        assert "traceorder" not in figure["layout"]["legend"]

    def test_uses_bottom_legend_without_setting_order_for_rotated_non_stacked_chart(
        self,
    ):
        figure = self._build_bar_figure(stacked=False)

        config = build_figure_config(figure=figure, rotate_compact=True)

        assert config["compact_rotated"]["layout"]["legend"] == {
            **figure["layout"]["legend"],
            "y": -0.2,
            "yanchor": "top",
        }
        assert "traceorder" not in config["compact_rotated"]["layout"]["legend"]
        assert "traceorder" not in figure["layout"]["legend"]

    def test_wraps_long_rotated_labels(self):
        long_category = "Bournemouth, Christchurch and Poole"
        categories = [long_category, *[f"Category {index}" for index in range(7)]]

        config = build_figure_config(
            figure={
                "data": [{"type": "bar", "x": categories, "y": list(range(8))}],
                "layout": {"xaxis": {}, "yaxis": {}},
            },
            rotate_compact=True,
        )

        rotated_layout = config["compact_rotated"]["layout"]
        assert rotated_layout["yaxis"]["tickvals"] == categories
        assert rotated_layout["yaxis"]["ticktext"][0] == (
            "Bournemouth,<br>Christchurch and<br>Poole"
        )
        assert rotated_layout["yaxis"]["autorange"] == "reversed"
        assert rotated_layout["height"] == MINIMUM_EXPECTED_COMPACT_HEIGHT

        assert "ticktext" not in config["compact"]["layout"]["xaxis"]
        assert "autorange" not in config["compact"]["layout"]["xaxis"]

    def test_preserves_non_string_and_empty_rotated_category_labels(self):
        categories = [1, ""]

        config = build_figure_config(
            figure={
                "data": [{"type": "bar", "x": categories, "y": [10, 20]}],
                "layout": {"xaxis": {}, "yaxis": {}},
            },
            rotate_compact=True,
        )

        rotated_y_axis = config["compact_rotated"]["layout"]["yaxis"]
        assert rotated_y_axis["tickvals"] == categories
        assert rotated_y_axis["ticktext"] == categories

    def test_rotates_subplot_axis_positions_and_axis_references(self):
        config = build_figure_config(
            figure={
                "data": [{"type": "bar", "x": ["A"], "y": [1]}],
                "layout": {
                    "xaxis2": {
                        "anchor": "y2",
                        "domain": [0.0, 0.4],
                        "matches": "x",
                        "scaleanchor": None,
                    },
                    "yaxis2": {
                        "position": 0.5,
                        "matches": "y",
                        "scaleanchor": "y2",
                    },
                },
            },
            rotate_compact=True,
        )

        rotated_layout = config["compact_rotated"]["layout"]
        assert rotated_layout["xaxis2"] == {
            "anchor": "y2",
            "domain": [0.0, 0.4],
            "matches": "x",
            "scaleanchor": "x2",
        }
        assert rotated_layout["yaxis2"] == {
            "position": 0.5,
            "matches": "y",
            "scaleanchor": None,
        }

    def test_rotates_partial_path_shapes(self):
        config = build_figure_config(
            figure={
                "data": [{"type": "bar", "x": ["A"], "y": [1]}],
                "layout": {
                    "shapes": [
                        {
                            "type": "path",
                            "path": "M 1 2 L -3.5 .4",
                            "x0": 10,
                            "y1": 20,
                            "xref": "x2",
                        }
                    ]
                },
            },
            rotate_compact=True,
        )

        assert config["compact_rotated"]["layout"]["shapes"] == [
            {
                "type": "path",
                "path": "M 2 1 L .4 -3.5",
                "y0": 10,
                "x1": 20,
                "xref": "x",
                "yref": "y2",
            }
        ]

    def test_rotates_axis_and_paper_annotations_but_not_watermarks(self):
        watermark = {
            "text": "UKHSA",
            "x": 0.5,
            "y": 0.5,
            "xref": "paper",
            "yref": "paper",
        }
        config = build_figure_config(
            figure={
                "data": [{"type": "bar", "x": ["A"], "y": [1]}],
                "layout": {
                    "xaxis": {"title": {"text": "Category"}},
                    "yaxis": {},
                    "annotations": [
                        watermark,
                        {
                            "text": "Threshold",
                            "x": 1,
                            "y": 2,
                            "xref": "x2",
                            "yref": "y2",
                            "xanchor": "unsupported",
                            "yanchor": "unsupported",
                        },
                        {
                            "text": "Axis title",
                            "x": 0.2,
                            "y": 0.8,
                            "xref": "paper",
                            "yref": "paper",
                            "xanchor": "left",
                            "yanchor": "top",
                        },
                    ],
                },
            },
            rotate_compact=True,
        )

        annotations = config["compact_rotated"]["layout"]["annotations"]
        assert annotations[0] == watermark
        assert annotations[1] == {
            "text": "Threshold",
            "x": 2,
            "y": 1,
            "xref": "x2",
            "yref": "y2",
            "xanchor": "auto",
            "yanchor": "auto",
        }
        assert annotations[2] == {
            "text": "Axis title",
            "x": 0.8,
            "y": 0.2,
            "xref": "paper",
            "yref": "paper",
            "xanchor": "right",
            "yanchor": "bottom",
            "textangle": -90,
        }
        assert annotations[3] == {
            "text": "Category",
            "xref": "paper",
            "yref": "paper",
            "x": 0,
            "y": 1.05,
            "xanchor": "center",
            "yanchor": "bottom",
            "showarrow": False,
            "align": "left",
            "textangle": 0,
            "font": {"size": 14},
        }

    def test_handles_invalid_figure_parts_and_trace_values(self):
        empty_mode = {"data": [], "layout": {}}
        assert build_figure_config(figure=None) == {
            "full": empty_mode,
            "compact": empty_mode,
            "compact_rotated": empty_mode,
        }

        config = build_figure_config(
            figure={
                "data": [
                    None,
                    {"type": "scatter"},
                    {
                        "type": "bar",
                        "x": "not-a-category-list",
                        "y": [1],
                        "hovertemplate": None,
                    },
                ],
                "layout": "not-a-layout",
            },
            rotate_compact=True,
        )

        assert config["compact_rotated"] == {
            "data": [
                {},
                {
                    "x": [1],
                    "y": "not-a-category-list",
                    "hovertemplate": None,
                    "orientation": "h",
                },
            ],
            "layout": {"height": MINIMUM_EXPECTED_COMPACT_HEIGHT},
        }

        assert build_figure_config(
            figure={"data": "not-traces", "layout": "not-a-layout"}
        ) == {
            "full": empty_mode,
            "compact": empty_mode,
            "compact_rotated": empty_mode,
        }

    def test_returns_consistent_three_mode_contract_for_empty_figure(self):
        empty_mode = {"data": [], "layout": {}}

        assert build_figure_config(figure={}) == {
            "full": empty_mode,
            "compact": empty_mode,
            "compact_rotated": empty_mode,
        }
