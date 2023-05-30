from unittest import mock

from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedRelatedField

from metrics.public_api.serializers.api_time_series_request_serializer import (
    APITimeSeriesDTO,
)
from metrics.public_api.serializers.linked_serializers import (
    SubThemeDetailSerializer,
    SubThemeListSerializer,
    ThemeDetailSerializer,
    ThemeListSerializer,
    TopicListSerializer,
)


class TestThemeListSerializer:
    @mock.patch.object(
        HyperlinkedIdentityField, "get_url", return_value="fake_url_for_themes/"
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
        assert serialized_data["link"] == "fake_url_for_themes/"
        assert serializer.fields["link"].lookup_field == "theme"


class TestThemeDetailSerializer:
    @mock.patch.object(
        HyperlinkedIdentityField,
        "get_url",
        return_value="fake_url_for_related_sub_themes/",
    )
    def test_can_serialize_successfully(self, spy_get_url: mock.MagicMock):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `ThemeDetailSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `sub_theme-list` view and the `theme` value of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        mocked_request = mock.MagicMock(
            parser_context={"kwargs": {"theme": theme_value}}
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=theme_value,
            theme=theme_value,
        )

        # When
        serializer = ThemeDetailSerializer(
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
            "sub_theme-list",
            # view -> `sub-theme-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["information"] == ""
        assert serialized_data["sub_themes"] == "fake_url_for_related_sub_themes/"


class TestSubThemeListSerializer:
    @mock.patch.object(
        NestedHyperlinkedRelatedField, "get_url", return_value="fake_url_for_sub_theme/"
    )
    def test_can_serialize_successfully(
        self,
        spy_get_url: mock.MagicMock,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `SubThemeListSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with `sub_theme-detail` view
        And the `sub_theme` value of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        sub_theme_value = "respiratory"
        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {"theme": theme_value, "sub_theme": sub_theme_value}
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=sub_theme_value, theme=theme_value, sub_theme=sub_theme_value
        )

        # When
        serializer = SubThemeListSerializer(
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
            "sub_theme-detail",
            # view -> `sub_theme-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == sub_theme_value
        assert serialized_data["link"] == "fake_url_for_sub_theme/"
        assert serializer.fields["link"].lookup_field == "sub_theme"


class TestSubThemeDetailSerializer:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_related_topics/",
    )
    def test_can_serialize_successfully(self, spy_get_url: mock.MagicMock):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `SubThemeDetailSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `topic-list` view
            as well as the `theme` and `sub_theme` values of the `APITimeSeriesDTO`
        """
        sub_theme_value = "respiratory"
        theme_value = "infectious_disease"
        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {"theme": theme_value, "sub_theme": sub_theme_value}
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=sub_theme_value,
            theme=theme_value,
            sub_theme=sub_theme_value,
        )

        # When
        serializer = SubThemeDetailSerializer(
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
            "topic-list",
            # view -> `topic-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["information"] == ""
        assert serialized_data["topics"] == "fake_url_for_related_topics/"


class TestTopicListSerializer:
    @mock.patch.object(
        NestedHyperlinkedRelatedField, "get_url", return_value="fake_url_for_topics/"
    )
    def test_can_serialize_successfully(
        self,
        spy_get_url: mock.MagicMock,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `TopicListSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `topic-detail` view
            as well as the `theme` and `sub_theme` values of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        sub_theme_value = "respiratory"
        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {"theme": theme_value, "sub_theme": sub_theme_value}
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=sub_theme_value, theme=theme_value, sub_theme=sub_theme_value
        )

        # When
        serializer = TopicListSerializer(
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
            "topic-detail",
            # view -> `topic-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == sub_theme_value
        assert serialized_data["link"] == "fake_url_for_topics/"
        assert serializer.fields["link"].lookup_field == "topic"
