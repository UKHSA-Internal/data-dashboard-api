from cms.whats_new.models import WhatsNewChildEntry
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeWhatsNewChildEntry(WhatsNewChildEntry):
    """
    A fake version of the Django model `WhatsNewChildEntry`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `WhatsNewChildEntry` model.
        """
        super().__init__(content_type_id=1, **kwargs)
