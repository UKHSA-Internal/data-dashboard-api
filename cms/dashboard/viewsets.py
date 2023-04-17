from rest_framework_api_key.permissions import HasAPIKey
from wagtail.api.v2.views import PagesAPIViewSet


class CMSPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = [HasAPIKey]
