from unittest import mock

from wagtail.api.v2.serializers import PageParentField

from cms.dashboard.fields import ListablePageParentField

MODULE_PATH = "cms.dashboard.fields"


class TestListablePageParentField:
    def test_returns_none_when_parent_instance_is_none(self):
        """
        Given a page instance which does not have a parent
        When `get_attribute()` is called from an instance
            of `ListablePageParentField`
        Then None is returned
        """
        # Given
        mocked_page_instance = mock.Mock()
        mocked_page_instance.get_parent.return_value = None
        listable_page_parent_field = ListablePageParentField(read_only=True)
        listable_page_parent_field._context = mock.MagicMock()

        # When
        returned_attribute = listable_page_parent_field.get_attribute(
            instance=mocked_page_instance
        )

        # Then
        assert returned_attribute is None

    @mock.patch.object(PageParentField, "get_attribute")
    def test_calls_super_method(self, spy_get_attribute: mock.MagicMock):
        """
        Given a page instance
        When `get_attribute()` is called from an instance
            of `ListablePageParentField`
        Then the call is delegated to the `get_attribute()`
            method on the parent class
        """
        # Given
        mocked_page_instance = mock.Mock()
        listable_page_parent_field = ListablePageParentField(read_only=True)

        # When
        returned_attribute = listable_page_parent_field.get_attribute(
            instance=mocked_page_instance
        )

        # Then
        spy_get_attribute.assert_called_once_with(instance=mocked_page_instance)
        assert returned_attribute == spy_get_attribute.return_value
