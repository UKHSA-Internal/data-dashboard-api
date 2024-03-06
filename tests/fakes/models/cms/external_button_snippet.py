from cms.snippets.models.external_button import ExternalButton
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeExternalButtonSnippet(ExternalButton):
    """
    A fake version of the external button snippet model for tests.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
