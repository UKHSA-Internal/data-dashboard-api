from cms.snippets.managers.global_banner import GlobalBannerManager
from cms.snippets.models.global_banner import GlobalBanner


class FakeGlobalBannerManager(GlobalBannerManager):
    """
    A fake version of the `GlobalBannerManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, global_banners: list[GlobalBanner], **kwargs):
        self.global_banners = global_banners
        super().__init__(**kwargs)

    def get_active_banners(self) -> list[GlobalBanner]:
        return [
            global_banner
            for global_banner in self.global_banners
            if global_banner.is_active is True
        ]
