from enum import Enum


class DataSourceFileType(Enum):
    # Headline types
    headline = "headline"

    # Timeseries types
    cases = "cases"
    deaths = "deaths"
    healthcare = "healthcare"
    testing = "testing"
    vaccinations = "vaccinations"


class Topic(Enum):
    COVID_19 = "COVID-19"
    INFLUENZA = "Influenza"
    RSV = "RSV"
    HMPV = "hMPV"
    PARAINFLUENZA = "Parainfluenza"
    RHINOVIRUS = "Rhinovirus"
    ADENOVIRUS = "Adenovirus"


class GeographyType(Enum):
    NATION = "Nation"
    LOWER_TIER_LOCAL_AUTHORITY = "Lower Tier Local Authority"
    NHS_REGION = "NHS Region"
    NHS_TRUST = "NHS Trust"
    UPPER_TIER_LOCAL_AUTHORITY = "Upper Tier Local Authority"
    UKHSA_REGION = "UKHSA Region"
    GOVERNMENT_OFFICE_REGION = "Government Office Region"
