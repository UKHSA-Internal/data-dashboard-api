from django.db.models import Manager

from metrics.api.settings import auth
from metrics.data.models.core_models import CoreHeadline, Topic
from metrics.domain.models.trends import TrendsParameters
from metrics.domain.trends.state import TREND_AS_DICT, Trend

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects
DEFAULT_TOPIC_MANAGER = Topic.objects


class TrendNumberDataNotFoundError(Exception):
    def __init__(self, *, topic_name: str, metric_name: str):
        message = f"Data for `{topic_name}` and `{metric_name}` could not be found."
        super().__init__(message)


class TrendsInterface:
    def __init__(
        self,
        *,
        trend_parameters: TrendsParameters,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
        topic_manager: Manager = DEFAULT_TOPIC_MANAGER,
    ):
        self.trend_parameters = trend_parameters
        self.core_headline_manager = core_headline_manager
        self.topic_manager = topic_manager

    def get_latest_metric_value(self, *, params: dict) -> CoreHeadline:
        """Gets the value for the record associated with the given `metric_name`

        Returns:
            The full matching `CoreHeadline` object
            which is the latest associated record
            which has also been released from embargo

        Raises:
            TrendNumberDataNotFoundError:
                If no data is found for the given combination of
                `topic` / `metric` / `percentage_metric`.

        """
        core_headline: CoreHeadline | None = (
            self.core_headline_manager.get_latest_headline(**params)
        )

        if core_headline is None:
            raise TrendNumberDataNotFoundError(
                topic_name=self.trend_parameters.topic_name,
                metric_name=params["metric"],
            )

        return core_headline

    def get_trend(self) -> Trend:
        """Creates a `Trend` model which represents the trend block.

        Returns:
            `Trend` model with the associated metric values, period_end dates
            and inherent colour and direction calculation logic

        Raises:
            TrendNumberDataNotFoundError:
                If no data is found for the given combination of
                `topic` / `metric` / `percentage_metric`.

        """
        main_metric_params = self.trend_parameters.to_dict_for_main_metric_query()
        percentage_metric_params = (
            self.trend_parameters.to_dict_for_percentage_metric_query()
        )

        if auth.AUTH_ENABLED:
            self._add_theme_info_to_params(params=main_metric_params)
            self._add_theme_info_to_params(params=percentage_metric_params)

        core_headline_percentage_metric: CoreHeadline = self.get_latest_metric_value(
            params=percentage_metric_params
        )
        core_headline_metric: CoreHeadline = self.get_latest_metric_value(
            params=main_metric_params
        )

        return Trend(
            metric_name=self.trend_parameters.metric_name,
            metric_value=core_headline_metric.metric_value,
            metric_period_end=core_headline_metric.period_end,
            percentage_metric_name=self.trend_parameters.percentage_metric_name,
            percentage_metric_value=core_headline_percentage_metric.metric_value,
            percentage_metric_period_end=core_headline_percentage_metric.period_end,
        )

    def _add_theme_info_to_params(self, *, params: dict) -> None:
        topic = self.topic_manager.get_by_name(name=self.trend_parameters.topic_name)
        params["theme"] = topic.sub_theme.theme.name
        params["sub_theme"] = topic.sub_theme.name


def generate_trend_numbers(
    *,
    trend_parameters: TrendsParameters,
) -> TREND_AS_DICT:
    """Gets the trend data for the given metric names.

    Args:
        trend_parameters: An enriched `TrendsParameters` model
            containing the requested parameters

    Returns:
        Dict containing the serialized trends data.
            E.g.
                {
                  "metric_name": "new_cases_7days_change",
                  "metric_value": -692,
                  "metric_period_end": "2024-02-29",
                  "percentage_metric_name": "new_deaths_7days_change_percentage",
                  "percentage_metric_value": 3.1,
                  "percentage_metric_period_end": "2024-02-29",
                  "direction": "down",
                  "colour": "green"
                }

    Raises:
        `TrendNumberDataNotFoundError`: If no data is found
            for the given combination of
            `topic` / `metric` / `percentage_metric`

    """
    interface = TrendsInterface(trend_parameters=trend_parameters)

    trend: Trend = interface.get_trend()
    data: TREND_AS_DICT = trend.model_dump()

    return data
