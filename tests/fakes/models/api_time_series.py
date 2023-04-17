from metrics.data.models.api_models import APITimeSeries
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeAPITimeSeries(APITimeSeries):
    """
    A fake version of the Django model `APITimeSeries`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `APITimeSeries` model.
        """
        super().__init__(**kwargs)
