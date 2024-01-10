from decimal import Decimal

from django.db.models import Manager

from metrics.data.models.core_models import CoreHeadline

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects


class HeadlinesInterface:
    def __init__(
        self,
        topic_name: str,
        metric_name: str,
        geography_name: str,
        geography_type_name: str,
        stratum_name: str,
        sex: str,
        age: str,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        self.topic_name = topic_name
        self.metric_name = metric_name
        self.geography_name = geography_name
        self.geography_type_name = geography_type_name
        self.stratum_name = stratum_name
        self.sex = sex
        self.age = age
        self.core_headline_manager = core_headline_manager

    def get_latest_metric_value(self) -> float:
        """Gets the latest metric_value for the associated headline data.

        Returns:
            The associated `metric_value` as a float

        Raises:
            `HeadlineNumberDataNotFoundError`: If the query returned no records.

        """
        latest_metric_value: [
            Decimal | None
        ] = self.core_headline_manager.get_latest_metric_value(
            topic_name=self.topic_name,
            metric_name=self.metric_name,
            geography_name=self.geography_name,
            geography_type_name=self.geography_type_name,
            age=self.age,
            stratum_name=self.stratum_name,
            sex=self.sex,
        )

        if latest_metric_value is None:
            raise HeadlineNumberDataNotFoundError

        return latest_metric_value


class BaseInvalidHeadlinesRequestError(Exception):
    ...


class HeadlineNumberDataNotFoundError(BaseInvalidHeadlinesRequestError):
    def __init__(self):
        message = "No data could be found for those parameters"
        super().__init__(message)


def generate_headline_number(
    topic_name: str,
    metric_name: str,
    geography_name: str,
    geography_type_name: str,
    stratum_name: str,
    sex: str,
    age: str,
) -> float:
    """Gets the headline number metric_value for the associated `CoreHeadline` record.

    Args:
        topic_name: The name of the disease being queried.
            E.g. `COVID-19`
        metric_name: The name of the metric being queried.
            E.g. `COVID-19_deaths_ONSByDay`
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
        float: The associated `metric_value`

    Raises:
        `HeadlineNumberDataNotFoundError`: If the query returned no records.

    """
    interface = HeadlinesInterface(
        topic_name=topic_name,
        metric_name=metric_name,
        geography_name=geography_name,
        geography_type_name=geography_type_name,
        stratum_name=stratum_name,
        sex=sex,
        age=age,
    )

    metric_value = interface.get_latest_metric_value()

    if metric_value is None:
        raise HeadlineNumberDataNotFoundError

    return metric_value
