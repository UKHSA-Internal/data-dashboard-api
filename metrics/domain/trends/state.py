from enum import Enum

from pydantic.main import BaseModel

from metrics.domain.charts.line_with_shaded_section.information import is_metric_improving


class Colour(Enum):
    """The colour that the front-end should paint the box.
        The colour indicates whether the metric is improving or worsening

    Red: Getting worse
    Green: Improving
    Neutral: No change

    The direction (-1, 0, 1) is determined by get_metric_state
    """

    red = -1
    neutral = 0
    green = 1


class ArrowDirection(Enum):
    """The arrow direction that the front-end should display.
        Direction indicates whether the metric has gone up or down

    The direction (-1, 0, 1) is determined by get_arrow_direction
    """

    down = -1
    neutral = 0
    up = 1


class Trend(BaseModel):
    metric_name: str
    metric_value: float
    percentage_metric_name: str
    percentage_metric_value: float

    @property
    def direction(self) -> ArrowDirection:
        if self.metric_value > 0:
            return ArrowDirection.up

        if self.metric_value == 0:
            return ArrowDirection.neutral

        return ArrowDirection.down

    @property
    def colour(self) -> Colour:
        if self.metric_value:
            return Colour.neutral

        metric_is_improving = is_metric_improving(
            change_in_metric_value=self.metric_value,
            metric_name=self.metric_name,
        )

        if metric_is_improving:
            return Colour.green

        return Colour.red


def get_metric_state(change_in_metric_value: float, metric_name: str) -> int:
    """Returns metric state.
    1 = positive change
    0 = no change
    -1 = negative change
    """
    if change_in_metric_value == 0:
        return 0

    return (
        1
        if is_metric_improving(
            change_in_metric_value=change_in_metric_value, metric_name=metric_name
        )
        else -1
    )