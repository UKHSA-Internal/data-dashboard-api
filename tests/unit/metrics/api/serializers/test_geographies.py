import datetime
from unittest import mock

from metrics.api.serializers.geographies import (
    GeographiesSerializer,
    GeographySerializer,
    GeographyTypesSerializer,
    _serialize_queryset,
)
from tests.fakes.factories.metrics.core_time_series_factory import (
    FakeCoreTimeSeriesFactory,
)
from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.geography_type_factory import (
    FakeGeographyTypeFactory,
)
from tests.fakes.managers.time_series_manager import FakeCoreTimeSeriesManager


class TestGeographySerializer:
    def test_returns_expected_serialized_data(self):
        """
        Given a `Geography` object
        When the object is serialized with the `GeographySerializer`
        Then the correct data is returned
        """
        # Given
        fake_geography = FakeGeographyFactory.build_example()

        # When
        serializer = GeographySerializer(instance=fake_geography)

        # Then
        serialized_data = serializer.data
        assert serialized_data["name"] == fake_geography.name
        assert serialized_data["id"] == fake_geography.id


class TestGeographyTypesSerializer:
    def test_returns_expected_serialized_data(self):
        """
        Given a `GeographyType` object
        When the object is serialized with the `GeographyTypesSerializer`
        Then the correct data is returned
        """
        # Given
        fake_geography_type = FakeGeographyTypeFactory.build_example()

        # When
        serializer = GeographyTypesSerializer(instance=fake_geography_type)

        # Then
        serialized_data = serializer.data
        assert serialized_data["name"] == fake_geography_type.name
        assert serialized_data["id"] == fake_geography_type.id


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
            metric_name="COVID-19_cases_countRollingMean",
            topic_name="COVID-19",
            date=date_stamp,
            geography_type_name=ltla,
            geography_name="Bexley",
        )
        hackney = FakeCoreTimeSeriesFactory.build_time_series(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name="COVID-19",
            date=date_stamp,
            geography_type_name=ltla,
            geography_name="Hackney",
        )
        england = FakeCoreTimeSeriesFactory.build_time_series(
            metric_name="COVID-19_cases_countRollingMean",
            topic_name="COVID-19",
            date=date_stamp,
            geography_type_name=nation,
            geography_name="England",
        )
        irrelavant_leeds_geography = FakeCoreTimeSeriesFactory.build_time_series(
            metric_name="influenza_healthcare_ICUHDUadmissionRateByWeek",
            topic_name="Influenza",
            date=date_stamp,
            geography_type_name=ltla,
            geography_name="Leeds",
        )
        fake_core_time_series_manager = FakeCoreTimeSeriesManager(
            time_series=[bexley, hackney, england, irrelavant_leeds_geography]
        )
        serializer = GeographiesSerializer(
            context={"core_time_series_manager": fake_core_time_series_manager},
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
                    {"name": bexley.geography.name},
                    {"name": hackney.geography.name},
                ],
            },
            {
                "geography_type": nation,
                "geographies": [{"name": england.geography.name}],
            },
        ]
        assert results == expected_results


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
            geography__name="Hackney", geography__geography_type__name=ltla
        )
        bexley = mock.Mock(
            geography__name="Bexley", geography__geography_type__name=ltla
        )
        england = mock.Mock(
            geography__name="England", geography__geography_type__name=nation
        )
        fake_queryset = [bexley, hackney, england]

        # When
        serialized_results = _serialize_queryset(queryset=fake_queryset)

        # Then
        expected_results = [
            {
                "geography_type": ltla,
                "geographies": [
                    {"name": bexley.geography__name},
                    {"name": hackney.geography__name},
                ],
            },
            {
                "geography_type": nation,
                "geographies": [{"name": england.geography__name}],
            },
        ]
        assert serialized_results == expected_results
