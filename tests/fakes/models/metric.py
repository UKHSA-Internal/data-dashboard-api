from metrics.data.models.core_models import Metric

from .fake_model_meta import FakeMeta


class FakeMetric(Metric):
    """
    A fake version of the Django model `Metric`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `Metric` model.
        """
        super().__init__(**kwargs)
