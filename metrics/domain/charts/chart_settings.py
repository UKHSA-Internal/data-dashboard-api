from metrics.domain.charts import colour_scheme

TICK_FONT = {
    "family": "Arial",
    "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
}

X_AXIS_TEXT_TYPE = {
    "type": "-",
    "dtick": None,
    "tickformat": None,
}

X_AXIS_DATE_TYPE = {
    "type": "date",
    "dtick": "M1",
    "tickformat": "%b %Y",
}

X_AXIS_SETTINGS = {
    "showgrid": False,
    "zeroline": False,
    "showline": False,
    "ticks": "outside",
    "tickson": "boundaries",
    "tickfont": TICK_FONT,
}

Y_AXIS_SETTINGS = {
    "showgrid": False,
    "showticklabels": False,
    "tickfont": TICK_FONT,
}


CHART_SETTINGS = {
    "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
    "margin": {
        "l": 0,
        "r": 0,
        "b": 0,
        "t": 0,
    },
    "autosize": False,
    "xaxis": X_AXIS_SETTINGS,
    "yaxis": Y_AXIS_SETTINGS,
}
