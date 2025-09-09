from tests.factories.metrics.headline import CoreHeadlineFactory
from tests.factories.metrics.time_series import CoreTimeSeriesFactory


def create_example_core_timeseries() -> None:
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name="6-in-1_coverage_coverageByYear",
        stratum_name="12m",
        date="2021-03-31",
        geography_name="Darlington",
        geography_type_name="Upper Tier Local Authority",
        metric_value=90,
    )
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name="6-in-1_coverage_coverageByYear",
        stratum_name="12m",
        date="2021-03-31",
        geography_name="North East",
        geography_type_name="Region",
        metric_value=97,
    )
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name="6-in-1_coverage_coverageByYear",
        stratum_name="12m",
        date="2021-03-31",
        geography_name="England",
        geography_type_name="Nation",
        metric_value=88,
    )

    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name="6-in-1_coverage_coverageByYear",
        stratum_name="24m",
        date="2021-03-31",
        geography_name="Darlington",
        geography_type_name="Upper Tier Local Authority",
        metric_value=87,
    )
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name="6-in-1_coverage_coverageByYear",
        stratum_name="24m",
        date="2021-03-31",
        geography_name="North East",
        geography_type_name="Region",
        metric_value=89,
    )
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name="6-in-1_coverage_coverageByYear",
        stratum_name="24m",
        date="2021-03-31",
        geography_name="England",
        geography_type_name="Nation",
        metric_value=78,
    )

    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="MMR1",
        metric_name="MMR1_coverage_coverageByYear",
        stratum_name="24m",
        date="2021-03-31",
        geography_name="Darlington",
        geography_type_name="Upper Tier Local Authority",
        metric_value=93,
    )
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="MMR1",
        metric_name="MMR1_coverage_coverageByYear",
        stratum_name="24m",
        date="2021-03-31",
        geography_name="North East",
        geography_type_name="Region",
        metric_value=84,
    )
    # There is intentionally no corresponding record for England / MMR1 / 24m


def create_example_core_headlines() -> None:
    CoreHeadlineFactory.create_record(
        theme="infectious_disease",
        sub_theme="respiratory",
        topic="COVID-19",
        metric="COVID-19_headline_tests_7DayTotal",
        stratum="default",
        period_start="2021-03-31",
        period_end="2021-03-31",
        geography="Darlington",
        geography_type="Upper Tier Local Authority",
        metric_value=86,
    )
    CoreHeadlineFactory.create_record(
        theme="infectious_disease",
        sub_theme="respiratory",
        topic="COVID-19",
        metric="COVID-19_headline_tests_7DayTotal",
        stratum="default",
        period_start="2021-03-31",
        period_end="2021-03-31",
        geography="North East",
        geography_type="Region",
        metric_value=85,
    )
    CoreHeadlineFactory.create_record(
        theme="infectious_disease",
        sub_theme="respiratory",
        topic="COVID-19",
        metric="COVID-19_headline_tests_7DayTotal",
        stratum="default",
        period_start="2021-03-31",
        period_end="2021-03-31",
        geography="England",
        geography_type="Nation",
        metric_value=90,
    )
