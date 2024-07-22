import factory

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
from tests.fakes.models.cms.composite import FakeCompositePage


class FakeCompositePageFactory(factory.Factory):
    """
    Factory for creating `FakeCompositePage` instances for tests
    """

    class Meta:
        model = FakeCompositePage

    @classmethod
    def build_blank_page(cls, **kwargs):
        return cls.build(**kwargs)

    @classmethod
    def build_page_from_template(cls, page_name, **kwargs):
        data = open_example_page_response(page_name=page_name)

        # Use the `slug` from the kwargs if available otherwise take it from the template
        try:
            slug = kwargs["slug"]
        except KeyError:
            slug = data["meta"]["slug"]
        else:
            data["meta"]["slug"] = slug
            kwargs.pop("slug")

        return cls.build(body=data["body"], title=data["title"], slug=slug, **kwargs)
