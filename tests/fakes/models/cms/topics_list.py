from cms.topics_list.models import TopicsListPage
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeTopicsListPage(TopicsListPage):
    """
    A fake version of the Django model `TopicsListPage`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `TopicsListPage` model.
        """
        super().__init__(content_type_id=1, **kwargs)
