from metrics.domain.charts.chart_settings.single_category import (
    COMPACT_X_AXIS_NTICKS,
    FULL_WIDTH_X_AXIS_NTICKS,
)
from metrics.domain.charts.figure_config import build_figure_config


class TestBuildFigureConfig:
    def test_builds_responsive_tick_limits_without_rotating_time_series(self):
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
            },
        }

        config = build_figure_config(figure=figure)

        assert config["full"]["layout"]["xaxis"]["nticks"] == FULL_WIDTH_X_AXIS_NTICKS
        assert config["compact"]["layout"]["xaxis"]["nticks"] == COMPACT_X_AXIS_NTICKS
        assert config["compact"]["data"] == config["full"]["data"]

    def test_rotates_bar_data_axes_tooltips_errors_and_threshold_details(self):
        figure = {
            "data": [
                {
                    "type": "bar",
                    "x": ["Category A"],
                    "y": [80],
                    "hovertemplate": "%{x}: %{y:.1f}",
                    "error_y": {"array": [2], "visible": True},
                }
            ],
            "layout": {
                "xaxis": {"title": {"text": "Category"}},
                "yaxis": {"title": {"text": "Percentage"}},
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
                "annotations": [
                    {
                        "text": "Target",
                        "x": 1,
                        "y": 90,
                        "xref": "paper",
                        "yref": "y",
                        "xanchor": "right",
                        "yanchor": "bottom",
                    }
                ],
            },
        }

        config = build_figure_config(figure=figure, rotate_compact=True)
        compact_layout = config["compact"]["layout"]

        assert config["full"]["data"] == [
            {
                "x": ["Category A"],
                "y": [80],
                "hovertemplate": "%{x}: %{y:.1f}",
                "error_y": {"array": [2], "visible": True},
                "orientation": "v",
            }
        ]
        assert config["compact"]["data"] == [
            {
                "x": [80],
                "y": ["Category A"],
                "hovertemplate": "%{y}: %{x:.1f}",
                "error_y": {"visible": False},
                "error_x": {"array": [2], "visible": True},
                "orientation": "h",
            }
        ]
        assert compact_layout["xaxis"]["title"]["text"] == "Percentage"
        assert compact_layout["yaxis"]["title"]["text"] == "Category"
        assert compact_layout["shapes"] == [
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
        assert compact_layout["annotations"] == [
            {
                "text": "Target",
                "x": 90,
                "y": 1,
                "xref": "x",
                "yref": "paper",
                "xanchor": "left",
                "yanchor": "top",
            }
        ]

    def test_preserves_each_subplot_axis_position_when_rotating(self):
        figure = {
            "data": [],
            "layout": {
                "xaxis": {"domain": [0, 0.4], "anchor": "y", "title": "A"},
                "yaxis": {"domain": [0, 1], "anchor": "x", "title": "Value A"},
                "xaxis2": {"domain": [0.6, 1], "anchor": "y2", "title": "B"},
                "yaxis2": {"domain": [0, 1], "anchor": "x2", "title": "Value B"},
            },
        }

        config = build_figure_config(figure=figure, rotate_compact=True)
        compact_layout = config["compact"]["layout"]

        assert compact_layout["xaxis"] == {
            "domain": [0, 0.4],
            "anchor": "y",
            "title": "Value A",
        }
        assert compact_layout["yaxis"] == {
            "domain": [0, 1],
            "anchor": "x",
            "title": "A",
        }
        assert compact_layout["xaxis2"] == {
            "domain": [0.6, 1],
            "anchor": "y2",
            "title": "Value B",
        }
        assert compact_layout["yaxis2"] == {
            "domain": [0, 1],
            "anchor": "x2",
            "title": "B",
        }

    def test_rotates_axis_references_paths_and_paper_annotations(self):
        figure = {
            "data": [],
            "layout": {
                "xaxis": {
                    "title": "Category",
                    "matches": "x2",
                    "scaleanchor": "y",
                },
                "yaxis": {
                    "title": "Value",
                    "matches": None,
                    "scaleanchor": "paper",
                },
                "shapes": [
                    {
                        "type": "path",
                        "path": "M 1 2 L -3.5 .4",
                    },
                    {
                        "type": "path",
                        "path": None,
                    },
                    {
                        "type": "line",
                        "x0": 1,
                        "y1": 2,
                        "xref": "x2",
                        "yref": "y2",
                    },
                ],
                "annotations": [
                    {
                        "text": "Watermark",
                        "xref": "paper",
                        "yref": "paper",
                    },
                    {
                        "text": "Axis title",
                        "x": 0.5,
                        "y": 0.25,
                        "xref": "paper",
                        "yref": "paper",
                        "xanchor": "unexpected",
                        "yanchor": "unexpected",
                        "textangle": 0,
                    },
                    {
                        "text": "Axis note",
                        "xref": "x2",
                        "yref": "y2",
                    },
                ],
            },
        }

        compact_layout = build_figure_config(figure=figure, rotate_compact=True)[
            "compact"
        ]["layout"]

        assert compact_layout["xaxis"]["matches"] is None
        assert compact_layout["xaxis"]["scaleanchor"] == "paper"
        assert compact_layout["yaxis"]["matches"] == "y2"
        assert compact_layout["yaxis"]["scaleanchor"] == "x"
        assert compact_layout["shapes"][0]["path"] == "M 2 1 L .4 -3.5"
        assert compact_layout["shapes"][1]["path"] is None
        assert compact_layout["shapes"][2] == {
            "type": "line",
            "x1": 2,
            "y0": 1,
            "xref": "x2",
            "yref": "y2",
        }
        assert compact_layout["annotations"][0] == figure["layout"]["annotations"][0]
        assert compact_layout["annotations"][1] == {
            "text": "Axis title",
            "x": 0.25,
            "y": 0.5,
            "xref": "paper",
            "yref": "paper",
            "xanchor": "auto",
            "yanchor": "auto",
            "textangle": -90,
        }
        assert compact_layout["annotations"][2] == {
            "text": "Axis note",
            "xref": "x2",
            "yref": "y2",
        }

    def test_preserves_non_rotated_categorical_layout_details(self):
        figure = {
            "data": [],
            "layout": {
                "xaxis": {"type": "category"},
                "yaxis": {"title": "Value"},
                "shapes": [{"type": "line", "x0": 0, "y0": 10}],
                "annotations": [{"text": "Target", "x": 0, "y": 10}],
            },
        }

        config = build_figure_config(figure=figure)

        assert "nticks" not in config["full"]["layout"]["xaxis"]
        assert "nticks" not in config["compact"]["layout"]["xaxis"]
        assert config["compact"]["layout"]["shapes"] == figure["layout"]["shapes"]
        assert (
            config["compact"]["layout"]["annotations"]
            == figure["layout"]["annotations"]
        )

    def test_only_rotates_bar_traces_and_handles_missing_optional_fields(self):
        figure = {
            "data": [
                {
                    "type": "scatter",
                    "x": ["Category A"],
                    "y": [10],
                    "hovertemplate": None,
                },
                {
                    "type": "bar",
                    "x": ["Category B"],
                    "y": [20],
                    "hovertemplate": None,
                    "orientation": "v",
                },
                {
                    "type": "bar",
                    "x": ["Category C"],
                    "y": [30],
                },
            ],
            "layout": {},
        }

        compact_data = build_figure_config(figure=figure, rotate_compact=True)[
            "compact"
        ]["data"]

        assert compact_data == [
            {
                "x": ["Category A"],
                "y": [10],
                "hovertemplate": None,
            },
            {
                "x": [20],
                "y": ["Category B"],
                "hovertemplate": None,
                "orientation": "h",
            },
            {
                "x": [30],
                "y": ["Category C"],
                "orientation": "h",
            },
        ]

    def test_ignores_invalid_figure_data_layout_and_axis_pairs(self):
        assert build_figure_config(figure=None) == {
            "full": {"data": [], "layout": {}},
            "compact": {"data": [], "layout": {}},
        }

        config = build_figure_config(
            figure={
                "data": "not-a-trace-list",
                "layout": "not-a-layout",
            }
        )
        assert config == {
            "full": {"data": [], "layout": {}},
            "compact": {"data": [], "layout": {}},
        }

        config = build_figure_config(
            figure={
                "data": [None],
                "layout": {
                    "xaxis": [],
                    "xaxis2": {},
                    "title": "Ignored",
                },
            }
        )
        assert config == {
            "full": {"data": [], "layout": {}},
            "compact": {"data": [], "layout": {}},
        }

    def test_returns_a_consistent_contract_for_an_empty_figure(self):
        assert build_figure_config(figure={}) == {
            "full": {"data": [], "layout": {}},
            "compact": {"data": [], "layout": {}},
        }
