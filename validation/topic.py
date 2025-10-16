from validation import enums
from validation.shared import format_child_and_parent_theme_name


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
        error_message = f"The `topic` of '{topic}' is not valid for the `child_theme` of '{child_theme}'"
        raise ValueError(error_message)
