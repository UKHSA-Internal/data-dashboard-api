import factory

from cms.dashboard.management.commands.build_cms_site import open_example_page_response
from tests.fakes.models.cms.home import FakeHomePage


class FakeHomePageFactory(factory.Factory):
    """
    Factory for creating `FakeHomePage` instances for tests
    """

    class Meta:
        model = FakeHomePage

    @classmethod
    def build_blank_page(cls, **kwargs):
        return cls.build(**kwargs)

    @classmethod
    def build_home_page_from_template(cls):
        data = open_example_page_response(page_name="respiratory_viruses")
        return cls.build(
            body=data["body"],
            title=data["title"],
            page_description=data["page_description"],
            slug=data["meta"]["slug"],
        )
