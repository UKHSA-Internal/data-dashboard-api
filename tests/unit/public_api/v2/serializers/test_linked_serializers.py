from unittest import mock

from rest_framework.serializers import HyperlinkedIdentityField
from rest_framework_nested.serializers import NestedHyperlinkedRelatedField

from public_api.version_02.serializers.api_time_series_request_serializer import (
    APITimeSeriesDTO,
)
from public_api.version_02.serializers.linked_serializers import (
    GeographyDetailSerializerv2,
    GeographyListSerializerv2,
    GeographyTypeDetailSerializerv2,
    GeographyTypeListSerializerv2,
    MetricListSerializerv2,
    SubThemeDetailSerializerv2,
    SubThemeListSerializerv2,
    ThemeDetailSerializerv2,
    ThemeListSerializerv2,
    TopicDetailSerializerv2,
    TopicListSerializerv2,
)


class TestThemeListSerializerV2:
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
        And creates a link in conjunction with `theme-detail` view
            as well as the `theme` value of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        mocked_request = mock.MagicMock(
            parser_context={"kwargs": {"theme": theme_value}}
        )
        timeseries_dto_slice = APITimeSeriesDTO(name=theme_value, theme=theme_value)

        # When
        serializer = ThemeListSerializerv2(
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
            "theme-detail-v2",
            # view -> `theme-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == theme_value
        assert serialized_data["link"] == spy_get_url.return_value
        assert serializer.fields["link"].lookup_field == "theme"


class TestThemeDetailSerializerV2:
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
        And creates a link in conjunction with the `sub_theme-list` view
            as well as the `theme` value of the `APITimeSeriesDTO`
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
        serializer = ThemeDetailSerializerv2(
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
            "sub_theme-list-v2",
            # view -> `sub-theme-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["sub_themes"] == spy_get_url.return_value


class TestSubThemeListSerializerV2:
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
        serializer = SubThemeListSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "sub_theme-detail-v2",
            # view -> `sub_theme-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == sub_theme_value
        assert serialized_data["link"] == spy_get_url.return_value
        assert serializer.fields["link"].lookup_field == "sub_theme"


class TestSubThemeDetailSerializerV2:
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
        serializer = SubThemeDetailSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "topic-list-v2",
            # view -> `topic-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["topics"] == spy_get_url.return_value


class TestTopicListSerializerV2:
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
        serializer = TopicListSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "topic-detail-v2",
            # view -> `topic-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == sub_theme_value
        assert serialized_data["link"] == spy_get_url.return_value
        assert serializer.fields["link"].lookup_field == "topic"


class TestTopicDetailSerializerV2:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_related_geography_types/",
    )
    def test_can_serialize_successfully(self, spy_get_url: mock.MagicMock):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `TopicDetailSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `geography_type-list` view
            as well as the `theme` and `sub_theme` values of the `APITimeSeriesDTO`
        """
        sub_theme_value = "respiratory"
        theme_value = "infectious_disease"
        topic_name = "COVID-19"
        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {
                    "theme": theme_value,
                    "sub_theme": sub_theme_value,
                    "topic": topic_name,
                }
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=topic_name,
            theme=theme_value,
            sub_theme=sub_theme_value,
            topic=topic_name,
        )

        # When
        serializer = TopicDetailSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "geography_type-list-v2",
            # view -> `geography_type-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["geography_types"] == spy_get_url.return_value


class TestGeographyTypeListSerializerV2:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_geography_types/",
    )
    def test_can_serialize_successfully(
        self,
        spy_get_url: mock.MagicMock,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `GeographyTypeListSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `geography_type-detail` view
            as well as the `theme`, `sub_theme` and `topic`
            values of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        sub_theme_value = "respiratory"
        topic_value = "COVID-19"

        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {
                    "theme": theme_value,
                    "sub_theme": sub_theme_value,
                    "topic": topic_value,
                }
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=topic_value,
            theme=theme_value,
            sub_theme=sub_theme_value,
            topic=topic_value,
        )

        # When
        serializer = GeographyTypeListSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "geography_type-detail-v2",
            # view -> `geography_type-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == topic_value
        assert serialized_data["link"] == spy_get_url.return_value
        assert serializer.fields["link"].lookup_field == "geography_type"


class TestGeographyTypeDetailSerializerV2:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_related_geographies/",
    )
    def test_can_serialize_successfully(self, spy_get_url: mock.MagicMock):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `GeographyTypeDetailSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `geography-list` view
            as well as the `theme`, `sub_theme`, `topic` and `geography_type`
            values of the `APITimeSeriesDTO`
        """
        sub_theme_value = "respiratory"
        theme_value = "infectious_disease"
        topic_name = "COVID-19"
        geography_type_name = "Nation"

        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {
                    "theme": theme_value,
                    "sub_theme": sub_theme_value,
                    "topic": topic_name,
                    "geography_type": geography_type_name,
                }
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=geography_type_name,
            theme=theme_value,
            sub_theme=sub_theme_value,
            topic=topic_name,
            geography_type=geography_type_name,
        )

        # When
        serializer = GeographyTypeDetailSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "geography-list-v2",
            # view -> `geography-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["geographies"] == spy_get_url.return_value


class TestGeographyListSerializerV2:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_geographies/",
    )
    def test_can_serialize_successfully(
        self,
        spy_get_url: mock.MagicMock,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `GeographyListSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `geography-detail` view
            as well as the `theme`, `sub_theme`, `topic` and `geography_type`
            values of the `APITimeSeriesDTO`
        """
        theme_value = "infectious_disease"
        sub_theme_value = "respiratory"
        topic_value = "COVID-19"
        geography_type_name = "Nation"

        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {
                    "theme": theme_value,
                    "sub_theme": sub_theme_value,
                    "topic": topic_value,
                    "geography_type": geography_type_name,
                }
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=geography_type_name,
            theme=theme_value,
            sub_theme=sub_theme_value,
            topic=topic_value,
            geography_type=geography_type_name,
        )

        # When
        serializer = GeographyListSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "geography-detail-v2",
            # view -> `geography-detail`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == geography_type_name
        assert serialized_data["link"] == spy_get_url.return_value
        assert serializer.fields["link"].lookup_field == "geography"


class TestGeographyDetailSerializerV2:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_related_metrics/",
    )
    def test_can_serialize_successfully(self, spy_get_url: mock.MagicMock):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `GeographyDetailSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `geography-list` view
            as well as the `theme`, `sub_theme`, `topic`, `geography_type`
            and `geography` values of the `APITimeSeriesDTO`
        """
        sub_theme_name = "respiratory"
        theme_name = "infectious_disease"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"

        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {
                    "theme": theme_name,
                    "sub_theme": sub_theme_name,
                    "topic": topic_name,
                    "geography_type": geography_type_name,
                    "geography": geography_name,
                }
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=geography_name,
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            geography_type=geography_type_name,
            geography=geography_name,
        )

        # When
        serializer = GeographyDetailSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "metric-list-v2",
            # view -> `metric-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["metrics"] == spy_get_url.return_value


class TestMetricListSerializerV2:
    @mock.patch.object(
        NestedHyperlinkedRelatedField,
        "get_url",
        return_value="fake_url_for_timeseries/",
    )
    def test_can_serialize_successfully(
        self,
        spy_get_url: mock.MagicMock,
    ):
        """
        Given a request which contains kwargs from the URL parameters
        And an `APITimeSeriesDTO`
        When the DTO is passed to an instance of the `MetricListSerializer`
        Then the serialized data uses the correct field from the `APITimeSeriesDTO`
        And creates a link in conjunction with the `timeseries-list` view
            as well as the `theme`, `sub_theme`, `topic`, `geography_type`,
            `geography` and `metric` values of the `APITimeSeriesDTO`
        """
        sub_theme_name = "respiratory"
        theme_name = "infectious_disease"
        topic_name = "COVID-19"
        geography_type_name = "Nation"
        geography_name = "England"

        mocked_request = mock.MagicMock(
            parser_context={
                "kwargs": {
                    "theme": theme_name,
                    "sub_theme": sub_theme_name,
                    "topic": topic_name,
                    "geography_type": geography_type_name,
                    "geography": geography_name,
                }
            }
        )
        timeseries_dto_slice = APITimeSeriesDTO(
            name=geography_name,
            theme=theme_name,
            sub_theme=sub_theme_name,
            topic=topic_name,
            geography_type=geography_type_name,
            geography=geography_name,
        )

        # When
        serializer = MetricListSerializerv2(
            timeseries_dto_slice,
            context={"request": mocked_request},
        )
        serialized_data = serializer.data

        # Then
        # The `get_url()` method is called for the `NestedHyperlinkedRelatedField`
        # with the correct positional arguments
        spy_get_url.assert_called_once_with(
            timeseries_dto_slice,
            # obj -> api_timeseries_dto instance
            "timeseries-list-v2",
            # view -> `timeseries-list`
            mocked_request,
            # request -> `mocked_request`
            None,
            # format -> None
        )
        assert serialized_data["name"] == geography_name
        assert serialized_data["link"] == spy_get_url.return_value
        assert serializer.fields["link"].lookup_field == "metric"
