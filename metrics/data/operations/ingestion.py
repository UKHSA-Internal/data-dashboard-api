from typing import Dict, List, Set, Tuple, Union

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
DEFAULT_METRIC_GROUP_MANAGER = core_models.Metric.objects
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
        return [self.to_model(record) for record in self.data]

    @staticmethod
    def to_model(data: Dict[str, Union[str, float]]) -> HeadlineDTO:
        return HeadlineDTO(
            theme=data["parent_theme"],
            sub_theme=data["child_theme"],
            metric_group=data["metric_group"],
            topic=data["topic"],
            metric=data["metric"],
            geography_type=data["geography_type"],
            geography=data["geography"],
            age=data["age"],
            sex=data["sex"],
            stratum=data["stratum"],
            period_start=data["period_start"],
            period_end=data["period_end"],
            metric_value=data["metric_value"],
            refresh_date=data["refresh_date"],
        )

    def get_unique_values_for_fields(self, keys: List[str]) -> Set[Tuple[str, ...]]:
        models = self.convert_to_models()
        return {tuple(getattr(model, key) for key in keys) for model in models}
