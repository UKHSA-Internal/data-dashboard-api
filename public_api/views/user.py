from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from metrics.api.serializers.user import (
    UserHierarchyRequestSerializer,
)

PUBLIC_API_TAG = "public-api"

class UserPermissionSetsByUserIdView(GenericAPIView):
    @extend_schema(tags=[PUBLIC_API_TAG])
    def get(self, request, user_id, *args, **kwargs):  # noqa: PLR6301
        """API endpoint to fetch a user's assigned permission set hierarchy using user_id"""
        # Pass query parameter to serializer
        serializer = UserHierarchyRequestSerializer(
            data={
                "user_id": user_id,
                "group_by": request.query_params.get("group_by", ""),
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data())
