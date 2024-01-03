import pytest

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models.plots import CompletePlotData, PlotParameters
from metrics.interfaces.downloads.access import merge_and_process_querysets
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


class TestMergeAndProcessQuerysets:
    @pytest.mark.django_db
    def test_returns_correct_queryset(self, fake_chart_plot_parameters: PlotParameters):
        """
        Given 2 sets of `CoreTimeSeries` resulting querysets
        When `merge_and_process_querysets()` is called
        Then the merged queryset contains the correct results
            in chronological order starting from the latest results
        """
        # Given
        dates = ("2023-01-01", "2023-01-02", "2023-01-03")
        for date in dates:
            CoreTimeSeriesFactory.create_record(date=date, sex="m", metric_value=123)
            CoreTimeSeriesFactory.create_record(date=date, sex="f", metric_value=456)

        male_queryset = CoreTimeSeries.objects.filter(sex="m").all()
        female_queryset = CoreTimeSeries.objects.filter(sex="f").all()
        complete_plots = [
            CompletePlotData(
                queryset=male_queryset, parameters=fake_chart_plot_parameters
            ),
            CompletePlotData(
                queryset=female_queryset, parameters=fake_chart_plot_parameters
            ),
        ]

        # When
        merged_queryset = merge_and_process_querysets(complete_plots=complete_plots)

        # Then
        # Check that the first 2 results in the queryset are for the latest date only
        # And that the resulting queryset is in choronological order
        first_record = merged_queryset[0]
        assert str(first_record.date) == str(merged_queryset[1].date) == dates[2]
        assert str(merged_queryset[2].date) == str(merged_queryset[3].date) == dates[1]
        assert str(merged_queryset[4].date) == str(merged_queryset[5].date) == dates[0]

        # Check that the sample first record taken from the results
        # has all the correct fields in the correct index position of the tuple
        # and they can be reached via the dunder notation
        assert len(first_record) == 12
        assert (
            first_record[0]
            == first_record.metric__topic__sub_theme__theme__name
            == "infectious_disease"
        )
        assert (
            first_record[1]
            == first_record.metric__topic__sub_theme__name
            == "respiratory"
        )
        assert first_record[2] == first_record.metric__topic__name == "COVID-19"
        assert (
            first_record[3] == first_record.geography__geography_type__name == "Nation"
        )
        assert first_record[4] == first_record.geography__name == "England"
        assert (
            first_record[5] == first_record.metric__name == "COVID-19_cases_casesByDay"
        )
        assert first_record[6] == first_record.sex == "f"
        assert first_record[7] == first_record.age__name == "all"
        assert first_record[8] == first_record.stratum__name == "default"
        assert first_record[9] == first_record.year == 2023
        assert str(first_record[10]) == str(first_record.date) == dates[2]
        assert str(first_record[11]) == str(first_record.metric_value) == f"{456:.4f}"
