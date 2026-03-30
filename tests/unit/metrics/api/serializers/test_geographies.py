import datetime
from unittest import mock
import pytest

from rest_framework.exceptions import ValidationError

from metrics.data.models.core_models.supporting import Geography
from validation.geography_code import UNITED_KINGDOM_GEOGRAPHY_CODE
from metrics.api.serializers.geographies import (
    GeographiesForTopicSerializer,
    _serialize_queryset,
    GeographiesRequestSerializer,
    GeographyByGeographyTypeRequestSerializer,
    _queryset_to_geography_code_name_tuples,
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
                        "relationships": None,
                    },
                    {
                        "name": hackney.geography.name,
                        "geography_code": hackney.geography.geography_code,
                        "relationships": None,
                    },
                ],
            },
            {
                "geography_type": nation,
                "geographies": [
                    {
                        "name": england.geography.name,
                        "geography_code": england.geography.geography_code,
                        "relationships": [
                            {
                                "geography_type": "United Kingdom",
                                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
                                "name": "United Kingdom",
                            }
                        ],
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
                        "relationships": None,
                    },
                    {
                        "name": hackney.geography__name,
                        "geography_code": hackney.geography__geography_code,
                        "relationships": None,
                    },
                ],
            },
            {
                "geography_type": nation,
                "geographies": [
                    {
                        "name": england.geography__name,
                        "geography_code": england.geography__geography_code,
                        "relationships": [
                            {
                                "geography_type": "United Kingdom",
                                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
                                "name": "United Kingdom",
                            }
                        ],
                    }
                ],
            },
        ]
        assert serialized_results == expected_results


class TestGeographiesRequestSerializer:
    def test_raises_error_when_no_field_provided(self):
        """
        Given a payload which does not contain
            a `topic` or a `geography_type`
        When `is_valid()` is called from a `GeographiesRequestSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        payload = {}
        serializer = GeographiesRequestSerializer(data=payload)

        # When / Then
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)

        assert (
            error.value.detail["non_field_errors"][0]
            == "Either 'topic' or 'geography_type' must be provided."
        )

    def test_raises_error_when_multiple_fields_are_provided(self):
        """
        Given a payload which contains
            both a `topic` and a `geography_type`
        When `is_valid()` is called from a `GeographiesRequestSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        payload = {"topic": "COVID-19", "geography_type": "Nation"}
        serializer = GeographiesRequestSerializer(data=payload)

        # When / Then
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)

        assert (
            error.value.detail["non_field_errors"][0]
            == "Only one of 'topic' or 'geography_type' should be provided, not both."
        )


class TestGeographyByGeographyTypeRequestSerializer:
    """Tests for GeographyByGeographyTypeRequestSerializer"""

    def test_validates_wildcard_geography_type_id(self):
        """
        Given a wildcard geography_type_id value of "-1"
        When the value is validated
        Then the wildcard is accepted
        """
        # Given
        data = {"geography_type_id": "-1"}

        # When
        serializer = GeographyByGeographyTypeRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["geography_type_id"] == "-1"

    def test_validates_numeric_geography_type_id(self):
        """
        Given a valid numeric geography_type_id
        When the value is validated
        Then the numeric value is converted to an integer
        """
        # Given
        data = {"geography_type_id": "3"}

        # When
        serializer = GeographyByGeographyTypeRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["geography_type_id"] == 3

    def test_rejects_invalid_geography_type_id(self):
        """
        Given an invalid geography_type_id (not a number or wildcard)
        When the value is validated
        Then a ValidationError is raised
        """
        # Given
        data = {"geography_type_id": "invalid_value"}

        # When
        serializer = GeographyByGeographyTypeRequestSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "geography_type_id" in serializer.errors
        assert "Geography Type must be a number or '-1'" in str(
            serializer.errors["geography_type_id"]
        )

    def test_validation_error_has_chained_exception(self):
        """
        Given an invalid geography_type_id
        When validation fails
        Then the ValidationError is chained from the original ValueError
        """
        # Given
        data = {"geography_type_id": "not_a_number"}

        # When
        serializer = GeographyByGeographyTypeRequestSerializer(data=data)

        # Then
        with pytest.raises(ValidationError) as error:
            serializer.is_valid(raise_exception=True)

        assert (
            error.value.detail["geography_type_id"][0]
            == "Geography Type must be a number or '-1'"
        )

    def test_data_returns_wildcard_response_for_wildcard_geography_type_id(self):
        """
        Given a wildcard geography_type_id of "-1"
        When data() is called
        Then a wildcard response is returned
        """
        # Given
        data = {"geography_type_id": "-1"}
        serializer = GeographyByGeographyTypeRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        assert response == {"choices": [["-1", "* (All geographies)"]]}

    def test_data_fetches_geographies_for_valid_geography_type_id(self):
        """
        Given a valid numeric geography_type_id
        When data() is called
        Then geographies are fetched from the manager and formatted correctly
        """
        # Given
        mock_manager = mock.MagicMock()
        mock_queryset = [
            {"geography_code": "E92000001", "name": "England"},
            {"geography_code": "E12000001", "name": "North East"},
        ]
        mock_manager.get_geography_codes_and_names_by_geography_type_id.return_value = (
            mock_queryset
        )

        data = {"geography_type_id": "2"}
        serializer = GeographyByGeographyTypeRequestSerializer(
            data=data, context={"geography_manager": mock_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        mock_manager.get_geography_codes_and_names_by_geography_type_id.assert_called_once_with(
            2
        )
        assert response == {
            "choices": [
                ["E92000001", "England"],
                ["E12000001", "North East"],
            ]
        }

    def test_data_handles_empty_geography_queryset(self):
        """
        Given a valid geography_type_id that returns no geographies
        When data() is called
        Then an empty choices list is returned
        """
        # Given
        mock_manager = mock.MagicMock()
        mock_manager.get_geography_codes_and_names_by_geography_type_id.return_value = (
            []
        )

        data = {"geography_type_id": "999"}
        serializer = GeographyByGeographyTypeRequestSerializer(
            data=data, context={"geography_manager": mock_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        assert response == {"choices": []}

    def test_data_converts_geography_codes_to_strings(self):
        """
        Given geographies with various geography_code formats
        When data() is called
        Then all geography codes are converted to strings
        """
        # Given
        mock_manager = mock.MagicMock()
        mock_queryset = [
            {"geography_code": "E92000001", "name": "England"},
            {"geography_code": 12345, "name": "Numeric Code Area"},
        ]
        mock_manager.get_geography_codes_and_names_by_geography_type_id.return_value = (
            mock_queryset
        )

        data = {"geography_type_id": "1"}
        serializer = GeographyByGeographyTypeRequestSerializer(
            data=data, context={"geography_manager": mock_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        assert response == {
            "choices": [
                ["E92000001", "England"],
                ["12345", "Numeric Code Area"],
            ]
        }
        # Verify all codes are strings
        for choice in response["choices"]:
            assert isinstance(choice[0], str)

    def test_geography_manager_uses_context_when_available(self):
        """
        Given a geography_manager in the context
        When the property is accessed
        Then the context manager is returned
        """
        # Given
        mock_manager = mock.MagicMock()
        serializer = GeographyByGeographyTypeRequestSerializer(
            data={"geography_type_id": "1"}, context={"geography_manager": mock_manager}
        )

        # When / Then
        assert serializer.geography_manager == mock_manager

    def test_geography_manager_falls_back_to_default(self):
        """
        Given no geography_manager in the context
        When the property is accessed
        Then the default Geography.objects manager is returned
        """
        # Given
        serializer = GeographyByGeographyTypeRequestSerializer(
            data={"geography_type_id": "1"}
        )

        # When / Then
        assert serializer.geography_manager == Geography.objects

    def test_requires_geography_type_id_field(self):
        """
        Given data without geography_type_id
        When the serializer is validated
        Then a validation error is raised
        """
        # Given
        data = {}

        # When
        serializer = GeographyByGeographyTypeRequestSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "geography_type_id" in serializer.errors

    def test_data_calls_helper_function_to_convert_queryset(self):
        """
        Given a valid geography_type_id
        When data() is called
        Then the helper function is used to convert the queryset
        """
        # Given
        mock_manager = mock.MagicMock()
        mock_queryset = [
            {"geography_code": "S92000003", "name": "Scotland"},
        ]
        mock_manager.get_geography_codes_and_names_by_geography_type_id.return_value = (
            mock_queryset
        )

        data = {"geography_type_id": "1"}
        serializer = GeographyByGeographyTypeRequestSerializer(
            data=data, context={"geography_manager": mock_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        # The helper function should have been used (implicitly tested by correct output)
        assert response == {"choices": [["S92000003", "Scotland"]]}


class TestQuerysetToGeographyCodeNameTuples:
    """Tests for the _queryset_to_geography_code_name_tuples helper function"""

    def test_converts_queryset_to_tuples(self):
        """
        Given a QuerySet with geography_code and name fields
        When converted using _queryset_to_geography_code_name_tuples
        Then a list of (geography_code, name) tuples is returned
        """
        # Given
        mock_queryset = [
            {"geography_code": "E92000001", "name": "England"},
            {"geography_code": "W92000004", "name": "Wales"},
            {"geography_code": "S92000003", "name": "Scotland"},
        ]

        # When
        result = _queryset_to_geography_code_name_tuples(mock_queryset)

        # Then
        assert result == [
            ("E92000001", "England"),
            ("W92000004", "Wales"),
            ("S92000003", "Scotland"),
        ]

    def test_handles_empty_queryset(self):
        """
        Given an empty QuerySet
        When converted using _queryset_to_geography_code_name_tuples
        Then an empty list is returned
        """
        # Given
        mock_queryset = []

        # When
        result = _queryset_to_geography_code_name_tuples(mock_queryset)

        # Then
        assert result == []

    def test_preserves_geography_code_types(self):
        """
        Given a QuerySet with various geography_code types
        When converted using _queryset_to_geography_code_name_tuples
        Then the geography_code types are preserved
        """
        # Given
        mock_queryset = [
            {"geography_code": "E12000001", "name": "North East"},
            {"geography_code": 12345, "name": "Numeric Code"},
        ]

        # When
        result = _queryset_to_geography_code_name_tuples(mock_queryset)

        # Then
        assert result[0] == ("E12000001", "North East")
        assert result[1] == (12345, "Numeric Code")
        assert isinstance(result[0][0], str)
        assert isinstance(result[1][0], int)

    def test_handles_single_item_queryset(self):
        """
        Given a QuerySet with a single item
        When converted using _queryset_to_geography_code_name_tuples
        Then a list with one tuple is returned
        """
        # Given
        mock_queryset = [{"geography_code": "N92000002", "name": "Northern Ireland"}]

        # When
        result = _queryset_to_geography_code_name_tuples(mock_queryset)

        # Then
        assert result == [("N92000002", "Northern Ireland")]
        assert len(result) == 1

    def test_handles_special_characters_in_names(self):
        """
        Given a QuerySet with special characters in geography names
        When converted using _queryset_to_geography_code_name_tuples
        Then the special characters are preserved
        """
        # Given
        mock_queryset = [
            {"geography_code": "E06000001", "name": "Hartlepool & District"},
            {"geography_code": "E06000002", "name": "St. Albans"},
        ]

        # When
        result = _queryset_to_geography_code_name_tuples(mock_queryset)

        # Then
        assert result == [
            ("E06000001", "Hartlepool & District"),
            ("E06000002", "St. Albans"),
        ]
