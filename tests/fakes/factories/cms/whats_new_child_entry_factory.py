import factory

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
from cms.whats_new.models import Badge
from tests.fakes.models.cms.whats_new_child import FakeWhatsNewChildEntry


class FakeWhatsNewChildEntryFactory(factory.Factory):
    """
    Factory for creating `FakeWhatsNewChildEntry` instances for tests
    """

    class Meta:
        model = FakeWhatsNewChildEntry

    @classmethod
    def build_page_from_template(cls, **kwargs):
        data = open_example_page_response(
            page_name="whats_new_soft_launch_of_the_ukhsa_data_dashboard"
        )
        badge = Badge(text=data["badge"]["text"], colour=data["badge"]["colour"])
        return cls.build(
            title=data["title"],
            body=data["body"],
            additional_details=data["additional_details"],
            slug=data["meta"]["slug"],
            badge=badge,
            **kwargs
        )
