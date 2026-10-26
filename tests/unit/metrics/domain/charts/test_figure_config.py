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

        assert config["full"]["layout"]["xaxis"]["nticks"] == 13
        assert config["compact"]["layout"]["xaxis"]["nticks"] == 5
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

    def test_returns_a_consistent_contract_for_an_empty_figure(self):
        assert build_figure_config(figure={}) == {
            "full": {"data": [], "layout": {}},
            "compact": {"data": [], "layout": {}},
        }
