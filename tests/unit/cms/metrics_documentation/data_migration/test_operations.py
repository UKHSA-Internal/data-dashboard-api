from unittest import mock

from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page,
)
from tests.fakes.managers.cms.metrics_documentation_parent_page_manager import (
    FakeMetricsDocumentationParentPageManager,
)
from tests.fakes.models.cms.metrics_documentation_parent import (
    FakeMetricsDocumentationParentPage,
)

MODULE_PATH = "cms.metrics_documentation.data_migration.operations"


class TestCreateMetricsDocumentationParentPage:
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
        returned_parent_page = create_metrics_documentation_parent_page(
            metrics_documentation_parent_page_manager=fake_metrics_documentation_parent_page_manager
        )

        # Then
        assert returned_parent_page == parent_page
        spy_create_metrics_documentation_parent_page.assert_not_called()
