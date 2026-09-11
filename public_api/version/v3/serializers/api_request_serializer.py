from dataclasses import dataclass

from public_api.version.v2.serializers.api_time_series_request_serializer import (
    APITimeSeriesRequestSerializerv2,
)


@dataclass
class APIDTO:
    information: str = ""
    name: str = ""
    theme: str = ""
    sub_theme: str = ""
    topic: str = ""
    geography_type: str = ""
    geography: str = ""
    metric: str = ""
    url_prefix: str = ""


NO_LOOKUP_FIELD_ERROR_MESSAGE = (
    "A `lookup_field` must be provided in the context of the serializer"
)


class APIRequestSerializerv3(APITimeSeriesRequestSerializerv2):

    @property
    def api_model(self) -> "APIManager":
        return self.context.get("api_model")

    def build_dto(self, value) -> APIDTO:
        """Builds a simple `APIDTO` from the kwargs of the request and the given `value`
        Also sets the `lookup_field` and `name` attributes on the dto to be the given `value`.

        Args:
            value: The lookup value retrieved from the queryset

        Returns:
            `APITimeSeriesDTO`: The created data transfer object

        """
        request_kwargs = self.context["request"].parser_context["kwargs"]

        api_dto = APIDTO(**request_kwargs)
        api_dto.name = " ".join(value.split("+"))
        api_dto.url_prefix = self.context["url_prefix"]
        setattr(api_dto, self.lookup_field, value)
        return api_dto

    def get_queryset(self, **kwargs) -> "APIQuerySet":
        """
        Returns:
            APIQuerySet: The column values as a queryset.
            Examples:
                `<APIQuerySet ['infectious_disease']>`

        """
        request_kwargs = self.context["request"].parser_context["kwargs"]
        return self.api_model.objects.get_distinct_column_values_with_filters(
            lookup_field=self.lookup_field,
            restrict_to_public=True,  # because we are not allowing non-public data through the public API
            **request_kwargs
        )

    def build_dto_slice(self) -> list[APIDTO]:
        """Builds a list of simple `APIDTO` from the kwargs of the request and the given `value`

        Returns:
            List[APIDTO]: List of created data transfer objects
        """
        queryset = self.get_queryset()
        return [self.build_dto(value="+".join(value.split(" "))) for value in queryset]
