from django.db.models.manager import Manager

from ingestion.consumer import HeadlineDTO
from metrics.data.models.core_models import CoreHeadline

DEFAULT_CORE_HEADLINE_MANAGER = CoreHeadline.objects
DEFAULT_BATCH_SIZE = 100


def create_core_headlines(
    headline_dtos: list[HeadlineDTO],
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
    core_headline_model_instances = [
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
