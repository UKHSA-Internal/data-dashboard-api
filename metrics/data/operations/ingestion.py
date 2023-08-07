from django.db.models.manager import Manager

from ingestion.data_transfer_models import OutgoingHeadlineDTO, OutgoingTimeSeriesDTO
from metrics.data.models.core_models import CoreHeadline, CoreTimeSeries

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects
DEFAULT_BATCH_SIZE = 100

DEFAULT_CORE_TIMESERIES_MANAGER = CoreTimeSeries.objects


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


def create_core_timeseries(
    timeseries_dtos: list[OutgoingTimeSeriesDTO],
    core_timeseries_manager: Manager = DEFAULT_CORE_TIMESERIES_MANAGER,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """Creates `CoreTimeSeries` records from a list of TimeSeriesDTOs

    Args:
        timeseries_dtos: A list of TimeSeriesDTOs
            which have been enriched with all the correct fields
            and ready to be translated into database records
        batch_size: Controls the number of objects created
            in a single write query to the database.
            Defaults to 100.
        core_timeseries_manager: The model manager for `CoreTimeSeries`
            Defaults to the concrete `CoreTimeSeriesManager`
            via `CoreTimeSeries.objects`

    Returns:
        None

    """
    core_timeseries_model_instances: list[CoreHeadline] = [
        core_timeseries_manager.model(
            metric_id=int(timeseries_dto.metric),
            geography_id=int(timeseries_dto.geography),
            stratum_id=int(timeseries_dto.stratum),
            age_id=int(timeseries_dto.age),
            sex=timeseries_dto.sex,
            metric_frequency=timeseries_dto.metric_frequency,
            year=timeseries_dto.year,
            month=timeseries_dto.month,
            epiweek=timeseries_dto.epiweek,
            date=timeseries_dto.date.split(" ")[0],
            refresh_date=timeseries_dto.refresh_date,
            metric_value=timeseries_dto.metric_value,
        )
        for timeseries_dto in timeseries_dtos
    ]

    core_timeseries_manager.bulk_create(
        objs=core_timeseries_model_instances,
        ignore_conflicts=True,
        batch_size=batch_size,
    )
