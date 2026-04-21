from http import HTTPStatus

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.user import (
    UserHierarchyRequestSerializer,
    UserPermissionSetResponseSerializer,
    UserRequestSerializer,
)

USER_API_TAG = "Authenticated User"


@extend_schema(
    request=UserRequestSerializer,
    tags=[USER_API_TAG],
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=str,
            location=OpenApiParameter.PATH,
            description="UUID of the user",
        )
    ],
    responses={
        HTTPStatus.OK.value: UserPermissionSetResponseSerializer,
        403: {"description": "Not authorized to view these permissions"},
        404: {"description": "User not found or has no permissions"},
    },
)
class UserPermissionSetsByUserIdView(APIView):
    """Get user permission sets filtered by user ID"""

    permission_classes = []

    def get(self, request, user_id, *args, **kwargs):  # noqa: PLR6301
        """API endpoint to fetch a users assigned permission sets using user_id"""
        serializer = UserRequestSerializer(data={"user_id": user_id})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data())


@extend_schema(
    request=UserRequestSerializer,
    tags=[USER_API_TAG],
    parameters=[
        OpenApiParameter(
            name="user_id",
            type=str,
            location=OpenApiParameter.PATH,
            description="UUID of the user",
        ),
        OpenApiParameter(
            name="group_by",
            type=str,
            location=OpenApiParameter.QUERY,
            description="Optional grouping strategy: 'geography_type', or 'theme'",
            required=False,
            enum=["geography_type", "theme"],
        ),
    ],
    responses={
        HTTPStatus.OK.value: UserPermissionSetResponseSerializer,
        400: {"description": "Invalid group_by parameter"},
        403: {"description": "Not authorized to view these permissions"},
        404: {"description": "User not found or has no permissions"},
    },
)
class UserPermissionHierarchyByUserIdView(APIView):
    """Get user permission sets filtered by user ID with optional grouping"""

    permission_classes = []

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
