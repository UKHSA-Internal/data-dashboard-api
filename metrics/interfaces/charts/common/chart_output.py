from dataclasses import dataclass

import plotly.graph_objects

HEX_COLOUR_BLACK = "#0b0c0c"


@dataclass
class ChartOutput:
    figure: plotly.graph_objects.Figure
    description: str
    is_headline: bool
    is_subplot: bool = False

    @property
    def interactive_chart_figure_output(self) -> dict:
        self._add_settings_for_interactive_charts()
        return self.figure.to_dict()

    @property
    def _interactive_charts_font_css_var(self):
        return "var(--font-primary), arial, sans-serif"

    def _add_settings_for_interactive_charts(self):
        self._unset_width()
        self._apply_font_to_ticks()
        self._apply_x_axis_styling()

        self._apply_autosizing()

        self._apply_hover_label_styling()
        self._disable_clicks_on_legend()
        self._apply_hover_template_to_all_plots()

    def _unset_width(self):
        self.figure.layout.width = None

    def _apply_font_to_ticks(self):
        self.figure.layout.xaxis.tickfont.update(
            family=self._interactive_charts_font_css_var
        )
        self.figure.layout.yaxis.tickfont.update(
            family=self._interactive_charts_font_css_var
        )

    def _apply_x_axis_styling(self):
        self.figure.layout.xaxis.showline = True
        self.figure.layout.xaxis.showspikes = False

    def _apply_autosizing(self):
        self.figure.layout.autosize = True

    def _apply_hover_label_styling(self):
        self.figure.layout.hoverlabel.bgcolor = HEX_COLOUR_BLACK
        self.figure.layout.hoverlabel.bordercolor = HEX_COLOUR_BLACK
        self.figure.layout.hoverlabel.font.update(
            size=16,
            color="white",
            family=self._interactive_charts_font_css_var,
        )

    def _apply_hover_template_to_all_plots(self):
        """
        Note:
            the plots hovertemplate property is used by plotly react
            on the front-end to control hover text formatting.

            To format dates using the hovertemplate you can use
            `D3-time-format` specifiers. examples can be found at:
            https://d3js.org/d3-time-format
        """
        hover_template = "%{y:,} (%{x|%d %b %Y})<extra></extra>"

        if self.is_headline:
            hover_template = "%{y:,} (%{x})<extra></extra>"

        if self.is_subplot:
            hover_template = "%{y} %{fullData.name}<extra></extra>"

        for plot in self.figure.data:
            plot.hovertemplate = hover_template

    def _disable_clicks_on_legend(self):
        self.figure.layout.legend.itemclick = False
        self.figure.layout.legend.itemdoubleclick = False
