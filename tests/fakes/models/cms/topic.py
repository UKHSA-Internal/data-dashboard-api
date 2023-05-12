from cms.topic.models import TopicPage
from tests.fakes.models.fake_model_meta import FakeMeta


class FakeTopicPage(TopicPage):
    """
    A fake version of the Django model `TopicPage`
    which has had its dependencies altered so that it does not interact with the database
    """

    Meta = FakeMeta

    def __init__(self, **kwargs):
        """
        Constructor takes the same arguments as a normal `TopicPage` model.
        """
        super().__init__(content_type_id=1, **kwargs)
