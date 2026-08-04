import csv
import io

PIVOT_VALUE_FIELDS = ["metric_value"]

HEADLINE_METADATA_FIELDS = (
    "theme",
    "sub_theme",
    "topic",
    "geography_type",
    "geography",
    "metric",
    "stratum",
    "period_start",
    "period_end",
)

TIMESERIES_METADATA_FIELDS = (
    "theme",
    "sub_theme",
    "topic",
    "geography_type",
    "geography",
    "metric",
    "stratum",
    "sex",
    "year",
    "in_reporting_delay_period",
)


def pivot_dual_category_download_rows(
    *,
    rows: list[dict],
    x_axis: str,
    secondary_category: str,
) -> list[dict]:
    """
    Collapse multiple segment rows that share the same primary axis value into one row.

    Args:
        rows: Serialized download rows with one record per plot query.
        x_axis: Field used to group rows, e.g. `age` or `date`.
        secondary_category: Field whose values become column/key names, e.g. `sex`.

    Returns:
        Collapsed rows with segment values as keys mapped to `metric_value`.

    Examples:
        Input::
        ```
        pivot_dual_category_download_rows (
            rows=[
                {
                    "topic": "Lead",
                    "metric": "lead_headline_ratesByAgeSex",
                    "stratum": "default",
                    "age": "00-01",
                    "sex": "f",
                    "metric_value": 12.3,
                },
                {
                    "topic": "Lead",
                    "metric": "lead_headline_ratesByAgeSex",
                    "stratum": "default",
                    "age": "00-01",
                    "sex": "m",
                    "metric_value": 11.8,
                },
            ],
            x_axis="age",
            secondary_category="sex",
        ):
        ```

        Output::
        ```
            [
                {
                    "topic": "Lead",
                    "metric": "lead_headline_ratesByAgeSex",
                    "stratum": "default",
                    "age": "00-01",
                    "f": 12.3,
                    "m": 11.8,
                }
            ]
        ```
    """
    grouped: dict[str, dict] = {}

    for row in rows:
        group_key = str(row[x_axis])
        if group_key not in grouped:
            pivoted_row = {x_axis: row[x_axis]}
            for key, value in row.items():
                if key in PIVOT_VALUE_FIELDS or key == secondary_category:
                    continue
                pivoted_row[key] = value
            grouped[group_key] = pivoted_row

        secondary_value = str(row[secondary_category])
        grouped[group_key][secondary_value] = row["metric_value"]

    return list(grouped.values())


def build_dual_category_csv_headers(
    *,
    is_headline: bool,
    x_axis: str,
    secondary_category: str,
    segment_secondary_values: list[str],
) -> list[str]:
    """Build CSV headers for a dual-category download export.

    Args:
        is_headline: Whether the export is for headline data.
        x_axis: Primary axis field name included in the header row.
        secondary_category: Pivoted dimension excluded from metadata columns.
        segment_secondary_values: Secondary segment values appended as columns.

    Returns:
        Ordered list of CSV column headers.
    """
    metadata_fields = (
        HEADLINE_METADATA_FIELDS if is_headline else TIMESERIES_METADATA_FIELDS
    )
    headers = [field for field in metadata_fields if field != secondary_category].copy()
    if x_axis not in headers:
        headers.append(x_axis)

    for segment_value in segment_secondary_values:
        headers.append(segment_value)

    return headers


def write_dual_category_data_to_csv(
    *,
    file: io.StringIO,
    rows: list[dict],
    headers: list[str],
) -> io.StringIO:
    """Write pivoted dual-category download rows to a CSV file.

    Args:
        file: CSV output buffer to write to.
        rows: Pivoted download rows to serialize.
        headers: Column headers for the CSV output.

    Returns:
        The CSV file buffer with header and row data written.
    """
    writer = csv.DictWriter(file, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return file
