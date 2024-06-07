from ingestion.data_transfer_models.validation.shared import (
    format_child_and_parent_theme_name,
)
from ingestion.utils import enums


def validate_child_theme(*, child_theme: str, parent_theme: str) -> None:
    """Validates the `child_theme` against an enum and the provided `parent_theme`

    Notes:
        raises a valueError if the `child_theme` is not present in the correct enum.

    Args:
        child_theme: string representing the `child_theme` we're validating
        parent_theme: string representing the `parent_theme` used to select the
            correct `child_theme` enum.

    Returns:
        None

    """
    if (
        child_theme
        not in enums.ChildTheme[
            format_child_and_parent_theme_name(parent_theme)
        ].return_list()
    ):
        raise ValueError
