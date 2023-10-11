from cms.whats_new.models import WhatsNewChildPage
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeWhatsNewChildPage(WhatsNewChildPage):
    """
    A fake version of the Django model `WhatsNewChildPage`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `WhatsNewChildPage` model.
        """
        super().__init__(content_type_id=1, **kwargs)
