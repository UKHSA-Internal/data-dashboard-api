from unittest import mock

from cms.metrics_documentation.data_migration.child_entries import (
    _load_source_data_as_worksheet,
    build_sections,
)
from metrics.api.settings import ROOT_LEVEL_BASE_DIR

MODULE_PATH = "cms.metrics_documentation.data_migration.child_entries"


class TestBuildSections:
    def test_returns_correct_list(self):
        """
        Given a list of tuples representing
            the title and body of each section
        When `build_sections()` is called
        Then the correct output is returned
        """
        # Given
        sections = [
            ("Rationale", "Fake rationale content"),
            ("Definition", "Fake definition content"),
            ("Methodology", "Fake methodology content"),
            ("Caveats", "Fake caveats content"),
        ]

        # When
        constructed_sections = build_sections(sections=sections)

        # Then
        for section in sections:
            expected_section = {
                "type": "section",
                "value": {"title": section[0], "body": section[1]},
            }
            assert expected_section in constructed_sections


class TestLoadSourceDataAsWorksheet:
    @mock.patch(f"{MODULE_PATH}.load_workbook")
    def test_delegates_call_with_correct_file_path(
        self, spy_load_workbook: mock.MagicMock
    ):
        """
        Given no input
        When `_load_source_data_as_worksheet()` is called
        Then the call is delegated to the `load_workbook()`
            function with the correct path to the source data sheet

        Patches:
            `spy_load_workbook`: For the main assertion
        """
        # Given / When
        worksheet = _load_source_data_as_worksheet()

        # Then
        assert worksheet == spy_load_workbook.return_value.active
        expected_filename: str = (
            f"{ROOT_LEVEL_BASE_DIR}/cms/metrics_documentation/data_migration/source_data"
            f"/metrics_definitions_migration_edit.xlsx"
        )
        spy_load_workbook.assert_called_with(filename=expected_filename, read_only=True)
