class MockButtonSnippet:
    """
    A fake version of the button snippet model for tests.
    """

    def __init__(self, text, loading_text, endpoint, method, button_type):
        self.text = text
        self.loading_text = loading_text
        self.endpoint = endpoint
        self.method = method
        self.button_type = button_type
