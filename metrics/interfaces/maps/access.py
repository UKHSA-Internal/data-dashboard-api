from dataclasses import dataclass

from django.db.models.manager import Manager

from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models.map import MapsParameters

INDIVIDUAL_GEOGRAPHY_DATA_TYPE = dict[str, str | float | list[dict[str, str | float]]]


@dataclass
class MapOutput:
    data: list[INDIVIDUAL_GEOGRAPHY_DATA_TYPE]
    latest_date: str = ""

    def output(self) -> dict:
        return {
            "data": self.data,
            "latest_date": self.latest_date,
        }


def get_maps_output(*, maps_parameters: MapsParameters) -> MapOutput:
    maps_interface = MapsInterface(maps_parameters=maps_parameters)
    return maps_interface.get_maps_data()


class MapsInterface:
    def __init__(
        self,
        *,
        maps_parameters: MapsParameters,
        core_time_series_manager: type[Manager] = CoreTimeSeries.objects,
    ):
        self.maps_parameters = maps_parameters
        self.core_time_series_manager = core_time_series_manager

    def get_maps_data(self):
        return MapOutput(
            data=self.build_maps_data(),
            latest_date="2025-01-01",
        )

    def build_maps_data(self) -> list[INDIVIDUAL_GEOGRAPHY_DATA_TYPE]:
        main_params = self.maps_parameters.parameters
        results: list[dict] = []

        for geography in self.maps_parameters.parameters.geographies:
            main_result = self.core_time_series_manager.query_for_data(
                theme=main_params.theme,
                sub_theme=main_params.sub_theme,
                topic=main_params.topic,
                metric=main_params.metric,
                geography=geography,
                geography_type=main_params.geography_type,
                stratum=main_params.stratum,
                sex=main_params.sex,
                age=main_params.age,
                date_from=self.maps_parameters.date_from,
                date_to=self.maps_parameters.date_to,
                field_to_order_by="-date",
                rbac_permissions=self.maps_parameters.rbac_permissions,
            ).first()

            accompanying_points_results = []

            for accompanying_point in self.maps_parameters.accompanying_points:
                accompanying_point_params = accompanying_point.parameters

                accompanying_point_record = (
                    self.core_time_series_manager.query_for_data(
                        theme=accompanying_point_params.theme,
                        sub_theme=accompanying_point_params.sub_theme,
                        topic=accompanying_point_params.topic,
                        metric=accompanying_point_params.metric,
                        geography=accompanying_point_params.geography,
                        geography_type=accompanying_point_params.geography_type,
                        stratum=accompanying_point_params.stratum,
                        sex=accompanying_point_params.sex,
                        age=accompanying_point_params.age,
                        date_from=self.maps_parameters.date_from,
                        date_to=self.maps_parameters.date_to,
                        field_to_order_by="-date",
                        rbac_permissions=self.maps_parameters.rbac_permissions,
                    ).first()
                )

                accompanying_points_results.append(
                    {
                        "label_prefix": accompanying_point.label_prefix,
                        "label_suffix": accompanying_point.label_suffix,
                        "metric_value": accompanying_point_record.metric_value,
                    }
                )

            results.append(
                {
                    "geography_code": main_result.geography.geography_code,
                    "geography_type": main_params.geography_type,
                    "geography": geography,
                    "metric_value": main_result.metric_value,
                    "accompanying_points": accompanying_points_results,
                }
            )

        return results
