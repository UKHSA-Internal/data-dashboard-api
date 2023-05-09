import factory

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
