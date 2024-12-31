from caching.private_api.crawler.type_hints import CMS_COMPONENT_BLOCK_TYPE
from metrics.domain.common.utils import (
    DataSourceFileType,
    extract_metric_group_from_metric,
)


class RequestPayloadBuilder:
    @classmethod
    def build_headlines_request_data(
        cls, *, headline_number_block: dict[str, str]
    ) -> dict[str, str]:
        """Builds the headlines endpoint request payload from the given `headline_number_block`

        Args:
            headline_number_block: The headline number block
                from the CMS

        Returns:
            A dict which can be used as the payload to the
            `headlines` endpoint

        """
        return {
            "topic": headline_number_block["topic"],
            "metric": headline_number_block["metric"],
            "geography": headline_number_block.get("geography", "England"),
            "geography_type": headline_number_block.get("geography_type", "Nation"),
            "sex": headline_number_block.get("sex", "all"),
            "age": headline_number_block.get("age", "all"),
            "stratum": headline_number_block.get("stratum", "default"),
        }

    @classmethod
    def build_trend_request_data(
        cls, *, trend_number_block: dict[str, str]
    ) -> dict[str, str]:
        """Builds the trends endpoint request payload from the given `trend_number_block`

        Args:
            trend_number_block: The trends number block from the CMS

        Returns:
            A dict which can be used as the payload to the
            `trends` endpoint

        """
        # The basis of the trends request is the same as the headlines request payload
        request_data = cls.build_headlines_request_data(
            headline_number_block=trend_number_block
        )
        request_data["percentage_metric"] = trend_number_block["percentage_metric"]
        return request_data

    def build_chart_request_data(
        self, *, chart_block: CMS_COMPONENT_BLOCK_TYPE, chart_is_double_width: bool
    ) -> dict[str, str | int, list[dict[str, str]]]:
        """Builds the charts endpoint request payload from the given `chart_block`

        Args:
            chart_block: The chart block from the CMS
            chart_is_double_width: If True, a chart width of 1100 is applied.
                If False, a chart width of 515 is applied.

        Returns:
            A dict which can be used as the payload to the
            `charts` endpoint

        """
        return {
            "plots": [
                self._build_plot_data_for_chart(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
            "file_format": "svg",
            "chart_width": 1100 if chart_is_double_width else 515,
            "chart_height": 260,
            "x_axis": chart_block.get("x_axis", ""),
            "y_axis": chart_block.get("y_axis", ""),
            "x_axis_title": chart_block.get("x_axis_title", ""),
            "y_axis_title": chart_block.get("y_axis_title", ""),
        }

    @classmethod
    def _build_plot_data(cls, *, plot_value: dict[str, str]) -> dict[str, str]:
        """Builds the individual plot data from the given `plot_value`

        Args:
            plot_value: The dict containing the plot data

        Returns:
            A dict which can be used to represent the individual plot
            within the `plots` list of the payload
            to the `charts` or `tables` endpoint

        """
        plot_data = {
            "topic": plot_value["topic"],
            "metric": plot_value["metric"],
            "chart_type": plot_value["chart_type"],
            "stratum": plot_value["stratum"],
            "geography": plot_value["geography"],
            "geography_type": plot_value["geography_type"],
            "sex": plot_value["sex"],
            "age": plot_value["age"],
            "label": plot_value["label"],
            "line_colour": plot_value["line_colour"],
        }

        if DataSourceFileType[
            extract_metric_group_from_metric(plot_value["metric"])
        ].is_timeseries:
            plot_data["date_to"] = plot_value["date_to"]
            plot_data["date_from"] = plot_value["date_from"]
            plot_data["line_type"] = plot_value["line_type"]

        return plot_data

    @classmethod
    def _build_plot_data_for_chart(
        cls, *, plot_value: dict[str, str]
    ) -> dict[str, str]:
        """Builds the individual plot data from the given `plot_value`

        Args:
            plot_value: The dict containing the plot data

        Returns:
            A dict which can be used to represent the individual plot
            within the `plots` list of the payload
            to the `charts` or `tables` endpoint

        """
        plot_data: dict[str, str] = cls._build_plot_data(plot_value=plot_value)
        plot_data["use_markers"] = plot_value.get("use_markers", False)
        plot_data["use_smooth_lines"] = plot_value.get("use_smooth_lines", True)

        return plot_data

    def build_tables_request_data(
        self, *, chart_block: CMS_COMPONENT_BLOCK_TYPE
    ) -> dict[str, str | int, list[dict[str, str]]]:
        """Builds the tables endpoint request payload from the given `chart_block`

        Args:
            chart_block: The chart block from the CMS

        Returns:
            A dict which can be used as the payload to the
            `tables` endpoint

        """
        return {
            "plots": [
                self._build_plot_data(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
            "x_axis": chart_block["x_axis"],
            "y_axis": chart_block["y_axis"],
        }

    def build_downloads_request_data(
        self,
        *,
        chart_block: CMS_COMPONENT_BLOCK_TYPE,
        file_format: str,
    ) -> dict[str, str | int, list[dict[str, str]]]:
        """Builds the tables endpoint request payload from the given `chart_block`

        Args:
            chart_block: The chart block from the CMS
            file_format: The request format for downloaded data.

        Returns:
            A dict which can be used as the payload to the
            `tables` endpoint

        """
        return {
            "plots": [
                self.build_downloads_plot_data(plot_value=plot["value"])
                for plot in chart_block["chart"]
            ],
            "x_axis": chart_block["x_axis"],
            "file_format": file_format,
        }

    @classmethod
    def build_downloads_plot_data(cls, *, plot_value: dict[str, str]) -> dict[str, str]:
        """Builds the individual downloadable plot data from the given `plot_value`

        Args:
            plot_value: The dict containing the plot data

        Returns:
            A dict which can be used to represent the individual plot
            within the `plots` list of the payload
            to the `downloads` endpoint only

        """
        plot_data = {
            "topic": plot_value["topic"],
            "metric": plot_value["metric"],
            "stratum": plot_value["stratum"],
            "geography": plot_value["geography"],
            "geography_type": plot_value["geography_type"],
            "sex": plot_value["sex"],
            "age": plot_value["age"],
        }

        if DataSourceFileType[
            extract_metric_group_from_metric(plot_value["metric"])
        ].is_timeseries:
            plot_data["date_to"] = plot_value["date_to"]
            plot_data["date_from"] = plot_value["date_from"]

        return plot_data
