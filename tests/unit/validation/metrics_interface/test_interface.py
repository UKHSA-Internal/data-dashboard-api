from metrics.domain.common.utils import DataSourceFileType
from validation.metrics_interface import interface


class TestMetricsAPIInterface:

    def test_get_datasource_enum(self):
        """
        Given an instance of the `MetricsAPIInterface`
        When `get_datasource_enum()` is called from that object
        Then the `DataSourceFileType` enum is returned
        """
        # Given
        metrics_api_interface = interface.MetricsAPIInterface()

        # When
        data_source_enum = metrics_api_interface.get_datasource_enum()

        # Then
        assert data_source_enum is DataSourceFileType
