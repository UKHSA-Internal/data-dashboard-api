class FakeButtonSnippet:
    """
    A fake version of the button snippet model for tests.
    """

    def __init__(
        self, text: str, loading_text: str, endpoint: str, method: str, button_type: str
    ):
        self.text = text
        self.loading_text = loading_text
        self.endpoint = endpoint
        self.method = method
        self.button_type = button_type
