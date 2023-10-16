import factory

from cms.dashboard.management.commands.build_cms_site import open_example_page_response
from tests.fakes.models.cms.whats_new_parent import FakeWhatsNewParentPage


class FakeWhatsNewParentPageFactory(factory.Factory):
    """
    Factory for creating `FakeWhatsNewParentPage` instances for tests
    """

    class Meta:
        model = FakeWhatsNewParentPage

    @classmethod
    def build_page_from_template(cls, **kwargs):
        data = open_example_page_response(page_name="whats_new")
        return cls.build(
            body=data["body"], title=data["title"], slug=data["meta"]["slug"], **kwargs
        )
