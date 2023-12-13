from unittest import mock

from cms.metrics_documentation.utils.import_metrics_documentation_child_entries import (
    get_metrics_definitions,
)

MODULE_PATH: str = (
    "cms.metrics_documentation.utils.import_metrics_documentation_child_entries"
)


class TestGetMetricsDefinition:
    work_sheet = mock.MagicMock()

    @mock.patch.object(openpyxl, "load_workbook")
    @mock.patch(f"{MODULE_PATH}.build_sections")
    @mock.patch(f"{MODULE_PATH}.build_entry_from_row_data")
    def test_delegates_calls_correctly(
        self,
        spy_build_entry_from_row_data: mock.MagicMock,
        spy_build_sections: mock.MagicMock,
    ):
        """
        Given a tuple containing row data from a spreadsheet.
        When `get_metrics_definition()` is called.
        Then `build_entry_from_row_data()` and `build_sections()` are called.
        """
        # Given

        # When
        get_metrics_definitions()

        # Then
        spy_build_entry_from_row_data.assert_called_once()
        spy_build_sections.assert_called_once()
