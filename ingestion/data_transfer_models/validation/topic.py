from ingestion.data_transfer_models.validation.shared import (
    format_child_and_parent_theme_name,
)
from ingestion.utils import enums


def validate_topic(*, topic: str, child_theme: str) -> None:
    """Validate a `topic` against an enum and the provided `child_theme`

    Notes:
        raises a valueError if the `topic` is not present in the correct enum.

    Args:
        topic: string representing the `topic` we're validating
        child_theme: string representing the `child_theme` used to select
            the correct `topic` enum.

    Returns:
        None

    """
    if (
        topic
        not in enums.Topic[
            format_child_and_parent_theme_name(child_theme)
        ].return_list()
    ):
        raise ValueError
