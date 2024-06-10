import logging

from cms.snippets.models.internal_button import InternalButton, InternalButtonTypes

logger = logging.getLogger(__name__)


def get_or_create_download_button_snippet(*args, **kwargs) -> None:
    """Creates a download button snippet.

    Returns:
       a bulk download button, used to download all chart data from the dashboard.
       Is an instance of `Button` snippet.

    Notes:
        This function has been deprecated due to a move from `Button` to `InternalButton` snippet
        it was left to avoid manually editing the migration files and order and its logic replaced
        with a log message.
    """
    logger.info(
        "Button snippet has been removed and replaced by InternalButton snippet."
    )


def remove_buttons_snippets(*args, **kwargs) -> None:
    """Removes all button snippets.

    Returns:
        None

    Notes:
        This function has been deprecated due to a move from `Button` to `InternalButton` snippet
        it was left to avoid manually editing the migration files and order and its logic replaced
        with a log message.
    """
    logger.info(
        "Button snippet has been removed and replaced by InternalButton snippet."
    )


def get_or_create_download_button_internal_button_snippet(
    *args, **kwargs
) -> InternalButton:
    """Creates a download internal button snippet.

    Returns:
       a bulk download button, used to download all chart data from the dashboard.
       Is an instance of `InternalButton` snippet.
    """
    obj, _ = InternalButton.objects.get_or_create(
        text="download (zip)",
        button_type=InternalButtonTypes.BULK_DOWNLOAD.value,
    )

    return obj


def remove_internal_button_snippets(*args, **kwargs) -> None:
    """Removes all internal button snippets.

    Returns:
        None
    """
    InternalButton.objects.all().delete()
