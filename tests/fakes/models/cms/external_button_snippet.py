class FakeExternalButtonSnippet:
    """
    A fake version of the external button snippet model for tests.
    """

    def __init__(self, text: str, url: str, button_type: str, icon: str):
        self.text = text
        self.url = url
        self.button_type = button_type
        self.icon = icon
