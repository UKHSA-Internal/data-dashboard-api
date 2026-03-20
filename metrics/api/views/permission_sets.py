from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from metrics.api.serializers.permission_sets import MetricRequestSerializer, PermissionSetResponseSerializer, SubThemeRequestSerializer, TopicRequestSerializer

PERMISSION_SETS_API_TAG = "data hierarchy"


@extend_schema(request=SubThemeRequestSerializer, tags=[PERMISSION_SETS_API_TAG], responses={HTTPStatus.OK.value: PermissionSetResponseSerializer})
class SubThemesByThemeView(APIView):
    """Get sub-themes filtered by theme ID"""
    permission_classes = []

    def get(self, request, theme_id, *args, **kwargs):
        """API endpoint to fetch sub-themes based on selected theme."""
        serializer = SubThemeRequestSerializer(data={'theme_id': theme_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data())


@extend_schema(request=TopicRequestSerializer, tags=[PERMISSION_SETS_API_TAG], responses={HTTPStatus.OK.value: PermissionSetResponseSerializer})
class TopicsBySubThemeView(APIView):
    """Get topics filtered by sub-theme ID"""
    permission_classes = []

    def get(self, request, sub_theme_id, *args, **kwargs):
        """API endpoint to fetch sub-themes based on selected theme."""
        serializer = TopicRequestSerializer(
            data={'sub_theme_id': sub_theme_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data())


@extend_schema(request=MetricRequestSerializer, tags=[PERMISSION_SETS_API_TAG], responses={HTTPStatus.OK.value: PermissionSetResponseSerializer})
class MetricsByTopicView(APIView):
    """Get metrics filtered by topic ID"""
    permission_classes = []

    def get(self, request, topic_id, *args, **kwargs):
        """API endpoint to fetch sub-themes based on selected theme."""
        serializer = MetricRequestSerializer(
            data={'topic_id': topic_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data())
