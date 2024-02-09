from cms.snippets.models import Button, ButtonTypes, Methods


def create_download_button_snippet(*args, **kwargs) -> None:
    """Creates a download button snippet.

    Returns:
        None
    """
    Button.objects.create(
        text="download (zip)",
        loading_text="",
        endpoint="/api/bulkdownloads/v1",
        method=Methods.POST,
        button_type=ButtonTypes.DOWNLOAD,
    )


def remove_buttons_snippets(*args, **kwargs) -> None:
    """Removes all button snippets.

    Returns:
        None
    """
    Button.objects.all().delete()
