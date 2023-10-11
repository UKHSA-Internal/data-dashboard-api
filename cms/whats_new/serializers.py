from rest_framework import serializers


class BadgeSerializer(serializers.Serializer):
    text = serializers.CharField()
    colour = serializers.CharField()
