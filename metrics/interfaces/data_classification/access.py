from enum import Enum

class DataClassification(Enum):
    official = "OFFICIAL"
    official_sensitive = "OFFICIAL-SENSITIVE"  
    protective_marking_not_set = "PROTECTIVE MARKING NOT SET"
    secret = "SECRET" # nosec #noqa: S105
    top_secret = "TOP SECRET" # nosec #noqa: S105
