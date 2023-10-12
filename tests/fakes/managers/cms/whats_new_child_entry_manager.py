from cms.whats_new.managers.child import WhatsNewChildEntryManager
from tests.fakes.models.cms.whats_new_child import WhatsNewChildEntry


class FakeWhatsNewChildEntryManager(WhatsNewChildEntryManager):
    """
    A fake version of the `WhatsNewChildEntryManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, pages, **kwargs):
        self.pages = pages
        super().__init__(**kwargs)

    def get_live_pages(self) -> list[WhatsNewChildEntry]:
        return [page for page in self.pages if page.live]
