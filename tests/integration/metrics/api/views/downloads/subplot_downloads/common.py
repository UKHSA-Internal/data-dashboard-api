from tests.factories.metrics.time_series import CoreTimeSeriesFactory


def create_example_core_timeseries()  -> None:
    CoreTimeSeriesFactory.create_record(
        theme_name="immunisation",
        sub_theme_name="childhood-vaccines",
        topic_name="6-in-1",
        metric_name=f"6-in-1_coverage_coverageByYear",
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
        metric_name=f"6-in-1_coverage_coverageByYear",
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
        metric_name=f"6-in-1_coverage_coverageByYear",
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
        metric_name=f"6-in-1_coverage_coverageByYear",
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
        metric_name=f"6-in-1_coverage_coverageByYear",
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
        metric_name=f"6-in-1_coverage_coverageByYear",
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
