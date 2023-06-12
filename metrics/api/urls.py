import config
from metrics.api import settings
from metrics.api.urls_construction import construct_urlpatterns

urlpatterns = construct_urlpatterns(app_mode=config.APP_MODE)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
