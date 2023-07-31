from metrics.data.models.core_models import Geography
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeGeography(Geography):
    """
    A fake version of the `Geography` model
    This has been altered so that it does not interact
    with the database.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `Geography` model.

        Args:
            **kwargs:
        """
        super().__init__(**kwargs)
