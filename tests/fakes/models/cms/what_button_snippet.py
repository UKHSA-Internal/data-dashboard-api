from cms.snippets.models.wha_button import WeatherAlertButton
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeWhaButtonSnippet(WeatherAlertButton):
    """
    A fake version of the wha button snippet model for tests.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
