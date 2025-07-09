import datetime
from unittest import mock

from metrics.api.serializers.geographies import (
    GeographiesForTopicSerializer,
    _serialize_queryset,
)
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager
from tests.fakes.managers.topic_manager import FakeTopicManager
from tests.fakes.models.metrics.topic import FakeTopic


class TestGeographiesSerializer:
    def test_get_results(self):
        """
        Given a `topic` and a number of `CoreTimeSeries` records
        When `get_results()` is called
            from an instance of the `GeographiesSerializer`
        Then the returned results contain the correct geographies
        """
        # Given
        ltla = "Lower Tier Local Authority"
        nation = "Nation"
        date_stamp = datetime.datetime(year=2024, month=1, day=1)

        bexley = FakeCoreTimeSeriesFactory.build_time_series(
            metric="COVID-19_cases_countRollingMean",
            topic="COVID-19",
            date=date_stamp,
            geography_type_name=ltla,
            geography_name="Bexley",
            geography_code="E09000004",
        )
        hackney = FakeCoreTimeSeriesFactory.build_time_series(
            metric="COVID-19_cases_countRollingMean",
            topic="COVID-19",
            date=date_stamp,
            geography_type_name=ltla,
            geography_name="Hackney",
            geography_code="E09000012",
        )
        england = FakeCoreTimeSeriesFactory.build_time_series(
            metric="COVID-19_cases_countRollingMean",
            topic="COVID-19",
            date=date_stamp,
            geography_type_name=nation,
            geography_name="England",
            geography_code="E92000001",
        )
        irrelevant_leeds_geography = FakeCoreTimeSeriesFactory.build_time_series(
            metric="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic="Influenza",
            date=date_stamp,
            geography_type_name=ltla,
            geography_name="Leeds",
            geography_code="E08000035",
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=[bexley, hackney, england, irrelevant_leeds_geography]
        )
        fake_topic_manager = FakeTopicManager(
            topics=[
                FakeTopic(name="COVID-19"),
                FakeTopic(name="Influenza"),
            ]
        )
        serializer = GeographiesForTopicSerializer(
            context={
                "core_time_series_manager": fake_core_time_series_manager,
                "topic_manager": fake_topic_manager,
            },
            data={"topic": "COVID-19"},
        )

        # When
        serializer.is_valid(raise_exception=True)
        results = serializer.data()

        # Then
        expected_results = [
            {
                "geography_type": ltla,
                "geographies": [
                    {
                        "name": bexley.geography.name,
                        "geography_code": bexley.geography.geography_code,
                    },
                    {
                        "name": hackney.geography.name,
                        "geography_code": hackney.geography.geography_code,
                    },
                ],
            },
            {
                "geography_type": nation,
                "geographies": [
                    {
                        "name": england.geography.name,
                        "geography_code": england.geography.geography_code,
                    }
                ],
            },
        ]
        assert results == expected_results

    def test_topic_validation_fails(self):
        """
        Given an invalid topic name
        When the `GeographiesSerializer` is initialised
        Then `serializer.is_valid()` will return False
        """
        # Given
        fake_topic_manager = FakeTopicManager(
            topics=[
                FakeTopic(name="COVID-19"),
                FakeTopic(name="Influenza"),
            ]
        )

        # When
        serializer = GeographiesForTopicSerializer(
            context={
                "topic_manager": fake_topic_manager,
            },
            data={"topic": "invalid-topic"},
        )

        # Then
        assert serializer.is_valid() is False

    def test_topic_validation_succeeds(self):
        """
        Given a valid topic name
        When the `GeographiesSerializer` is initialised
        Then `serializer.is_valid()` will return True
        """
        # Given
        fake_topic_manager = FakeTopicManager(
            topics=[
                FakeTopic(name="COVID-19"),
                FakeTopic(name="Influenza"),
            ]
        )

        # When
        serializer = GeographiesForTopicSerializer(
            context={
                "topic_manager": fake_topic_manager,
            },
            data={"topic": "COVID-19"},
        )

        # Then
        assert serializer.is_valid()


class TestSerializeQuerySet:
    def test_returns_correct_result(self):
        """
        Given a fake `QuerySet` containing geography results
        When `_serialize_queryset()` is called
        Then the correct results are returned
        """
        # Given
        ltla = "Lower Tier Local Authority"
        nation = "Nation"
        hackney = mock.Mock(
            geography__name="Hackney",
            geography__geography_type__name=ltla,
            geography__geography_code="E09000012",
        )
        bexley = mock.Mock(
            geography__name="Bexley",
            geography__geography_type__name=ltla,
            geography__geography_code="E09000004",
        )
        england = mock.Mock(
            geography__name="England",
            geography__geography_type__name=nation,
            geography__geography_code="E92000001",
        )
        fake_queryset = [bexley, hackney, england]

        # When
        serialized_results = _serialize_queryset(queryset=fake_queryset)

        # Then
        expected_results = [
            {
                "geography_type": ltla,
                "geographies": [
                    {
                        "name": bexley.geography__name,
                        "geography_code": bexley.geography__geography_code,
                    },
                    {
                        "name": hackney.geography__name,
                        "geography_code": hackney.geography__geography_code,
                    },
                ],
            },
            {
                "geography_type": nation,
                "geographies": [
                    {
                        "name": england.geography__name,
                        "geography_code": england.geography__geography_code,
                    }
                ],
            },
        ]
        assert serialized_results == expected_results
