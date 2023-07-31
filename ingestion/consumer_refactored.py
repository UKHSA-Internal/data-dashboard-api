from typing import Callable, NamedTuple, Optional, Type

import pandas as pd
from django.db.models import Manager

from ingestion.data_transfer_models_refactored import (
    IncomingBaseDTO,
    IncomingHeadlineDTO,
    OutgoingHeadlineDTO,
    OutgoingTimeSeriesDTO,
)
from ingestion.data_transfer_models_refactored.incoming import IncomingTimeSeriesDTO
from ingestion.metrics_interfaces.interface import MetricsAPIInterface
from ingestion.reader_refactored import Reader


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
DEFAULT_CORE_TIMESERIES_MANAGER = MetricsAPIInterface.get_core_timeseries_manager()

CREATE_CORE_HEADLINES: Callable = MetricsAPIInterface.get_create_core_headlines()
CREATE_CORE_TIMESERIES: Callable = MetricsAPIInterface.get_create_core_timeseries()


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
    core_timeseries_manager : `CoreTimeSeriesManager`
        The model manager for `CoreTimeSeries`
        Defaults to the concrete `CoreTimeSeriesManager` via `CoreTimeSeries.objects`

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
        core_timeseries_manager: Manager = DEFAULT_CORE_TIMESERIES_MANAGER,
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
        self.core_timeseries_manager = core_timeseries_manager

    def update_supporting_models(
        self, incoming_dtos: list[IncomingBaseDTO]
    ) -> list[IncomingBaseDTO]:
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
            incoming_dtos: The list of incoming DTOs to be processed

        Returns:
            A list of DTOs which have been processed for each supporting model.
            The relevant supporting model attributes
            on each DTO will be changed so that their
            original text representation has been replaced
            with the corresponding database record IDs

        """
        all_related_fields_and_model_managers: list[
            FieldsAndModelManager
        ] = self.get_all_related_fields_and_model_managers()

        for related_fields_and_model_manager in all_related_fields_and_model_managers:
            incoming_dtos: list[IncomingBaseDTO] = self.reader.maintain_model(
                incoming_dtos=incoming_dtos,
                fields=related_fields_and_model_manager.fields,
                model_manager=related_fields_and_model_manager.model_manager,
            )

        return incoming_dtos

    def get_all_related_fields_and_model_managers(self) -> list[FieldsAndModelManager]:
        """Get a list of all related fields and model managers as named tuples

        Notes:
            Each named tuple in the returned list is enriched with
            1) `fields`         -  A dict containing the related fields
            2) `model_manager`  - The corresponding model manager

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

    # Data transfer object creation

    def _convert_to_outgoing_headline_dtos(
        self, processed_headline_dtos: list[IncomingHeadlineDTO]
    ) -> list[OutgoingHeadlineDTO]:
        """Converts the given `processed_headline_dtos` to a list of `OutgoingHeadlineDTO`s

        Notes:
            This handles the translations between column names
            from the data source to the column names expected by the database.
            E.g. the value in the "parent_theme" column of the source file
            will be passed into each `OutgoingHeadlineDTO` as "theme"

        Args:
            processed_headline_dtos: The parsed iterable, for which each item
                can be consumed by an `OutgoingHeadlineDTO`

        Returns:
            A list of `OutgoingHeadlineDTO` which are enriched
            with the corresponding values from the source file

        """
        return [
            self.to_outgoing_headline_dto(incoming_headline_dto=processed_headline_dto)
            for processed_headline_dto in processed_headline_dtos
        ]

    @staticmethod
    def to_outgoing_headline_dto(
        incoming_headline_dto: IncomingHeadlineDTO,
    ) -> OutgoingHeadlineDTO:
        """Takes the given `incoming_headline_dto` and returns a single enriched `OutgoingHeadlineDTO`

        Args:
            incoming_headline_dto: An individual `IncomingHeadlineDTO`
                instance which has been processed and enriched
                according to the data being passed
                into the write query to the db

        Returns:
            An `OutgoingHeadlineDTO` object with the correct fields
            populated from the given `incoming_headline_dto`

        """
        return OutgoingHeadlineDTO(
            theme=incoming_headline_dto.parent_theme,
            sub_theme=incoming_headline_dto.child_theme,
            metric_group=incoming_headline_dto.metric_group,
            topic=incoming_headline_dto.topic,
            metric=incoming_headline_dto.metric,
            geography_type=incoming_headline_dto.geography_type,
            geography=incoming_headline_dto.geography,
            age=incoming_headline_dto.age,
            sex=incoming_headline_dto.sex,
            stratum=incoming_headline_dto.stratum,
            period_start=incoming_headline_dto.period_start,
            period_end=incoming_headline_dto.period_end,
            metric_value=incoming_headline_dto.metric_value,
            refresh_date=incoming_headline_dto.refresh_date,
        )

    def _convert_to_outgoing_timeseries_dtos(
        self, processed_timeseries_dtos: list[IncomingTimeSeriesDTO]
    ) -> list[OutgoingTimeSeriesDTO]:
        """Converts the given `processed_timeseries_dtos` to a list of `OutgoingTimeSeriesDTO`s

        Notes:
            This handles the translations between column names
            from the data source to the column names expected by the database.
            E.g. the value in the "parent_theme" column of the source file
            will be passed into each `OutgoingTimeSeriesDTO` as "theme"

        Args:
            processed_timeseries_dtos: The parsed iterable, for which each item
                can be consumed by an `OutgoingTimeSeriesDTO`

        Returns:
            A list of `OutgoingTimeSeriesDTO` which are enriched
            with the corresponding values from the source file

        """
        return [
            self.to_outgoing_timeseries_dto(
                incoming_timeseries_dto=processed_timeseries_dto
            )
            for processed_timeseries_dto in processed_timeseries_dtos
        ]

    @staticmethod
    def to_outgoing_timeseries_dto(
        incoming_timeseries_dto: IncomingTimeSeriesDTO,
    ) -> OutgoingTimeSeriesDTO:
        """Takes the given `incoming_timeseries_dto` and returns a single enriched `OutgoingTimeSeriesDTO`

        Args:
            incoming_timeseries_dto: An individual `IncomingTimeSeriesDTO`
                instance which has been processed and enriched
                according to the data being passed
                into the write query to the db

        Returns:
            An `OutgoingTimeSeriesDTO` object with the correct fields
            populated from the given `data_record`

        """
        return OutgoingTimeSeriesDTO(
            theme=incoming_timeseries_dto.parent_theme,
            sub_theme=incoming_timeseries_dto.child_theme,
            metric_group=incoming_timeseries_dto.metric_group,
            topic=incoming_timeseries_dto.topic,
            metric=incoming_timeseries_dto.metric,
            geography_type=incoming_timeseries_dto.geography_type,
            geography=incoming_timeseries_dto.geography,
            age=incoming_timeseries_dto.age,
            sex=incoming_timeseries_dto.sex,
            stratum=incoming_timeseries_dto.stratum,
            metric_frequency=incoming_timeseries_dto.metric_frequency,
            year=incoming_timeseries_dto.year,
            month=incoming_timeseries_dto.month,
            epiweek=incoming_timeseries_dto.epiweek,
            metric_value=incoming_timeseries_dto.metric_value,
            date=str(incoming_timeseries_dto.date),
            refresh_date=incoming_timeseries_dto.refresh_date,
        )

    def _parse_data(self) -> list[IncomingBaseDTO]:
        """Convert the data to a list of DTOs and update supporting core models

        Notes:
            This will handle the following pre-processing steps:
            1)  Creates any new supporting models required.
                For example, if the ingested data contains a new value
                for the `topic` field, then a new `Topic` model
                will be created and that record will be inserted
                into the database.
            2)  The supporting model columns will also
                instead use their corresponding database record IDs.
                For example, if the data showed `COVID-19`
                for the `topic` field of each entry.
                Then the returned iterable will instead now show `123`,
                which will be the ID/pk of the `Topic` model
                which has the name `COVID-19`.
            3)  Remove all rows with `NaN` in the `metric_value` column

        Returns:
            A list of `IncomingBaseDTO` type instances which are
            enriched with all the data required to
            insert a new database record in the table

        """
        incoming_dtos: list[IncomingBaseDTO] = self.reader.open_source_file()
        parsed_incoming_dtos: list[IncomingBaseDTO] = self.update_supporting_models(
            incoming_dtos=incoming_dtos
        )
        return self.reader.post_process_incoming_dtos(
            incoming_dtos=parsed_incoming_dtos
        )

    def create_outgoing_headlines_dtos_from_source(self) -> list[OutgoingHeadlineDTO]:
        """Creates a list of `OutgoingHeadlineDTO` instances and updates supporting models

        Returns:
            A list of enriched `OutgoingHeadlineDTO` instances
            which can be used to create the corresponding `CoreHeadline` records.

        """
        processed_incoming_dtos: list[IncomingHeadlineDTO] = self._parse_data()
        return self._convert_to_outgoing_headline_dtos(
            processed_headline_dtos=processed_incoming_dtos
        )

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
        outgoing_headline_dtos: list[
            OutgoingHeadlineDTO
        ] = self.create_outgoing_headlines_dtos_from_source()

        return CREATE_CORE_HEADLINES(
            headline_dtos=outgoing_headline_dtos,
            core_headline_manager=self.core_headline_manager,
            batch_size=batch_size,
        )

    def create_outgoing_timeseries_dtos_from_source(
        self,
    ) -> list[OutgoingTimeSeriesDTO]:
        """Creates a list of `OutgoingTimeSeriesDTO` instances and updates supporting models

        Returns:
            A list of enriched `OutgoingTimeSeriesDTO`s which can be used
            to create the corresponding `CoreTimeSeries` records.

        """
        processed_incoming_dtos: list[IncomingTimeSeriesDTO] = self._parse_data()
        return self._convert_to_outgoing_timeseries_dtos(
            processed_timeseries_dtos=processed_incoming_dtos
        )

    def create_timeseries(self, batch_size: int = 100) -> None:
        """Creates `CoreTimeSeries` records from the ingested data

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreTimeSeries` records.
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
        timeseries_dtos: list[
            OutgoingTimeSeriesDTO
        ] = self.create_outgoing_timeseries_dtos_from_source()

        return CREATE_CORE_TIMESERIES(
            timeseries_dtos=timeseries_dtos,
            core_timeseries_manager=self.core_timeseries_manager,
            batch_size=batch_size,
        )
