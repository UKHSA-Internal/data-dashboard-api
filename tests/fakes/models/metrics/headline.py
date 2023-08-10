from metrics.data.models.core_models import CoreHeadline
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeCoreHeadline(CoreHeadline):
    """
    A fake version of the Django model `CoreHeadline`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `CoreHeadline` model.
        """
        super().__init__(**kwargs)
