import json

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from ingestion.data_transfer_models.incoming import IncomingBaseDTO
from ingestion.metrics_interfaces.interface import MetricsAPIInterface

COLUMN_NAMES_WITH_FOREIGN_KEYS: list[str] = [
    "parent_theme",
    "child_theme",
    "topic",
    "geography",
    "geography_type",
    "metric_group",
    "metric",
    "stratum",
    "age",
]

SEX_OPTIONS = {"male": "M", "female": "F", "all": "ALL"}

TIME_PERIOD_ENUM = MetricsAPIInterface.get_time_period_enum()


class Reader:
    def __init__(self, data):
        self.data = data

    def maintain_model(
        self,
        incoming_dtos: list[IncomingBaseDTO],
        fields: dict[str, str],
        model_manager: Manager,
    ) -> list[IncomingBaseDTO]:
        """Update the individual supporting core model by inserting new records as necessary.

        Notes:
            The following steps are taken:
                1) Get set of unique values from `incoming_dtos`
                2) Get existing records for model
                3) Add IDs from queried records to unique values set
                4) Extract unique values which do not have a corresponding record
                5) Create new records for extracted unique values from step 5
                6) Add IDs from queried records to unique values dicts.
                   This is a repeat of step 3 to capture newly created records
                7) Loop over `incoming_dtos` and add the IDs in place
                   for the current model in question

        Args:
            incoming_dtos: List of DTOs which are to be processed
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            A list of DTOs which are to be processed.
            In doing so, the relevant supporting model attributes
            on each DTO will be changed so that their
            original text representation has been replaced
            with the corresponding database record IDs

        """
        uniques_value_groups: set[
            tuple[tuple[str, str]]
        ] = self._get_unique_value_groups_from_incoming_dtos_for_model(
            incoming_dtos=incoming_dtos, fields=fields
        )

        unique_value_groups_from_incoming_dtos: list[
            dict[str, dict[str, str] | None]
        ] = self._convert_unique_value_groups(unique_value_groups=uniques_value_groups)

        primary_field: str = list(fields.keys())[0]

        (
            unique_value_groups_from_incoming_dtos,
            values_for_new_records,
        ) = self.map_existing_ids_onto_unique_value_groups(
            unique_value_groups_from_incoming_dtos=unique_value_groups_from_incoming_dtos,
            fields=fields,
            model_manager=model_manager,
        )

        self._create_records_for_new_values(
            values_for_new_records=values_for_new_records, model_manager=model_manager
        )

        (
            unique_value_groups_from_incoming_dtos,
            _,
        ) = self.map_existing_ids_onto_unique_value_groups(
            unique_value_groups_from_incoming_dtos=unique_value_groups_from_incoming_dtos,
            fields=fields,
            model_manager=model_manager,
        )

        self._add_pk_as_primary_field_to_all_incoming_dtos(
            incoming_dtos=incoming_dtos,
            unique_value_groups_from_incoming_dtos=unique_value_groups_from_incoming_dtos,
            primary_field=primary_field,
            fields=fields,
        )

        return incoming_dtos

    def _add_pk_as_primary_field_to_all_incoming_dtos(
        self,
        incoming_dtos: list[type[IncomingBaseDTO]],
        unique_value_groups_from_incoming_dtos,
        primary_field: str,
        fields: dict[str, str],
    ) -> None:
        """Adds the pk from the `unique_value_groups_from_incoming_dtos` onto the `primary_field` of each `incoming_dto`

        Args:
            incoming_dtos: List of DTOs to add IDs/pks onto.
            unique_value_groups_from_incoming_dtos: A list of dicts
                whereby each dict encapsulates 1 of the given unique value groups
                along with a "pk" key value pair
            primary_field: The main field for the model to add the ID/pk to.
                E.g. for the `Theme` model, this will be `parent_theme`
            fields: Dict of the model field names and the names
                of the relevant attributes from the source file.
                E.g. For the `Theme` model,
                the `fields` argument will be
                {'parent_theme': 'name'}

        Returns:
            List of dicts whereby each dict encapsulates
            1 of the unique value groups
            along with a "pk" key value pair

        """
        for incoming_dto in incoming_dtos:
            self._add_pk_as_primary_field_on_incoming_dto(
                incoming_dto=incoming_dto,
                unique_value_groups_from_incoming_dtos=unique_value_groups_from_incoming_dtos,
                primary_field=primary_field,
                fields=fields,
            )

    @staticmethod
    def _add_pk_as_primary_field_on_incoming_dto(
        incoming_dto: type[IncomingBaseDTO],
        unique_value_groups_from_incoming_dtos,
        primary_field: str,
        fields: dict[str, str],
    ) -> None:
        """Adds the pk from the `unique_value_groups_from_incoming_dtos` onto the `primary_field` of the `incoming_dto`

        Args:
            incoming_dto: The DTO to add the pk onto.
            unique_value_groups_from_incoming_dtos: A list of dicts
                whereby each dict encapsulates 1 of the given unique value groups
                along with a "pk" key value pair
            primary_field: The main field for the model to add the ID/pk to.
                E.g. for the `Theme` model, this will be `parent_theme`
            fields: Dict of the model field names and the names
                of the relevant attributes from the source file.
                E.g. For the `Theme` model,
                the `fields` argument will be
                {'parent_theme': 'name'}

        Returns:
            List of dicts whereby each dict encapsulates
            1 of the unique value groups
            along with a "pk" key value pair

        """
        try:
            available_matching_data = next(
                unique_value_group
                for unique_value_group in unique_value_groups_from_incoming_dtos
                if all(
                    getattr(incoming_dto, field) == unique_value_group["fields"][field]
                    for field in fields
                )
            )
        except StopIteration:
            return

        setattr(incoming_dto, primary_field, available_matching_data["pk"])

    def map_existing_ids_onto_unique_value_groups(
        self,
        unique_value_groups_from_incoming_dtos: list[dict[str, dict[str, str] | None]],
        fields: dict[str, str],
        model_manager: Manager,
    ) -> tuple[dict[str, dict[str, str] | None], list[dict[str, str]]]:
        """Maps any existing ID/pks to the corresponding value groups. Gathers non-existent values seperately.

        Args:
            unique_value_groups_from_incoming_dtos: A list of dicts
                whereby each dict encapsulates 1 of the given unique value groups
                along with a "pk" key value pair
            fields: Dict of the model field names and the names
                of the relevant attributes from the source file.
                E.g. For the `Theme` model,
                the `fields` argument will be
                {'parent_theme': 'name'}
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            Tuple containing:
            1) List of dicts whereby each dict encapsulates
                1 of the unique value groups
                along with a "pk" key value pair
            2) A list of fields which could not be matched
                and therefore require new records to be created
                for each of them

        """
        values_for_new_records = []

        for values_for_unique_fields in unique_value_groups_from_incoming_dtos:
            values_for_unique_fields = self.map_fields_for_unique_values(
                fields_for_unique_values=values_for_unique_fields,
                fields=fields,
            )

            try:
                values_for_unique_fields = self._add_pk_to_values_for_unique_fields(
                    values_for_unique_fields=values_for_unique_fields,
                    model_manager=model_manager,
                )
            except ObjectDoesNotExist:
                values_for_new_records.append(values_for_unique_fields["mapped_fields"])

        return unique_value_groups_from_incoming_dtos, values_for_new_records

    @staticmethod
    def _add_pk_to_values_for_unique_fields(
        values_for_unique_fields: dict[str, dict[str, str]], model_manager: Manager
    ) -> dict[str, int | dict[str, str]]:
        """Populates the "pk" key-pair from the record via the `model_manager` with the "mapped_fields" key-value pair

        Args:
            values_for_unique_fields: Dict which encapsulates
                a specific unique value group
                along with a "pk" key value pair
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            Dict which encapsulates a specific unique value group
            along with a "pk" key value pair populated via the model manager.

        Raises:
            `ObjectDoesNotExist`: If no existing record
                can be matched with the "mapped_fields" nested dict

        """
        existing_record = model_manager.get(**values_for_unique_fields["mapped_fields"])
        values_for_unique_fields["pk"] = existing_record.pk
        return values_for_unique_fields

    @staticmethod
    def map_fields_for_unique_values(
        fields_for_unique_values: dict[str, dict[str, str] | None],
        fields: dict[str, str],
    ) -> dict[str, dict[str, str] | None]:
        """Maps the given `fields` on the `fields_for_unique_values`

        Examples:
            >>> fields_for_unique_values = {'pk': None, 'fields': {'parent_theme': 'infectious_disease'}}
            >>> fields = {"parent_theme": "name"}
            >>> map_fields_for_unique_values(fields_for_unique_values, fields)
            {'pk': None, 'fields': {'parent_theme': 'infectious_disease'}, 'mapped_fields': {'name': 'infectious_disease'}}

        Args:
            fields_for_unique_values: Dict which encapsulates
                a specific unique value group
                along with a "pk" key value pair
            fields: Dict of the model field names and the names
                of the relevant attributes from the source file.
                E.g. For the `Theme` model,
                the `fields` argument will be
                {'parent_theme': 'name'}

        Returns:
            Dict containing a key of "mapped_fields" which
            whereby the key is the corresponding column name of the table

        """
        unmapped_fields = fields_for_unique_values["fields"]

        fields_for_unique_values["mapped_fields"] = {
            fields.get(f): unmapped_fields[f] for f in unmapped_fields
        }

        return fields_for_unique_values

    def _create_records_for_new_values(
        self, values_for_new_records: list[dict[str, str]], model_manager: Manager
    ) -> None:
        """Creates new records via the `model_manager`

        Args:
            values_for_new_records: A list of dicts containing
                the field values required for each new record
                in the current model.
                E.g. if the `Theme` model is being updated
                for 2 new records, one might expect the following:
                    [{"name": "infectious_disease"}, {"name": "allergies"}]
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            None

        """
        for values_for_new_record in values_for_new_records:
            self._create_record(
                values_for_new_record=values_for_new_record, model_manager=model_manager
            )

    @staticmethod
    def _convert_unique_value_groups(
        unique_value_groups: set[tuple[tuple[str, str]]]
    ) -> list[dict[str, dict[str, str] | None]]:
        """Converts the `unique_value_groups` into a list of dicts which each have a "pk" key value pair

        Examples:
            >>> unique_value_groups = {(("parent_theme", "infectious_disease"),)}
            >>> _convert_unique_value_groups_to_dict(unique_value_groups)
            [{'pk': None, 'fields': {'parent_theme': 'infectious_disease'}}]

        Args:
            unique_value_groups: The unique values for the current fields.
                E.g. {(("parent_theme", "infectious_disease"),)}

        Returns:
            A list of dicts whereby each dict encapsulates
            1 of the given `unique_value_groups`
            along with a "pk" key value pair

        """
        processed_unique_value_groups = []
        for unique_value_group in unique_value_groups:
            unique_values_with_pk = {
                "pk": None,
                "fields": {
                    field_name: field_value
                    for field_name, field_value in unique_value_group
                },
            }
            processed_unique_value_groups.append(unique_values_with_pk)

        return processed_unique_value_groups

    @staticmethod
    def _create_record(
        values_for_new_record: dict[str, str], model_manager: type[Manager]
    ) -> None:
        """Creates a new individual record via the `model_manager`

        Args:
            values_for_new_record: A dict containing the field values
                required for the new record in the current model.
                E.g. if the `Theme` model is being updated,
                one might expect the following:
                    {"name": "infectious_disease"}
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            None

        """
        model_manager.create(**values_for_new_record)

    @staticmethod
    def _get_unique_value_groups_from_incoming_dtos_for_model(
        incoming_dtos: list[IncomingBaseDTO], fields: dict[str, str]
    ) -> set[tuple[tuple[str, str]]]:
        """Pulls all unique values from the given `incoming_dtos` for the `fields`

        Examples:
            If the `fields` of {"parent_theme": "name"} is provided.
            Then this method will return all the values
            for the field combination dictated by the keys.
            In this case, the "parent_theme" would return "infectious_disease"
            >>> _get_unique_values_from_incoming_dtos_for_model(
            >>>        incoming_dtos=incoming_dtos,
            >>>        fields={"parent_theme": "name"}
            >>> )
                {(("parent_theme", "infectious_disease"),)}

        Args:
            incoming_dtos: List of DTOs from which all unique values
                related to the given `fields` will be extracted
            fields: Dict of the model field names and the names
                of the relevant attributes from the source file.
                E.g. For the `Theme` model,
                the `fields` argument will be
                {'parent_theme': 'name'}

        Returns:
            A set containing nested tuples representing
            all groups of unique values
            as dictated by the given `fields` dict

        """
        unique_value_groups = set()
        for incoming_dto in incoming_dtos:
            values_from_dtos: tuple[tuple[str, str]] = tuple(
                tuple((field, getattr(incoming_dto, field))) for field in fields
            )
            unique_value_groups.add(values_from_dtos)

        return unique_value_groups

    @staticmethod
    def _get_existing_records_for_values(
        fields: dict[str, str], model_manager: type[Manager]
    ) -> QuerySet:
        """Gets the IDs of all existing records via the given `model_manager`

        Notes:
            If there are no existing matching records,
            then an empty `QuerySet` is returned

        Args:
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            A `QuerySet` which contains the ID/pks of any
            existing records which are relevant
            to the given `fields`

        """
        return model_manager.all().values("pk", *fields.values())

    def post_process_incoming_dtos(
        self, incoming_dtos: list[IncomingBaseDTO]
    ) -> list[IncomingBaseDTO]:
        """Parse the given `incoming_dtos` by casting expected values.

        Notes:
            This will handle the following post-processing steps:
            1)  Removes all DTOs in the which have None as the `metric_value` attribute
            2)  Casts the `sex` attribute in each DTO to an expected value
            3)  Casts the `metric_frequency` attribute in each DTO to an expected value

        Args:
            incoming_dtos: List of DTOs which are to be processed

        Returns:
            A list of DTOs which have undergone the final processing steps
            before they can be consumed by the data layer of the application

        """
        incoming_dtos: list[
            IncomingBaseDTO
        ] = self._remove_any_dtos_with_none_metric_value(incoming_dtos=incoming_dtos)

        incoming_dtos: list[
            IncomingBaseDTO
        ] = self._cast_sex_on_dtos_to_expected_values(incoming_dtos=incoming_dtos)

        try:
            incoming_dtos: list[
                IncomingBaseDTO
            ] = self._cast_metric_frequency_on_dtos_to_expected_values(
                incoming_dtos=incoming_dtos
            )
        except AttributeError:
            # The headline data does not contain the "metric_frequency" column
            # so this can be safely bypassed
            pass

        return incoming_dtos

    @staticmethod
    def _remove_any_dtos_with_none_metric_value(
        incoming_dtos: list[IncomingBaseDTO],
    ) -> list[IncomingBaseDTO]:
        """Removes all DTOs in the `incoming_dtos` which have None as the `metric_value` attribute

        Args:
            incoming_dtos: List of DTOs which are to be processed

        Returns:
            A list of DTOs with no None values
            as the `metric_value` attribute

        """
        return [
            incoming_dto
            for incoming_dto in incoming_dtos
            if incoming_dto.metric_value is not None
        ]

    @staticmethod
    def _cast_sex_on_dtos_to_expected_values(
        incoming_dtos: list[IncomingBaseDTO],
    ) -> list[IncomingBaseDTO]:
        """Casts the `sex` attribute in each DTO to one of the expected values

        Notes:
            Expected values are one of the following:
            1) "ALL"    - All genders with no filtering applied
            2) "F"      - Females
            3) "M"      - Males

        Args:
            incoming_dtos: List of DTOs which are to be processed

        Returns:
            A list of DTOs where the `sex` attribute
            on each DTO has been parsed with the expected values

        """

        def _cast_sex_value(value: str) -> str:
            return SEX_OPTIONS.get(value.lower(), "ALL")

        for incoming_dto in incoming_dtos:
            incoming_dto.sex = _cast_sex_value(incoming_dto.sex)

        return incoming_dtos

    @staticmethod
    def _cast_metric_frequency_on_dtos_to_expected_values(
        incoming_dtos: list[IncomingBaseDTO],
    ) -> list[IncomingBaseDTO]:
        """Casts the `metric_frequency` attribute in each DTO to one of the expected values

        Notes:
            Expected values are dictated by the `TimePeriod` enum

        Args:
            incoming_dtos: List of DTOs which are to be processed

        Returns:
            A list of DTOs where the "metric_frequency" attribute
            on each DTO has been parsed with the expected values

        """

        def _cast_metric_frequency_value(value: str) -> str:
            return TIME_PERIOD_ENUM[value.title()].value

        for incoming_dto in incoming_dtos:
            incoming_dto.metric_frequency = _cast_metric_frequency_value(
                incoming_dto.metric_frequency
            )

        return incoming_dtos

    @property
    def supporting_model_column_names(self) -> list[str]:
        """Gets a list of column names, for each of the supporting models

        Notes:
            Supporting models are those which
            link to the main core models via foreign keys.
            E.g. the topic of `COVID-19` would be
            represented by the supporting model `Topic`
            which would have the name of `COVID-19`

        Returns:
            A list of strings, for each column name
            which should be represented as a supporting model

        """
        return COLUMN_NAMES_WITH_FOREIGN_KEYS

    def open_source_file(self) -> list[dict[str, str | int | float]]:
        """Opens the JSON `data` as an object

        Returns:
            An object containing the raw JSON data

        """
        lines = self.data.readlines()[0]
        return json.loads(lines)
