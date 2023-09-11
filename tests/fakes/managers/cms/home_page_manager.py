from cms.home.managers import HomePageManager
from tests.fakes.models.cms.home import FakeHomePage


class FakeHomePageManager(HomePageManager):
    """
    A fake version of the `HomePageManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, pages, **kwargs):
        self.pages = pages
        super().__init__(**kwargs)

    def get_landing_page(self) -> FakeHomePage | None:
        try:
            return next(page for page in self.pages if page.slug == "dashboard")
        except StopIteration:
            return None
