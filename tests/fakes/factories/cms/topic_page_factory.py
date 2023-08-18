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
    def _build_page(cls, page_name: str):
        data = open_example_page_response(page_name=page_name)
        return cls.build(
            body=data["body"],
            title=data["title"],
            page_description=data["page_description"],
            slug=data["meta"]["slug"],
        )

    @classmethod
    def build_covid_19_page_from_template(cls) -> FakeTopicPage:
        return cls._build_page(page_name="covid_19")

    @classmethod
    def build_other_respiratory_viruses_page_from_template(cls) -> FakeTopicPage:
        return cls._build_page(page_name="other_respiratory_viruses")

    @classmethod
    def build_influenza_page_from_template(cls) -> FakeTopicPage:
        return cls._build_page(page_name="influenza")
