import logging

logger = logging.getLogger(__name__)


class GlobalFilterCMSBlockParser:
    DEFAULT_GEOGRAPHY_TYPE = "Upper Tier Local Authority"

    def __init__(self, global_filter: dict) -> None:
        self.global_filter = global_filter

    def get_time_periods_from_global_filter(self) -> list[dict[str, str]]:
        """Extract all time periods from the global filter

        Returns:
            List of dictionaries containing `date_from` and `date_to` keys

        """
        time_range_block = self.global_filter["value"]["time_range"]
        time_periods = time_range_block.get("time_periods", [])

        time_ranges: list[dict[str, str]] = []
        for time_period in time_periods:
            period_value = time_period.get("value", {})

            time_range = {
                "date_from": period_value["date_from"],
                "date_to": period_value["date_to"],
            }
            time_ranges.append(time_range)

        return time_ranges

    def get_rows(self) -> list[dict]:
        """Extract row values from the global filter.

        Returns:
            List of row value dictionaries

        """
        rows = self.global_filter["value"].get("rows", [])
        return [row.get("value", {}) for row in rows if "value" in row]

    @classmethod
    def get_main_geography_type(cls) -> str:
        """Get the main geography type for the data filters

        Notes:
            This is hardcoded for now to
            return UTLA.
            In future this should be derived from
            a selection made in the CMS

        Returns:
            The default geography type string

        """
        return cls.DEFAULT_GEOGRAPHY_TYPE

    def get_data_filters(self) -> list[dict]:
        """Extract data filter blocks from all rows.

        Returns:
            List of data filter dictionaries

        """
        data_filters = []
        rows = self.get_rows()

        for row in rows:
            filters = row.get("filters", [])
            for filter_block in filters:
                if filter_block.get("type") == "data_filters":
                    data_filters.append(filter_block)

        return data_filters

    @classmethod
    def get_all_individual_data_filter_selection(
        cls, *, data_filter: dict
    ) -> list[dict]:
        """Extract individual data filter selections.

        Args:
            data_filter: Data filter dictionary

        Returns:
            List of individual data filter selections
        """
        return data_filter.get("value", {}).get("data_filters", [])

    def build_main_params_for_payload_from_data_filter(
        self, *, data_filter: dict
    ) -> dict:
        """Build main parameters for payload from data filter.

        Args:
            data_filter: Individual data filter dictionary

        Returns:
            Dictionary of main parameters with geographies and geography_type
        """
        parameters = data_filter.get("parameters", {})
        main_params = self._extract_values(input_data=parameters)
        main_params.update(
            {"geographies": [], "geography_type": self.get_main_geography_type()}
        )
        return main_params

    @staticmethod
    def _extract_values(input_data: dict) -> dict:
        """Extract values from nested dictionary structure.

        Args:
            input_data: Dictionary with nested value structures

        Returns:
            Flattened dictionary with extracted values
        """
        result = {}

        for key, nested_dict in input_data.items():
            result[key] = nested_dict["value"]

        return result

    def build_complete_payloads_for_maps_api(self) -> list[dict]:
        """Build complete payloads by combining data filters and time periods.

        Returns:
            List of complete payload dictionaries which
            can be used as individual requests to the `maps` API

        """
        payloads = []

        data_filters = self.get_data_filters()
        time_periods = self.get_time_periods_from_global_filter()

        for data_filter in data_filters:
            individual_data_filters = self.get_all_individual_data_filter_selection(
                data_filter=data_filter
            )

            for individual_data_filter in individual_data_filters:
                filter_value = individual_data_filter.get("value", {})

                main_params = self.build_main_params_for_payload_from_data_filter(
                    data_filter=filter_value
                )
                accompanying_points = self._extract_accompanying_point_payloads(
                    data_filter=filter_value
                )

                base_payload = {
                    "parameters": main_params,
                    "accompanying_points": accompanying_points,
                }

                # Create a payload for each time period / data filter permutation
                for time_period in time_periods:
                    payload = {**base_payload, **time_period}
                    payloads.append(payload)

        return payloads

    def _extract_accompanying_point_payloads(self, *, data_filter: dict) -> list[dict]:
        """Extract accompanying point payloads from data filter.

        Args:
            data_filter: Data filter dictionary

        Returns:
            List of accompanying point payload dictionaries
        """
        accompanying_point_payloads = []
        accompanying_points = data_filter.get("accompanying_points", [])

        for accompanying_point in accompanying_points:
            payload = self._extract_accompanying_point_payload(
                accompanying_point=accompanying_point
            )
            accompanying_point_payloads.append(payload)

        return accompanying_point_payloads

    @classmethod
    def _extract_accompanying_point_payload(cls, *, accompanying_point: dict) -> dict:
        """Extract payload from a single accompanying point.

        Args:
            accompanying_point: Accompanying point dictionary

        Returns:
            Dictionary containing label_prefix, label_suffix, and parameters

        Raises:
            ValueError: If accompanying point structure is invalid
        """
        point_value = accompanying_point["value"]

        payload = {
            "label_prefix": point_value.get("label_prefix", ""),
            "label_suffix": point_value.get("label_suffix", ""),
            "parameters": {},
        }

        parameters = point_value.get("parameters", [])
        for parameter_block in parameters:
            if not isinstance(parameter_block, dict):
                continue

            field_type = parameter_block.get("type")
            param_value = parameter_block.get("value", {})

            if field_type and isinstance(param_value, dict) and "value" in param_value:
                payload["parameters"][field_type] = param_value["value"]

        return payload
