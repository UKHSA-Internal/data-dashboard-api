"""
Back-end source of truth for data classifications.

WARNING: The front-end repo has a copy of these constants that match.
"""


class DataClassificationInterface:
    # Fail-safe (if not provided)
    DEFAULT = "OFFICIAL-SENSITIVE"

    # Display labels for the classification values
    LIST = {
        "official": "OFFICIAL",
        "official_sensitive": "OFFICIAL-SENSITIVE",
        "protective_marking_not_set": "PROTECTIVE MARKING NOT SET",
        "secret": "SECRET",  # nosec #noqa: S105
        "top_secret": "TOP SECRET",  # nosec #noqa: S105
    }
