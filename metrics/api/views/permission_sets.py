from http import HTTPStatus

from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from metrics.api.serializers.permission_sets import PermissionSetResponseSerializer, SubThemeRequestSerializer

PERMISSION_SETS_API_TAG = "data hierarchy"


@extend_schema(request=PermissionSetResponseSerializer, tags=[PERMISSION_SETS_API_TAG], responses={HTTPStatus.OK.value: PermissionSetResponseSerializer})
class SubThemesByThemeView(APIView):
    """Get sub-themes filtered by theme ID"""
    permission_classes = []

    def get(self, request, theme_id, *args, **kwargs):
        """API endpoint to fetch sub-themes based on selected theme."""
        serializer = SubThemeRequestSerializer(data={'theme_id': theme_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data())


@extend_schema(tags=[PERMISSION_SETS_API_TAG])
class TopicsBySubThemeView(APIView):
    """Get topics filtered by sub-theme ID"""
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """API endpoint to fetch topics based on selected sub-theme."""
        sub_theme_id = self.kwargs['sub_theme_id']

        if not sub_theme_id:
            return Response({'error': 'sub_theme_id required'}, status=status.HTTP_400_BAD_REQUEST)

        if sub_theme_id == "-1":
            return Response({'choices': [["-1", "* (All topics)"]]})

        try:
            # Your interface call here
            return Response({
                'choices': [
                    ['10', 'COVID-19'],
                    ['11', 'Influenza'],
                    ['12', 'Measles']
                ],
                'sub_theme_id_received': sub_theme_id
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(tags=[PERMISSION_SETS_API_TAG])
class MetricsByTopicView(APIView):
    """Get metrics filtered by topic ID"""
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """API endpoint to fetch metrics based on selected topic."""
        topic_id = self.kwargs['topic_id']

        if not topic_id:
            return Response({'error': 'topic_id required'}, status=status.HTTP_400_BAD_REQUEST)

        if topic_id == "-1":
            return Response({'choices': [["-1", "* (All metrics)"]]})

        try:
            # Your interface call here
            return Response({
                'choices': [
                    ['100', 'Cases per 100k'],
                    ['101', 'Deaths total'],
                    ['102', 'Hospital admissions']
                ],
                'topic_id_received': topic_id
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
