from unittest import mock

import pytest
from rest_framework import serializers as drf_serializers

from metrics.api.serializers.permission_sets import (
    MetricRequestSerializer,
    PermissionSetResponseSerializer,
    SubThemeRequestSerializer,
    TopicRequestSerializer,
    _queryset_to_id_name_tuples,
)
from metrics.data.models.core_models.supporting import Metric, SubTheme, Topic


class TestSubThemeRequestSerializer:
    """Tests for SubThemeRequestSerializer"""

    def test_validates_wildcard_theme_id(self):
        """
        Given a wildcard theme_id value of "-1"
        When the value is validated
        Then the wildcard is accepted
        """
        # Given
        data = {"theme_id": "-1"}

        # When
        serializer = SubThemeRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["theme_id"] == "-1"

    def test_validates_numeric_theme_id(self):
        """
        Given a valid numeric theme_id
        When the value is validated
        Then the numeric value is accepted
        """
        # Given
        data = {"theme_id": "123"}

        # When
        serializer = SubThemeRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["theme_id"] == "123"

    def test_rejects_invalid_theme_id(self):
        """
        Given an invalid theme_id (not a number or wildcard)
        When the value is validated
        Then a ValidationError is raised
        """
        # Given
        data = {"theme_id": "invalid"}

        # When
        serializer = SubThemeRequestSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "theme_id" in serializer.errors
        assert "theme_id must be a number or '-1'" in str(
            serializer.errors["theme_id"])

    def test_data_returns_wildcard_response_for_wildcard_theme_id(self):
        """
        Given a wildcard theme_id of "-1"
        When data() is called
        Then a wildcard response is returned
        """
        # Given
        data = {"theme_id": "-1"}
        serializer = SubThemeRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        assert response == {"choices": [["-1", "* (All sub-themes)"]]}

    def test_data_fetches_sub_themes_for_valid_theme_id(self):
        """
        Given a valid numeric theme_id
        When data() is called
        Then sub-themes are fetched from the manager and formatted correctly
        """
        # Given
        metrics_manager = mock.MagicMock()
        mock_queryset = [
            {"id": 1, "name": "respiratory"},
            {"id": 2, "name": "gastrointestinal"},
        ]
        metrics_manager.get_filtered_unique_names_related_to_theme.return_value = (
            mock_queryset
        )

        data = {"theme_id": "5"}
        serializer = SubThemeRequestSerializer(
            data=data, context={"sub_theme_manager": metrics_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        metrics_manager.get_filtered_unique_names_related_to_theme.assert_called_once_with(
            5
        )
        assert response == {
            "choices": [["1", "respiratory"], ["2", "gastrointestinal"]]
        }

    def test_sub_theme_manager_uses_context_when_available(self):
        """
        Given a sub_theme_manager in the context
        When the property is accessed
        Then the context manager is returned
        """
        # Given
        metrics_manager = mock.MagicMock()
        serializer = SubThemeRequestSerializer(
            data={"theme_id": "1"}, context={"sub_theme_manager": metrics_manager}
        )

        # When / Then
        assert serializer.sub_theme_manager == metrics_manager

    def test_sub_theme_manager_falls_back_to_default(self):
        """
        Given no sub_theme_manager in the context
        When the property is accessed
        Then the default SubTheme.objects manager is returned
        """
        # Given
        serializer = SubThemeRequestSerializer(data={"theme_id": "1"})

        # When / Then
        assert serializer.sub_theme_manager == SubTheme.objects


class TestTopicRequestSerializer:
    """Tests for TopicRequestSerializer"""

    def test_validates_wildcard_sub_theme_id(self):
        """
        Given a wildcard sub_theme_id value of "-1"
        When the value is validated
        Then the wildcard is accepted
        """
        # Given
        data = {"sub_theme_id": "-1"}

        # When
        serializer = TopicRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["sub_theme_id"] == "-1"

    def test_validates_numeric_sub_theme_id(self):
        """
        Given a valid numeric sub_theme_id
        When the value is validated
        Then the numeric value is accepted
        """
        # Given
        data = {"sub_theme_id": "456"}

        # When
        serializer = TopicRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["sub_theme_id"] == "456"

    def test_rejects_invalid_sub_theme_id(self):
        """
        Given an invalid sub_theme_id (not a number or wildcard)
        When the value is validated
        Then a ValidationError is raised
        """
        # Given
        data = {"sub_theme_id": "not_a_number"}

        # When
        serializer = TopicRequestSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "sub_theme_id" in serializer.errors
        assert "sub_theme_id must be a number or '-1'" in str(
            serializer.errors["sub_theme_id"]
        )

    def test_data_returns_wildcard_response_for_wildcard_sub_theme_id(self):
        """
        Given a wildcard sub_theme_id of "-1"
        When data() is called
        Then a wildcard response is returned
        """
        # Given
        data = {"sub_theme_id": "-1"}
        serializer = TopicRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        assert response == {"choices": [["-1", "* (All topics)"]]}

    def test_data_fetches_topics_for_valid_sub_theme_id(self):
        """
        Given a valid numeric sub_theme_id
        When data() is called
        Then topics are fetched from the manager and formatted correctly
        """
        # Given
        metrics_manager = mock.MagicMock()
        mock_queryset = [
            {"id": 10, "name": "COVID-19"},
            {"id": 11, "name": "Influenza"},
        ]
        metrics_manager.get_filtered_unique_names_related_to_sub_theme.return_value = (
            mock_queryset
        )

        data = {"sub_theme_id": "3"}
        serializer = TopicRequestSerializer(
            data=data, context={"topic_manager": metrics_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        metrics_manager.get_filtered_unique_names_related_to_sub_theme.assert_called_once_with(
            3
        )
        assert response == {"choices": [
            ["10", "COVID-19"], ["11", "Influenza"]]}

    def test_topic_manager_uses_context_when_available(self):
        """
        Given a topic_manager in the context
        When the property is accessed
        Then the context manager is returned
        """
        # Given
        metrics_manager = mock.MagicMock()
        serializer = TopicRequestSerializer(
            data={"sub_theme_id": "1"}, context={"topic_manager": metrics_manager}
        )

        # When / Then
        assert serializer.topic_manager == metrics_manager

    def test_topic_manager_falls_back_to_default(self):
        """
        Given no topic_manager in the context
        When the property is accessed
        Then the default Topic.objects manager is returned
        """
        # Given
        serializer = TopicRequestSerializer(data={"sub_theme_id": "1"})

        # When / Then
        assert serializer.topic_manager == Topic.objects


class TestMetricRequestSerializer:
    """Tests for MetricRequestSerializer"""

    def test_validates_wildcard_topic_id(self):
        """
        Given a wildcard topic_id value of "-1"
        When the value is validated
        Then the wildcard is accepted
        """
        # Given
        data = {"topic_id": "-1"}

        # When
        serializer = MetricRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["topic_id"] == "-1"

    def test_validates_numeric_topic_id(self):
        """
        Given a valid numeric topic_id
        When the value is validated
        Then the numeric value is accepted
        """
        # Given
        data = {"topic_id": "789"}

        # When
        serializer = MetricRequestSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data["topic_id"] == "789"

    def test_rejects_invalid_topic_id(self):
        """
        Given an invalid topic_id (not a number or wildcard)
        When the value is validated
        Then a ValidationError is raised
        """
        # Given
        data = {"topic_id": "abc123"}

        # When
        serializer = MetricRequestSerializer(data=data)

        # Then
        assert not serializer.is_valid()
        assert "topic_id" in serializer.errors
        assert "topic_id must be a number or '-1'" in str(
            serializer.errors["topic_id"])

    def test_data_returns_wildcard_response_for_wildcard_topic_id(self):
        """
        Given a wildcard topic_id of "-1"
        When data() is called
        Then a wildcard response is returned
        """
        # Given
        data = {"topic_id": "-1"}
        serializer = MetricRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        assert response == {"choices": [["-1", "* (All metrics)"]]}

    def test_data_fetches_metrics_for_valid_topic_id(self):
        """
        Given a valid numeric topic_id
        When data() is called
        Then metrics are fetched from the manager and formatted correctly
        """
        # Given
        metrics_manager = mock.MagicMock()
        mock_queryset = [
            {"id": 100, "name": "COVID-19_cases_rate"},
            {"id": 101, "name": "COVID-19_deaths_rate"},
        ]
        metrics_manager.get_filtered_unique_names_related_to_parent_topic_id.return_value = (
            mock_queryset
        )

        data = {"topic_id": "15"}
        serializer = MetricRequestSerializer(
            data=data, context={"metric_manager": metrics_manager}
        )
        serializer.is_valid(raise_exception=True)

        # When
        response = serializer.data()

        # Then
        metrics_manager.get_filtered_unique_names_related_to_parent_topic_id.assert_called_once_with(
            15
        )
        assert response == {
            "choices": [
                ["100", "COVID-19_cases_rate"],
                ["101", "COVID-19_deaths_rate"],
            ]
        }

    def test_metric_manager_uses_context_when_available(self):
        """
        Given a metric_manager in the context
        When the property is accessed
        Then the context manager is returned
        """
        # Given
        metrics_manager = mock.MagicMock()
        serializer = MetricRequestSerializer(
            data={"topic_id": "1"}, context={"metric_manager": metrics_manager}
        )

        # When / Then
        assert serializer.metric_manager == metrics_manager

    def test_metric_manager_falls_back_to_default(self):
        """
        Given no metric_manager in the context
        When the property is accessed
        Then the default Metric.objects manager is returned
        """
        # Given
        serializer = MetricRequestSerializer(data={"topic_id": "1"})

        # When / Then
        assert serializer.metric_manager == Metric.objects


class TestPermissionSetResponseSerializer:
    """Tests for PermissionSetResponseSerializer"""

    def test_serializes_valid_choices_structure(self):
        """
        Given a valid choices structure
        When the data is serialized
        Then the serializer validates successfully
        """
        # Given
        data = {"choices": [["1", "Option 1"], ["2", "Option 2"]]}

        # When
        serializer = PermissionSetResponseSerializer(data=data)

        # Then
        assert serializer.is_valid()
        assert serializer.validated_data == data

    def test_rejects_invalid_choice_structure(self):
        """
        Given an invalid choices structure (not pairs)
        When the data is serialized
        Then validation fails
        """
        # Given
        data = {"choices": [["1", "Option 1", "Extra"], ["2"]]}

        # When
        serializer = PermissionSetResponseSerializer(data=data)

        # Then
        assert not serializer.is_valid()

    def test_choices_field_has_correct_help_text(self):
        """
        Given the PermissionSetResponseSerializer
        When the fields are inspected
        Then the choices field has the expected help text
        """
        # Given
        serializer = PermissionSetResponseSerializer()

        # When
        choices_field = serializer.fields["choices"]

        # Then
        assert choices_field.help_text == "List of [id, name] pairs for dropdown options"


class TestQuerysetToIdNameTuples:
    """Tests for the _queryset_to_id_name_tuples helper function"""

    def test_converts_queryset_to_tuples(self):
        """
        Given a QuerySet with id and name fields
        When converted using _queryset_to_id_name_tuples
        Then a list of (id, name) tuples is returned
        """
        # Given
        mock_queryset = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            {"id": 3, "name": "Third"},
        ]

        # When
        result = _queryset_to_id_name_tuples(mock_queryset)

        # Then
        assert result == [(1, "First"), (2, "Second"), (3, "Third")]

    def test_handles_empty_queryset(self):
        """
        Given an empty QuerySet
        When converted using _queryset_to_id_name_tuples
        Then an empty list is returned
        """
        # Given
        mock_queryset = []

        # When
        result = _queryset_to_id_name_tuples(mock_queryset)

        # Then
        assert result == []

    def test_preserves_id_types(self):
        """
        Given a QuerySet with various id types
        When converted using _queryset_to_id_name_tuples
        Then the id types are preserved
        """
        # Given
        mock_queryset = [
            {"id": 999, "name": "Large ID"},
            {"id": 1, "name": "Small ID"},
        ]

        # When
        result = _queryset_to_id_name_tuples(mock_queryset)

        # Then
        assert result[0][0] == 999
        assert result[1][0] == 1
        assert isinstance(result[0][0], int)
