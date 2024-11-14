import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.data.models.core_models import CoreHeadline
from metrics.api.views.audit.serializers import AuditCoreHeadlineSerializer


@pytest.fixture
def mock_core_headline() -> mock.MagicMock:
    return mock.MagicMock(
        spec=CoreHeadline,
        metric__topic__sub_theme__theme__name="infectious_disease",
        metric__topic__sub_theme__name="respiratory",
        metric_topic="COVID-19",
        metric__name="COVID-19_cases_rateRollingMean",
        geography__name="England",
        geography__geography_type__name="Nation",
        stratum__name="default",
        age__name="all",
        sex="all",
        year=2024,
        date=datetime.date(day=1, month=1, year=2024),
        metric_value=Decimal("1.000"),
        refresh_date=datetime.datetime(day=1, month=1, year=2024),
        embargo=datetime.datetime(day=3, month=3, year=2024),
        period_start=datetime.datetime(day=1, month=1, year=2024),
        period_end=datetime.datetime(day=2, month=2, year=2024),
    )


class TestCoreHeadlineSerializer:

    def test_metric_value_is_serialized_correctly(
        self, mock_core_headline: mock.MagicMock
    ):
        """
        Given a mocked `CoreHeadline` model object
        When the mock is passed to the `CoreHeadlineSerializer`
        Then the `metric_value` field is returned in the expected format.
        """
        # Given
        example_metric_value = Decimal("1.9000")
        mocked_core_headline = mock_core_headline
        mocked_core_headline.metric_value = example_metric_value

        # When
        serializer = AuditCoreHeadlineSerializer(instance=mocked_core_headline)

        # Then
        serialized_metric_value: str = serializer.data["metric_value"]
        expected_metric_value = str(mocked_core_headline.metric_value)

        assert serialized_metric_value == expected_metric_value

    def test_period_start_is_serialized_correctly(
        self, mock_core_headline: mock.MagicMock
    ):
        """
        Given a mocked `CoreHeadline` model object
        When the mock is passed to the `CoreHeadlineSerializer`
        Then the `period_start` field is returned in the expected format.
        """
        # Given
        mocked_core_headline = mock_core_headline

        # When
        serializer = AuditCoreHeadlineSerializer(instance=mocked_core_headline)

        # Then
        serialized_date: str = serializer.data["period_start"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(mocked_core_headline.period_start)

        assert serialized_date == expected_date_value

    def test_period_end_is_serialized_correctly(
        self, mock_core_headline: mock.MagicMock
    ):
        """
        Given a mocked `CoreHeadline` model object
        When the mock is passed to the `CoreHeadlineSerializer`
        Then the `period_end` field is returned in the expected format.
        """
        # Given
        mocked_core_headline = mock_core_headline

        # When
        serializer = AuditCoreHeadlineSerializer(instance=mocked_core_headline)

        # Then
        serialized_date: str = serializer.data["period_end"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(mocked_core_headline.period_end)

        assert serialized_date == expected_date_value

    def test_refresh_date_is_serialized_correctly(
        self, mock_core_headline: mock.MagicMock
    ):
        """
        Given a mocked `CoreHeadline` model object
        When the mock is passed to the `CoreHeadlineSerializer`
        Then the `refresh_date` field is returned in the expected format.
        """
        # Given
        mocked_core_headline = mock_core_headline

        # When
        serializer = AuditCoreHeadlineSerializer(instance=mocked_core_headline)

        # Then
        serialized_date: str = serializer.data["refresh_date"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(mocked_core_headline.refresh_date)

        assert serialized_date == expected_date_value

    def test_embargo_is_serialized_correctly(self, mock_core_headline: mock.MagicMock):
        """
        Given a mocked `CoreHeadline` model object
        When the mock is passed to the `CoreHeadlineSerializer`
        Then the `embargo` field is returned in the expected format.
        """
        # Given
        mocked_core_headline = mock_core_headline

        # When
        serializer = AuditCoreHeadlineSerializer(instance=mocked_core_headline)

        # Then
        serialized_date: str = serializer.data["embargo"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(mocked_core_headline.embargo)

        assert serialized_date == expected_date_value

    @pytest.mark.parametrize(
        "expected_field",
        [
            "theme",
            "sub_theme",
            "topic",
            "geography_type",
            "geography",
            "geography_code",
            "metric",
            "age",
            "stratum",
            "period_start",
            "period_end",
            "refresh_date",
            "embargo",
        ],
    )
    def test_expected_fields_are_returned(
        self, expected_field: str, mock_core_headline: mock.MagicMock
    ):
        """
        Given a mocked `CoreTimeseries` model object
        When the object is passed through the `CoreTimeSeriesSerializer`
        Then the expected fields are returned.
        """
        # Given
        mocked_core_headline = mock_core_headline

        # When
        serializer = AuditCoreHeadlineSerializer(instance=mocked_core_headline)

        # Then
        assert expected_field in serializer.fields
