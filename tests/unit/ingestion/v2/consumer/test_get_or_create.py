from unittest import mock

from ingestion.v2.consumer import ConsumerV2

EXAMPLE_DATA_TYPE = dict[str, str | list[dict[str, str | float]]]


class TestConsumerGetOrCreateMethods:
    def test_get_or_create_theme(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_theme()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `ThemeManager` with the correct args
        """
        # Given
        spy_theme_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_theme_manager.get_or_create.return_value = expected_model, True

        consumer = ConsumerV2(
            data=example_headline_data_v2, theme_manager=spy_theme_manager
        )

        # When
        created_model = consumer.get_or_create_theme()

        # Then
        assert created_model == expected_model
        spy_theme_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["parent_theme"]
        )

    def test_get_or_create_sub_theme(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_sub_theme()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `SubThemeManager` with the correct args
        """
        # Given
        spy_sub_theme_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_sub_theme_manager.get_or_create.return_value = expected_model, True

        mocked_theme = mock.Mock()
        consumer = ConsumerV2(
            data=example_headline_data_v2, sub_theme_manager=spy_sub_theme_manager
        )

        # When
        created_model = consumer.get_or_create_sub_theme(theme=mocked_theme)

        # Then
        assert created_model == expected_model
        spy_sub_theme_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["child_theme"], theme_id=mocked_theme.id
        )

    def test_get_or_create_topic(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_topic()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `TopicManager` with the correct args
        """
        # Given
        spy_topic_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_topic_manager.get_or_create.return_value = expected_model, True

        mocked_sub_theme = mock.Mock()
        consumer = ConsumerV2(
            data=example_headline_data_v2, topic_manager=spy_topic_manager
        )

        # When
        created_model = consumer.get_or_create_topic(sub_theme=mocked_sub_theme)

        # Then
        assert created_model == expected_model
        spy_topic_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["topic"], sub_theme_id=mocked_sub_theme.id
        )

    def test_get_or_create_geography_type(
        self, example_headline_data_v2: EXAMPLE_DATA_TYPE
    ):
        """
        Given incoming headline data
        When `get_or_create_geography_type()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `GeographyTypeManager` with the correct args
        """
        # Given
        spy_geography_type_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_geography_type_manager.get_or_create.return_value = expected_model, True

        consumer = ConsumerV2(
            data=example_headline_data_v2,
            geography_type_manager=spy_geography_type_manager,
        )

        # When
        created_model = consumer.get_or_create_geography_type()

        # Then
        assert created_model == expected_model
        spy_geography_type_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["geography_type"],
        )

    def test_get_or_create_geography(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_geography()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `GeographyManager` with the correct args
        """
        # Given
        spy_geography_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_geography_manager.get_or_create.return_value = expected_model, True

        mocked_geography_type = mock.Mock()
        consumer = ConsumerV2(
            data=example_headline_data_v2, geography_manager=spy_geography_manager
        )

        # When
        created_model = consumer.get_or_create_geography(
            geography_type=mocked_geography_type
        )

        # Then
        assert created_model == expected_model
        spy_geography_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["geography"],
            geography_type_id=mocked_geography_type.id,
            geography_code=example_headline_data_v2["geography_code"],
        )

    def test_get_or_create_metric_group(
        self, example_headline_data_v2: EXAMPLE_DATA_TYPE
    ):
        """
        Given incoming headline data
        When `get_or_create_metric_group()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `MetricGroupManager` with the correct args
        """
        # Given
        spy_metric_group_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_metric_group_manager.get_or_create.return_value = expected_model, True

        mocked_topic = mock.Mock()
        consumer = ConsumerV2(
            data=example_headline_data_v2, metric_group_manager=spy_metric_group_manager
        )

        # When
        created_model = consumer.get_or_create_metric_group(topic=mocked_topic)

        # Then
        assert created_model == expected_model
        spy_metric_group_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["metric_group"],
            topic_id=mocked_topic.id,
        )

    def test_get_or_create_metric(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_metric()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `MetricManager` with the correct args
        """
        # Given
        spy_metric_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_metric_manager.get_or_create.return_value = expected_model, True

        mocked_topic = mock.Mock()
        mocked_metric_group = mock.Mock()
        consumer = ConsumerV2(
            data=example_headline_data_v2, metric_manager=spy_metric_manager
        )

        # When
        created_model = consumer.get_or_create_metric(
            metric_group=mocked_metric_group, topic=mocked_topic
        )

        # Then
        assert created_model == expected_model
        spy_metric_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["metric"],
            topic_id=mocked_topic.id,
            metric_group_id=mocked_metric_group.id,
        )

    def test_get_or_create_stratum(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_stratum()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `StratumManager` with the correct args
        """
        # Given
        spy_stratum_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_stratum_manager.get_or_create.return_value = expected_model, True

        consumer = ConsumerV2(
            data=example_headline_data_v2, stratum_manager=spy_stratum_manager
        )

        # When
        created_model = consumer.get_or_create_stratum()

        # Then
        assert created_model == expected_model
        spy_stratum_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["stratum"],
        )

    def test_get_or_create_age(self, example_headline_data_v2: EXAMPLE_DATA_TYPE):
        """
        Given incoming headline data
        When `get_or_create_age()` is called
            from an instance of the `Consumer`
        Then the call is delegated to the
            `AgeManager` with the correct args
        """
        # Given
        spy_age_manager = mock.Mock()
        expected_model = mock.Mock()
        spy_age_manager.get_or_create.return_value = expected_model, True

        consumer = ConsumerV2(
            data=example_headline_data_v2, age_manager=spy_age_manager
        )

        # When
        created_model = consumer.get_or_create_age()

        # Then
        assert created_model == expected_model
        spy_age_manager.get_or_create.assert_called_once_with(
            name=example_headline_data_v2["age"],
        )
