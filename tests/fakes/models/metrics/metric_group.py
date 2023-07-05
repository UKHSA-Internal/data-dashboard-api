from metrics.data.models.core_models import MetricGroup
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeMetricGroup(MetricGroup):
    """
    A fake version of the Django model `MetricGroup`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `MetricGroup` model.
        """
        super().__init__(**kwargs)
