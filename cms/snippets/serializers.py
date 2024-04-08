from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from cms.snippets.models import GlobalBanner


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
    def data(self) -> ReturnDict[str, str] | None:
        if self.instance is None:
            return None
        return super().data


def get_active_global_banner() -> ReturnDict[str, str] | None:

def get_active_global_banner(
    global_banner_manager: Manager,
) -> ReturnDict[str, str] | None:
    """Gets the currently active global banner information

    Args:
        `global_banner_manager`: The `GlobalBanner`
            model manager used to query for records

    Returns:
        Dict representation the of the active global banner.
        If no global banner is active, then None is returned

    """
    global_banner = global_banner_manager.get_active_banner()
    serializer = GlobalBannerResponseSerializer(instance=global_banner)
    return serializer.data
