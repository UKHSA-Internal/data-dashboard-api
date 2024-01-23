from cms.composite.models import CompositePage
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeCompositePage(CompositePage):
    """
    A fake version of the Django model `CompositePage`
    which has had its dependencies altered so that it does not interact with the datebase.
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `CompositePage` model.
        """
        super().__init__(content_type_id=1, **kwargs)
