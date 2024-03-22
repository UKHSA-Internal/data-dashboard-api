from django.db import models

DEFAULT_BATCH_SIZE = 100


def create_records(
    *,
    model_instances: list[models.Model],
    model_manager: models.Manager,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """Writes records to the database from the list of `model_instances`

    Args:
        model_instances: A list of enriched model instances
            which are ready to be written to the database
        model_manager: The model manager to use to write the records
            for the given `model_instances` to the database
        batch_size: Controls the number of objects created
            in a single write query to the database.
            Defaults to 100.

    Returns:
        None

    """
    model_manager.bulk_create(
        objs=model_instances,
        ignore_conflicts=True,
        batch_size=batch_size,
    )
