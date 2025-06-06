from unittest import mock

import pytest
from rest_framework.exceptions import ValidationError

from metrics.api.serializers.trends import (
    TrendsQuerySerializer,
    TrendsResponseSerializer,
)
from tests.fakes.factories.metrics.age_factory import FakeAgeFactory
from tests.fakes.factories.metrics.geography_factory import FakeGeographyFactory
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.factories.metrics.stratum_factory import FakeStratumFactory
from tests.fakes.managers.age_manager import FakeAgeManager
from tests.fakes.managers.geography_manager import FakeGeographyManager
from tests.fakes.managers.geography_type_manager import FakeGeographyTypeManager
from tests.fakes.managers.metric_manager import FakeMetricManager
from tests.fakes.managers.stratum_manager import FakeStratumManager
from tests.fakes.managers.topic_manager import FakeTopicManager


class TestTrendsQuerySerializer:
    DATA_PAYLOAD_HINT = dict[str, str]

    @classmethod
    def _setup_valid_data_payload_and_model_managers(
        cls,
    ) -> tuple[
        DATA_PAYLOAD_HINT,
        FakeMetricManager,
        FakeTopicManager,
        FakeGeographyManager,
        FakeGeographyTypeManager,
        FakeAgeManager,
        FakeStratumManager,
    ]:
        metric_name = "COVID-19_headline_ONSdeaths_7DayChange"

        fake_metric = FakeMetricFactory.build_example_metric(
            metric_name=metric_name,
            metric_group_name="headline",
        )
        fake_topic = fake_metric.metric_group.topic
        fake_percentage_metric = FakeMetricFactory.build_example_metric(
            metric_name="COVID-19_headline_ONSdeaths_7DayPercentChange",
            metric_group_name="headline",
        )
        fake_geography = FakeGeographyFactory.build_example(
            geography_name="England",
            geography_type_name="Nation",
            geography_code="E92000001",
        )
        fake_age = FakeAgeFactory.build_example(age_name="all")
        fake_stratum = FakeStratumFactory.build_example(stratum_name="default")

        data: cls.DATA_PAYLOAD_HINT = {
            "topic": fake_topic.name,
            "metric": fake_metric.name,
            "percentage_metric": fake_percentage_metric.name,
            "stratum": fake_stratum.name,
            "age": fake_age.name,
            "sex": "all",
            "geography": fake_geography.name,
            "geography_type": fake_geography.geography_type.name,
        }

        return (
            data,
            FakeMetricManager([fake_metric, fake_percentage_metric]),
            FakeTopicManager([fake_topic]),
            FakeGeographyManager([fake_geography]),
            FakeGeographyTypeManager([fake_geography.geography_type]),
            FakeAgeManager([fake_age]),
            FakeStratumManager([fake_stratum]),
        )

    def test_can_validate_successfully(self):
        """
        Given a valid payload passed to the `TrendsQuerySerializer` object
        When `is_valid()` is called from the serializer
        Then True is returned
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "age_manager": age_manager,
                "stratum_manager": stratum_manager,
            },
        )

        # When
        validated: bool = serializer.is_valid()

        # Then
        assert validated

    @pytest.mark.parametrize(
        "field_to_be_serialized", ["topic", "metric", "percentage_metric"]
    )
    def test_invalid_field_value(self, field_to_be_serialized: str):
        """
        Given an invalid value passed to a field on the `TrendsQuerySerializer` object
        And valid values given to the remaining fields
        When `is_valid()` is called from the serializer
        Then a `ValidationError` is raised
        """
        # Given
        (
            data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        data_payload[field_to_be_serialized] = "invalid-value"

        serializer = TrendsQuerySerializer(
            data=data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "stratum_manager": age_manager,
                "age_manager": stratum_manager,
            },
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_metric_manager_is_used_to_build_choices_for_metric_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_unique_change_type_names()` from the `MetricManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "stratum_manager": age_manager,
                "age_manager": stratum_manager,
            },
        )

        # Then
        expected_metric_names: set[str] = set(
            metric_manager.get_all_unique_change_type_names()
        )
        assert set(serializer.fields["metric"].choices) == expected_metric_names

    def test_metric_manager_is_used_to_build_choices_for_percentage_metric_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_unique_percent_change_type_names()`
            from the `MetricManager`is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "stratum_manager": age_manager,
                "age_manager": stratum_manager,
            },
        )

        # Then
        expected_metric_names: list[str] = (
            metric_manager.get_all_unique_percent_change_type_names()
        )
        assert (
            list(serializer.fields["percentage_metric"].choices)
            == expected_metric_names
        )

    def test_topic_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `TopicManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "stratum_manager": age_manager,
                "age_manager": stratum_manager,
            },
        )

        # Then
        expected_topic_names: list[str] = topic_manager.get_all_names()
        assert list(serializer.fields["topic"].choices) == expected_topic_names

    def test_geography_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `GeographyManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        geography_manager = FakeGeographyManager(geographies=[mock.Mock()])

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "stratum_manager": age_manager,
                "age_manager": stratum_manager,
            },
        )

        # Then
        expected_geography_names: list[str] = geography_manager.get_all_names()
        assert list(serializer.fields["geography"].choices) == expected_geography_names

    def test_geography_type_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `GeographyTypeManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        geography_type_manager = FakeGeographyTypeManager(geography_types=[mock.Mock()])

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "geography_type_manager": geography_type_manager,
                "geography_manager": geography_type_manager,
                "stratum_manager": age_manager,
                "age_manager": stratum_manager,
            },
        )

        # Then
        expected_geography_type_names: list[str] = (
            geography_type_manager.get_all_names()
        )
        assert (
            list(serializer.fields["geography_type"].choices)
            == expected_geography_type_names
        )

    def test_stratum_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `StratumManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        stratum_manager = FakeStratumManager(strata=[mock.Mock()])

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "stratum_manager": stratum_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "age_manager": age_manager,
            },
        )

        # Then
        expected_stratum_names: list[str] = stratum_manager.get_all_names()
        assert list(serializer.fields["stratum"].choices) == expected_stratum_names

    def test_age_manager_is_used_to_build_choices_for_field(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When the serializer is initialized
        Then the result of `get_all_names()` from the `AgeManager`
            is used to populate the correct field choices
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        age_manager = FakeAgeManager(ages=[mock.Mock()])

        # When
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "topic_manager": topic_manager,
                "metric_manager": metric_manager,
                "age_manager": age_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "stratum_manager": stratum_manager,
            },
        )

        # Then
        expected_age_names: list[str] = age_manager.get_all_names()
        assert list(serializer.fields["age"].choices) == expected_age_names

    def test_to_models(self):
        """
        Given a valid payload passed to a `TrendsQuerySerializer` object
        When `to_models()` is called from the serializer
        Then a model is returned containing the correct fields
        """
        # Given
        (
            valid_data_payload,
            metric_manager,
            topic_manager,
            geography_manager,
            geography_type_manager,
            age_manager,
            stratum_manager,
        ) = self._setup_valid_data_payload_and_model_managers()
        serializer = TrendsQuerySerializer(
            data=valid_data_payload,
            context={
                "metric_manager": metric_manager,
                "topic_manager": topic_manager,
                "geography_manager": geography_manager,
                "geography_type_manager": geography_type_manager,
                "age_manager": age_manager,
                "stratum_manager": stratum_manager,
            },
        )
        serializer.is_valid(raise_exception=True)

        # When
        trends_parameters = serializer.to_models(request=None)

        # Then
        assert trends_parameters.topic_name == valid_data_payload["topic"]
        assert trends_parameters.metric_name == valid_data_payload["metric"]
        assert (
            trends_parameters.percentage_metric_name
            == valid_data_payload["percentage_metric"]
        )


class TestTrendsResponseSerializer:
    def test_can_validate_successfully(self):
        """
        Given a valid payload containing the correct associated trends fields
        When `is_valid()` is called from an instance of the `TrendsResponseSerializer`
        Then True is returned
        """
        # Given
        payload = {
            "metric_name": "COVID-19_headline_ONSdeaths_7DayChange",
            "metric_value": 10,
            "percentage_metric_name": "COVID-19_headline_ONSdeaths_7DayPercentChange",
            "percentage_metric_value": 3.2,
            "direction": "up",
            "colour": "red",
        }

        serializer = TrendsResponseSerializer(data=payload)

        # When
        validated: bool = serializer.is_valid()

        # Then
        assert validated
