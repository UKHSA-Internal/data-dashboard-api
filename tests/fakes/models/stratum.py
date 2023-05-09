from metrics.data.models.core_models import Stratum

from .fake_model_meta import FakeMeta


class FakeStratum(Stratum):
    """
    A fake version of the Django model `Stratum`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `Stratum` model.
        """
        super().__init__(**kwargs)
