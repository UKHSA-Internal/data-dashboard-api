from django.db.models import Manager
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from cms.snippets.models import GlobalBanner


class GlobalBannerResponseSerializer(serializers.ModelSerializer):
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


class GlobalBannerSerializer(serializers.Serializer):
    @property
    def global_banner_manager(self) -> Manager:
        return self.context.get("global_banner_manager", GlobalBanner.objects)

    @property
    def data(self) -> dict[str, ReturnDict[str, str]]:
        active_global_banner_data: ReturnDict[str, str] = get_active_global_banners(
            global_banner_manager=self.global_banner_manager
        )
        return {"active_global_banners": active_global_banner_data}


class GlobalBannerSerializerV1(serializers.Serializer):
    @property
    def global_banner_manager(self) -> Manager:
        return self.context.get("global_banner_manager", GlobalBanner.objects)

    @property
    def data(self) -> dict[str, ReturnDict[str, str] | None]:
        active_global_banner_data: ReturnDict[str, str] | None = (
            get_active_global_banner(global_banner_manager=self.global_banner_manager)
        )
        return {"active_global_banner": active_global_banner_data}


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
    global_banner = global_banner_manager.get_active_banners().first()
    serializer = GlobalBannerResponseSerializer(instance=global_banner)
    return serializer.data


def get_active_global_banners(
    global_banner_manager: Manager,
) -> ReturnDict[str, str]:
    """Gets all currently active global banners

    Args:
        `global_banner_manager`: The `GlobalBanner`
            model manager used to query for records

    Returns:
        Dict representation of the active global banners.
        If there are no active global banners, then [] is returned.

    """
    global_banners = global_banner_manager.get_active_banners()
    serializer = GlobalBannerResponseSerializer(instance=global_banners, many=True)
    return serializer.data
