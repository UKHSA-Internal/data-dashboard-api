import factory

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
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

        # Use the `slug` from the kwargs if possible otherwise take it from the template
        try:
            slug = kwargs["slug"]
        except KeyError:
            slug = data["meta"]["slug"]
        else:
            data["meta"]["slug"] = slug
            kwargs.pop("slug")

        seo_title = data["meta"]["seo_title"]

        return cls.build(
            body=data["body"],
            title=data["title"],
            slug=slug,
            seo_title=seo_title,
            **kwargs
        )
