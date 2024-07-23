import factory

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
from tests.fakes.models.cms.metrics_documentation_parent import (
    FakeMetricsDocumentationParentPage,
)


class FakeMetricsDocumentationParentPageFactory(factory.Factory):
    """
    Factory for creating `FakeMetricsDocumentationParentPage` instances for tests
    """

    class Meta:
        model = FakeMetricsDocumentationParentPage

    @classmethod
    def build_page_from_template(cls, **kwargs):
        data = open_example_page_response(page_name="metrics_documentation")

        # Use the `slug` from the kwargs if available otherwise take it from the template
        try:
            slug = kwargs["slug"]
        except KeyError:
            slug = data["meta"]["slug"]
        else:
            data["meta"]["slug"] = slug
            kwargs.pop("slug")

        return cls.build(body=data["body"], title=data["title"], slug=slug, **kwargs)
