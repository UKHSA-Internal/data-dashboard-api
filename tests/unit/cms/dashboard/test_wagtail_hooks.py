from unittest import mock

from cms.dashboard import wagtail_hooks

MODULE_PATH = "cms.dashboard.wagtail_hooks"


@mock.patch(f"{MODULE_PATH}.config")
@mock.patch(f"{MODULE_PATH}.frontend.revalidate_page_via_api_client")
def test_revalidate_frontend_cache_calls_revalidate_page_via_api_client(
    revalidate_page_via_api_client_spy: mock.Mock(),
    mocked_config: mock.Mock(),
):
    """
    Given a page which has been published recently
    When `revalidate_frontend_cache()` is called
    Then `revalidate_page_via_api_client()` is called with the correct args
    """
    # Given
    mocked_page = mock.Mock()

    # When
    wagtail_hooks.revalidate_frontend_cache(sender=mock.Mock(), instance=mocked_page)

    # Then
    revalidate_page_via_api_client_spy.assert_called_once_with(
        slug=mocked_page.slug, config=mocked_config
    )
