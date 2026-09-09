from wagtail.api.v2.views import PageSerializer

from cms.dashboard.fields import ListablePageParentField


class ListablePageSerializer(PageSerializer):
    parent = ListablePageParentField(read_only=True)
