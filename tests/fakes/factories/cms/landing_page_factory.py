import factory

from cms.dashboard.management.commands.build_cms_site_helpers.pages import (
    open_example_page_response,
)

from tests.fakes.models.cms.landing_page import FakeLandingPage


class FakeLandingPageFactory(factory.Factory):
    """
    Factory for creating `FakeHomePage` instances for tests
    """

    class Meta:
        model = FakeLandingPage

    @classmethod
    def build_blank_page(cls, **kwargs):
        return cls.build(**kwargs)
