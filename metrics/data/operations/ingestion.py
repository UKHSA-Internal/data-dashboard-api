from typing import Dict, List, Set, Tuple, Type, Union

from django.db.models import Manager
from pydantic import BaseModel

from metrics.data.models import core_models


class HeadlineDTO(BaseModel):
    theme: str
    sub_theme: str
    topic: str
    metric_group: str
    metric: str
    geography_type: str
    geography: str
    age: str
    sex: str
    stratum: str

    period_start: str
    period_end: str
    refresh_date: str

    metric_value: float


DEFAULT_THEME_MANAGER = core_models.Theme.objects
DEFAULT_SUB_THEME_MANAGER = core_models.SubTheme.objects
DEFAULT_TOPIC_MANAGER = core_models.Topic.objects
DEFAULT_METRIC_GROUP_MANAGER = core_models.MetricGroup.objects
DEFAULT_METRIC_MANAGER = core_models.Metric.objects
DEFAULT_GEOGRAPHY_TYPE_MANAGER = core_models.GeographyType.objects
DEFAULT_GEOGRAPHY_MANAGER = core_models.Geography.objects
DEFAULT_AGE_MANAGER = core_models.Age.objects
DEFAULT_STRATUM_MANAGER = core_models.Stratum.objects
DEFAULT_CORE_TIME_SERIES_MANAGER = core_models.CoreTimeSeries.objects


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
        core_time_series_manager: Manager = DEFAULT_CORE_TIME_SERIES_MANAGER,
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
        self.core_time_series_manager = core_time_series_manager

    def convert_to_models(self) -> List[HeadlineDTO]:
        return [self.to_model(data_record=record) for record in self.data]

    @staticmethod
    def to_model(data_record: Dict[str, Union[str, float]]) -> HeadlineDTO:
        """Takes the given `data_record` and returns an enriched `HeadlineDTO`

        Args:
            data_record: An individual record from the loaded JSON file

        Returns:
            A `HeadlineDTO` object with the correct fields
            populated from the given `data_record`

        """
        return HeadlineDTO(
            theme=data_record["parent_theme"],
            sub_theme=data_record["child_theme"],
            metric_group=data_record["metric_group"],
            topic=data_record["topic"],
            metric=data_record["metric"],
            geography_type=data_record["geography_type"],
            geography=data_record["geography"],
            age=data_record["age"],
            sex=data_record["sex"],
            stratum=data_record["stratum"],
            period_start=data_record["period_start"],
            period_end=data_record["period_end"],
            metric_value=data_record["metric_value"],
            refresh_date=data_record["refresh_date"],
        )

    def get_unique_values_for_fields(self, keys: List[str]) -> Set[Tuple[str, ...]]:
        models = self.convert_to_models()
        return {tuple(getattr(model, key) for key in keys) for model in models}

    def get_model_manager_for_fields(self, keys: List[str]) -> Type[Manager]:
        """Get the corresponding model manager for the given `keys`

        Args:
            keys: list of strings representing the keys needed.
            i.e. ["sub_theme", "theme"] would return `SubThemeManager`

        Returns:
            A model manager related to those set of keys

        Raises:
            `ValueError` if the given `keys` cannot be matched
            to a particular model manager

        """
        match keys:
            case ["theme"]:
                return self.theme_manager
            case ["sub_theme", "theme"]:
                return self.sub_theme_manager
            case ["topic", "sub_theme"]:
                return self.topic_manager
            case ["metric_group", "topic"]:
                return self.metric_group_manager
            case ["metric", "metric_group", "topic"]:
                return self.metric_manager
            case ["geography_type"]:
                return self.geography_type_manager
            case ["geography", "geography_type"]:
                return self.geography_manager
            case ["age"]:
                return self.age_manager
            case ["stratum"]:
                return self.stratum_manager

        raise ValueError
