from metrics.domain.common.utils import DataSourceFileType


class MetricsAPIInterface:
    @staticmethod
    def get_datasource_enum() -> DataSourceFileType:
        return DataSourceFileType
