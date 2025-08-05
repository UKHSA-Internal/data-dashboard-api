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
        """Gets the complete maps data output along with the latest date associated with the data.

        Returns:
            A `MapOutput` object containing
            all the processed data and
            the latest associated date.

        """
        results, associated_dates = self.build_maps_data()
        latest_date = max(associated_dates, default=None)

        return MapOutput(
            data=results,
            latest_date=latest_date,
        )

    def build_maps_data(self) -> tuple[list[MapGeographyResult], set[datetime.date]]:
        """Gets the results for all the requested geographies across the map as well as the associated dates.

        Notes:
            If a specific geography cannot be found,
            then the result will be returned with None
            in place for the requisite fields.

        Returns:
            Tuple of (list of enriched `MapGeographyResult`, and a set of associated dates)

        """
        self._ensure_geographies_are_populated_for_main_parameters()

        results: list[MapGeographyResult] = []
        associated_dates: set[datetime.date] = set()

        for geography in self.maps_parameters.parameters.geographies:
            main_result = self._query_for_main_data_geography(geography=geography)

            if main_result is None:
                null_result_for_geography: MapGeographyResult = (
                    self._create_null_geography_result(geography=geography)
                )
                results.append(null_result_for_geography)
                continue

            associated_dates.add(main_result.date)

            accompanying_points: list[AccompanyingPointResult] = (
                self._process_accompanying_points(geography=geography)
            )
            result_for_geography = MapGeographyResult(
                geography_code=main_result.geography.geography_code,
                geography_type=self.maps_parameters.parameters.geography_type,
                geography=geography,
                metric_value=main_result.metric_value,
                accompanying_points=accompanying_points,
            )

            results.append(result_for_geography)

        return results, associated_dates

    def _ensure_geographies_are_populated_for_main_parameters(self) -> None:
        if not self.maps_parameters.parameters.geographies:
            self.maps_parameters.parameters.geographies = (
                self.geography_manager.get_all_geography_names_by_geography_type(
                    geography_type_name=self.maps_parameters.parameters.geography_type,
                )
            )

    def _get_related_geography_for_accompanying_point(
        self, *, accompanying_point, main_geography: str
    ) -> str | None:
        """Gets the related geography for the accompanying point if required.

        Args:
            accompanying_point: The accompanying point configuration
            main_geography: The main geography being processed

        Returns:
            The related geography name for the given accompanying point.

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
        self, *, geography: str, main_geography_type: str, target_geography_type: str
    ) -> str:
        """
        Fetch related geography for the specified geography type.

        Args:
            geography: Source geography name
            main_geography_type: Type of the main geography
            target_geography_type: Target geography type to find

        Returns:
            Related geography name or None if not found

        Raises:
            `GeographyNotFoundForAccompanyingPointError`: If
                a given geography cannot be found
                for the accompanying point

        """
        try:
            geography_code: str = (
                self.geography_manager.get_geography_code_for_geography(
                    geography=geography,
                    geography_type=main_geography_type,
                )
            )
        except Geography.DoesNotExist as error:
            raise GeographyNotFoundForAccompanyingPointError from error

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

    def _create_null_geography_result(self, *, geography: str) -> MapGeographyResult:
        """Creates a `MapGeographyResult` object for the given geography to act as the null case for that data point.

        Args:
            geography: The name of the geography being processed

        Returns:
            A `MapsGeographyResult` object with None
            in place for the requisite fields

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
        self, *, geography: str
    ) -> list[AccompanyingPointResult]:
        """Process all accompanying points for a given geography.

        Notes:
            If an accompanying point cannot be handled
            for the geography, it will be skipped.

        Args:
            geography: The name of the geography being processed

        Returns:
            List of processed accompanying point results

        """
        results: list[AccompanyingPointResult] = []

        for accompanying_point in self.maps_parameters.accompanying_points:
            accompanying_point_result: AccompanyingPointResult | None = (
                self._process_accompanying_point(
                    accompanying_point=accompanying_point,
                    geography=geography,
                )
            )

            if accompanying_point_result:
                results.append(accompanying_point_result)

        return results

    def _process_accompanying_point(
        self, *, accompanying_point, geography: str
    ) -> AccompanyingPointResult | None:
        """Build the resul for a given accompanying_point / geography combination.

        Notes:
            If the selected geography cannot be found,
            either as an explicit selection or via
            relationships then None will be returned.

            If an accompanying point cannot be handled
            for the geography, None will be returned
            for the `metric_value` field

        Args:
            geography: The name of the geography being processed

        Returns:
            An individual `AccompanyingPointResult` object
            containing the associated labels and the `metric_value`

        """
        params = accompanying_point.parameters

        try:
            selected_geography: str = (
                self._get_related_geography_for_accompanying_point(
                    accompanying_point=accompanying_point,
                    main_geography=geography,
                )
            )
        except GeographyNotFoundForAccompanyingPointError:
            return None

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

        return AccompanyingPointResult(
            label_prefix=accompanying_point.label_prefix,
            label_suffix=accompanying_point.label_suffix,
            metric_value=metric_value,
        )

    def _query_for_main_data_geography(self, *, geography: str):
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


def get_maps_output(*, maps_parameters: MapsParameters) -> MapOutput:
    maps_interface = MapsInterface(maps_parameters=maps_parameters)
    return maps_interface.get_maps_data()
