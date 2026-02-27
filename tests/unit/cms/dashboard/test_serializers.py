from unittest import mock

import pytest
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from wagtail.api.v2.views import PageSerializer
from wagtail.models import Page

from cms.dashboard.serializers import CMSDraftPagesSerializer


class TestCMSDraftPagesSerializer:
    def test_fields_can_be_constructed_without_serializer_class_errors(self):
        """
        Given a `CMSDraftPagesSerializer` instance
        When the serializer fields are accessed
        Then only expected fields are exposed
        """
        # Given
        serializer = CMSDraftPagesSerializer()

        # When
        fields = serializer.fields

        # Then
        assert "latest_revision" in fields
        assert "type" not in fields
        assert "detail_url" not in fields
        assert "parent" not in fields
        assert "alias_of" not in fields

    def test_build_relational_field_falls_back_for_unmapped_fields(self):
        """
        Given an unmapped relational field
        When `build_relational_field()` is called
        Then fallback serializer field settings are used
        """
        # Given
        serializer = CMSDraftPagesSerializer()
        relation_info = mock.Mock()
        relation_info.model_field.null = True

        # When
        field_class, field_kwargs = serializer.build_relational_field(
            field_name="latest_revision", relation_info=relation_info
        )

        # Then
        assert field_class is serializers.PrimaryKeyRelatedField
        assert field_kwargs == {"read_only": True, "allow_null": True}

    @mock.patch.object(PageSerializer, "build_relational_field")
    def test_build_relational_field_uses_page_serializer_for_mapped_fields(
        self, spy_page_serializer_build_relational_field: mock.MagicMock
    ):
        """
        Given a mapped relational field in `CMSDraftPagesSerializer`
        When `build_relational_field()` is called
        Then the call delegates to `PageSerializer.build_relational_field`

        Patches:
            `spy_page_serializer_build_relational_field`: For the main assertion.
                To verify call delegation and return-value passthrough.
        """
        # Given
        spy_page_serializer_build_relational_field.return_value = (
            mock.sentinel.field_class,
            {"mapped": True},
        )
        serializer = CMSDraftPagesSerializer()
        serializer.child_serializer_classes = {"latest_revision": object()}

        # When
        field_class, field_kwargs = serializer.build_relational_field(
            field_name="latest_revision", relation_info=mock.Mock()
        )

        # Then
        assert field_class is mock.sentinel.field_class
        assert field_kwargs == {"mapped": True}
        spy_page_serializer_build_relational_field.assert_called_once()

    def test_to_representation_raises_error_if_page_has_no_unpublished_changes(self):
        """
        Given a mocked `Page` which has no unpublished changes
        When `to_representation()` is called
            from an instance of the `CMSDraftPagesSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        mocked_page = mock.Mock(spec_set=Page, has_unpublished_changes=False)
        serializer = CMSDraftPagesSerializer(instance=mocked_page)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.to_representation(instance=mocked_page)

    @mock.patch.object(PageSerializer, "to_representation")
    def test_to_representation_calls_super_when_page_has_unpublished_changes(
        self, spy_to_representation: mock.MagicMock
    ):
        """
        Given a mocked `Page` which has unpublished changes
        When `to_representation()` is called
            from an instance of the `CMSDraftPagesSerializer`
        Then the `super().to_representation()` method is called

        Patches:
            `spy_to_representation`: For the main assertion

        """
        # Given
        mocked_page = mock.Mock(spec_set=Page, has_unpublished_changes=True)
        serializer = CMSDraftPagesSerializer(instance=mocked_page)

        # When
        representation = serializer.to_representation(instance=mocked_page)

        # Then
        assert representation == spy_to_representation.return_value
        spy_to_representation.assert_called_once_with(instance=mocked_page)
