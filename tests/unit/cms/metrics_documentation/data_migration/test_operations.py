from unittest import mock

from _pytest.logging import LogCaptureFixture
from django.core.exceptions import ValidationError

from cms.metrics_documentation.data_migration.operations import (
    create_metrics_documentation_parent_page_and_child_entries,
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


class TestCreateMetricsDocumentationParentPageAndChildEntries:
    @mock.patch(f"{MODULE_PATH}._build_metrics_documentation_child_entry")
    @mock.patch(f"{MODULE_PATH}.add_page_as_subpage_to_parent")
    @mock.patch(f"{MODULE_PATH}.get_or_create_metrics_documentation_parent_page")
    @mock.patch(f"{MODULE_PATH}.remove_metrics_documentation_child_entries")
    def test_log_recorded_when_metric_not_available_for_child_page(
        self,
        mocked_remove_metrics_documentation_child_entries: mock.MagicMock,
        mocked_get_or_create_metrics_documentation_parent_page: mock.MagicMock,
        mocked_add_page_as_subpage_to_parent: mock.MagicMock,
        mocked_build_metrics_documentation_child_entry,
        caplog: LogCaptureFixture,
    ):
        """
        Given a metric which does not exist
        And the `add_page_as_subpage_to_parent()` function
            which will subsequently throw a `ValidationError`
        When `create_metrics_documentation_parent_page_and_child_entries()` is called
        Then the correct log is recorded

        Patches:
            `mocked_build_metrics_documentation_child_entry`: To remove
                the side effect of building the `MetricsDocumentationChildEntry`
                model which makes a db call to get available metrics
                as part of its initialization
            `mocked_add_page_as_subpage_to_parent`: To simulate
                the side effect of a `ValidationError` being raised
                when adding the page to the parent page
            `mocked_get_or_create_metrics_documentation_parent_page`: To remove
                the side effect of creating a `MetricsDocumentationParentPage`
                model and having to interact with the db
            `mocked_remove_metrics_documentation_child_entries`: To remove
                the side effect of removing all `MetricsDocumentationChildEntry`
                records, which would also have resulted in
                having to interact with the db

        """
        # Given
        fake_metric = "COVID-19_cases_rateRollingMean"
        mocked_add_page_as_subpage_to_parent.side_effect = ValidationError(fake_metric)

        # When
        create_metrics_documentation_parent_page_and_child_entries()

        # Then
        expected_log = (
            f"Metrics Documentation Child Entry for {fake_metric} was not created. "
            "Because the corresponding `Metric` was not created beforehand"
        )

        assert expected_log in caplog.text
