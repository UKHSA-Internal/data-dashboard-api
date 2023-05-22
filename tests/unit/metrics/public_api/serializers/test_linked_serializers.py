from unittest import mock

from rest_framework.serializers import HyperlinkedIdentityField

from metrics.public_api.serializers.api_time_series_request_serializer import (
    APITimeSeriesDTO,
)
from metrics.public_api.serializers.linked_serializers import ThemeListSerializer


class TestThemeListSerializer:
    @mock.patch.object(
        HyperlinkedIdentityField, "get_url", return_value="fake_url_for_theme"
    )
    def test_can_serialize_successfully(
        self,
        spy_get_url: mock.MagicMock,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `ThemeListSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with `theme-detail` view and the `theme` value of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        mocked_request = mock.MagicMock(
            parser_context={"kwargs": {"theme": theme_value}}
        )
        timeseries_dto_slice = APITimeSeriesDTO(name=theme_value, theme=theme_value)

        # When
        serializer = ThemeListSerializer(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `HyperlinkedIdentityField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "theme-detail",
            # view -> `theme-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == theme_value
        assert serialized_data["link"] == "fake_url_for_theme"
        assert serializer.fields["link"].lookup_field == "theme"
