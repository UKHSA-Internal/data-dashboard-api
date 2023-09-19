from django.db.models.manager import Manager

from ingestion.data_transfer_models import OutgoingHeadlineDTO, OutgoingTimeSeriesDTO
from ingestion.operations.api_models import generate_api_time_series
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects
DEFAULT_BATCH_SIZE = 100

DEFAULT_CORE_TIMESERIES_MANAGER = CoreTimeSeries.objects
DEFAULT_API_TIMESERIES_MANAGER = APITimeSeries.objects


def create_core_headlines(
    headline_dtos: list[OutgoingHeadlineDTO],
    core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """Creates `CoreHeadline` records from a list of HeadlineDTOs

    Args:
        headline_dtos: A list of HeadlineDTOs
            which have been enriched with all the correct fields
            and ready to be translated into database records
        batch_size: Controls the number of objects created
            in a single write query to the database.
            Defaults to 100.
        core_headline_manager: The model manager for `CoreHeadline`
            Defaults to the concrete `CoreHeadlineManager`
            via `CoreHeadline.objects`

    Returns:
        None

    """
    core_headline_model_instances: list[CoreHeadline] = [
        core_headline_manager.model(
            metric_id=int(headline_dto.metric),
            geography_id=int(headline_dto.geography),
            stratum_id=int(headline_dto.stratum),
            age_id=int(headline_dto.age),
            sex=headline_dto.sex,
            refresh_date=headline_dto.refresh_date,
            period_start=headline_dto.period_start,
            period_end=headline_dto.period_end,
            metric_value=headline_dto.metric_value,
        )
        for headline_dto in headline_dtos
    ]

    core_headline_manager.bulk_create(
        objs=core_headline_model_instances,
        ignore_conflicts=True,
        batch_size=batch_size,
    )


def create_core_and_api_timeseries(
    timeseries_dtos: list[OutgoingTimeSeriesDTO],
    core_time_series_manager: Manager = DEFAULT_CORE_TIMESERIES_MANAGER,
    api_time_series_manager: Manager = DEFAULT_API_TIMESERIES_MANAGER,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """Creates `CoreTimeSeries` and `APITimeSeries` records from a list of TimeSeriesDTOs

    Args:
        timeseries_dtos: A list of TimeSeriesDTOs
            which have been enriched with all the correct fields
            and ready to be translated into database records
        core_time_series_manager: The model manager for `CoreTimeSeries`
            Defaults to the concrete `CoreTimeSeriesManager`
            via `CoreTimeSeries.objects`
        api_time_series_manager: The model manager for `APITimeSeries`
            Defaults to the concrete `APITimeSeriesManager`
            via `APITimeSeries.objects`
        batch_size: Controls the number of objects created
            in a single write query to the database.
            Defaults to 100.

    Returns:
        None

    """
    core_timeseries_model_instances: list[CoreTimeSeries] = generate_core_time_series(
        timeseries_dtos=timeseries_dtos,
        core_time_series_manager=core_time_series_manager,
        batch_size=batch_size,
    )

    generate_api_time_series(
        all_core_time_series=core_timeseries_model_instances,
        api_time_series_manager=api_time_series_manager,
    )


def generate_core_time_series(
    timeseries_dtos: list[OutgoingTimeSeriesDTO],
    core_time_series_manager: DEFAULT_CORE_TIMESERIES_MANAGER,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[CoreTimeSeries]:
    """Creates 'CoreTimeSeries' records and returns the corresponding model instances

    Args:
        timeseries_dtos: A list of TimeSeriesDTOs
            which have been enriched with all the correct fields
            and ready to be translated into database records
        core_time_series_manager: The model manager for `CoreTimeSeries`
            Defaults to the concrete `CoreTimeSeriesManager`
            via `CoreTimeSeries.objects`
        batch_size: Controls the number of objects created
            in a single write query to the database.
            Defaults to 100.

    Returns:
        None

    """
    core_timeseries_model_instances = _create_core_timeseries_model_instances(
        timeseries_dtos=timeseries_dtos,
        core_time_series_manager=core_time_series_manager,
    )
    core_time_series_manager.bulk_create(
        objs=core_timeseries_model_instances,
        ignore_conflicts=True,
        batch_size=batch_size,
    )

    return core_timeseries_model_instances


def _create_core_timeseries_model_instances(
    timeseries_dtos: list[OutgoingTimeSeriesDTO],
    core_time_series_manager: DEFAULT_CORE_TIMESERIES_MANAGER,
) -> list[CoreTimeSeries]:
    first_timeseries_dto = timeseries_dtos[0]
    metric_id = int(first_timeseries_dto.metric)
    metric_frequency = first_timeseries_dto.metric_frequency
    refresh_date = first_timeseries_dto.refresh_date

    return [
        core_time_series_manager.model(
            metric_id=metric_id,
            geography_id=int(timeseries_dto.geography),
            stratum_id=int(timeseries_dto.stratum),
            age_id=int(timeseries_dto.age),
            sex=timeseries_dto.sex,
            metric_frequency=metric_frequency,
            year=timeseries_dto.year,
            month=timeseries_dto.month,
            epiweek=timeseries_dto.epiweek,
            date=timeseries_dto.date.split(" ")[0],
            refresh_date=refresh_date,
            metric_value=timeseries_dto.metric_value,
        )
        for timeseries_dto in timeseries_dtos
    ]
