from rest_framework import serializers


class ButtonSerializer(serializers.Serializer):
    text = serializers.CharField()
    loading_text = serializers.CharField()
    link = serializers.CharField()
    button_type = serializers.CharField()
