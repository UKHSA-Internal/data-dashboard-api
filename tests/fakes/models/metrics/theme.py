from metrics.data.models.core_models import Theme
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeTheme(Theme):
    """
    A fake version of the Django model `Theme`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `Theme` model.
        """
        super().__init__(**kwargs)
