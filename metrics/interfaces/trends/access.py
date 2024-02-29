from django.db.models import Manager

from metrics.data.models.core_models import CoreHeadline
from metrics.domain.trends.state import TREND_AS_DICT, Trend

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class TrendNumberDataNotFoundError(Exception):
    def __init__(self, topic_name: str, metric_name: str):
        message = f"Data for `{topic_name}` and `{metric_name}` could not be found."
        super().__init__(message)


class TrendsInterface:
    def __init__(
        self,
        topic_name: str,
        metric_name: str,
        percentage_metric_name: str,
        geography_name: str,
        geography_type_name: str,
        stratum_name: str,
        sex: str,
        age: str,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        self.topic_name = topic_name
        self.metric_name = metric_name
        self.percentage_metric_name = percentage_metric_name
        self.geography_name = geography_name
        self.geography_type_name = geography_type_name
        self.stratum_name = stratum_name
        self.sex = sex
        self.age = age
        self.core_headline_manager = core_headline_manager

    def get_latest_metric_value(self, metric_name: str) -> CoreHeadline:
        """Gets the value for the record associated with the given `metric_to_lookup`

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
            self.core_headline_manager.get_latest_headline(
                topic_name=self.topic_name,
                metric_name=metric_name,
                geography_name=self.geography_name,
                geography_type_name=self.geography_type_name,
                age=self.age,
                stratum_name=self.stratum_name,
                sex=self.sex,
            )
        )

        if core_headline is None:
            raise TrendNumberDataNotFoundError(
                topic_name={self.topic_name},
                metric_name={metric_name},
            )

        return core_headline

    def get_trend(self) -> Trend:
        """Creates a `Trend` model which represents the trend block.

        Returns:
            `Trend` model with the associated metric values
            and inherent colour and direction calculation logic

        Raises:
            TrendNumberDataNotFoundError:
                If no data is found for the given combination of
                `topic` / `metric` / `percentage_metric`.

        """
        core_headline_metric: CoreHeadline = self.get_latest_metric_value(
            metric_name=self.metric_name
        )
        core_headline_percentage_metric: CoreHeadline = self.get_latest_metric_value(
            metric_name=self.percentage_metric_name
        )

        return Trend(
            metric_name=self.metric_name,
            metric_value=core_headline_metric.metric_value,
            metric_period_end=core_headline_metric.period_end,
            percentage_metric_name=self.percentage_metric_name,
            percentage_metric_value=core_headline_percentage_metric.metric_value,
            percentage_metric_period_end=core_headline_percentage_metric.period_end,
        )


def generate_trend_numbers(
    topic_name: str,
    metric_name: str,
    percentage_metric_name: str,
    geography_name: str,
    geography_type_name: str,
    stratum_name: str,
    sex: str,
    age: str,
) -> TREND_AS_DICT:
    """Gets the trend data for the given metric names.

    Args:
        topic_name: The name of the disease being queried.
            E.g. `COVID-19`
        metric_name: The name of the metric being queried.
            E.g. `COVID-19_deaths_ONSByDay`
        percentage_metric_name: The name of the corresponding
            percentage metric being queried.
            E.g. `new_tests_7days_change_percentage`
        geography_name: The name of the geography being queried.
            E.g. `England`
        geography_type_name: The name of the geography
            type being queried.
            E.g. `Nation`
        stratum_name: The value of the stratum to apply additional filtering to.
            E.g. `default`, which would be used to capture all strata.
        sex: The gender to apply additional filtering to.
            E.g. `F`, would be used to capture Females.
            Note that options are `M`, `F`, or `ALL`.
        age: The age range to apply additional filtering to.
            E.g. `0_4` would be used to capture the age of 0-4 years old

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
    interface = TrendsInterface(
        topic_name=topic_name,
        metric_name=metric_name,
        percentage_metric_name=percentage_metric_name,
        geography_name=geography_name,
        geography_type_name=geography_type_name,
        stratum_name=stratum_name,
        sex=sex,
        age=age,
    )

    trend: Trend = interface.get_trend()
    data: TREND_AS_DICT = trend.model_dump()

    return data
