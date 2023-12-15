from unittest import mock

from cms.metrics_documentation.data_migration.operations import (
    get_or_create_metrics_documentation_parent_page,
)
from tests.fakes.managers.cms.metrics_documentation_parent_page_manager import (
    FakeMetricsDocumentationParentPageManager,
)
from tests.fakes.models.cms.metrics_documentation_parent import (
    FakeMetricsDocumentationParentPage,
)

MODULE_PATH = "cms.metrics_documentation.data_migration.operations"


class TestGetOrCreateMetricsDocumentationParentPage:
    @mock.patch(f"{MODULE_PATH}._create_metrics_documentation_parent_page")
    def test_defaults_to_existing_parent_page_if_available(
        self, spy_create_metrics_documentation_parent_page: mock.MagicMock
    ):
        """
        Given an existing `MetricsDocumentationParentPage` model
        When `get_or_create_metrics_documentation_parent_page()` is called
        Then the pre-existing `MetricsDocumentationParentPage`
            model is returned

        Patches:
            `spy_create_metrics_documentation_parent_page`: To check
                that a new model is not created when there is
                already a valid existing model

        """
        # Given
        parent_page = FakeMetricsDocumentationParentPage(slug="metrics-documentation")
        fake_metrics_documentation_parent_page_manager = (
            FakeMetricsDocumentationParentPageManager(pages=[parent_page])
        )

        # When
        returned_parent_page = get_or_create_metrics_documentation_parent_page(
            metrics_documentation_parent_page_manager=fake_metrics_documentation_parent_page_manager
        )

        # Then
        assert returned_parent_page == parent_page
        spy_create_metrics_documentation_parent_page.assert_not_called()

    @mock.patch(f"{MODULE_PATH}._create_metrics_documentation_parent_page")
    def test_delegates_call_to_create_metrics_documentation_parent_page_when_not_readily_available(
        self, spy_create_metrics_documentation_parent_page: mock.MagicMock
    ):
        """
        Given no existing `MetricsDocumentationParentPage` model
        When `get_or_create_metrics_documentation_parent_page()` is called
        Then the call is delegated to
            `_create_metrics_documentation_parent_page()`

        Patches:
            `spy_create_metrics_documentation_parent_page`: To check
                that a new model is created when there is
                no pre-existing valid parent page model

        """
        # Given
        fake_metrics_documentation_parent_page_manager = (
            FakeMetricsDocumentationParentPageManager(pages=[])
        )

        # When
        returned_parent_page = get_or_create_metrics_documentation_parent_page(
            metrics_documentation_parent_page_manager=fake_metrics_documentation_parent_page_manager
        )

        # Then
        assert (
            returned_parent_page
            == spy_create_metrics_documentation_parent_page.return_value
        )
        spy_create_metrics_documentation_parent_page.assert_called_once()
