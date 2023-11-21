from enum import Enum


class DataSourceFileType(Enum):
    # Headline types
    headline = "headline"

    # Timeseries types
    cases = "cases"
    deaths = "deaths"
    healthcare = "healthcare"
    testing = "testing"
    vaccinations = "vaccinations"

    @classmethod
    def headline_types(cls) -> list[str]:
        return [f"{cls.headline.value}_"]

    @classmethod
    def timeseries_types(cls) -> list[str]:
        timeseries_file_types = (
            cls.cases,
            cls.deaths,
            cls.healthcare,
            cls.testing,
            cls.vaccinations,
        )
        return [
            f"{timeseries_file_type.value}_"
            for timeseries_file_type in timeseries_file_types
        ]
