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
        """Removes problematic fields that cause serialization errors for draft pages.

        Note: This hardening was added during preview feature development (CDD-1379)
        after discovering serialization crashes in Wagtail/DRF field construction.
        The original draft API in main didn't have these issues under light usage,
        but thorough preview testing exposed edge cases.

        Wagtail's PageSerializer expects certain router/viewset context when
        serializing these fields:
        - `type` and `detail_url`: Require full API router context
        - `parent` and `alias_of`: Trigger recursive Page serialization that
          expects viewset state and can cause KeyError or infinite recursion

        These fields aren't needed for preview rendering - the frontend only
        needs the page content itself, not its position in the CMS tree.

        Returns:
            dict: Field definitions with problematic relational fields removed
        """
        fields = super().get_fields()
        fields.pop("type", None)
        fields.pop("detail_url", None)
        fields.pop("parent", None)
        fields.pop("alias_of", None)
        return fields

    def build_relational_field(self, field_name, relation_info):
        """Safely handles relational field serialization with fallback for unmapped fields.

        This override prevents crashes when Wagtail's PageSerializer encounters
        relational fields (e.g. ForeignKeys like `latest_revision`) that don't have
        explicit serializer mappings. Without this, DRF would raise
        `KeyError: serializer_class` when building fields.

        The method checks `child_serializer_classes` for explicit mappings:
        - If unmapped: Returns a simple PrimaryKeyRelatedField (just the ID)
        - If mapped: Delegates to parent class to use the specified serializer

        This was added during CDD-1379 after discovering that Wagtail's Page model
        has several relational fields that cause serialization failures without
        explicit handling.

        Args:
            field_name: The name of the relational field being serialized
            relation_info: Metadata about the relation (model, related model, etc.)

        Returns:
            tuple: (field_class, field_kwargs) defining how to serialize this relation
        """
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
