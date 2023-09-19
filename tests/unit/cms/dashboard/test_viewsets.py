from rest_framework_api_key.permissions import HasAPIKey

from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.dashboard.viewsets import CMSDraftPagesViewSet, CMSPagesAPIViewSet


class TestCMSDraftPagesViewSet:
    def test_base_serializer_class_is_set_with_correct_serializer(self):
        """
        Given an instance of the `CMSDraftPagesViewSet`
        When the `base_serializer_class` attribute is called
        Then the `CMSDraftPagesSerializer` class is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        base_serializer_class = draft_pages_viewset.base_serializer_class

        # Then
        assert base_serializer_class is CMSDraftPagesSerializer

    def test_get_urlpatterns(self):
        """
        Given an instance of the `CMSDraftPagesViewSet`
        When `get_urlpatterns()` is called
        Then only 1 detail-type url pattern is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        urlpatterns = draft_pages_viewset.get_urlpatterns()

        # Then
        assert len(urlpatterns) == 1
        assert urlpatterns[0].name == "detail"

    def test_permission_classes_has_no_api_key_constraint(self):
        """
        Given an instance of the `CMSDraftPagesViewSet`
        When `permission_classes` is called
        Then an empty list is returned
        """
        # Given
        draft_pages_viewset = CMSDraftPagesViewSet()

        # When
        permission_classes = draft_pages_viewset.permission_classes

        # Then
        assert permission_classes == []


class TestCMSPagesAPIViewSet:
    def test_base_serializer_class_is_set_with_correct_serializer(self):
        """
        Given an instance of the `CMSPagesAPIViewSet`
        When the `base_serializer_class` attribute is called
        Then the `ListablePageSerializer` class is returned
        """
        # Given
        pages_viewset = CMSPagesAPIViewSet()

        # When
        base_serializer_class = pages_viewset.base_serializer_class

        # Then
        assert base_serializer_class is ListablePageSerializer

    def test_listing_default_fields_is_set_with_show_in_menus(self):
        """
        Given an instance of the `CMSPagesAPIViewSet`
        When the `listing_default_fields` attribute is called
        Then "show_in_menus" is found within the returned list of fields
        """
        # Given
        pages_viewset = CMSPagesAPIViewSet()

        # When
        listing_default_fields = pages_viewset.listing_default_fields

        # Then
        assert "show_in_menus" in listing_default_fields
