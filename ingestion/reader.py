from typing import Any, Iterable

import pandas as pd
from django.db.models.manager import Manager

from metrics.data.enums import TimePeriod

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

frequency = {
    "weekly": TimePeriod.Weekly.value,
    "daily": TimePeriod.Daily.value,
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
        """
        Maintain the individual models that are used in the normalisation of the Core source file
        New values in the source file will be added to the model
        All rows in the source file will get changed from the supplied cell
        value (eg infectious_disease) to the pk for that value. eg 1

        Args:
            incoming_dataframe: This is the entire source file in a DataFrame
            fields: Dictionary of the model field names and the names of the relevant columns in the source file
            model_manager: The model we want to maintain

        Returns:
            incoming_df with the relevant column changed to the primary keys for that model
            So, if the column cotained values like 'infectious_disease' it'll now be, say, 1 (the primary key for 'infectious_disease')
        """
        incoming_data = self._get_unique_values_from_dataframe_for_keys(
            dataframe=incoming_dataframe, fields=fields
        )

        existing_data: pd.DataFrame = self._get_existing_records_for_values(
            fields=fields, model_manager=model_manager
        )

        dataframe: pd.DataFrame = self._left_join_merge(
            left_data=incoming_data, right_data=existing_data, fields=fields
        )

        new_data: list[dict[str, str]] = self._get_new_data_in_source(
            dataframe=dataframe, fields=fields
        )

        # Add the new values to the model and pull back the pk for them.
        new_records: list[dict[str, str]] = [
            {**{"pk": model_manager.create(**data).pk}, **data} for data in new_data
        ]

        added_data = self._concatenate_new_records(
            dataframe=existing_data, new_records=new_records
        )

        dataframe = self._inner_merge(
            left_data=incoming_dataframe, right_data=added_data, fields=fields
        )

        dataframe = self._drop_text_representations_of_columns(
            dataframe=dataframe, fields=fields
        )
        dataframe = self._rename_columns_to_original_names(
            dataframe=dataframe, fields=fields
        )

        # At this point the rows for the parent_theme column for example have been changed
        # from "infectious_disease" to, say, 1
        # ie. the Foreign Key for "infectious_disease" in the Theme model.
        return dataframe

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
            fields: The fields associated with the
                model currently being updated.
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
            fields: The fields associated with the
                model currently being updated.
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
        return dataframe.rename(columns={"pk": list(fields.keys())[0]})

    @staticmethod
    def _drop_text_representations_of_columns(
        dataframe: pd.DataFrame, fields: dict[str, str]
    ) -> pd.DataFrame:
        return dataframe.drop(columns=[*list(fields.items())[0], *fields.values()])

    @staticmethod
    def _left_join_merge(left_data, right_data, fields: dict[str, str]) -> pd.DataFrame:
        return pd.merge(
            left=left_data,
            right=right_data,
            how="left",
            left_on=list(fields.keys()),
            right_on=list(fields.values()),
            indicator=True,
        )

    @staticmethod
    def _inner_merge(left_data, right_data, fields: dict[str, str]) -> pd.DataFrame:
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
        return (
            dataframe.loc[dataframe["_merge"] == "left_only"][fields.keys()]
            .rename(columns=fields)
            .to_dict("records")
        )

    @staticmethod
    def _concatenate_new_records(
        dataframe: pd.DataFrame, new_records: list[dict[str, str]]
    ) -> pd.DataFrame:
        # Turn the new records into a dataframe
        added_data: pd.DataFrame = pd.DataFrame(new_records)

        # Add them onto the end of the data that we already had
        return pd.concat([dataframe, added_data])

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
        return self._create_named_tuple_iterable_from(dataframe=dataframe)

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
    def _create_named_tuple_iterable_from(dataframe: pd.DataFrame) -> Iterable[Any]:
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
