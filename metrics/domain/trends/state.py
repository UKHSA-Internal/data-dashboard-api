from enum import Enum
from typing import Dict, Union

from pydantic.main import BaseModel

from metrics.domain.charts.line_with_shaded_section.information import (
    is_metric_improving,
)


class Colour(Enum):
    """The colour that the front-end should paint the box.
        The colour indicates whether the metric is improving or worsening

    Red: Getting worse
    Green: Improving
    Neutral: No change

    The direction (-1, 0, 1) is determined by get_metric_state
    """

    green = 1
    neutral = 0
    red = -1


class ArrowDirection(Enum):
    """The arrow direction that the front-end should display.
        Direction indicates whether the metric has gone up or down

    The direction (-1, 0, 1) is determined by get_arrow_direction
    """

    up = 1
    neutral = 0
    down = -1


TREND_AS_DICT = Dict[str, Union[str, float]]


class Trend(BaseModel):
    metric_name: str
    metric_value: Union[int, float]
    percentage_metric_name: str
    percentage_metric_value: float

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)

        data = self._remove_metric_names(data=data)
        return self._add_arrow_direction_and_colour(data=data)

    @staticmethod
    def _remove_metric_names(data: TREND_AS_DICT) -> TREND_AS_DICT:
        data.pop("metric_name")
        data.pop("percentage_metric_name")
        return data

    def _add_arrow_direction_and_colour(self, data: TREND_AS_DICT) -> TREND_AS_DICT:
        data["direction"] = self.direction
        data["colour"] = self.colour
        return data

    @property
    def direction(self) -> str:
        if self.metric_value > 0:
            return ArrowDirection.up.name

        if self.metric_value == 0:
            return ArrowDirection.neutral.name

        return ArrowDirection.down.name

    @property
    def colour(self) -> str:
        if self.metric_value == 0:
            return Colour.neutral.name

        metric_is_improving = is_metric_improving(
            change_in_metric_value=self.metric_value,
            metric_name=self.metric_name,
        )

        if metric_is_improving:
            return Colour.green.name

        return Colour.red.name
