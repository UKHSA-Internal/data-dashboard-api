from dataclasses import dataclass
from typing import Dict, List

from rest_framework.serializers import Serializer

from metrics.data.managers.api_models.time_series import (
    APITimeSeriesManager,
    APITimeSeriesQuerySet,
)
from metrics.data.models.api_models import APITimeSeries


@dataclass
class APITimeSeriesDTO:
    information: str = ""
    name: str = ""
    theme: str = ""
    sub_theme: str = ""
    topic: str = ""
    geography_type: str = ""
    geography: str = ""
    metric: str = ""


NO_LOOKUP_FIELD_ERROR_MESSAGE = (
    "A `lookup_field` must be provided in the context of the serializer"
)


class APITimeSeriesRequestSerializer(Serializer):
    @property
    def lookup_field(self):
        try:
            return self.context["lookup_field"]
        except KeyError as error:
            raise NotImplementedError(NO_LOOKUP_FIELD_ERROR_MESSAGE) from error

    @property
    def api_time_series_manager(self) -> APITimeSeriesManager:
        return self.context.get("api_time_series_manager", APITimeSeries.objects)

    def get_kwargs_from_request(self) -> Dict[str, str]:
        """Gets the kwargs from the request passed into the context by the view object.
        Note that the `kwargs` are provided by the caller in the form of the URL parameters.

        Returns:
            Dict[str, str]: kwargs dict of the URL parameters and their values.
            Examples:
                `{"theme": "infectious_disease"}

        """
        return self.context["request"].parser_context["kwargs"]

    def build_timeseries_dto(self, value) -> APITimeSeriesDTO:
        """Builds a simple `APITimeSeriesDTO` from the kwargs of the request and the given `value`
        Also sets the `lookup_field` and `name` attributes on the dto to be the given `value`.

        Args:
            value: The lookup value retrieved from the queryset

        Returns:
            `APITimeSeriesDTO`: The created data transfer object

        """
        request_kwargs = self.get_kwargs_from_request()
        api_timeseries_dto = APITimeSeriesDTO(**request_kwargs)

        api_timeseries_dto.name = value
        setattr(api_timeseries_dto, self.lookup_field, value)
        return api_timeseries_dto

    def get_queryset(self) -> APITimeSeriesQuerySet:
        """Calls out to the `APITimeSeriesManager` to get the distinct values as dictated the request kwargs.

        Returns:
            APITimeSeriesQuerySet: The unique column values as a queryset.
            Examples:
                `<APITimeSeriesQuerySet ['infectious_disease']>`

        """
        kwargs: Dict[str, str] = self.get_kwargs_from_request()
        return self.api_time_series_manager.get_distinct_column_values_with_filters(
            lookup_field=self.lookup_field, **kwargs
        )

    def build_timeseries_dto_slice(self) -> List[APITimeSeriesDTO]:
        """Builds a list of simple `APITimeSeriesDTO` from the kwargs of the request and the given `value`

        Returns:
            List[APITimeSeriesDTO]: List of created data transfer objects

        """
        queryset: APITimeSeriesQuerySet = self.get_queryset()
        return [self.build_timeseries_dto(value) for value in queryset]
