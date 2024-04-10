from cms.snippets.models.button import Button, ButtonTypes, Methods
from cms.snippets.models.internal_button import InternalButton, InternalButtonTypes


def get_or_create_download_button_snippet(*args, **kwargs) -> Button:
    """Creates a download button snippet.

    Returns:
       a bulk download button, used to download all chart data from the dashboard.
       Is an instance of `Button` snippet.
    """
    obj, _ = Button.objects.get_or_create(
        text="download (zip)",
        loading_text="",
        endpoint="/api/bulkdownloads/v1",
        method=Methods.POST.value,
        button_type=ButtonTypes.DOWNLOAD.value,
    )

    return obj


def remove_buttons_snippets(*args, **kwargs) -> None:
    """Removes all button snippets.

    Returns:
        None
    """
    Button.objects.all().delete()


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
