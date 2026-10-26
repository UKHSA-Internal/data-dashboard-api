from metrics.data.models.api_models import APIHeadline
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeAPIHeadline(APIHeadline):
    """
    A fake version of the Django model `APIHeadline`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `APIHeadline` model.
        """
        super().__init__(**kwargs)
