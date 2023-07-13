from typing import Callable, Iterable, NamedTuple, Optional, Type

import pandas as pd
from django.db.models import Manager

from ingestion.data_transfer_models import HeadlineDTO, TimeSeriesDTO
from ingestion.metrics_interfaces.interface import MetricsAPIInterface
from ingestion.reader import Reader


class FieldsAndModelManager(NamedTuple):
    fields: dict[str, str]
    model_manager: Type[Manager]


DEFAULT_THEME_MANAGER = MetricsAPIInterface.get_theme_manager()
DEFAULT_SUB_THEME_MANAGER = MetricsAPIInterface.get_sub_theme_manager()
DEFAULT_TOPIC_MANAGER = MetricsAPIInterface.get_topic_manager()
DEFAULT_METRIC_GROUP_MANAGER = MetricsAPIInterface.get_metric_group_manager()
DEFAULT_METRIC_MANAGER = MetricsAPIInterface.get_metric_manager()
DEFAULT_GEOGRAPHY_TYPE_MANAGER = MetricsAPIInterface.get_geography_type_manager()
DEFAULT_GEOGRAPHY_MANAGER = MetricsAPIInterface.get_geography_manager()
DEFAULT_AGE_MANAGER = MetricsAPIInterface.get_age_manager()
DEFAULT_STRATUM_MANAGER = MetricsAPIInterface.get_stratum_manager()
DEFAULT_CORE_HEADLINE_MANAGER = MetricsAPIInterface.get_core_headline_manager()

CREATE_CORE_HEADLINES: Callable = MetricsAPIInterface.get_create_core_headlines()


class Ingestion:
    """This is responsible for ingesting raw JSON data and ultimately creating the core models in the database

    Parameters:
    -----------
    data: FilePath | ReadBuffer[str] | ReadBuffer[bytes]
        The file or buffer containing the raw JSON data
    reader : `Reader`
        The reader object used to parse the data
        Defaults to a `Reader` object
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
    core_headline_manager : `CoreHeadlineManager`
        The model manager for `CoreHeadline`
        Defaults to the concrete `CoreHeadlineManager` via `CoreHeadline.objects`

    """

    def __init__(
        self,
        data: pd._typing.FilePath
        | pd._typing.ReadBuffer[str]
        | pd._typing.ReadBuffer[bytes],
        reader: Optional[Reader] = None,
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
        self.reader = reader or Reader(data=data)

        # Model managers
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

    def _convert_to_headline_dtos(self, processed_data: Iterable) -> list[HeadlineDTO]:
        """Converts the given `processed_data` to a list of HeadlineDTOs

        Notes:
            This handles the translations between column names
            from the data source to the column names expected by the database.
            E.g. the value in the "parent_theme" column of the source file
            will be passed into each `HeadlineDTO` as "theme"

        Args:
            processed_data: The parsed iterable, for which each item
                can be consumed by a `HeadlineDTO`

        Returns:
            list[HeadlineDTO]: A list of `HeadlineDTO` which
                are enriched with the corresponding values
                from the source file

        """
        return [self.to_headline_dto(data_record=record) for record in processed_data]

    @staticmethod
    def to_headline_dto(data_record: pd.DataFrame) -> HeadlineDTO:
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

    def _convert_to_timeseries_dtos(
        self, processed_data: Iterable
    ) -> list[HeadlineDTO]:
        """Converts the given `processed_data` to a list of TimeSeriesDTOs

        Notes:
            This handles the translations between column names
            from the data source to the column names expected by the database.
            E.g. the value in the "parent_theme" column of the source file
            will be passed into each `TimeSeriesDTO` as "theme"

        Args:
            processed_data: The parsed iterable, for which each item
                can be consumed by a `TimeSeriesDTO`

        Returns:
            list[TimeSeriesDTO]: A list of `TimeSeriesDTO` which
                are enriched with the corresponding values
                from the source file

        """
        return [self.to_timeseries_dto(data_record=record) for record in processed_data]

    @staticmethod
    def to_timeseries_dto(data_record: pd.DataFrame) -> HeadlineDTO:
        """Takes the given `data_record` and returns a single enriched `TimeSeriesDTO`

        Args:
            data_record: An individual record from the loaded JSON file

        Returns:
            A `TimeSeriesDTO` object with the correct fields
            populated from the given `data_record`

        """
        return TimeSeriesDTO(
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
            metric_frequency=data_record.metric_frequency,
            year=data_record.year,
            month=data_record.month,
            epiweek=data_record.epiweek,
            metric_value=data_record.metric_value,
            date=data_record.date,
            refresh_date=data_record.refresh_date,
        )

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
            dataframe: pd.DataFrame = self.reader.maintain_model(
                incoming_dataframe=dataframe,
                fields=related_fields_and_model_manager.fields,
                model_manager=related_fields_and_model_manager.model_manager,
            )

        return dataframe

    def create_headlines_dtos_from_source(self) -> list[HeadlineDTO]:
        """Creates a list of `HeadlineDTO`s and updates supporting models

        Returns:
            A list of enriched `HeadlineDTO`s which can be used
            to create the corresponding `CoreHeadline` records.

        """
        dataframe: pd.DataFrame = self.reader.open_data_as_dataframe()
        dataframe: pd.DataFrame = self.update_supporting_models(dataframe=dataframe)
        processed_data: Iterable = self.reader.parse_dataframe_as_iterable(
            dataframe=dataframe
        )
        return self._convert_to_headline_dtos(processed_data=processed_data)

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
        headline_dtos: list[HeadlineDTO] = self.create_headlines_dtos_from_source()

        return CREATE_CORE_HEADLINES(
            headline_dtos=headline_dtos,
            core_headline_manager=self.core_headline_manager,
            batch_size=batch_size,
        )
