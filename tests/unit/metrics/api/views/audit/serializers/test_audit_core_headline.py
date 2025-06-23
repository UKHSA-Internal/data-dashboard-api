import datetime
from decimal import Decimal
from unittest import mock

import pytest

from metrics.data.models.core_models import CoreHeadline
from metrics.api.views.audit.serializers import AuditCoreHeadlineSerializer

from tests.fakes.factories.metrics.headline_factory import FakeCoreHeadlineFactory


class TestCoreHeadlineSerializer:

    @staticmethod
    def _setup_fake_headline_record():
        return FakeCoreHeadlineFactory.build_record(
            topic="COVID-19",
            metric="COVID-19_headline_tests_7DayChange",
            period_start=datetime.datetime(day=1, month=1, year=2024),
            period_end=datetime.datetime(day=2, month=2, year=2024),
            refresh_date=datetime.datetime(day=1, month=1, year=2024),
            embargo=datetime.datetime(day=1, month=1, year=2024),
            metric_value=1,
        )

    def test_period_start_is_serialized_correctly(self):
        """
        Given a fake `CoreHeadline` model object
        When the fake is passed to the `CoreHeadlineSerializer`
        Then the `period_start` field is returned in the expected format.
        """
        # Given
        fake_core_headline = self._setup_fake_headline_record()

        # When
        serializer = AuditCoreHeadlineSerializer(instance=fake_core_headline)

        # Then
        serialized_date: str = serializer.data["period_start"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(fake_core_headline.period_start)

        assert serialized_date == expected_date_value

    def test_period_end_is_serialized_correctly(self):
        """
        Given a fake `CoreHeadline` model object
        When the fake is passed to the `CoreHeadlineSerializer`
        Then the `period_end` field is returned in the expected format.
        """
        # Given
        fake_core_headline = self._setup_fake_headline_record()

        # When
        serializer = AuditCoreHeadlineSerializer(instance=fake_core_headline)

        # Then
        serialized_date: str = serializer.data["period_end"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(fake_core_headline.period_end)

        assert serialized_date == expected_date_value

    def test_refresh_date_is_serialized_correctly(self):
        """
        Given a fake `CoreHeadline` model object
        When the fake is passed to the `CoreHeadlineSerializer`
        Then the `refresh_date` field is returned in the expected format.
        """
        # Given
        fake_core_headline = self._setup_fake_headline_record()

        # When
        serializer = AuditCoreHeadlineSerializer(instance=fake_core_headline)

        # Then
        serialized_date: str = serializer.data["refresh_date"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(fake_core_headline.refresh_date)

        assert serialized_date == expected_date_value

    def test_embargo_is_serialized_correctly(self):
        """
        Given a fake `CoreHeadline` model object
        When the fake is passed to the `CoreHeadlineSerializer`
        Then the `embargo` field is returned in the expected format.
        """
        # Given
        fake_core_headline = self._setup_fake_headline_record()

        # When
        serializer = AuditCoreHeadlineSerializer(instance=fake_core_headline)

        # Then
        serialized_date: str = serializer.data["embargo"]
        # The serialized field should return the string representation of the datetime.datetime object
        expected_date_value = str(fake_core_headline.embargo)

        assert serialized_date == expected_date_value

    def test_null_embargo_is_serialized_correctly(self):
        """
        Given a fake `CoreHeadline` model object and a null embargo timestamp
        When the fake is passed to the `CoreHeadlineSerializer`
        Then the `embargo` field is returned in the expected format.
        """
        # Given
        fake_core_headline = self._setup_fake_headline_record()
        fake_core_headline.embargo = None

        # When
        serializer = AuditCoreHeadlineSerializer(instance=fake_core_headline)

        # Then
        serialized_date: str = serializer.data["embargo"]
        assert serialized_date == ""

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
    def test_expected_fields_are_returned(self, expected_field: str):
        """
        Given a mocked `CoreTimeseries` model object
        When the object is passed through the `CoreTimeSeriesSerializer`
        Then the expected fields are returned.
        """
        # Given
        fake_core_headline = self._setup_fake_headline_record()

        # When
        serializer = AuditCoreHeadlineSerializer(instance=fake_core_headline)

        # Then
        assert expected_field in serializer.fields
