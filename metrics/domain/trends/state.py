import datetime
from enum import Enum

from pydantic.main import BaseModel

from metrics.domain.charts.line_with_shaded_section.information import (
    is_metric_improving,
)


class Colour(Enum):
    """The colour of the associated trend block"""

    green = 1
    neutral = 0
    red = -1


class ArrowDirection(Enum):
    """The direction of the associated trend arrow"""

    up = 1
    neutral = 0
    down = -1


TREND_AS_DICT = dict[str, str | int | float]


class Trend(BaseModel):
    metric_name: str
    metric_value: int | float
    metric_period_end: datetime.date | str
    percentage_metric_name: str
    percentage_metric_value: float
    percentage_metric_period_end: datetime.date | str

    def model_dump(self, *args, **kwargs) -> TREND_AS_DICT:
        data = super().model_dump(*args, **kwargs)
        return self._add_arrow_direction_and_colour(data=data)

    def _add_arrow_direction_and_colour(self, data: TREND_AS_DICT) -> TREND_AS_DICT:
        data["direction"] = self.direction
        data["colour"] = self.colour
        return data

    @property
    def direction(self) -> str:
        """Returns the direction in which the trend arrow should be pointed towards.

        Returns:
            str: The name of the direction.
                Can be either "up", "neutral" or "down"
                depending on the `metric_value`

        """
        if self.metric_value > 0:
            return ArrowDirection.up.name

        if self.metric_value == 0:
            return ArrowDirection.neutral.name

        return ArrowDirection.down.name

    @property
    def colour(self) -> str:
        """Returns the colour for which the trend should be considered.

        Returns:
            str: The name of the colour.
                Can be either "green", "neutral" or "red"
                depending on the `metric_value`

        """
        if self.metric_value == 0:
            return Colour.neutral.name

        metric_is_improving = is_metric_improving(
            change_in_metric_value=self.metric_value,
            metric_name=self.metric_name,
        )

        if metric_is_improving:
            return Colour.green.name

        return Colour.red.name
