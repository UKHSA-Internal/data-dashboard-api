from cms.snippets.models.button import Button, ButtonTypes, Methods


def get_or_create_download_button_snippet(*args, **kwargs) -> dict[str, str]:
    """Creates a download button snippet.

    Returns:
        None
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
