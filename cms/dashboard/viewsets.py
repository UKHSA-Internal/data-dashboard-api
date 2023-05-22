from drf_spectacular.utils import extend_schema
from rest_framework_api_key.permissions import HasAPIKey
from wagtail.api.v2.views import PagesAPIViewSet


@extend_schema(tags=["cms"])
class CMSPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = [HasAPIKey]
