from metrics.data.managers.api_models.time_series import APITimeSeriesManager


class FakeAPITimeSeriesManager(APITimeSeriesManager):
    """
    A fake version of the `APITimeSeriesManager` which allows the methods and properties
    to be overriden to allow the database to be abstracted away.
    """

    def __init__(self, time_series, **kwargs):
        self.time_series = time_series
        super().__init__(**kwargs)

    def get_distinct_column_values_with_filters(
        self, lookup_field, **kwargs
    ) -> list[str]:
        filtered_time_series = self.time_series
        for field_name, field_value in kwargs.items():
            filtered_time_series = [
                t for t in filtered_time_series if getattr(t, field_name) == field_value
            ]

        lookup_values_of_timeseries: set[str] = {
            getattr(x, lookup_field) for x in filtered_time_series
        }
        return list(lookup_values_of_timeseries)

    def exists(self) -> bool:
        return bool(self.time_series)
