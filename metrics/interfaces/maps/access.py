from metrics.data.models.core_models import CoreTimeSeries
from metrics.domain.models.map import MapsParameters


def get_maps_data(*, maps_parameters: MapsParameters):
    maps_interface = MapsInterface(maps_parameters=maps_parameters)
    return maps_interface.get_maps_data()


class MapsInterface:
    def __init__(
        self,
        *,
        maps_parameters: MapsParameters,
        core_time_series_manager = CoreTimeSeries.objects,
    ):
        self.maps_parameters = maps_parameters
        self.core_time_series_manager = core_time_series_manager

    def get_maps_data(self):
        return {}