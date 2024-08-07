from rest_framework import serializers


class ButtonSerializer(serializers.Serializer):
    text = serializers.CharField()
    loading_text = serializers.CharField()
    endpoint = serializers.CharField()
    method = serializers.CharField()
    button_type = serializers.CharField()


class InternalButtonSerializer(serializers.Serializer):
    text = serializers.CharField()
    button_type = serializers.CharField()
    endpoint = serializers.CharField()
    method = serializers.CharField()


class ExternalButtonSerializer(serializers.Serializer):
    text = serializers.CharField()
    url = serializers.CharField()
    button_type = serializers.CharField()
    icon = serializers.CharField()
