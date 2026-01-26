from .default import *

match config.APIENV:
    case "LOCAL":
        from .local import *
    case "STANDALONE":
        from .standalone import *

match config.APP_MODE:
    case "INGESTION":
        from .ingestion import *
    case "PUBLIC_API":
        from .public_api import *
    case "PRIVATE_API":
        from .private_api import *
    case "FEEDBACK_API":
        from .feedback_api import *
    case "UTILITY_WORKER":
        from .backend_utility_worker import *
    case "CMS_ADMIN":
        from .cms_admin import *
