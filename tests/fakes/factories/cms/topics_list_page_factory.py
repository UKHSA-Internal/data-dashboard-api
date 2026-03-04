import factory

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)
from tests.fakes.models.cms.topics_list import FakeTopicsListPage


class FakeTopicsListPageFactory(factory.Factory):
    """
    Factory for creating `FakeTopicListPage` instance for tests
    """

    class Meta:
        model = FakeTopicsListPage

    @classmethod
    def build_blank_page(cls, **kwargs):
        return cls.build(**kwargs)
