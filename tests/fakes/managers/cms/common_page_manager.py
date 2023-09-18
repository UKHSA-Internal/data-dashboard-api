from cms.topic.managers import TopicPageManager
from tests.fakes.models.cms.common import FakeCommonPage


class FakeCommonPageManager(TopicPageManager):
    """
    A fake version of the `CommonPageManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, pages, **kwargs):
        self.pages = pages
        super().__init__(**kwargs)

    def get_live_pages(self) -> list[FakeCommonPage]:
        return [page for page in self.pages if page.live]
