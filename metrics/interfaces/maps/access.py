import datetime
from dataclasses import asdict, dataclass

from django.db.models.manager import Manager

from metrics.data.in_memory_models.geography_relationships.handlers import (
    OPTIONAL_UPSTREAM_RELATIONSHIPS,
    get_upstream_relationships_for_geography,
)
from metrics.data.models.core_models import CoreTimeSeries, Geography
from metrics.domain.models.map import MapMainParameters, MapsParameters


@dataclass
class AccompanyingPointResult:
    label_prefix: str
    label_suffix: str
    metric_value: float | None


@dataclass
class MapGeographyResult:
    geography_code: str
    geography_type: str
    geography: str
    metric_value: float | None
    accompanying_points: list[AccompanyingPointResult] | None


@dataclass
class MapOutput:
    data: list[MapGeographyResult]
    latest_date: str | None

    def output(self) -> dict:
        return asdict(self)


class GeographyNotFoundForAccompanyingPointError(Exception): ...


class MapsInterface:
    def __init__(
        self,
        *,
        maps_parameters: MapsParameters,
        core_time_series_manager: type[Manager] = None,
        geography_manager: type[Manager] = None,
    ):
        self.maps_parameters = maps_parameters
        self.core_time_series_manager = (
            core_time_series_manager or CoreTimeSeries.objects
        )
        self.geography_manager = geography_manager or Geography.objects

    def get_maps_data(self) -> MapOutput:
        """
        Get complete maps data with associated dates.

        Returns:
            MapOutput containing processed data and latest date.

        """
        results, associated_dates = self.build_maps_data()
        latest_date = max(associated_dates, default=None)

        return MapOutput(
            data=results,
            latest_date=latest_date,
        )

    def _ensure_geographies_are_populated(self) -> None:
        """Inject all geographies for geography type if none are provided."""
        if not self.maps_parameters.parameters.geographies:
            self.maps_parameters.parameters.geographies = (
                self.geography_manager.get_all_geography_names_by_geography_type(
                    geography_type_name=self.maps_parameters.parameters.geography_type,
                )
            )

    def _get_related_geography_for_accompanying_point(
        self, accompanying_point, main_geography: str
    ) -> str | None:
        """
        Get related geography if required for the accompanying point.

        Args:
            accompanying_point: The accompanying point configuration
            main_geography: The main geography being processed

        Returns:
            Related geography name or None if not found/required

        """
        selected_geography: str = accompanying_point.parameters.geography
        selected_geography_type: str = accompanying_point.parameters.geography_type
        main_geography_type: str = self.maps_parameters.parameters.geography_type

        # If the geography has been explicitly defined
        # or if the types are the same, we fall back to the selected geography
        # for this accompanying point
        if selected_geography or selected_geography_type == main_geography_type:
            return selected_geography

        return self._fetch_related_geography_by_type(
            geography=main_geography,
            main_geography_type=main_geography_type,
            target_geography_type=selected_geography_type,
        )

    def _fetch_related_geography_by_type(
        self, geography: str, main_geography_type: str, target_geography_type: str
    ) -> str:
        """
        Fetch related geography for the specified geography type.

        Args:
            geography: Source geography name
            main_geography_type: Type of the main geography
            target_geography_type: Target geography type to find

        Returns:
            Related geography name or None if not found

        """
        geography_code: str = self.geography_manager.get_geography_code_for_geography(
            geography=geography,
            geography_type=main_geography_type,
        )

        upstream_relationships: OPTIONAL_UPSTREAM_RELATIONSHIPS = (
            get_upstream_relationships_for_geography(
                geography_code=geography_code,
                geography_type=main_geography_type,
            )
        )
        upstream_relationships = upstream_relationships or []

        try:
            related_geography: dict[str, str] = next(
                relationship
                for relationship in upstream_relationships
                if target_geography_type == relationship["geography_type"]
            )
        except StopIteration as error:
            raise GeographyNotFoundForAccompanyingPointError from error

        return related_geography["name"]

    def _create_null_geography_data(self, geography: str) -> MapGeographyResult:
        """
        Create null case data for geography with no available data.

        Args:
            geography: Geography name

        Returns:
            MapsGeographyResult with null metric value

        """
        try:
            geography_code = self.geography_manager.get_geography_code_for_geography(
                geography=geography,
                geography_type=self.maps_parameters.parameters.geography_type,
            )
        except Geography.DoesNotExist:
            geography_code = ""

        return MapGeographyResult(
            geography_type=self.maps_parameters.parameters.geography_type,
            geography=geography,
            geography_code=geography_code,
            metric_value=None,
            accompanying_points=None,
        )

    def _process_accompanying_points(
        self, geography: str
    ) -> list[AccompanyingPointResult]:
        """
        Process all accompanying points for a given geography.

        Args:
            geography: The main geography being processed

        Returns:
            List of processed accompanying point results

        """
        results = []

        for accompanying_point in self.maps_parameters.accompanying_points:
            params = accompanying_point.parameters

            try:
                selected_geography: str = (
                    self._get_related_geography_for_accompanying_point(
                        accompanying_point=accompanying_point,
                        main_geography=geography,
                    )
                )
            except GeographyNotFoundForAccompanyingPointError:
                continue

            accompanying_point_record = self.core_time_series_manager.query_for_data(
                theme=params.theme,
                sub_theme=params.sub_theme,
                topic=params.topic,
                metric=params.metric,
                geography=selected_geography,
                geography_type=params.geography_type,
                stratum=params.stratum,
                sex=params.sex,
                age=params.age,
                date_from=self.maps_parameters.date_from,
                date_to=self.maps_parameters.date_to,
                field_to_order_by="-date",
                rbac_permissions=self.maps_parameters.rbac_permissions,
            ).first()

            try:
                metric_value = accompanying_point_record.metric_value
            except AttributeError:
                metric_value = None

            results.append(
                AccompanyingPointResult(
                    label_prefix=accompanying_point.label_prefix,
                    label_suffix=accompanying_point.label_suffix,
                    metric_value=metric_value,
                )
            )

        return results

    def _query_main_data_for_geography(self, geography: str):
        """
        Query main time series data for a specific geography.

        Args:
            geography: Geography name to query

        Returns:
            Query result or None if no data found
        """
        params: MapMainParameters = self.maps_parameters.parameters

        return self.core_time_series_manager.query_for_data(
            theme=params.theme,
            sub_theme=params.sub_theme,
            topic=params.topic,
            metric=params.metric,
            geography=geography,
            geography_type=params.geography_type,
            stratum=params.stratum,
            sex=params.sex,
            age=params.age,
            date_from=self.maps_parameters.date_from,
            date_to=self.maps_parameters.date_to,
            field_to_order_by="-date",
            rbac_permissions=self.maps_parameters.rbac_permissions,
        ).first()

    def build_maps_data(self) -> tuple[list[MapGeographyResult], set[datetime.date]]:
        """
        Build complete maps data for all geographies.

        Returns:
            Tuple of (geography data list, set of associated dates)
        """
        self._ensure_geographies_are_populated()

        results: list[MapGeographyResult] = []
        associated_dates: set[datetime.date] = set()

        for geography in self.maps_parameters.parameters.geographies:
            main_result = self._query_main_data_for_geography(geography)

            if main_result is None:
                null_data = self._create_null_geography_data(geography)
                results.append(null_data)
                continue

            associated_dates.add(main_result.date)

            accompanying_points: list[AccompanyingPointResult] = (
                self._process_accompanying_points(geography)
            )

            geography_data = MapGeographyResult(
                geography_code=main_result.geography.geography_code,
                geography_type=self.maps_parameters.parameters.geography_type,
                geography=geography,
                metric_value=main_result.metric_value,
                accompanying_points=accompanying_points,
            )

            results.append(geography_data)

        return results, associated_dates


def get_maps_output(*, maps_parameters: MapsParameters) -> MapOutput:
    maps_interface = MapsInterface(maps_parameters=maps_parameters)
    return maps_interface.get_maps_data()
