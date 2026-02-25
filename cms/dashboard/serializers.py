from collections import OrderedDict

from rest_framework import serializers
from wagtail.api.v2.views import PageSerializer
from wagtail.models import Page

from cms.dashboard.fields import ListablePageParentField

PAGE_HAS_NO_DRAFTS = (
    "Page has no unpublished changes. Use the `api/pages/` for live pages instead."
)


class CMSDraftPagesSerializer(PageSerializer):
    meta_fields = []
    child_serializer_classes = {}

    class Meta:
        model = Page
        fields = "__all__"

    def get_fields(self):
        fields = super().get_fields()
        fields.pop("type", None)
        fields.pop("detail_url", None)
        fields.pop("parent", None)
        fields.pop("alias_of", None)
        return fields

    def build_relational_field(self, field_name, relation_info):
        child_serializer_classes = getattr(self, "child_serializer_classes", {})
        if field_name not in child_serializer_classes:
            return serializers.PrimaryKeyRelatedField, {
                "read_only": True,
                "allow_null": relation_info.model_field.null,
            }

        return super().build_relational_field(field_name, relation_info)

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
