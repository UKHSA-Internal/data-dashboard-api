from metrics.data.models.core_models import CoreTimeSeries
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeCoreTimeSeries(CoreTimeSeries):
    """
    A fake version of the Django model `CoreTimeSeries`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `CoreTimeSeries` model.
        """
        super().__init__(**kwargs)
