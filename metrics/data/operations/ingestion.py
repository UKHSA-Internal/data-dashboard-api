from typing import NamedTuple, Type

import pandas as pd
from django.db.models import Manager
from pydantic import BaseModel

from metrics.data.enums import TimePeriod
from metrics.data.models import core_models


class HeadlineDTO(BaseModel):
    theme: str | int
    sub_theme: str | int
    topic: str | int
    metric_group: str | int
    metric: str | int
    geography_type: str | int
    geography: str | int
    age: str | int
    sex: str
    stratum: str | int

    period_start: str
    period_end: str
    refresh_date: str

    metric_value: float


class FieldsAndModelManager(NamedTuple):
    fields: dict[str, str]
    model_manager: Type[Manager]


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


DEFAULT_THEME_MANAGER = core_models.Theme.objects
DEFAULT_SUB_THEME_MANAGER = core_models.SubTheme.objects
DEFAULT_TOPIC_MANAGER = core_models.Topic.objects
DEFAULT_METRIC_GROUP_MANAGER = core_models.MetricGroup.objects
DEFAULT_METRIC_MANAGER = core_models.Metric.objects
DEFAULT_GEOGRAPHY_TYPE_MANAGER = core_models.GeographyType.objects
DEFAULT_GEOGRAPHY_MANAGER = core_models.Geography.objects
DEFAULT_AGE_MANAGER = core_models.Age.objects
DEFAULT_STRATUM_MANAGER = core_models.Stratum.objects
DEFAULT_CORE_HEADLINE_MANAGER = core_models.CoreHeadline.objects


class Ingestion:
    """This is responsible for ingesting raw JSON data and ultimately creating the core models in the database

    Parameters:
    -----------
    data: List[dict]

    theme_manager : `ThemeManager`
        The model manager for `Theme`
        Defaults to the concrete `ThemeManager` via `Theme.objects`
    sub_theme_manager : `SubThemeManager`
        The model manager for `SubTheme`
        Defaults to the concrete `SubThemeManager` via `SubTheme.objects`
    topic_manager : `TopicManager`
        The model manager for `Topic`
        Defaults to the concrete `TopicManager` via `Topic.objects`
    metric_group_manager : `MetricGroupManager`
        The model manager for `MetricGroup`
        Defaults to the concrete `MetricGroupManager` via `MetricGroup.objects`
    metric_manager : `MetricManager`
        The model manager for `Metric`
        Defaults to the concrete `MetricManager` via `Metric.objects`
    geography_type_manager : `GeographyTypeManager`
        The model manager for `GeographyType`
        Defaults to the concrete `GeographyTypeManager` via `GeographyType.objects`
    geography_manager : `GeographyManager`
        The model manager for `Geography`
        Defaults to the concrete `GeographyManager` via `Geography.objects`
    age_manager : `AgeManager`
        The model manager for `Age`
        Defaults to the concrete `AgeManager` via `Age.objects`
    stratum_manager : `StratumManager`
        The model manager for `Stratum`
        Defaults to the concrete `StratumManager` via `Stratum.objects`
    core_time_series_manager : `CoreTimeSeriesManager`
        The model manager for `CoreTimeSeries`
        Defaults to the concrete `CoreTimeSeriesManager` via `CoreTimeSeries.objects`

    """

    def __init__(
        self,
        data,
        theme_manager: Manager = DEFAULT_THEME_MANAGER,
        sub_theme_manager: Manager = DEFAULT_SUB_THEME_MANAGER,
        topic_manager: Manager = DEFAULT_TOPIC_MANAGER,
        metric_group_manager: Manager = DEFAULT_METRIC_GROUP_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
        geography_type_manager: Manager = DEFAULT_GEOGRAPHY_TYPE_MANAGER,
        geography_manager: Manager = DEFAULT_GEOGRAPHY_MANAGER,
        age_manager: Manager = DEFAULT_AGE_MANAGER,
        stratum_manager: Manager = DEFAULT_STRATUM_MANAGER,
        core_headline_manager: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        self.data = data
        self.theme_manager = theme_manager
        self.sub_theme_manager = sub_theme_manager
        self.topic_manager = topic_manager
        self.metric_group_manager = metric_group_manager
        self.metric_manager = metric_manager
        self.geography_type_manager = geography_type_manager
        self.geography_manager = geography_manager
        self.age_manager = age_manager
        self.stratum_manager = stratum_manager
        self.core_headline_manager = core_headline_manager

    def _convert_to_models(self, dataframe: pd.DataFrame) -> list[HeadlineDTO]:
        """Converts the given `dataframe` to a list of HeadlineDTOs

        Notes:
            This handles the translations between column names
            from the data source to the column names expected by the database.
            E.g. the value in the "parent_theme" column of the source file
            will be passed into each `HeadlineDTO` as "theme"

        Args:
            dataframe: The parsed pandas.DataFrame which should be
                consumed by the `HeadlineDTO`

        Returns:
            list[HeadlineDTO]: A list of `HeadlineDTO` which
                are enriched with the corresponding values
                from the source file

        """
        return [self.to_model(data_record=record) for record in dataframe]

    @staticmethod
    def to_model(data_record: pd.DataFrame) -> HeadlineDTO:
        """Takes the given `data_record` and returns a single enriched `HeadlineDTO`

        Args:
            data_record: An individual record from the loaded JSON file

        Returns:
            A `HeadlineDTO` object with the correct fields
            populated from the given `data_record`

        """
        return HeadlineDTO(
            theme=data_record.parent_theme,
            sub_theme=data_record.child_theme,
            metric_group=data_record.metric_group,
            topic=data_record.topic,
            metric=data_record.metric,
            geography_type=data_record.geography_type,
            geography=data_record.geography,
            age=data_record.age,
            sex=data_record.sex,
            stratum=data_record.stratum,
            period_start=data_record.period_start,
            period_end=data_record.period_end,
            metric_value=data_record.metric_value,
            refresh_date=data_record.refresh_date,
        )

    def maintain_model(
        self,
        incoming_df: pd.DataFrame,
        fields: dict[str, str],
        model: Manager = DEFAULT_CORE_HEADLINE_MANAGER,
    ):
        """
        Maintain the individual models that are used in the normalisation of the Core source file
        New values in the source file will be added to the model
        All rows in the source file will get changed from the supplied cell
        value (eg infectious_disease) to the pk for that value. eg 1

        Args:
            incoming_df: This is the entire source file in a DataFrame
            fields: Dictionary of the model field names and the names of the relevant columns in the source file
            model: The model we want to maintain

        Returns:
            incoming_df with the relevant column changed to the primary keys for that model
            So, if the column cotained values like 'infectious_disease' it'll now be, say, 1 (the primary key for 'infectious_disease')
        """

        # From the source file, pull out the unique list of row values for this particular model
        incoming_data: pd.DataFrame = incoming_df[fields.keys()].drop_duplicates()

        # From the model, pull back the existing records along with their pks
        existing_data: pd.DataFrame = pd.DataFrame.from_records(
            model.all().values("pk", *fields.values())
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
            {**{"pk": model.create(**data).pk}, **data} for data in new_data
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
    def column_names_with_foreign_keys(self) -> list[str, ...]:
        return COLUMN_NAMES_WITH_FOREIGN_KEYS

    def open_data_as_dataframe(self) -> pd.DataFrame:
        """Opens the JSON `data` as a dataframe

        Returns:
            A dataframe containing the raw JSON data

        """
        return pd.read_json(self.data)

    def get_all_related_fields_and_model_managers(self) -> list[FieldsAndModelManager]:
        """Get a list of all related fields and model managers as named tuples

        Notes:
            Each named tuple in the returned list is enriched with
            1) `fields` -  A dict containing the related fields
            2) `model_manager` - The corresponding model manager

        Returns:
            list[FieldsAndModelManager] - A list of named tuples
                containing the related fields and model managers

        """
        return [
            FieldsAndModelManager(
                fields={"parent_theme": "name"}, model_manager=self.theme_manager
            ),
            FieldsAndModelManager(
                fields={"child_theme": "name", "parent_theme": "theme_id"},
                model_manager=self.sub_theme_manager,
            ),
            FieldsAndModelManager(
                fields={"topic": "name", "child_theme": "sub_theme_id"},
                model_manager=self.topic_manager,
            ),
            FieldsAndModelManager(
                fields={"geography_type": "name"},
                model_manager=self.geography_type_manager,
            ),
            FieldsAndModelManager(
                fields={"geography": "name", "geography_type": "geography_type_id"},
                model_manager=self.geography_manager,
            ),
            FieldsAndModelManager(
                fields={"metric_group": "name", "topic": "topic_id"},
                model_manager=self.metric_group_manager,
            ),
            FieldsAndModelManager(
                fields={
                    "metric": "name",
                    "metric_group": "metric_group_id",
                    "topic": "topic_id",
                },
                model_manager=self.metric_manager,
            ),
            FieldsAndModelManager(
                fields={"stratum": "name"}, model_manager=self.stratum_manager
            ),
            FieldsAndModelManager(
                fields={"age": "name"}, model_manager=self.age_manager
            ),
        ]

    def update_supporting_models(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Updates all supporting models, also replaces instances in the dataframe with IDs

        Notes:
            This method will accomplish 2 main things:
            1)  Creates any new supporting models required.
                For example, if the ingested data contains a new value
                for the `topic` field, then a new `Topic` model
                will be created and that record will be inserted
                into the database.
            2)  This method will also update supporting model columns
                to instead use their corresponding database record IDS.
                For example, if the dataframe showed `COVID-19`
                for the `topic` field of each entry.
                Then the dataframe will instead now show `123`,
                which will be the ID/pk of the `Topic` model
                which has the name `COVID-19`.

        Args:
            dataframe: The incoming dataframe containing
                the raw JSON data

        Returns:
            An updated version of the dataframe, containing
            corresponding database records instead of names
            for the supporting model columns.

        """
        all_related_fields_and_model_managers: list[
            FieldsAndModelManager
        ] = self.get_all_related_fields_and_model_managers()

        for related_fields_and_model_manager in all_related_fields_and_model_managers:
            dataframe: pd.DataFrame = self.maintain_model(
                incoming_df=dataframe,
                fields=related_fields_and_model_manager.fields,
                model=related_fields_and_model_manager.model_manager,
            )

        return dataframe

    def create_dtos_from_source(self) -> list[HeadlineDTO]:
        """Creates a list of `HeadlineDTO`s and updates supporting models

        Returns:
            A list of enriched `HeadlineDTO`s which can be used
            to create the corresponding `CoreHeadline` records.

        """
        dataframe: pd.DataFrame = self.open_data_as_dataframe()
        dataframe: pd.DataFrame = self.update_supporting_models(dataframe=dataframe)
        return self.convert_df_to_models(dataframe=dataframe)

    def convert_df_to_models(self, dataframe) -> list[HeadlineDTO]:
        """Convert the given `dataframe` to a list of `HeadlineDTO`

        Notes:
            This will also handle certain processing steps:
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
        dataframe: pd.DataFrame = self._create_named_tuple_iterable_from(
            dataframe=dataframe
        )

        return self._convert_to_models(dataframe=dataframe)

    @staticmethod
    def _remove_rows_with_nan_metric_value(dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe[dataframe["metric_value"].notnull()]

    def _cast_int_type_on_columns_with_foreign_keys(
        self, dataframe: pd.DataFrame
    ) -> pd.DataFrame:
        dataframe[self.column_names_with_foreign_keys] = dataframe[
            self.column_names_with_foreign_keys
        ].applymap(int)
        return dataframe

    @staticmethod
    def _create_named_tuple_iterable_from(dataframe: pd.DataFrame) -> pd.DataFrame:
        return dataframe.itertuples(index=False)

    def create_headlines(self, batch_size: int = 100) -> None:
        """Creates `CoreHeadline` records from the ingested data

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreHeadline` records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Args:
            batch_size: Controls the number of objects created
                in a single write query to the database.
                Defaults to 100.

        Returns:
            None

        """
        headline_dtos: list[HeadlineDTO] = self.create_dtos_from_source()

        model_instances = [
            self.core_headline_manager.model(
                metric_id=int(headline_dto.metric),
                geography_id=int(headline_dto.geography),
                stratum_id=int(headline_dto.stratum),
                age_id=int(headline_dto.age),
                sex=headline_dto.sex,
                refresh_date=headline_dto.refresh_date,
                period_start=headline_dto.period_start,
                period_end=headline_dto.period_end,
                metric_value=headline_dto.metric_value,
            )
            for headline_dto in headline_dtos
        ]

        self.core_headline_manager.bulk_create(
            model_instances,
            ignore_conflicts=True,
            batch_size=batch_size,
        )
