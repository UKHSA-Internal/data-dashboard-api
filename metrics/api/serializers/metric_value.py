from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP


class MetricValueSerializer(serializers.Serializer):

    def format_to_one_decimal_place(value, places=1):
        """
        Ensure a Decimal value has at least the specified number of decimal places
        while maintaining the Decimal type.

        Args:
            value: The Decimal value to format
            places: Number of decimal places to ensure (default: 1)

        Returns:
            Decimal object with at least the specified decimal places
        """
        if value is None:
            return None

        # Convert to Decimal if not already
        if not isinstance(value, Decimal):
            value = Decimal(str(value))

        # Create the quantize template
        template = Decimal('0.' + '0' * (places-1) + '1')

        # Quantize to ensure the decimal places and return a Decimal object
        return value.quantize(template, rounding=ROUND_HALF_UP)
