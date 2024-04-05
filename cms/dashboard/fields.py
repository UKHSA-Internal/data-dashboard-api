from rest_framework.fields import Field
from rest_framework.utils.serializer_helpers import ReturnDict
from wagtail.api.v2.serializers import PageParentField
from wagtail.models import Page

from cms.snippets.serializers import get_active_global_banner


class ListablePageParentField(PageParentField):
    def get_attribute(self, instance: Page) -> Page | None:
        """Gets the parent of the `instance` if available

        Args:
            instance: Page instance being queried for

        Returns:
            The parent instance of the page if available.
            Otherwise, None is returned.

        """
        try:
            return super().get_attribute(instance=instance)
        except AttributeError:
            return None


class GlobalBannerField(Field):
    def get_attribute(self, instance: Page) -> ReturnDict[str, str] | None:
        """Gets the global banner information if available

        Args:
            instance: Page instance being queried for

        Returns:
            The data associated with the
            currently active global banner.
            If not available, None is returned

        """
        return get_active_global_banner()
