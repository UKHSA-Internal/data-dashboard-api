import pytest

from cms.dashboard.serializers import CMSDraftPagesSerializer, ListablePageSerializer
from cms.dashboard.viewsets import (
    CMSDraftPagesViewSet,
    CMSPagesAPIViewSet,
    check_permissions,
)


class TestCheckPermissions:
    @pytest.mark.parametrize(
        "user_permissions, theme_id, sub_theme_id, topic_id",
        [
            ([{"theme": {"id": "-1"}}], "10", "20", "30"),
            ([{"theme": {"id": "10"}, "sub_theme": {"id": "-1"}}], "10", "20", "30"),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            (
                [
                    {"theme": {"id": "5"}, "sub_theme": {"id": "-1"}},
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                    },
                ],
                "10",
                "20",
                "30",
            ),
        ],
    )
    def test_check_permissions_valid_access(
        self, user_permissions, theme_id, sub_theme_id, topic_id
    ):
        """
        Given a permission set that does grant access to the provided ids
        When the `check_permissions` function is called
        Then the function returns true
        """
        assert (
            check_permissions(
                permission_sets=user_permissions,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
            )
            == True
        )

    @pytest.mark.parametrize(
        "user_permissions, theme_id, sub_theme_id, topic_id",
        [
            ([{"theme": {"id": "99"}, "sub_theme": {"id": "-1"}}], "10", "20", "30"),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "99"},
                        "topic": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "99"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            ([], "10", "20", "30"),
        ],
    )
    def test_check_permissions_invalid_access(
        self, user_permissions, theme_id, sub_theme_id, topic_id
    ):
        """
        Given a permission set that does not grant access to the provided ids
        When the `check_permissions` function is called
        Then the function returns false
        """
        assert (
            check_permissions(
                permission_sets=user_permissions,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
            )
            == False
        )

    @pytest.mark.parametrize(
        "user_permissions, theme_id, sub_theme_id, topic_id",
        [
            ([{}], "10", "20", "30"),
            (None, "10", "20", "30"),
            ([{"sub_theme": {"id": "-1"}, "topic": {"id": "-1"}}], "10", "20", "30"),
            (
                [{"theme": {}, "sub_theme": {"id": "-1"}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
            ),
            ([{"theme": {"id": "10"}, "topic": {"id": "-1"}}], "10", "20", "30"),
            (
                [{"theme": {"id": "10"}, "sub_theme": {}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
            ),
            ([{"theme": {"id": "10"}, "sub_theme": {"id": "20"}}], "10", "20", "30"),
            (
                [{"theme": {"id": "10"}, "sub_theme": {"id": "20"}, "topic": {}}],
                "10",
                "20",
                "30",
            ),
        ],
    )
    def test_check_permissions_with_missing_values(
        self, user_permissions, theme_id, sub_theme_id, topic_id
    ):
        """
        Given a permission set that is missing values
        When the `check_permissions` function is called
        Then the function returns false
        """
        assert (
            check_permissions(
                permission_sets=user_permissions,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
            )
            == False
        )


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
