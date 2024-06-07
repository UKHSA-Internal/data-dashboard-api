from unittest import mock

from wagtail.admin.views.chooser import BrowseView

from cms.dashboard.views import LinkBrowseView


class TestLinkBrowseView:
    @mock.patch.object(BrowseView, "get")
    def test_get_endpoint_intercepts_request(
        self, spy_parent_class_get_method: mock.MagicMock
    ):
        """
        Given a fake request object
        When the `get()` method is called
            from an instance of the `LinkBrowseView` class
        Then the request object is intercepted
            and the email & phone link params are set to False
        """

        # Given
        class FakeRequest:
            GET = {}

        fake_request = FakeRequest()
        mocked_parent_page_id = mock.Mock()
        view = LinkBrowseView()

        # When
        view.get(request=fake_request, parent_page_id=mocked_parent_page_id)

        # Then
        assert fake_request.GET["allow_email_link"] is False
        assert fake_request.GET["allow_phone_link"] is False
        spy_parent_class_get_method.assert_called_once_with(
            request=fake_request, parent_page_id=mocked_parent_page_id
        )
