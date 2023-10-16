from cms.whats_new.managers.parent import WhatsNewParentPageManager
from cms.whats_new.models import WhatsNewParentPage


class FakeWhatsNewParentPageManager(WhatsNewParentPageManager):
    """
    A fake version of the `WhatsNewParentPageManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, pages, **kwargs):
        self.pages = pages
        super().__init__(**kwargs)

    def get_live_pages(self) -> list[WhatsNewParentPage]:
        return [page for page in self.pages if page.live]
