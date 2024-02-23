from enum import Enum


class AppMode(Enum):
    CMS_ADMIN = "CMS_ADMIN"
    PRIVATE_API = "PRIVATE_API"
    PUBLIC_API = "PUBLIC_API"
    FEEDBACK_API = "FEEDBACK_API"
    INGESTION = "INGESTION"

    @classmethod
    def dependent_on_db(cls) -> list[str]:
        return [
            cls.CMS_ADMIN.value,
            cls.PRIVATE_API.value,
            cls.PUBLIC_API.value,
            cls.INGESTION.value,
        ]

    @classmethod
    def dependent_on_cache(cls) -> list[str]:
        return [cls.PRIVATE_API.value]
