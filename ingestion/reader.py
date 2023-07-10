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
        incoming_df: pd.DataFrame,
        fields: dict[str, str],
        model_manager: Manager,
    ):
        """
        Maintain the individual models that are used in the normalisation of the Core source file
        New values in the source file will be added to the model
        All rows in the source file will get changed from the supplied cell
        value (eg infectious_disease) to the pk for that value. eg 1

        Args:
            incoming_df: This is the entire source file in a DataFrame
            fields: Dictionary of the model field names and the names of the relevant columns in the source file
            model_manager: The model we want to maintain

        Returns:
            incoming_df with the relevant column changed to the primary keys for that model
            So, if the column cotained values like 'infectious_disease' it'll now be, say, 1 (the primary key for 'infectious_disease')
        """

        # From the source file, pull out the unique list of row values for this particular model
        incoming_data: pd.DataFrame = incoming_df[fields.keys()].drop_duplicates()

        # From the model, pull back the existing records along with their pks
        existing_data: pd.DataFrame = pd.DataFrame.from_records(
            model_manager.all().values("pk", *fields.values())
        )

        if existing_data.empty:
            existing_data: pd.DataFrame = pd.DataFrame(columns=list(fields.values()))

        # Left join on incoming_data & existing_data dataframes
        df: pd.DataFrame = pd.merge(
            left=incoming_data,
            right=existing_data,
            how="left",
            left_on=list(fields.keys()),
            right_on=list(fields.values()),
            indicator=True,
        )

        # left_only = those values in the source file which are not present the Model. So, these are new ones
        new_data: list[dict[str, str]] = (
            df.loc[df["_merge"] == "left_only"][fields.keys()]
            .rename(columns=fields)
            .to_dict("records")
        )

        # Add the new values to the model and pull back the pk for them.
        new_records: list[dict[str, str]] = [
            {**{"pk": model_manager.create(**data).pk}, **data} for data in new_data
        ]

        # Turn the new records into a dataframe
        added_data: pd.DataFrame = pd.DataFrame(new_records)

        # Add them onto the end of the data that we already had
        all_data: pd.DataFrame = pd.concat([existing_data, added_data])

        # Now join this back onto the original dataframe.
        # So, we're joining the pk and the relevant fields for this model onto the original dataframe
        df = pd.merge(
            left=incoming_df,
            right=all_data,
            how="inner",
            left_on=list(fields.keys()),
            right_on=list(fields.values()),
        )

        # Drop the original column(s) as we're now using the primary keys and not the text representation of them
        # Drop the model field names too (were only here to make debugging easier)
        df = df.drop(columns=[*list(fields.items())[0], *fields.values()])

        # Rename the new columns back to what they are in the source file.
        # So for the parent theme model we are changing it from pk back to parent_theme
        df = df.rename(columns={"pk": list(fields.keys())[0]})

        # At this point the rows for the parent_theme column for example have been changed
        # from "infectious_disease" to, say, 1
        # ie. the Foreign Key for "infectious_disease" in the Theme model.
        return df

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
        return dataframe[dataframe["metric_value"].notnull()]

    def _cast_int_type_on_columns_with_foreign_keys(
        self, dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        dataframe[self.supporting_model_column_names] = dataframe[
            self.supporting_model_column_names
        ].applymap(int)
        return dataframe

    @staticmethod
    def _create_named_tuple_iterable_from(dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.itertuples(index=False)
