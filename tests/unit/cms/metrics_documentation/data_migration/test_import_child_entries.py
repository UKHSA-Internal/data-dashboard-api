import pytest

from cms.metrics_documentation.data_migration.import_child_entries import build_sections


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
