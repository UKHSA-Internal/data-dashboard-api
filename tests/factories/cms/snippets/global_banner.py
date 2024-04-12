import factory

from cms.snippets.models.global_banner import GlobalBanner


class GlobalBannerFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating `GlobalBanner` instances for tests
    """

    class Meta:
        model = GlobalBanner
