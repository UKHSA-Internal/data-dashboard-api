from django.db import models


class BadgeColours(models.Choices):
    """Enum for badge colours which conform to the GDS specification for tags

    References:
        - https://design-system.service.gov.uk/components/tag/all-colours/index.html

    """

    BLUE = "BLUE"
    GREEN = "GREEN"
    GREY = "GREY"
    ORANGE = "ORANGE"
    PINK = "PINK"
    PURPLE = "PURPLE"
    RED = "RED"
    TURQUOISE = "TURQUOISE"
    YELLOW = "YELLOW"
