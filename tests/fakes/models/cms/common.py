from cms.common.models import CommonPage
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeCommonPage(CommonPage):
    """
    A fake version of the Django model `CommonPage`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `CommonPage` model.
        """
        super().__init__(content_type_id=1, **kwargs)
