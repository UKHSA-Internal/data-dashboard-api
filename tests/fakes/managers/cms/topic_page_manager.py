from cms.topic.managers import TopicPageManager
from tests.fakes.models.cms.topic import FakeTopicPage


class FakeTopicPageManager(TopicPageManager):
    """
    A fake version of the `TopicPageManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, pages, **kwargs):
        self.pages = pages
        super().__init__(**kwargs)

    def get_live_pages(self) -> list[FakeTopicPage]:
        return [page for page in self.pages if page.live]

    def get_covid_page(self) -> FakeTopicPage | None:
        try:
            return next(x for x in self.get_live_pages() if x.title == "COVID-19")
        except StopIteration:
            return None
