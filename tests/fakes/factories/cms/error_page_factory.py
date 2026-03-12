import factory

from tests.fakes.models.cms.error import FakeErrorPage


class FakeErrorPageFactory(factory.Factory):
    """
    Factory for creating `FakeErrorPage` instances for tests
    """

    class Meta:
        model = FakeErrorPage

    @classmethod
    def build_blank_page(cls, **kwargs):
        return cls.build(**kwargs)
