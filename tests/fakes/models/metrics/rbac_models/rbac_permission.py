from metrics.data.models import RBACPermission
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeRBACPermission(RBACPermission):
    """
    A fake version of the Django model `FakeRBACPermission`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `RBACPermission` model.
        """
        super().__init__(**kwargs)
