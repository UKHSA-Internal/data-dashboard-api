import config


def frontend_url(request):
    return {"frontend_url": config.FRONTEND_URL}
