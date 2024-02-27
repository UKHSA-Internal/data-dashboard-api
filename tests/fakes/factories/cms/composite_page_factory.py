import factory

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
