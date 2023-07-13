from typing import Any, Iterable

import pandas as pd
from django.db.models.manager import Manager

from ingestion.metrics_interfaces.interface import MetricsAPIInterface

COLUMN_NAMES_WITH_FOREIGN_KEYS: list[str, ...] = [
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

sex_options = {"male": "M", "female": "F", "all": "ALL"}

TIME_PERIOD_ENUM = MetricsAPIInterface.get_time_period_enum()
frequency = {
    "weekly": TIME_PERIOD_ENUM.Weekly.value,
    "daily": TIME_PERIOD_ENUM.Daily.value,
}


class Reader:
    def __init__(self, data):
        self.data = data

    def maintain_model(
        self,
        incoming_dataframe: pd.DataFrame,
        fields: dict[str, str],
        model_manager: Manager,
    ):
        """Update the individual supporting core model by inserting new records as necessary.

        Notes:
            As the supporting core models are created and queried for,
            the original text representations are replaced by their
            corresponding ID/pks.
            E.g. If the original column value for `parent_theme` is
                "infectious_disease". This will be replaced by `123`
                i.e. the foreign key for the `Theme` model
                which has the name "infectious_disease"

        Args:
            incoming_dataframe: The raw `DataFrame` opened from the source data file
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            The `DataFrame` with the relevant supporting model columns
            renamed so that their original text representation has been
            replaced with the corresponding database record IDs

        """
        incoming_data = self._get_unique_values_from_dataframe_for_keys(
            dataframe=incoming_dataframe, fields=fields
        )
        existing_data: pd.DataFrame = self._get_existing_records_for_values(
            fields=fields, model_manager=model_manager
        )
        dataframe: pd.DataFrame = self._merge_left_join(
            left_data=incoming_data, right_data=existing_data, fields=fields
        )

        new_data: list[dict[str, str]] = self._get_new_data_in_source(
            dataframe=dataframe, fields=fields
        )
        new_records_data: list[dict[str, str]] = self._create_new_records_data(
            new_data=new_data, model_manager=model_manager
        )
        added_data = self._concatenate_new_records(
            dataframe=existing_data, new_records_data=new_records_data
        )

        dataframe = self._merge_inner(
            left_data=incoming_dataframe, right_data=added_data, fields=fields
        )
        dataframe = self._drop_text_representations_of_columns(
            dataframe=dataframe, fields=fields
        )
        dataframe = self._rename_columns_to_original_names(
            dataframe=dataframe, fields=fields
        )

        return dataframe

    @staticmethod
    def _create_new_records_data(
        new_data: list[dict[str, str]], model_manager: type[Manager]
    ) -> list[dict[str, str]]:
        """Creates new records via the `model_manager` and rebuilds a dict containing the new ID/pks

        Args:
            new_data: A list of dicts containing the fields
                required for each of the new records
                required for the current model being updated.
                E.g. if the `Theme` model is being updated,
                one might expect the following:
                    [{"name": "infectious_disease"}]
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            A list of dictionaries with new values replaced by
            the corresponding ID/pk for the new database records

        """
        return [
            {**{"pk": model_manager.create(**data).pk}, **data} for data in new_data
        ]

    @staticmethod
    def _get_unique_values_from_dataframe_for_keys(
        dataframe: pd.DataFrame, fields: dict[str, str]
    ) -> pd.DataFrame:
        """Pulls all the values in the given `dataframe` for the field keys.

        Examples:
            If the `fields` of {"parent_theme": "name"} is provided.
            Then this method will return all the values
            for the field combination dictated by the keys.
            In this case, the "parent_theme" would return "infectious_disease"
            >>> _get_unique_values_for_keys(dataframe=dataframe, fields={"parent_theme": "name"})
                         parent_theme
                0  infectious_disease

        Args:
            dataframe: The initial opened `dataframe`
                prior to any processing steps
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}
        Returns:
            A new `DataFrame` which contains only the values
            speicific to the keys of the `fields` dict

        """
        return dataframe[fields.keys()].drop_duplicates()

    @staticmethod
    def _get_existing_records_for_values(
        fields: dict[str, str], model_manager: type[Manager]
    ) -> pd.DataFrame:
        """Gets the IDs of all existing records via the given `model_manager`

        Notes:
            If there are no existing matching records,
            then an empty `DataFrame` is returned
            which is set with the correct column names
            via the values of the `fields` dict

        Args:
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}
            model_manager: The model manager associated
                with the model currently being updated.

        Returns:
            A new `DataFrame` which contains the ID/pks of any
            existing records which are relevant to the given
            `fields`.

        """
        existing_data: pd.DataFrame = pd.DataFrame.from_records(
            model_manager.all().values("pk", *fields.values())
        )

        if existing_data.empty:
            return pd.DataFrame(columns=list(fields.values()))

        return existing_data

    @staticmethod
    def _rename_columns_to_original_names(
        dataframe: pd.DataFrame, fields: dict[str, str]
    ) -> pd.DataFrame:
        """Renames the "pk" column and replaces it with the first value of the given `fields`

        Notes:
            At this point the rows for the supporting model columns
            have been changed.
            E.g. The original column value for `parent_theme` is
                "infectious_disease". This will be replaced by `123`
                i.e. the foreign key for the `Theme` model
                which has the name "infectious_disease"

        Args:
            dataframe: The `DataFrame` to be processed
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}

        Returns:
            The `DataFrame` with the relevant supporting model columns
            renamed so that their original text representation has been
            replaced with the corresponding database record IDs

        """
        return dataframe.rename(columns={"pk": list(fields.keys())[0]})

    @staticmethod
    def _drop_text_representations_of_columns(
        dataframe: pd.DataFrame, fields: dict[str, str]
    ) -> pd.DataFrame:
        """Drop the relevant columns with text representations as they will be replaced by ID/pks values

        Args:
            dataframe: The `DataFrame` to be processed
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}

        Returns:
            The `DataFrame` with the relevant supporting model columns dropped

        """
        return dataframe.drop(columns=[*list(fields.items())[0], *fields.values()])

    @staticmethod
    def _merge_left_join(
        left_data: pd.DataFrame, right_data: pd.DataFrame, fields: dict[str, str]
    ) -> pd.DataFrame:
        """Left merge the `left_data` and `right_data` dataframes

        Args:
            left_data: The incoming `DataFrame`
            right_data: The right side `DataFrame` to be merged in
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}

        Returns:
            The merged `DataFrame`

        """
        return pd.merge(
            left=left_data,
            right=right_data,
            how="left",
            left_on=list(fields.keys()),
            right_on=list(fields.values()),
            indicator=True,
        )

    @staticmethod
    def _merge_inner(
        left_data: pd.DataFrame, right_data: pd.DataFrame, fields: dict[str, str]
    ) -> pd.DataFrame:
        """Inner merge the `left_data` and `right_data` dataframes

        Args:
            left_data: The incoming `DataFrame`
            right_data: The right side `DataFrame` to be merged in
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}

        Returns:
            The merged `DataFrame`

        """
        return pd.merge(
            left=left_data,
            right=right_data,
            how="inner",
            left_on=list(fields.keys()),
            right_on=list(fields.values()),
        )

    @staticmethod
    def _get_new_data_in_source(
        dataframe: pd.DataFrame, fields: dict[str, str]
    ) -> list[dict[str, str]]:
        """Gets the field keys of the left side of the pre-merged `dataframe`

        Args:
            dataframe: The `DataFrame` to be processed
            fields: Dict of the model field names and the names
                of the relevant columns from the source file.
                E.g. For the `Theme` model,
                the `fields` argument is likely to be
                {'parent_theme': 'name'}

        Returns:
            A list of dicts containing the fields
            required for each of the new records
            required for the current model being updated.
            E.g. if the `Theme` model is being updated,
            one might expect the following:
                [{"name": "infectious_disease"}]

        """
        return (
            dataframe.loc[dataframe["_merge"] == "left_only"][fields.keys()]
            .rename(columns=fields)
            .to_dict("records")
        )

    @staticmethod
    def _concatenate_new_records(
        dataframe: pd.DataFrame, new_records_data: list[dict[str, str]]
    ) -> pd.DataFrame:
        """Turns the `new_records_data` into a `DataFrame` and concatenates it to the given `dataframe`

        Args:
            dataframe: The `DataFrame` to be processed
            new_records_data: A list of dicts containing
                the fields for each new record with their
                ID/pks included.
                E.g. [{'name': 'infectious_disease', 'pk': 1}]

        Returns:
            The updated `DataFrame` including rows representing
            the updated supporting models

        """
        new_record_dataframe: pd.DataFrame = pd.DataFrame(new_records_data)

        return pd.concat([dataframe, new_record_dataframe])

    def parse_dataframe_as_iterable(self, dataframe) -> pd.DataFrame:
        """Convert the given `dataframe` to an iterable

        Notes:
            This will handle the following pre-processing steps:
            1)  Remove all rows with `NaN` in the `metric_value` column
            2)  Cast all columns with foreign keys to int types
            3)  Create an easy to use iterable from the dataframe

            This method also assumes supporting model columns
            have been replaced with database record IDS.
            For example, if the dataframe showed `COVID-19`
            for the `topic` field of each entry.
            Then the dataframe should instead show `123`,
            which should be the ID/pk of the `Topic` model
            which has the name `COVID-19`.

        Args:
            dataframe: The incoming `DataFrame` which has replaced
                the text representation of supporting models
                with corresponding database record IDs

        Returns:
            A list of `HeadlineDTO` instances which are
            enriched with all the data required to
            insert a new database record in the table

        """
        dataframe: pd.DataFrame = self._remove_rows_with_nan_metric_value(
            dataframe=dataframe
        )
        dataframe: pd.DataFrame = self._cast_int_type_on_columns_with_foreign_keys(
            dataframe=dataframe
        )
        return self._create_named_tuple_iterable(dataframe=dataframe)

    @staticmethod
    def _remove_rows_with_nan_metric_value(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Removes all rows in the `dataframe` which have NaN in the `metric_value` column

        Args:
            dataframe: The `DataFrame` to be processed

        Returns:
            A `DataFrame` with no NaN values
            in the `metric_value` column of its rows

        """
        return dataframe[dataframe["metric_value"].notnull()]

    def _cast_int_type_on_columns_with_foreign_keys(
        self, dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        """Casts the supporting model columns to int types

        Notes:
            A previous processing step would have
            set available IDs of corresponding model records
            on the corresponding model columns.
            For example, if the dataframe showed `COVID-19`
            for the `topic` field of each entry.
            Then the dataframe will be altered to instead
            show `123`, which should be the ID/pk
            of the `Topic` model which has the name `COVID-19`.

        Args:
            dataframe: The `DataFrame` to be processed

        Returns:
            A `DataFrame` where all supporting model column
            values have been cast as integers

        """
        dataframe[self.supporting_model_column_names] = dataframe[
            self.supporting_model_column_names
        ].applymap(int)
        return dataframe

    @staticmethod
    def _create_named_tuple_iterable(dataframe: pd.DataFrame) -> Iterable[Any]:
        """Takes the given `dataframe` and returns an iterable of named tuples

        Notes:
            Each named tuple in the returned iterable
            contains a field for each of the column names

        Args:
            dataframe: The final dataframe with all of
                its processing steps having been completed

        Returns:
            An object to iterate over named tuples
            for each row in the DataFrame

        """
        return dataframe.itertuples(index=False)

    @property
    def supporting_model_column_names(self) -> list[str, ...]:
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

    def open_data_as_dataframe(self) -> pd.DataFrame:
        """Opens the JSON `data` as a dataframe

        Returns:
            A dataframe containing the raw JSON data

        """
        return pd.read_json(self.data)
