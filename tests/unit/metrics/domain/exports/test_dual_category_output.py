import io

import pytest

from metrics.domain.exports.dual_category_output import (
    build_dual_category_csv_headers,
    pivot_dual_category_download_rows,
    write_dual_category_data_to_csv,
)


class TestPivotDualCategoryDownloadRows:
    def test_pivots_headline_rows_by_secondary_category(self):
        """
        Given flat headline rows grouped by age with sex as the secondary category
        When `pivot_dual_category_download_rows()` is called
        Then one row is returned with segment values as keys for metric values
        """
        # Given
        rows = [
            {
                "theme": "t",
                "topic": "Lead",
                "metric": "lead_headline_ratesByAgeSex",
                "stratum": "default",
                "age": "00-01",
                "sex": "f",
                "metric_value": 12.3,
            },
            {
                "theme": "t",
                "topic": "Lead",
                "metric": "lead_headline_ratesByAgeSex",
                "stratum": "default",
                "age": "00-01",
                "sex": "m",
                "metric_value": 11.8,
            },
        ]

        # When
        result = pivot_dual_category_download_rows(
            rows=rows,
            x_axis="age",
            secondary_category="sex",
        )

        # Then
        assert len(result) == 1
        assert result[0]["age"] == "00-01"
        assert result[0]["metric"] == "lead_headline_ratesByAgeSex"
        assert result[0]["stratum"] == "default"
        assert result[0]["f"] == pytest.approx(12.3)
        assert result[0]["m"] == pytest.approx(11.8)
        assert "sex" not in result[0]
        assert "metric_value" not in result[0]


class TestDualCategoryCsvOutput:
    def test_writes_pivoted_rows_to_csv(self):
        """
        Given pivoted download rows and headline CSV headers
        When `write_dual_category_data_to_csv()` is called
        Then the CSV contains segment columns and the pivoted metric values
        """
        # Given
        rows = [
            {
                "topic": "Lead",
                "metric": "lead_headline_ratesByAgeSex",
                "stratum": "default",
                "age": "00-01",
                "f": 12.3,
                "m": 11.8,
            }
        ]
        headers = build_dual_category_csv_headers(
            is_headline=True,
            x_axis="age",
            secondary_category="sex",
            segment_secondary_values=["f", "m"],
        )
        output = io.StringIO()

        # When
        write_dual_category_data_to_csv(file=output, rows=rows, headers=headers)
        csv_content = output.getvalue()

        # Then
        normalised_csv = csv_content.replace("\r\n", "\n")
        header_row = normalised_csv.splitlines()[0]
        data_row = normalised_csv.splitlines()[1]
        assert "metric" in header_row
        assert "stratum" in header_row
        assert "f,m" in header_row
        assert "lead_headline_ratesByAgeSex" in data_row
        assert "default" in data_row
        assert "00-01,12.3,11.8" in data_row
