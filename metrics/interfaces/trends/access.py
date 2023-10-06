from decimal import Decimal
from typing import Optional

from django.db.models import Manager

from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries
from metrics.domain.trends.state import TREND_AS_DICT, Trend

DEFAULT_CORE_TIME_SERIES_MANAGER = CoreTimeSeries.objects
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
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
    ):
        self.topic_name = topic_name
        self.metric_name = metric_name
        self.percentage_metric_name = percentage_metric_name
        self.core_time_series_manager = core_time_series_manager

    def get_latest_metric_value(self, metric_name: str) -> Decimal:
        """Gets the value for the record associated with the given `metric_to_lookup`

        Returns:
            Decimal: The associated `metric_value`

        Raises:
            TrendNumberDataNotFoundError:
                If no data is found for the given combination of
                `topic` / `metric` / `percentage_metric`.

        """
        latest_metric_value: Optional[
            Decimal
        ] = self.core_time_series_manager.get_latest_metric_value(
            topic_name=self.topic_name,
            metric_name=metric_name,
        )

        if latest_metric_value is None:
            raise TrendNumberDataNotFoundError(
                topic_name={self.topic_name},
                metric_name={metric_name},
            )

        return latest_metric_value

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
        metric_value: Decimal = self.get_latest_metric_value(
            metric_name=self.metric_name
        )
        percentage_metric_value: Decimal = self.get_latest_metric_value(
            metric_name=self.percentage_metric_name
        )

        return Trend(
            metric_name=self.metric_name,
            metric_value=metric_value,
            percentage_metric_name=self.percentage_metric_name,
            percentage_metric_value=percentage_metric_value,
        )


class TrendsInterfaceBeta:
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

    def get_latest_metric_value(self, metric_name: str) -> Decimal:
        """Gets the value for the record associated with the given `metric_to_lookup`

        Returns:
            Decimal: The associated `metric_value`

        Raises:
            TrendNumberDataNotFoundError:
                If no data is found for the given combination of
                `topic` / `metric` / `percentage_metric`.

        """
        latest_metric_value: Optional[
            Decimal
        ] = self.core_headline_manager.get_latest_metric_value(
            topic_name=self.topic_name,
            metric_name=metric_name,
            geography_name=self.geography_name,
            geography_type_name=self.geography_type_name,
            age=self.age,
            stratum_name=self.stratum_name,
            sex=self.sex,
        )

        if latest_metric_value is None:
            raise TrendNumberDataNotFoundError(
                topic_name={self.topic_name},
                metric_name={metric_name},
            )

        return latest_metric_value

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
        metric_value: Decimal = self.get_latest_metric_value(
            metric_name=self.metric_name
        )
        percentage_metric_value: Decimal = self.get_latest_metric_value(
            metric_name=self.percentage_metric_name
        )

        return Trend(
            metric_name=self.metric_name,
            metric_value=metric_value,
            percentage_metric_name=self.percentage_metric_name,
            percentage_metric_value=percentage_metric_value,
        )


def generate_trend_numbers(
    topic: str, metric_name: str, percentage_metric_name: str
) -> TREND_AS_DICT:
    """Gets the trend data for the given metric names.

    Args:
        topic: The name of the disease being queried.
            E.g. `COVID-19`
        metric_name: The name of the corresponding main metric
            being queried.
            E.g. `new_tests_7days_change`
        percentage_metric_name: The name of the corresponding
            percentage metric being queried.
            E.g. `new_tests_7days_change_percentage`

    Returns:
        Dict[str, Union[str, int, float]]: Dict containing the serialized trends data.
            E.g.
                {
                  "metric_name": "new_cases_7days_change",
                  "metric_value": -692,
                  "percentage_metric_name": "new_deaths_7days_change_percentage",
                  "percentage_metric_value": 3.1,
                  "direction": "down",
                  "colour": "green"
                }

    """
    interface = TrendsInterface(
        topic_name=topic,
        metric_name=metric_name,
        percentage_metric_name=percentage_metric_name,
    )

    trend: Trend = interface.get_trend()
    data: TREND_AS_DICT = trend.model_dump()

    return data


def generate_trend_numbers_beta(
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
                  "percentage_metric_name": "new_deaths_7days_change_percentage",
                  "percentage_metric_value": 3.1,
                  "direction": "down",
                  "colour": "green"
                }

    Raises:
        `TrendNumberDataNotFoundError`: If no data is found
            for the given combination of
            `topic` / `metric` / `percentage_metric`

    """
    interface = TrendsInterfaceBeta(
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
