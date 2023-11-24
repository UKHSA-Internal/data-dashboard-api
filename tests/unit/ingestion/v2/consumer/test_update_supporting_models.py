from unittest import mock

import pytest

from ingestion.v2.consumer import ConsumerV2


@pytest.fixture()
def consumer_with_mocked_model_managers() -> ConsumerV2:
    mocked_manager = mock.Mock()
    mocked_manager.get_or_create.return_value = mock.Mock(), mock.Mock()
    return ConsumerV2(
        source_data=mock.MagicMock(),
        dto=mock.Mock(),
        theme_manager=mocked_manager,
        sub_theme_manager=mocked_manager,
        topic_manager=mocked_manager,
        metric_group_manager=mocked_manager,
        metric_manager=mocked_manager,
        geography_type_manager=mocked_manager,
        geography_manager=mocked_manager,
        age_manager=mocked_manager,
        stratum_manager=mocked_manager,
    )


class TestConsumerUpdateSupportingModels:
    @mock.patch.object(ConsumerV2, "get_or_create_theme")
    @mock.patch.object(ConsumerV2, "get_or_create_sub_theme")
    @mock.patch.object(ConsumerV2, "get_or_create_topic")
    def test_updates_theme_sub_theme_and_topic(
        self,
        spy_get_or_create_topic: mock.MagicMock,
        spy_get_or_create_sub_theme: mock.MagicMock,
        spy_get_or_create_theme: mock.MagicMock,
        consumer_with_mocked_model_managers: ConsumerV2,
    ):
        """
        Given an instance of the `Consumer`
        When `update_supporting_models()` is called
        Then the `Theme`, `SubTheme` and `Topic` records
            are created by delegating the calls accordingly

        Patches:
            `spy_get_or_create_topic`: To check the
                `Topic` record is created with the
                previously created `SubTheme` record
            `spy_get_or_create_sub_theme`: To check the
                `SubTheme` record is created with the
                previously created `Theme` record
            `spy_get_or_create_theme`: To check the
                `Theme` record is created

        """
        # Given
        consumer = consumer_with_mocked_model_managers

        # When
        consumer.update_supporting_models()

        # Then
        spy_get_or_create_theme.assert_called_once()
        spy_get_or_create_sub_theme.assert_called_once_with(
            theme=spy_get_or_create_theme.return_value
        )
        spy_get_or_create_topic.assert_called_once_with(
            sub_theme=spy_get_or_create_sub_theme.return_value
        )

    @mock.patch.object(ConsumerV2, "get_or_create_geography_type")
    @mock.patch.object(ConsumerV2, "get_or_create_geography")
    def test_updates_geography_and_geography_type(
        self,
        spy_get_or_create_geography: mock.MagicMock,
        spy_get_or_create_geography_type: mock.MagicMock,
        consumer_with_mocked_model_managers: ConsumerV2,
    ):
        """
        Given an instance of the `Consumer`
        When `update_supporting_models()` is called
        Then the `Geography` and `GeographyType` records
            are created by delegating the calls accordingly

        Patches:
            `spy_get_or_create_geography`: To check the
                `Geography` record is created with the
                previously created `GeographyType` record
            `spy_get_or_create_geography_type`: To check the
                `GeographyType` record is created

        """
        # Given
        consumer = consumer_with_mocked_model_managers

        # When
        consumer.update_supporting_models()

        # Then
        spy_get_or_create_geography_type.assert_called_once()
        spy_get_or_create_geography.assert_called_once_with(
            geography_type=spy_get_or_create_geography_type.return_value
        )

    @mock.patch.object(ConsumerV2, "get_or_create_topic")
    @mock.patch.object(ConsumerV2, "get_or_create_metric_group")
    @mock.patch.object(ConsumerV2, "get_or_create_metric")
    def test_updates_metric_and_metric_group(
        self,
        spy_get_or_create_metric: mock.MagicMock,
        spy_get_or_create_metric_group: mock.MagicMock,
        spy_get_or_create_topic: mock.MagicMock,
        consumer_with_mocked_model_managers: ConsumerV2,
    ):
        """
        Given an instance of the `Consumer`
        When `update_supporting_models()` is called
        Then the `Metric` and `MetricGroup` records
            are created by delegating the calls accordingly

        Patches:
            `spy_get_or_create_metric`: To check the
                `Metric` record is created with the
                previously created `MetricGroup`
                and `Topic` records
            `spy_get_or_create_metric_group`: To check the
                `MetricGroup` record is created with the
                previously created `Topic` record
            `spy_get_or_create_topic`: To check the
                previously created `Topic` record
                is passed to the call when creating
                the `Metric` and `MetricGroup` records

        """
        # Given
        consumer = consumer_with_mocked_model_managers

        # When
        consumer.update_supporting_models()

        # Then
        spy_get_or_create_metric_group.assert_called_once_with(
            topic=spy_get_or_create_topic.return_value
        )
        spy_get_or_create_metric.assert_called_once_with(
            metric_group=spy_get_or_create_metric_group.return_value,
            topic=spy_get_or_create_topic.return_value,
        )

    @mock.patch.object(ConsumerV2, "get_or_create_stratum")
    def test_updates_stratum(
        self,
        spy_get_or_create_stratum: mock.MagicMock,
        consumer_with_mocked_model_managers: ConsumerV2,
    ):
        """
        Given an instance of the `Consumer`
        When `update_supporting_models()` is called
        Then the `Stratum` record is created
            by delegating the call accordingly

        Patches:
            `spy_get_or_create_stratum`: To check the
                `Stratum` record is created

        """
        # Given
        consumer = consumer_with_mocked_model_managers

        # When
        consumer.update_supporting_models()

        # Then
        spy_get_or_create_stratum.assert_called_once()

    @mock.patch.object(ConsumerV2, "get_or_create_age")
    def test_updates_age(
        self,
        spy_get_or_create_age: mock.MagicMock,
        consumer_with_mocked_model_managers: ConsumerV2,
    ):
        """
        Given an instance of the `Consumer`
        When `update_supporting_models()` is called
        Then the `Age` record is created
            by delegating the call accordingly

        Patches:
            `spy_get_or_create_age`: To check the
                `Age` record is created

        """
        # Given
        consumer = consumer_with_mocked_model_managers

        # When
        consumer.update_supporting_models()

        # Then
        spy_get_or_create_age.assert_called_once()

    @mock.patch.object(ConsumerV2, "get_or_create_stratum")
    @mock.patch.object(ConsumerV2, "get_or_create_age")
    @mock.patch.object(ConsumerV2, "get_or_create_geography")
    @mock.patch.object(ConsumerV2, "get_or_create_metric")
    def test_returns_supporting_models_lookup(
        self,
        spy_get_or_create_metric: mock.MagicMock,
        spy_get_or_create_geography: mock.MagicMock,
        spy_get_or_create_age: mock.MagicMock,
        spy_get_or_create_stratum: mock.MagicMock,
        consumer_with_mocked_model_managers: ConsumerV2,
    ):
        """
        Given an instance of the `Consumer`
        When `update_supporting_models()` is called
        Then the `Geography` and `GeographyType` records
            are created by delegating the calls accordingly

        Patches:
            `spy_get_or_create_metric`: To check the
                ID of the `Metric` record is used
                to enrich the returned `SupportingModelsLookup`
            `spy_get_or_create_geography`: To check the
                ID of the `Geography` record is used
                to enrich the returned `SupportingModelsLookup`
            `spy_get_or_create_age`: To check the
                ID of the `Age` record is used
                to enrich the returned `SupportingModelsLookup`
            `spy_get_or_create_stratum`: To check the
                ID of the `Stratum` record is used
                to enrich the returned `SupportingModelsLookup`

        """
        # Given
        consumer = consumer_with_mocked_model_managers
        consumer.dto.sex = "all"
        consumer.dto.refresh_date = "2023-11-17"

        # When
        supporting_models_lookup = consumer.update_supporting_models()

        # The IDs of the relevant supporting models
        # are used to enrich the `SupportingModelsLookup` object
        assert (
            supporting_models_lookup.metric_id
            == spy_get_or_create_metric.return_value.id
        )
        assert (
            supporting_models_lookup.geography_id
            == spy_get_or_create_geography.return_value.id
        )
        assert (
            supporting_models_lookup.stratum_id
            == spy_get_or_create_stratum.return_value.id
        )
        assert supporting_models_lookup.age_id == spy_get_or_create_age.return_value.id
