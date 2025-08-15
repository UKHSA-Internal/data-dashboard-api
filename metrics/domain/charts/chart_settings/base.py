import logging
from abc import ABC, abstractmethod
from decimal import Decimal

from metrics.domain.charts import colour_scheme
from metrics.domain.charts.type_hints import DICT_OF_STR_ONLY
from metrics.domain.common.utils import DEFAULT_CHART_WIDTH
from metrics.domain.models.plots import ChartGenerationPayload

logger = logging.getLogger(__name__)


class ChartSettings(ABC):
    narrow_chart_width = DEFAULT_CHART_WIDTH

    def __init__(self, *, chart_generation_payload: ChartGenerationPayload):
        self._chart_generation_payload = chart_generation_payload

    @property
    def width(self) -> int:
        return self._chart_generation_payload.chart_width

    @property
    def height(self) -> int:
        return self._chart_generation_payload.chart_height

    @property
    def y_axis_minimum_value(self) -> int | Decimal:
        return self._chart_generation_payload.y_axis_minimum_value

    @property
    def y_axis_maximum_value(self) -> int | Decimal | None:
        return self._chart_generation_payload.y_axis_maximum_value

    @staticmethod
    def _get_tick_font_config() -> DICT_OF_STR_ONLY:
        return {
            "family": "Arial",
            "color": colour_scheme.RGBAColours.DARK_BLUE_GREY.stringified,
        }

    @abstractmethod
    def _get_x_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
        """prepare initial x_axis config properties dict"""

    @abstractmethod
    def _get_y_axis_config(self) -> dict[str, str | bool | DICT_OF_STR_ONLY]:
        """prepare initial y_axis config properties dict"""

    def _get_base_chart_config(self):
        return {
            "paper_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "plot_bgcolor": colour_scheme.RGBAColours.WHITE.stringified,
            "hoverlabel": {
                "align": "left",
                "bgcolor": "white",
            },
            "margin": {
                "l": 0,
                "r": 0,
                "b": 0,
                "t": 0,
            },
            "autosize": False,
            "xaxis": self._get_x_axis_config(),
            "yaxis": self._get_y_axis_config(),
            "height": self.height,
            "width": self.width,
            "showlegend": True,
        }

    def _get_date_tick_format(self, *, weekly: bool = False) -> str:
        if weekly:
            return "%d %b<br>%Y"

        return "%b %Y" if self.width > self.narrow_chart_width else "%b<br>%Y"
