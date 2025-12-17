from typing import NamedTuple

from django.db.models import Manager

from ingestion.data_transfer_models.handlers import (
    build_headline_dto_from_source,
    build_time_series_dto_from_source,
)
from ingestion.data_transfer_models.headline import HeadlineDTO
from ingestion.data_transfer_models.time_series import TimeSeriesDTO
from ingestion.metrics_interface.interface import (
    DataSourceFileType,
    MetricsAPIInterface,
)
from ingestion.operations.batch_record_creation import create_records
from ingestion.utils import type_hints

DEFAULT_THEME_MANAGER = MetricsAPIInterface.get_theme_manager()
DEFAULT_SUB_THEME_MANAGER = MetricsAPIInterface.get_sub_theme_manager()
DEFAULT_TOPIC_MANAGER = MetricsAPIInterface.get_topic_manager()
DEFAULT_METRIC_GROUP_MANAGER = MetricsAPIInterface.get_metric_group_manager()
DEFAULT_METRIC_MANAGER = MetricsAPIInterface.get_metric_manager()
DEFAULT_GEOGRAPHY_TYPE_MANAGER = MetricsAPIInterface.get_geography_type_manager()
DEFAULT_GEOGRAPHY_MANAGER = MetricsAPIInterface.get_geography_manager()
DEFAULT_AGE_MANAGER = MetricsAPIInterface.get_age_manager()
DEFAULT_STRATUM_MANAGER = MetricsAPIInterface.get_stratum_manager()
API_TIME_SERIES_MODEL = MetricsAPIInterface.get_api_timeseries()
CORE_TIME_SERIES_MODEL = MetricsAPIInterface.get_core_timeseries()
CORE_HEADLINE_MODEL = MetricsAPIInterface.get_core_headline()


class SupportingModelsLookup(NamedTuple):
    metric_id: int
    geography_id: int
    stratum_id: int
    age_id: int


class Consumer:
    """Ingests inbound data and ultimately creates the core & api models in the database

    Notes:
    ------
    The given raw `source_data` is passed to a `HeadlineDTO` or `TimeSeriesDTO`
    depending on whether the incoming data is headline or time series type.
    This casts validation over incoming data ensuring that:
        a) The required fields are all in place
        b) They conform to the structure set by the underlying pydantic models.
            i.e. is the provided `geography_code` a string between 3 and 9 characters.

    The DTO is then used for the data ingestion.

    Parameters:
    -----------
    source_data: dict[str, str | list[dict[str, str | float]]]
        The raw source data to be ingested
    dto: HeadlineDTO | TimeSeriesDTO | None
        The parsed and validated DTO for the headline or timeseries data.
        If not provided, this will be created from the source data
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
    api_timeseries_manager : `APITimeSeriesManager`
        The model manager for `APITimeSeries`
        Defaults to the concrete `APITimeSeriesManager` via `APITimeSeries.objects`

    """

    def __init__(
        self,
        *,
        source_data: type_hints.INCOMING_DATA_TYPE,
        dto: HeadlineDTO | TimeSeriesDTO | None = None,
        theme_manager: Manager = DEFAULT_THEME_MANAGER,
        sub_theme_manager: Manager = DEFAULT_SUB_THEME_MANAGER,
        topic_manager: Manager = DEFAULT_TOPIC_MANAGER,
        metric_group_manager: Manager = DEFAULT_METRIC_GROUP_MANAGER,
        metric_manager: Manager = DEFAULT_METRIC_MANAGER,
        geography_type_manager: Manager = DEFAULT_GEOGRAPHY_TYPE_MANAGER,
        geography_manager: Manager = DEFAULT_GEOGRAPHY_MANAGER,
        age_manager: Manager = DEFAULT_AGE_MANAGER,
        stratum_manager: Manager = DEFAULT_STRATUM_MANAGER,
        core_headline_manager: Manager = CORE_HEADLINE_MODEL.objects,
        core_timeseries_manager: Manager = CORE_TIME_SERIES_MODEL.objects,
        api_timeseries_manager: Manager = API_TIME_SERIES_MODEL.objects,
    ):
        self._source_data = source_data
        self.dto = dto or self._build_dto()

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
        self.api_timeseries_manager = api_timeseries_manager

    def _build_dto(self) -> HeadlineDTO | TimeSeriesDTO:
        if self.is_headline_data:
            return build_headline_dto_from_source(source_data=self._source_data)
        return build_time_series_dto_from_source(source_data=self._source_data)

    @property
    def is_headline_data(self) -> bool:
        return self._source_data["metric_group"] == DataSourceFileType.headline.value

    # get or create supporting model methods

    @staticmethod
    def _get_or_create_record(*, model_manager, **kwargs):
        """Returns a record for the given `model_manager` and kwargs, creates one if not already available.

        Notes:
            The `get_or_create()` method called on the underlying model manager
            returns a tuple of (object, created), where created is a boolean
            specifying whether an object was created.
            This will simply return the object for convenience

        Args:
            model_manager: The model manager to be used when querying/writing the record
            **kwargs: The keyword arguments to be passed to the read/write to the model manager

        Returns:
            The model instance reflecting the given kwargs

        """
        record, _ = model_manager.get_or_create(**kwargs)
        return record

    def _get_or_create_theme(self):
        """Returns the corresponding `Theme` record to be associated with the current `data`

        Returns:
            A `Theme` model instance matching the "parent_theme" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.theme_manager,
            name=self.dto.parent_theme,
        )

    def _get_or_create_sub_theme(self, *, theme):
        """Returns the corresponding `SubTheme` record to be associated with the current `data`

        Args:
            theme: The `Theme` model instance
                associated with this `SubTheme`

        Returns:
            A `SubTheme` model instance matching the "child_theme" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.sub_theme_manager,
            name=self.dto.child_theme,
            theme_id=theme.id,
        )

    def _get_or_create_topic(self, *, sub_theme):
        """Returns the corresponding `Topic` record to be associated with the current `data`

        Args:
            sub_theme: The `SubTheme` model instance
                associated with this `Topic`

        Returns:
            A `Topic` model instance matching the "topic" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.topic_manager,
            name=self.dto.topic,
            sub_theme_id=sub_theme.id,
        )

    def _get_or_create_geography_type(self):
        """Returns the corresponding `GeographyType` record to be associated with the current `data`

        Returns:
            A `GeographyType` model instance matching the "geography_type" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.geography_type_manager,
            name=self.dto.geography_type,
        )

    def _get_or_create_geography(self, *, geography_type):
        """Returns the corresponding `Geography` record to be associated with the current `data`

        Args:
            geography_type: The `GeographyType` model instance
                associated with this `Geography`

        Returns:
            A `Geography` model instance matching the "geography" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.geography_manager,
            name=self.dto.geography,
            geography_code=self.dto.geography_code,
            geography_type_id=geography_type.id,
        )

    def _get_or_create_metric_group(self, *, topic):
        """Returns the corresponding `MetricGroup` record to be associated with the current `data`

        Args:
            topic: The `Topic` model instance associated
                with this `Metric`

        Returns:
            A `MetricGroup` model instance matching the "metric" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.metric_group_manager,
            name=self.dto.metric_group,
            topic_id=topic.id,
        )

    def _get_or_create_metric(self, *, metric_group, topic):
        """Returns the corresponding `Metric` record to be associated with the current `data`

        Args:
            metric_group: The `MetricGroup` model instance
                associated with this `Metric`
            topic: The `Topic` model instance associated
                with this `Metric`

        Returns:
            A `Metric` model instance matching the "metric" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.metric_manager,
            name=self.dto.metric,
            metric_group_id=metric_group.id,
            topic_id=topic.id,
        )

    def _get_or_create_stratum(self):
        """Returns the corresponding `Stratum` record to be associated with the current `data`

        Returns:
            A `Stratum` model instance matching the "stratum" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.stratum_manager,
            name=self.dto.stratum,
        )

    def _get_or_create_age(self):
        """Returns the corresponding `Age` record to be associated with the current `data`

        Returns:
            An `Age` model instance matching the "age" from the `data`

        """
        return self._get_or_create_record(
            model_manager=self.age_manager,
            name=self.dto.age,
        )

    def update_supporting_models(self) -> SupportingModelsLookup:
        """Updates the supporting core models by creating new records when new value combinations are encountered

        Notes:
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created accordingly
            and that record will be inserted into the database.

        Returns:
            An enriched `SupportingModelsLookup` named tuple
            which can be used to provide quick lookup info
            when creating the `CoreHeadline` or `CoreTimeSeries` records

        """
        theme = self._get_or_create_theme()
        sub_theme = self._get_or_create_sub_theme(theme=theme)
        topic = self._get_or_create_topic(sub_theme=sub_theme)

        geography_type = self._get_or_create_geography_type()
        geography = self._get_or_create_geography(geography_type=geography_type)

        metric_group = self._get_or_create_metric_group(topic=topic)
        metric = self._get_or_create_metric(metric_group=metric_group, topic=topic)

        stratum = self._get_or_create_stratum()
        age = self._get_or_create_age()

        return SupportingModelsLookup(
            metric_id=metric.id,
            geography_id=geography.id,
            stratum_id=stratum.id,
            age_id=age.id,
        )

    def process_core_headlines(self) -> None:
        """Creates `CoreHeadline` database records from the ingested data after stale records are deleted ahead of time.

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreHeadline` records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Returns:
            None

        """
        self.clear_stale_headlines()
        self.create_core_headlines()

    def process_core_and_api_timeseries(self) -> None:
        """Creates `APITimeSeries` and `CoreTimeSeries` records from the ingested data after stale records are deleted.

        Any necessary supporting models will be created
            as required for the records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Returns:
            None

        """
        self.clear_stale_timeseries()
        self.create_core_and_api_timeseries()

    # build and create model methods

    def build_core_headlines(self) -> list[CORE_HEADLINE_MODEL]:
        """Builds `CoreHeadline` model instances from the ingested data

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreHeadline` records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Returns:
            List of `CoreHeadline` model instances

        """
        supporting_models_lookup: SupportingModelsLookup = (
            self.update_supporting_models()
        )

        return [
            CORE_HEADLINE_MODEL(
                metric_id=supporting_models_lookup.metric_id,
                geography_id=supporting_models_lookup.geography_id,
                stratum_id=supporting_models_lookup.stratum_id,
                age_id=supporting_models_lookup.age_id,
                sex=self.dto.sex,
                refresh_date=self.dto.refresh_date,
                embargo=headline_data.embargo,
                period_start=headline_data.period_start,
                period_end=headline_data.period_end,
                metric_value=headline_data.metric_value,
                upper_confidence=headline_data.upper_confidence,
                lower_confidence=headline_data.lower_confidence,
                is_public=headline_data.is_public,
            )
            for headline_data in self.dto.data
        ]

    def create_core_headlines(self) -> None:
        """Creates `CoreHeadline` database records from the ingested data

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreHeadline` records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Returns:
            None

        """
        core_headlines = self.build_core_headlines()
        return create_records(
            model_manager=self.core_headline_manager, model_instances=core_headlines
        )

    def build_core_time_series(self) -> list[CORE_TIME_SERIES_MODEL]:
        """Builds `CoreTimeSeries` model instances from the ingested data

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreTimeSeries` records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Returns:
            List of `CoreTimeSeries` model instances

        """
        supporting_models_lookup: SupportingModelsLookup = (
            self.update_supporting_models()
        )

        created_core_time_series = []
        for time_series_data in self.dto.time_series:
            year, month, _ = str(time_series_data.date).split("-")
            core_time_series = CORE_TIME_SERIES_MODEL(
                metric_id=supporting_models_lookup.metric_id,
                geography_id=supporting_models_lookup.geography_id,
                stratum_id=supporting_models_lookup.stratum_id,
                age_id=supporting_models_lookup.age_id,
                sex=self.dto.sex,
                refresh_date=self.dto.refresh_date,
                embargo=time_series_data.embargo,
                metric_frequency=self.dto.metric_frequency,
                date=time_series_data.date,
                epiweek=time_series_data.epiweek,
                year=int(year),
                month=int(month),
                metric_value=time_series_data.metric_value,
                in_reporting_delay_period=time_series_data.in_reporting_delay_period,
                force_write=time_series_data.force_write,
                is_public=time_series_data.is_public,
            )
            created_core_time_series.append(core_time_series)

        return created_core_time_series

    def create_core_time_series(self) -> None:
        """Creates `CoreTimeSeries` database records from the ingested data

        Notes:
            Any necessary supporting models will be created
            as required for the `CoreTimeSeries` records.
            For example, if the ingested data contains a new value
            for the `topic` field which is not already available as a `Topic` model,
            then a new `Topic` model will be created
            and that record will be inserted into the database.

        Returns:
            None

        """
        core_time_series = self.build_core_time_series()
        return create_records(
            model_manager=self.core_timeseries_manager, model_instances=core_time_series
        )

    def clear_stale_headlines(self):
        """Deletes all stale records for the `CoreHeadline` records relevant to the ingested dataset

        Returns:
            None

        """
        params = {
            "topic": self.dto.topic,
            "metric": self.dto.metric,
            "geography": self.dto.geography,
            "geography_type": self.dto.geography_type,
            "geography_code": self.dto.geography_code,
            "stratum": self.dto.stratum,
            "sex": self.dto.sex,
            "age": self.dto.age,
        }
        self.core_headline_manager.delete_superseded_data(
            **params,
            is_public=True,
        )
        self.core_headline_manager.delete_superseded_data(
            **params,
            is_public=False,
        )

    def build_api_time_series(self) -> list[API_TIME_SERIES_MODEL]:
        """Builds `APITimeSeries` model instances from the ingested data

        Returns:
            List of `APITimeSeries` model instances

        """
        created_api_time_series = []

        for time_series_data in self.dto.time_series:
            year, month, _ = str(time_series_data.date).split("-")

            api_time_series = API_TIME_SERIES_MODEL(
                metric_frequency=self.dto.metric_frequency,
                age=self.dto.age,
                month=int(month),
                year=int(year),
                geography_code=self.dto.geography_code,
                metric_group=self.dto.metric_group,
                metric=self.dto.metric,
                theme=self.dto.parent_theme,
                sub_theme=self.dto.child_theme,
                topic=self.dto.topic,
                geography_type=self.dto.geography_type,
                geography=self.dto.geography,
                stratum=self.dto.stratum,
                sex=self.dto.sex,
                epiweek=time_series_data.epiweek,
                refresh_date=self.dto.refresh_date,
                embargo=time_series_data.embargo,
                date=time_series_data.date,
                metric_value=time_series_data.metric_value,
                in_reporting_delay_period=time_series_data.in_reporting_delay_period,
                force_write=time_series_data.force_write,
                is_public=time_series_data.is_public,
            )
            created_api_time_series.append(api_time_series)

        return created_api_time_series

    def create_api_time_series(self) -> None:
        """Creates `APITimeSeries` database records from the ingested data

        Returns:
            None

        """
        api_time_series = self.build_api_time_series()
        return create_records(
            model_manager=self.api_timeseries_manager, model_instances=api_time_series
        )

    def create_core_and_api_timeseries(self) -> None:
        """Creates `APITimeSeries` and `CoreTimeSeries` database records from the ingested data

        Returns:
            None

        """
        self.create_core_time_series()
        self.create_api_time_series()

    def clear_stale_timeseries(self):
        """Deletes all stale records for both `CoreTimeSeries` and `APITimeSeries` relevant to the ingested dataset

        Returns:
            None

        """
        self._clear_stale_core_timeseries()
        self._clear_stale_api_timeseries()

    def _clear_stale_core_timeseries(self):
        params = {
            "metric": self.dto.metric,
            "geography": self.dto.geography,
            "geography_type": self.dto.geography_type,
            "geography_code": self.dto.geography_code,
            "stratum": self.dto.stratum,
            "sex": self.dto.sex,
            "age": self.dto.age,
        }
        self.core_timeseries_manager.delete_superseded_data(**params, is_public=True)
        self.core_timeseries_manager.delete_superseded_data(**params, is_public=False)

    def _clear_stale_api_timeseries(self):
        params = {
            "theme": self.dto.parent_theme,
            "sub_theme": self.dto.child_theme,
            "topic": self.dto.topic,
            "metric": self.dto.metric,
            "geography": self.dto.geography,
            "geography_type": self.dto.geography_type,
            "geography_code": self.dto.geography_code,
            "stratum": self.dto.stratum,
            "sex": self.dto.sex,
            "age": self.dto.age,
        }
        self.api_timeseries_manager.delete_superseded_data(**params, is_public=True)
        self.api_timeseries_manager.delete_superseded_data(**params, is_public=False)
