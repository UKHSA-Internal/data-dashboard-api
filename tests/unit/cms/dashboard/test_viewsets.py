from cms.dashboard.serializers import CMSDraftPagesSerializer
from cms.dashboard.viewsets import CMSDraftPagesViewSet


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
