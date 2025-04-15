from django.db.models import Manager

from metrics.data.models.core_models import CoreHeadline
from metrics.domain.headlines.state import Headline
from metrics.domain.models.headline import HeadlineParameters

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects

EXPECTED_DATE_FORMAT = "%Y-%m-%d"


class HeadlinesInterface:
    def __init__(
        self,
        *,
        headline_parameters: HeadlineParameters,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        self.headline_parameters = headline_parameters
        self.core_headline_manager = core_headline_manager

    def get_latest_metric_value(self) -> Headline:
        """Gets the latest metric_value for the associated headline data.

        Returns:
            An enriched `Headline` model containing:
                - The individual metric_value number
                - The date associated with the `period_end` for that number

            Raises:
                `HeadlineNumberDataNotFoundError`: If the query returned no records.

        """
        core_headline: CoreHeadline | None = (
            self.core_headline_manager.get_latest_headline(
                topic_name=self.headline_parameters.topic_name,
                metric_name=self.headline_parameters.metric_name,
                geography_name=self.headline_parameters.geography_name,
                geography_type_name=self.headline_parameters.geography_type_name,
                stratum_name=self.headline_parameters.stratum_name,
                age=self.headline_parameters.age,
                sex=self.headline_parameters.sex,
            )
        )

        try:
            headline = Headline(
                metric_value=core_headline.metric_value,
                period_end=core_headline.period_end.strftime(EXPECTED_DATE_FORMAT),
            )
        except AttributeError as error:
            # If the returned `core_headline` is None
            # i.e. there is no data available for those parameters
            # then an `AttributeError` will be thrown
            raise HeadlineNumberDataNotFoundError from error

        return headline


class BaseInvalidHeadlinesRequestError(Exception): ...


class HeadlineNumberDataNotFoundError(BaseInvalidHeadlinesRequestError):
    def __init__(self):
        message = "No data could be found for those parameters"
        super().__init__(message)


def generate_headline_number(*, headline_parameters: HeadlineParameters) -> Headline:
    """Gets the headline number metric_value for the associated `CoreHeadline` record.

    Args:
        headline_parameters: An enriched `HeadlineParameters` model
            containing the requested parameters

    Returns:
        An enriched `Headline` model containing:
            - The individual metric_value number
            - The date associated with the `period_end` for that number

    Raises:
        `HeadlineNumberDataNotFoundError`: If the query returned no records.

    """
    interface = HeadlinesInterface(headline_parameters=headline_parameters)

    return interface.get_latest_metric_value()
