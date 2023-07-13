import factory

from tests.fakes.models.cms.common import FakeCommonPage


class FakeCommonPageFactory(factory.Factory):
    """
    Factory for creating `FakeCommonPage` instances for tests
    """

    class Meta:
        model = FakeCommonPage

    @classmethod
    def build_blank_page(cls, **kwargs):
        return cls.build(**kwargs)
