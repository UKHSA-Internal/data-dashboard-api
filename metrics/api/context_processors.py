from typing import Dict

from rest_framework.request import Request

import config


def frontend_url(request: Request) -> Dict[str, str]:
    return {"frontend_url": config.FRONTEND_URL}
