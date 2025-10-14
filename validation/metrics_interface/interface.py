from metrics.data.enums import TimePeriod
from metrics.domain.common.utils import DataSourceFileType


class MetricsAPIInterface:
    @staticmethod
    def get_datasource_enum() -> DataSourceFileType:
        return DataSourceFileType

    @staticmethod
    def get_time_period_enum() -> TimePeriod:
        return TimePeriod
