from metrics.api.serializers.downloads.single_category import (
    DownloadListSerializer,
    SingleCategoryDownloadsSerializer,
)


class DualCategoryDownloadSerializer(SingleCategoryDownloadsSerializer):
    plots = DownloadListSerializer()
