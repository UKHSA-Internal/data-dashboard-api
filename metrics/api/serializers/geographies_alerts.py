from rest_framework import serializers

from metrics.api.enums import Alerts
from metrics.data.models.core_models import Geography


class GeographiesForAlertsSerializer(serializers.Serializer):
    geography_code = serializers.CharField()

    def validate_geography_code(self, value) -> str:
        if not self.geography_manager.does_geography_code_exist(
            geography_code=value,
            geography_type_name=Alerts.ALERT_GEOGRAPHY_TYPE_NAME.value,
        ):
            raise serializers.ValidationError(
                {"name": "Please enter a valid geography code."}
            )

        return value

    @property
    def geography_manager(self):
        """
        Fetch the topic manager from the context if available.
        If not get the Manager which has been declared on the `Geography` model.
        """
        return self.context.get("geography_manager", Geography.objects)

    def data(self):
        return self.geography_manager.get_geography_codes_and_names_by_geography_type(
            geography_type_name=Alerts.ALERT_GEOGRAPHY_TYPE_NAME.value
        )
