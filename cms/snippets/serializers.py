from rest_framework import serializers

from cms.snippets.models import GlobalBanner
from rest_framework.utils.serializer_helpers import ReturnDict


class ButtonSerializer(serializers.Serializer):
    text = serializers.CharField()
    loading_text = serializers.CharField()
    endpoint = serializers.CharField()
    method = serializers.CharField()
    button_type = serializers.CharField()


class ExternalButtonSerializer(serializers.Serializer):
    text = serializers.CharField()
    url = serializers.CharField()
    button_type = serializers.CharField()
    icon = serializers.CharField()


class GlobalBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalBanner
        fields = [
            "title",
            "body",
            "banner_type",
        ]

    @property
    def data(self) -> ReturnDict | None:
        if self.instance is None:
            return None
        return super().data


def get_active_global_banner() -> ReturnDict | None:
    """Gets the currently active global banner information

    Returns:
        Dict representation the of the active global banner.
        If no global banner is active, then None is returned

    """
    global_banner = GlobalBanner.objects.get_active_banner()
    serializer = GlobalBannerSerializer(instance=global_banner)
    return serializer.data
