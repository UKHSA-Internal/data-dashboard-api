import factory

from cms.dashboard.management.commands.build_cms_site import open_example_page_response
from tests.fakes.models.cms.topic import FakeTopicPage


class FakeTopicPageFactory(factory.Factory):
    """
    Factory for creating `FakeTopicPage` instances for tests
    """

    class Meta:
        model = FakeTopicPage

    @classmethod
    def build_coronavirus_page_from_template(cls):
        data = open_example_page_response(page_name="coronavirus")
        return cls.build(
            body=data["body"],
            title=data["title"],
            page_description=data["page_description"],
            slug=data["meta"]["slug"],
        )
