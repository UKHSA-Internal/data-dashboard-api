from unittest import mock

import pytest

from ingestion.data_transfer_models.incoming import (
    IncomingHeadlineDTO,
    IncomingTimeSeriesDTO,
)
from ingestion.reader import COLUMN_NAMES_WITH_FOREIGN_KEYS, Reader
from metrics.data.enums import TimePeriod
from tests.fakes.factories.metrics.metric_factory import FakeMetricFactory
from tests.fakes.managers.metric_manager import FakeMetricManager

MODULE_PATH = "ingestion.reader"


class TestReader:
    def test_supporting_model_column_names(self):
        """
        Given mocked data
        When the `supporting_model_column_names` property
            is called from an instance of `Reader`
        Then the correct list of strings is returned
        """
        # Given
        mocked_data = mock.Mock()
        reader = Reader(data=mocked_data)

        # When
        returned_column_names: list[str] = reader.supporting_model_column_names

        # Then
        assert returned_column_names == COLUMN_NAMES_WITH_FOREIGN_KEYS

    # Tests for `post_process_incoming_dtos()`

    @mock.patch.object(Reader, "_remove_any_dtos_with_none_metric_value")
    def test_post_process_incoming_dtos_calls_method_to_remove_none_metric_values(
        self,
        spy_remove_any_dtos_with_none_metric_value: mock.MagicMock,
    ):
        """
        Given mocked `incoming_dtos`
        When `post_process_incoming_dtos()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_remove_any_dtos_with_none_metric_value()` method

        Patches:
            `spy_remove_any_dtos_with_none_metric_value`: For
                the main assertion
        """
        # Given
        mocked_incoming_dtos = mock.MagicMock()
        reader = Reader(data=mock.Mock())

        # When
        reader.post_process_incoming_dtos(incoming_dtos=mocked_incoming_dtos)

        # Then
        spy_remove_any_dtos_with_none_metric_value.assert_called_once_with(
            incoming_dtos=mocked_incoming_dtos
        )

    @mock.patch.object(Reader, "_remove_any_dtos_with_none_metric_value")
    @mock.patch.object(Reader, "_cast_sex_on_dtos_to_expected_values")
    def test_post_process_incoming_dtos_calls_method_to_cast_sex_attr(
        self,
        spy_cast_sex_on_dtos_to_expected_values: mock.MagicMock,
        spy_remove_any_dtos_with_none_metric_value: mock.MagicMock,
    ):
        """
        Given mocked `incoming_dtos`
        When `post_process_incoming_dtos()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_cast_sex_on_dtos_to_expected_values()` method

        Patches:
            `spy_cast_sex_on_dtos_to_expected_values`: For
                the main assertion
            `spy_remove_any_dtos_with_none_metric_value`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_cast_sex_on_dtos_to_expected_values()`

        """
        # Given
        mocked_incoming_dtos = mock.MagicMock()
        reader = Reader(data=mock.Mock())

        # When
        reader.post_process_incoming_dtos(incoming_dtos=mocked_incoming_dtos)

        # Then
        incoming_dtos_from_previous_callee_method = (
            spy_remove_any_dtos_with_none_metric_value.return_value
        )
        spy_cast_sex_on_dtos_to_expected_values.assert_called_once_with(
            incoming_dtos=incoming_dtos_from_previous_callee_method
        )

    @mock.patch.object(Reader, "_cast_sex_on_dtos_to_expected_values")
    @mock.patch.object(Reader, "_cast_metric_frequency_on_dtos_to_expected_values")
    def test_post_process_incoming_dtos_calls_method_to_cast_metric_frequency_attr(
        self,
        spy_cast_metric_frequency_on_dtos_to_expected_values: mock.MagicMock,
        spy_cast_sex_on_dtos_to_expected_values: mock.MagicMock,
    ):
        """
        Given mocked `incoming_dtos`
        When `post_process_incoming_dtos()` is called
            from an instance of `Reader`
        Then a call is delegated to the
            `_cast_metric_frequency_on_dtos_to_expected_values()` method

        Patches:
            `spy_cast_metric_frequency_on_dtos_to_expected_values`: For
                the main assertion
            `spy_cast_sex_on_dtos_to_expected_values`: To isolate
                 the return value, so it can be used to check
                 the contract on the call to
                 `_cast_metric_frequency_on_dtos_to_expected_values()`

        """
        # Given
        mocked_incoming_dtos = mock.MagicMock()
        reader = Reader(data=mock.Mock())

        # When
        reader.post_process_incoming_dtos(incoming_dtos=mocked_incoming_dtos)

        # Then
        incoming_dtos_from_previous_callee_method = (
            spy_cast_sex_on_dtos_to_expected_values.return_value
        )
        spy_cast_metric_frequency_on_dtos_to_expected_values.assert_called_once_with(
            incoming_dtos=incoming_dtos_from_previous_callee_method
        )

    @mock.patch.object(Reader, "_cast_metric_frequency_on_dtos_to_expected_values")
    def test_post_process_incoming_dtos_calls_method_for_return_value(
        self,
        spy_cast_metric_frequency_on_dtos_to_expected_values: mock.MagicMock,
    ):
        """
        Given mocked `incoming_dtos`
        When `post_process_incoming_dtos()` is called
            from an instance of `Reader`
        Then the final call is delegated to the
            `_cast_metric_frequency_on_dtos_to_expected_values()`
            method for the return value

        Patches:
            `spy_cast_metric_frequency_on_dtos_to_expected_values`: For
                the main assertion

        """
        # Given
        mocked_incoming_dtos = mock.MagicMock()
        reader = Reader(data=mock.Mock())

        # When
        returned_dtos = reader.post_process_incoming_dtos(
            incoming_dtos=mocked_incoming_dtos
        )

        # Then
        assert (
            returned_dtos
            == spy_cast_metric_frequency_on_dtos_to_expected_values.return_value
        )

    @mock.patch.object(Reader, "_cast_sex_on_dtos_to_expected_values")
    @mock.patch.object(Reader, "_cast_metric_frequency_on_dtos_to_expected_values")
    def test_post_process_incoming_dtos_returns_correctly_when_metric_frequency_call_errors(
        self,
        mocked_cast_metric_frequency_on_dtos_to_expected_values: mock.MagicMock,
        spy_cast_sex_on_dtos_to_expected_values: mock.MagicMock,
    ):
        """
        Given mocked `incoming_dtos`
        When `post_process_incoming_dtos()` is called
            from an instance of `Reader`
        Then the final call is delegated to the
            `_cast_metric_frequency_on_dtos_to_expected_values()`
            method for the return value in spite
            of an `AttributeError` being raised

        Patches:
            `spy_cast_metric_frequency_on_dtos_to_expected_values`: To
                trigger the `AttributeError`
            `spy_cast_sex_on_dtos_to_expected_values`: For
                the main assertion

        """
        # Given
        mocked_incoming_dtos = mock.MagicMock()
        reader = Reader(data=mock.Mock())
        mocked_cast_metric_frequency_on_dtos_to_expected_values.side_effect = (
            AttributeError
        )

        # When
        returned_dtos = reader.post_process_incoming_dtos(
            incoming_dtos=mocked_incoming_dtos
        )

        # Then
        assert returned_dtos == spy_cast_sex_on_dtos_to_expected_values.return_value

    ####

    def test_get_unique_values_from_incoming_dtos_for_model(
        self, example_incoming_headline_dto: IncomingHeadlineDTO
    ):
        """
        Given a list of `IncomingHeadlineDTO` instances
            with duplicate values for a specified field
        When `_get_unique_values_from_incoming_dtos_for_model()`
            is called from an instance of `Reader`
        Then a set is returned containing unique values
            for the specified field
        """
        # Given
        incoming_headline_dtos = [example_incoming_headline_dto] * 3
        fields = {"parent_theme": "name"}
        reader = Reader(data=incoming_headline_dtos)

        # When
        unique_value_for_fields: set = (
            reader._get_unique_value_groups_from_incoming_dtos_for_model(
                incoming_dtos=incoming_headline_dtos, fields=fields
            )
        )

        # Then
        # In this case, the "parent_theme" key was requested
        # So this field is the focus of the returned set of values
        assert unique_value_for_fields == {
            (("parent_theme", example_incoming_headline_dto.parent_theme),)
        }

    @pytest.mark.parametrize(
        "fields, expected_unique_values",
        (
            [{"parent_theme": "name"}, {(("parent_theme", "infectious_disease"),)}],
            [
                {"child_theme": "name", "parent_theme": "theme_id"},
                {
                    (
                        ("child_theme", "respiratory"),
                        ("parent_theme", "infectious_disease"),
                    )
                },
            ],
            [
                {"topic": "name", "child_theme": "sub_theme_id"},
                {(("topic", "COVID-19"), ("child_theme", "respiratory"))},
            ],
            [{"geography_type": "name"}, {(("geography_type", "Nation"),)}],
            [
                {"geography": "name", "geography_type": "geography_type_id"},
                {(("geography", "England"), ("geography_type", "Nation"))},
            ],
            [
                {"metric_group": "name", "topic": "topic_id"},
                {(("metric_group", "deaths"), ("topic", "COVID-19"))},
            ],
            [
                {
                    "metric": "name",
                    "metric_group": "metric_group_id",
                    "topic": "topic_id",
                },
                {
                    (
                        ("metric", "COVID-19_deaths_ONSByDay"),
                        ("metric_group", "deaths"),
                        ("topic", "COVID-19"),
                    )
                },
            ],
            [{"stratum": "name"}, {(("stratum", "default"),)}],
            [{"age": "name"}, {(("age", "all"),)}],
        ),
    )
    def test_get_unique_values_from_incoming_dtos_for_model_all_types(
        self,
        fields: dict[str, str],
        expected_unique_values: set[tuple[tuple[str, str]]],
        example_timeseries_data: list[dict[str, str | int | float]],
    ):
        """
        Given a list of `IncomingHeadlineDTO` instances
            with multiple specified fields
        When `_get_unique_values_from_incoming_dtos_for_model()`
            is called from an instance of `Reader`
        Then a set is returned containing unique values
            for each specified field
        """
        # Given
        incoming_headline_dtos = [
            IncomingTimeSeriesDTO(**data) for data in example_timeseries_data
        ]
        reader = Reader(data=incoming_headline_dtos)

        # When
        unique_value_for_fields: set = (
            reader._get_unique_value_groups_from_incoming_dtos_for_model(
                incoming_dtos=incoming_headline_dtos, fields=fields
            )
        )

        # Then
        assert unique_value_for_fields == expected_unique_values

    @pytest.mark.parametrize(
        "unique_values, expected_converted_unique_values",
        (
            [
                {(("parent_theme", "infectious_disease"),)},
                {"parent_theme": "infectious_disease"},
            ],
            [
                {
                    (
                        ("child_theme", "respiratory"),
                        ("parent_theme", "infectious_disease"),
                    )
                },
                {"child_theme": "respiratory", "parent_theme": "infectious_disease"},
            ],
            [
                {(("topic", "COVID-19"), ("child_theme", "respiratory"))},
                {"topic": "COVID-19", "child_theme": "respiratory"},
            ],
            [{(("geography_type", "Nation"),)}, {"geography_type": "Nation"}],
            [
                {(("geography", "England"), ("geography_type", "Nation"))},
                {"geography": "England", "geography_type": "Nation"},
            ],
            [
                {(("metric_group", "deaths"), ("topic", "COVID-19"))},
                {"metric_group": "deaths", "topic": "COVID-19"},
            ],
            [
                {
                    (
                        ("metric", "COVID-19_deaths_ONSByDay"),
                        ("metric_group", "deaths"),
                        ("topic", "COVID-19"),
                    )
                },
                {
                    "metric": "COVID-19_deaths_ONSByDay",
                    "metric_group": "deaths",
                    "topic": "COVID-19",
                },
            ],
            [{(("stratum", "default"),)}, {"stratum": "default"}],
            [{(("age", "all"),)}, {"age": "all"}],
        ),
    )
    def test_convert_unique_values_groups(
        self,
        unique_values: set[tuple[tuple[str, str]]],
        expected_converted_unique_values: dict[str, str],
        example_timeseries_data: list[dict[str, str | int | float]],
    ):
        """
        Given a list of unique values
        When `_convert_unique_values_to_dict()`
            is called from an instance of `Reader`
        Then a dict is returned containing unique values
            for each specified field and a "pk" key-value pair
        """
        # Given
        reader = Reader(data=mock.Mock())

        # When
        unique_value_for_fields: list[
            dict[str, dict[str, str] | None]
        ] = reader._convert_unique_value_groups(unique_value_groups=unique_values)

        # Then
        expected_return_value = [
            {"fields": expected_converted_unique_values, "pk": None}
        ]
        assert unique_value_for_fields == expected_return_value

    def test_remove_any_dtos_with_none_metric_value(
        self, example_incoming_headline_dto: IncomingHeadlineDTO
    ):
        """
        Given a list of `IncomingHeadlineDTO` instances
            where one instance has a None `metric_value`
        When `_remove_any_dtos_with_none_metric_value()` is called
            from an instance of `Reader`
        Then the DTO without a `metric_value` is removed
            from the returned `IncomingHeadlineDTO` instances
        """
        # Given
        incoming_dto_with_none_metric_value = example_incoming_headline_dto.copy()
        incoming_dto_with_none_metric_value.metric_value = None
        fake_incoming_dtos = [
            example_incoming_headline_dto,
            incoming_dto_with_none_metric_value,
        ]

        reader = Reader(data=mock.Mock())

        # When
        returned_dtos = reader._remove_any_dtos_with_none_metric_value(
            incoming_dtos=fake_incoming_dtos
        )

        # Then
        assert all(
            returned_dto.metric_value is not None for returned_dto in returned_dtos
        )
        assert len(returned_dtos) == len(fake_incoming_dtos) - 1 == 1

    def test_remove_any_dtos_with_none_metric_value_does_not_remove_valid_rows(
        self, example_incoming_headline_dto: IncomingHeadlineDTO
    ):
        """
        Given a list of `IncomingHeadlineDTO` instances
            where each has a valid `metric_value`
        When `_remove_any_dtos_with_none_metric_value()` is called
            from an instance of `Reader`
        Then no DTOs are removed from the returned
            list of `IncomingHeadlineDTO` instances
        """
        # Given
        incoming_dto_with_valid_metric_value = example_incoming_headline_dto.copy()
        incoming_dto_with_valid_metric_value.metric_value = 456
        fake_incoming_dtos = [
            example_incoming_headline_dto,
            incoming_dto_with_valid_metric_value,
        ]

        reader = Reader(data=mock.Mock())

        # When
        returned_dtos = reader._remove_any_dtos_with_none_metric_value(
            incoming_dtos=fake_incoming_dtos
        )

        # Then
        assert all(
            returned_dto.metric_value is not None for returned_dto in returned_dtos
        )
        assert len(returned_dtos) == len(fake_incoming_dtos)

    def test_create_record(self):
        """
        Given a dict of data required to create new records
        When `_create_record()`
            is called from an instance of `Reader`
        Then the call is delegated to the `create`
            method on the model manager
        """
        # Given
        spy_model_manager = mock.Mock()
        values_for_new_records = {"name": "infectious_disease"}
        reader = Reader(data=mock.Mock())

        # When
        reader._create_record(
            values_for_new_record=values_for_new_records,
            model_manager=spy_model_manager,
        )

        # Then
        spy_model_manager.create.assert_called_once_with(**values_for_new_records)

    @mock.patch.object(Reader, "_create_record")
    def test_create_records_for_new_values(self, spy_create_record: mock.MagicMock):
        """
        Given a list of mocked values to be created for multiple records
        When `_create_records_for_new_values()` is called
            from an instance of `Reader`
        Then the call is delegated to the `_create_record()` method
            for each individual record to be created

        Patches:
            `spy_create_record`: For the main assertion.
                To check this callee method is invoked
                for each of the input values

        """
        # Given
        mocked_values_to_be_created = [mock.Mock()] * 3
        reader = Reader(data=mock.Mock())
        mocked_model_manager = mock.Mock()

        # When
        reader._create_records_for_new_values(
            values_for_new_records=mocked_values_to_be_created,
            model_manager=mocked_model_manager,
        )

        # Then
        expected_calls = [
            mock.call(
                values_for_new_record=mocked_values, model_manager=mocked_model_manager
            )
            for mocked_values in mocked_values_to_be_created
        ]
        spy_create_record.assert_has_calls(calls=expected_calls, any_order=True)

    def test_get_existing_records_for_values_returns_queryset_for_existing_records(
        self,
    ):
        """
        Given a model manager which contain an existing record
        When `_get_existing_records_for_values()` is called
            from an instance of `Reader`
        Then a queryset is returned with the data for
            any matching existing records
        """
        # Given
        mocked_model_manager = mock.MagicMock()
        mocked_model_manager.all.return_value.values.return_value = [
            {"parent_theme": "infectious_disease", "pk": 123},
        ]
        fields = {"parent_theme": "name"}
        reader = Reader(data=mock.Mock())

        # When
        returned_queryset = reader._get_existing_records_for_values(
            fields=fields, model_manager=mocked_model_manager
        )

        # Then
        record = returned_queryset[0]
        assert record["parent_theme"] == "infectious_disease"
        assert record["pk"] == 123

    def test_get_existing_records_for_values_delegates_call_to_model_manager(
        self,
    ):
        """
        Given a model manager
        When `_get_existing_records_for_values()` is called
            from an instance of `Reader`
        Then the call is delegated to the model manager

        """
        # Given
        spy_model_manager = mock.MagicMock()
        fields = {"parent_theme": "name"}
        reader = Reader(data=mock.Mock())

        # When
        reader._get_existing_records_for_values(
            fields=fields, model_manager=spy_model_manager
        )

        # Then
        spy_model_manager.all.return_value.values.assert_called_once_with(
            "pk", *fields.values()
        )

    @pytest.mark.parametrize(
        "sex_attribute_value, expected_value",
        (
            ["all", "ALL"],
            ["female", "F"],
            ["male", "M"],
        ),
    )
    def test_cast_sex_on_dtos_to_expected_values(
        self,
        sex_attribute_value: str,
        expected_value: str,
        example_incoming_headline_dto: IncomingHeadlineDTO,
    ):
        """
        Given a list containing a `IncomingHeadlineDTO` instance
        When `_cast_sex_on_dtos_to_expected_values()` is called
            from an instance of `Reader`
        Then the returned DTOs has cast the `sex` attr
            to one of the expected values
        """
        # Given
        example_incoming_headline_dto.sex = sex_attribute_value
        fake_incoming_dtos = [example_incoming_headline_dto]

        reader = Reader(data=mock.Mock())

        # When
        returned_dtos: list[
            IncomingHeadlineDTO
        ] = reader._cast_sex_on_dtos_to_expected_values(
            incoming_dtos=fake_incoming_dtos,
        )

        # Then
        assert returned_dtos[0].sex == expected_value

    @pytest.mark.parametrize(
        "metric_frequency_attribute_value, expected_value",
        (
            ["daily", TimePeriod.Daily.value],
            ["weekly", TimePeriod.Weekly.value],
            ["monthly", TimePeriod.Monthly.value],
            ["quarterly", TimePeriod.Quarterly.value],
            ["annual", TimePeriod.Annual.value],
        ),
    )
    def test_cast_metric_frequency_on_dtos_to_expected_values(
        self,
        metric_frequency_attribute_value: str,
        expected_value: str,
        example_incoming_timeseries_dto: IncomingTimeSeriesDTO,
    ):
        """
        Given a list containing a `IncomingTimeSeriesDTO` instance
        When `_cast_metric_frequency_on_dtos_to_expected_values()`
            is called from an instance of `Reader`
        Then the returned DTOs has cast the `metric_frequency` attr
            to one of the expected values
        """
        # Given
        example_incoming_timeseries_dto.metric_frequency = (
            metric_frequency_attribute_value
        )
        fake_incoming_dtos = [example_incoming_timeseries_dto]

        reader = Reader(data=mock.Mock())

        # When
        returned_dtos: list[
            IncomingTimeSeriesDTO
        ] = reader._cast_metric_frequency_on_dtos_to_expected_values(
            incoming_dtos=fake_incoming_dtos,
        )

        # Then
        assert returned_dtos[0].metric_frequency == expected_value

    @pytest.mark.parametrize(
        "unmapped_fields, fields, expected_mapped_fields",
        (
            [
                {"parent_theme": "infectious_disease"},
                {"parent_theme": "name"},
                {"name": "infectious_disease"},
            ],
            [
                {"parent_theme": "infectious_disease", "child_theme": "respiratory"},
                {"child_theme": "name", "parent_theme": "theme_id"},
                {"name": "respiratory", "theme_id": "infectious_disease"},
            ],
            [
                {"topic": "COVID-19", "child_theme": "respiratory"},
                {"topic": "name", "child_theme": "sub_theme_id"},
                {"name": "COVID-19", "sub_theme_id": "respiratory"},
            ],
            [
                {"geography_type": "Nation"},
                {"geography_type": "name"},
                {"name": "Nation"},
            ],
            [
                {"geography": "England", "geography_type": "Nation"},
                {"geography": "name", "geography_type": "geography_type_id"},
                {"name": "England", "geography_type_id": "Nation"},
            ],
            [
                {"metric_group": "headline", "topic": "COVID-19"},
                {"metric_group": "name", "topic": "topic_id"},
                {"name": "headline", "topic_id": "COVID-19"},
            ],
            [
                {
                    "metric": "COVID-19_headline_positivity_latest",
                    "metric_group": "headline",
                    "topic": "COVID-19",
                },
                {
                    "metric": "name",
                    "metric_group": "metric_group_id",
                    "topic": "topic_id",
                },
                {
                    "name": "COVID-19_headline_positivity_latest",
                    "metric_group_id": "headline",
                    "topic_id": "COVID-19",
                },
            ],
            [{"stratum": "default"}, {"stratum": "name"}, {"name": "default"}],
            [{"age": "all"}, {"age": "name"}, {"name": "all"}],
        ),
    )
    def test_map_fields_for_unique_values(
        self,
        unmapped_fields: dict[str, str],
        fields: dict[str, str],
        expected_mapped_fields: dict[str, str],
    ):
        """
        Given a dict containing unmapped fields
        And a dict containing the fields to map to
        When `map_fields_for_unique_values()` is called
            from an instance of `Reader`
        Then the returned dict contains a key value pair of "mapped_fields"
            which contains the original unmapped fields, mapped according
            to the `fields` dict
        """
        # Given
        fields_for_unique_values = {"pk": None, "fields": unmapped_fields}
        reader = Reader(data=mock.Mock())

        # When
        fields_for_mapped_unique_values: dict[
            str, dict[str, str] | None
        ] = reader.map_fields_for_unique_values(
            fields_for_unique_values=fields_for_unique_values,
            fields=fields,
        )

        # Then
        assert (
            fields_for_mapped_unique_values["mapped_fields"] == expected_mapped_fields
        )

    def test_add_pk_to_values_for_unique_fields(self):
        """
        Given a model manager containing a record
            which can be mapped to a given dict of fields
        When `_add_pk_to_values_for_unique_fields()`
            is called from an instance of `Reader`
        Then the returned dict contains the
            ID/pk of the matching record
        """
        # Given
        fake_metric = FakeMetricFactory.build_example_metric()
        fake_metric.pk = 123
        fake_metric.metric_group_id = 456
        fake_metric.topic_id = 789
        fake_metric_manager = FakeMetricManager(metrics=[fake_metric])
        reader = Reader(data=mock.Mock())

        values_for_unique_fields = {
            "pk": None,
            "fields": {
                "metric": "name",
                "metric_group": "metric_group_id",
                "topic": "topic_id",
            },
            "mapped_fields": {
                "name": fake_metric.name,
                "metric_group_id": fake_metric.metric_group_id,
                "topic_id": fake_metric.topic_id,
            },
        }

        # When
        returned_values_for_unique_fields: dict[
            str, int | dict[str, str]
        ] = reader._add_pk_to_values_for_unique_fields(
            values_for_unique_fields=values_for_unique_fields,
            model_manager=fake_metric_manager,
        )

        # Then
        # The ID/pk of the matching record
        # is added to the "pk" key in the returned dict
        assert returned_values_for_unique_fields["pk"] == fake_metric.pk

        # The "fields" nested dict remains unchanged
        assert (
            returned_values_for_unique_fields["fields"]
            == values_for_unique_fields["fields"]
        )

        # The "mapped_fields" nested dict remains unchanged
        assert (
            returned_values_for_unique_fields["mapped_fields"]
            == values_for_unique_fields["mapped_fields"]
        )

    def test_add_pk_as_primary_field_on_incoming_dto(
        self, example_incoming_headline_dto: IncomingHeadlineDTO
    ):
        """
        Given an `IncomingBaseDTO` and fields which map to a set of attributes
        When `_add_pk_as_primary_field_on_incoming_dto()`
            is called from an instance of `Reader`
        Then the primary field on the `IncomingBaseDTO` is set with an ID/pk
        """
        # Given
        unique_value_groups_from_incoming_dtos = [
            {
                "pk": 1,
                "fields": {"parent_theme": "infectious_disease"},
                "mapped_fields": {"name": "infectious_disease"},
            }
        ]
        incoming_dto = example_incoming_headline_dto
        primary_field = "parent_theme"
        fields = {"parent_theme": "name"}

        reader = Reader(data=mock.Mock())

        # When
        reader._add_pk_as_primary_field_on_incoming_dto(
            unique_value_groups_from_incoming_dtos=unique_value_groups_from_incoming_dtos,
            primary_field=primary_field,
            incoming_dto=incoming_dto,
            fields=fields,
        )

        # Then
        assert (
            getattr(incoming_dto, primary_field)
            == unique_value_groups_from_incoming_dtos[0]["pk"]
        )

    @mock.patch.object(Reader, "_add_pk_as_primary_field_on_incoming_dto")
    def test_add_pk_as_primary_field_to_all_incoming_dtos_delegates_call(
        self, spy_add_pk_as_primary_field_on_incoming_dto: mock.MagicMock
    ):
        """
        Given a list of mocked incoming DTOs
        When `_add_pk_as_primary_field_to_all_incoming_dtos()`
            is called from an instance of `Reader`
        Then the call is delegated to `_add_pk_as_primary_field_on_incoming_dto()`
            for each of the DTOs
        """
        # Given
        mocked_incoming_dtos = [mock.Mock() for _ in range(3)]
        mocked_unique_value_groups_from_incoming_dtos = mock.Mock()
        mocked_primary_field = mock.Mock()
        mocked_fields = mock.Mock()

        reader = Reader(data=mock.Mock())

        # When
        reader._add_pk_as_primary_field_to_all_incoming_dtos(
            incoming_dtos=mocked_incoming_dtos,
            unique_value_groups_from_incoming_dtos=mocked_unique_value_groups_from_incoming_dtos,
            primary_field=mocked_primary_field,
            fields=mocked_fields,
        )

        # Then
        expected_calls = [
            mock.call(
                incoming_dto=mocked_incoming_dto,
                unique_value_groups_from_incoming_dtos=mocked_unique_value_groups_from_incoming_dtos,
                primary_field=mocked_primary_field,
                fields=mocked_fields,
            )
            for mocked_incoming_dto in mocked_incoming_dtos
        ]
        spy_add_pk_as_primary_field_on_incoming_dto.assert_has_calls(
            expected_calls, any_order=True
        )
