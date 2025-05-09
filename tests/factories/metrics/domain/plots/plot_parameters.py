import datetime

import factory

from metrics.domain.models import PlotParameters


class FakePlotParameters(factory.Factory):
    """
    Factory for creating `FakePlotParameters` instances for tests.
    """

    class Meta:
        model = PlotParameters

    @classmethod
    def build_plot_parameters(
        cls,
        chart_type: str = "line_multi_coloured",
        topic: str = "COVID-19",
        metric: str = "COVID-19_cases_casesByDay",
        stratum: str = "default",
        geography: str = "England",
        geography_type: str = "Nation",
        age: str = "all",
        sex: str = "all",
        date_from: datetime.datetime | str = str(datetime.date(2023, 2, 10)),
        date_to: datetime.datetime | str = str(datetime.date(2024, 2, 10)),
        x_axis: str = "date",
        y_axis: str = "metric",
    ) -> PlotParameters:

        return cls.build(
            chart_type=chart_type,
            topic=topic,
            metric=metric,
            stratum=stratum,
            geography=geography,
            geography_type=geography_type,
            age=age,
            sex=sex,
            date_from=date_from,
            date_to=date_to,
            x_axis=x_axis,
            y_axis=y_axis,
        )
