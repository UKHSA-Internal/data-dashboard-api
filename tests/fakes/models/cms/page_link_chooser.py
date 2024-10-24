class FakePageLinkChooser:
    """
    A fake version of the `PageLinkChooserBlock`
    which has had its dependencies altered so that it does not interact with the database.
    """

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `PageChooserBlock`.
        """
        super().__init__(**kwargs)
