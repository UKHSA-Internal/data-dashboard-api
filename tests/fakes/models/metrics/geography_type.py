from metrics.data.models.core_models import GeographyType
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeGeographyType(GeographyType):
    """
    A fake version of the `GeographyType` model
    This has been altered so that it does not interact
    with the database.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `GeographyType` model.

        Args:
            **kwargs

        """
        super().__init__(**kwargs)
