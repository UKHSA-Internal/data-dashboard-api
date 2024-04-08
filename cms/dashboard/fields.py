from wagtail.api.v2.serializers import PageParentField
from wagtail.models import Page


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
