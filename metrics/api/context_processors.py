from rest_framework.request import Request

import config


def frontend_url(request: Request) -> dict[str, str]:
    return {"frontend_url": config.FRONTEND_URL}
