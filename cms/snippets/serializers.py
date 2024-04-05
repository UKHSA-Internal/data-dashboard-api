from rest_framework import serializers

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
