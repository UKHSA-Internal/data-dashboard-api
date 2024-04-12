from cms.snippets.models.internal_button import InternalButton
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeInternalButtonSnippet(InternalButton):
    """
    A fake version of the internal button snippet model for tests.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
