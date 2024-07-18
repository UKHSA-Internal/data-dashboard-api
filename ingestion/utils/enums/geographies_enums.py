from enum import Enum


class GeographyType(Enum):
    NATION = "Nation"
    LOWER_TIER_LOCAL_AUTHORITY = "Lower Tier Local Authority"
    NHS_REGION = "NHS Region"
    NHS_TRUST = "NHS Trust"
    UPPER_TIER_LOCAL_AUTHORITY = "Upper Tier Local Authority"
    UKHSA_REGION = "UKHSA Region"
    GOVERNMENT_OFFICE_REGION = "Government Office Region"
    INTEGRATED_CARE_BOARD = "Integrated Care Board"
    SUB_INTEGRATED_CARE_BOARD = "Sub-Integrated Care Board"
