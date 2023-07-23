from typing import OrderedDict

from rest_framework import serializers
from wagtail.api.v2.views import PageSerializer
from wagtail.models import Page

from cms.dashboard.fields import ListablePageParentField

PAGE_HAS_NO_DRAFTS = (
    "Page has no unpublished changes. Use the `api/pages/` for live pages instead."
)


class CMSDraftPagesSerializer(PageSerializer):
    class Meta:
        model = Page
        fields = "__all__"

    def to_representation(self, instance: Page) -> OrderedDict:
        """Provides a representation of the serialized instance

        Notes:
            This provides some additional logic to ensure
            the `instance` being serialized has unpublished changes.
            If not, then the serializer is invalidated

        Args:
            instance: The `Page` model being serialized

        Returns:
            A dict representation of the serialized instance

        """
        if not instance.has_unpublished_changes:
            raise serializers.ValidationError({"error_message": PAGE_HAS_NO_DRAFTS})

        return super().to_representation(instance=instance)


class ListablePageSerializer(PageSerializer):
    parent = ListablePageParentField(read_only=True)
