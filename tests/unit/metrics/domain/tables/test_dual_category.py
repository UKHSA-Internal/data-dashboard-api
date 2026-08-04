import datetime
from decimal import Decimal

from metrics.domain.common.utils import ChartAxisFields
from metrics.domain.models.plots import PlotGenerationData, PlotParameters
from metrics.domain.models.tables.dual_category import DualCategoryTableRequestParams
from metrics.domain.tables.generation import (
    LOWER_CONFIDENCE,
    UPPER_CONFIDENCE,
    DualCategoryTabularData,
)


def _plot(
    *,
    label: str,
    x_axis_values: list,
    y_axis_values: list,
    x_axis: str = ChartAxisFields.date.name,
    in_reporting_delay_period: list[bool] | None = None,
) -> PlotGenerationData:
    additional_values = {}
    if in_reporting_delay_period is not None:
        additional_values["in_reporting_delay_period"] = in_reporting_delay_period

    return PlotGenerationData(
        parameters=PlotParameters(
            topic="Lead",
            metric="lead_headline_ratesByAgeSex",
            label=label,
            x_axis=x_axis,
            y_axis=ChartAxisFields.metric.name,
            sex="f" if label == "Females" else "m",
        ),
        x_axis_values=x_axis_values,
        y_axis_values=y_axis_values,
        additional_values=additional_values,
    )


def _request_params(**kwargs) -> DualCategoryTableRequestParams:
    defaults = {
        "plots": [],
        "file_format": "svg",
        "chart_width": 515,
        "chart_height": 220,
        "x_axis": ChartAxisFields.date.name,
        "y_axis": ChartAxisFields.metric.name,
    }
    defaults.update(kwargs)
    return DualCategoryTableRequestParams(**defaults)


class TestDualCategoryTabularData:
    def test_headline_groups_by_primary_axis_with_segment_labels(self):
        """
        Given a dual-category tabular data is created
        When `create_tabular_plots()` is called on `DualCategoryTabularData`
        Then the data is grouped by primary axis with segment labels
        """
        # Given
        request_params = _request_params(
            secondary_category="sex",
            segment_secondary_values=["f", "m"],
            primary_field_values=["00-01", "01-04"],
            x_axis=ChartAxisFields.age.name,
        )
        plots = [
            _plot(
                label="Females",
                x_axis_values=["00 - 01"],
                y_axis_values=[Decimal("10.0000")],
                x_axis=ChartAxisFields.age.name,
            ),
            _plot(
                label="Males",
                x_axis_values=["00 - 01"],
                y_axis_values=[Decimal("1.0000")],
                x_axis=ChartAxisFields.age.name,
            ),
            _plot(
                label="Females",
                x_axis_values=["01 - 04"],
                y_axis_values=[Decimal("20.0000")],
                x_axis=ChartAxisFields.age.name,
            ),
            _plot(
                label="Males",
                x_axis_values=["01 - 04"],
                y_axis_values=[Decimal("2.0000")],
                x_axis=ChartAxisFields.age.name,
            ),
        ]

        # When
        result = DualCategoryTabularData(
            plots=plots,
            primary_field_values=request_params.primary_field_values,
        ).create_tabular_plots()

        # Then
        assert result == [
            {
                "reference": "00 - 01",
                "values": [
                    {
                        "label": "Females",
                        "value": "10.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Males",
                        "value": "1.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "01 - 04",
                "values": [
                    {
                        "label": "Females",
                        "value": "20.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Males",
                        "value": "2.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]

    def test_timeseries_groups_by_date_with_segment_labels(self):
        """
        Given a dual-category timeseries tabular data is created
        When `create_tabular_plots()` is called on `DualCategoryTabularData`
        Then the data is grouped by date with segment labels
        """
        # Given
        request_params = _request_params(
            secondary_category="sex",
            segment_secondary_values=["f", "m"],
            primary_field_values=[],
        )
        plots = [
            _plot(
                label="Females",
                x_axis_values=[
                    datetime.date(2024, 12, 30),
                    datetime.date(2024, 12, 29),
                ],
                y_axis_values=[Decimal("10.0000"), Decimal("11.0000")],
                in_reporting_delay_period=[False, True],
            ),
            _plot(
                label="Males",
                x_axis_values=[
                    datetime.date(2024, 12, 30),
                    datetime.date(2024, 12, 29),
                ],
                y_axis_values=[Decimal("1.0000"), Decimal("1.5000")],
                in_reporting_delay_period=[False, False],
            ),
        ]

        # When
        result = DualCategoryTabularData(
            plots=plots,
            primary_field_values=request_params.primary_field_values,
        ).create_tabular_plots()

        # Then
        assert result == [
            {
                "reference": "2024-12-30",
                "values": [
                    {
                        "label": "Females",
                        "value": "10.0000",
                        "in_reporting_delay_period": False,
                    },
                    {
                        "label": "Males",
                        "value": "1.0000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
            {
                "reference": "2024-12-29",
                "values": [
                    {
                        "label": "Females",
                        "value": "11.0000",
                        "in_reporting_delay_period": True,
                    },
                    {
                        "label": "Males",
                        "value": "1.5000",
                        "in_reporting_delay_period": False,
                    },
                ],
            },
        ]

    def test_add_plot_data_to_combined_plots_includes_confidence_intervals(
        self, valid_plot_parameters: PlotParameters
    ):
        """
        Given plot data with confidence intervals
        When `add_plot_data_to_combined_plots()` is called on `DualCategoryTabularData`
        Then the confidence intervals are included in the result.

        Notes:
            For Dual-category tabular data, we won't need upper and lower confidence intervals
            as these are not supported for this type of data but we need this test to have 100% coverage
            since we are subclassing from `TabularData` which needs this test.
        """
        # Given
        plot_data = {datetime.date(2023, 1, 1): Decimal("10.5")}
        upper_confidence_lookup = {datetime.date(2023, 1, 1): Decimal("12.0")}
        lower_confidence_lookup = {datetime.date(2023, 1, 1): Decimal("9.0")}

        tabular_data = DualCategoryTabularData(
            plots=[
                PlotGenerationData(
                    parameters=valid_plot_parameters,
                    x_axis_values="",
                    y_axis_values="",
                )
            ]
        )

        # When
        tabular_data.add_plot_data_to_combined_plots(
            plot_data=plot_data,
            plot_label="Females",
            upper_confidence_lookup=upper_confidence_lookup,
            lower_confidence_lookup=lower_confidence_lookup,
        )

        # Then
        assert tabular_data.combined_plots["2023-01-01"][UPPER_CONFIDENCE] == "12.0"
        assert tabular_data.combined_plots["2023-01-01"][LOWER_CONFIDENCE] == "9.0"
