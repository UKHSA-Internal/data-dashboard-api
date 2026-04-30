from http import HTTPStatus

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from metrics.api.serializers.user import (
    FlatPermissionHierarchyResponseSerializer,
    GroupedByGeographyTypeResponseSerializer,
    GroupedByThemeResponseSerializer,
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
            description=(
                "Optional grouping strategy:\n"
                "- (omitted): Returns flat list of deduplicated permissions\n"
                "- 'geography_type': Groups by geography type → geography → permissions\n"
                "- 'theme': Groups by theme → sub_theme → topic → geographies"
            ),
            required=False,
            enum=["geography_type", "theme"],
        ),
    ],
    responses={
        200: FlatPermissionHierarchyResponseSerializer,  # Use one as the default schema
        400: {"description": "Invalid group_by parameter or user_id format"},
        403: {"description": "Not authorized to view these permissions"},
        404: {"description": "User not found or has no permissions"},
    },
    examples=[
        OpenApiExample(
            name="No grouping (default)",
            description="Flat list of deduplicated permissions with summary",
            value={
                "permission_sets": [
                    {
                        "theme": {"id": "2", "name": "infectious_disease"},
                        "sub_theme": {"id": "2", "name": "respiratory"},
                        "topic": {"id": "3", "name": "COVID-19"},
                        "metric": {"id": "-1", "name": "* (All)"},
                        "geography_type": {"id": "3", "name": "Nation"},
                        "geography": {"id": "E92000001", "name": "England"}
                    }
                ],
                "summary": {
                    "total_permission_sets": 1,
                    "deduplicated_count": 1,
                    "removed_count": 0,
                    "has_global_access": False,
                    "wildcard_themes": []
                }
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Grouped by geography_type",
            description="Nested structure grouped by geography type",
            value={
                "permission_sets": {
                    "3": {
                        "geography_type_name": "Nation",
                        "geographies": {
                            "E92000001": {
                                "geography_name": "England",
                                "permissions": [
                                    {
                                        "themes": [{"id": "2", "name": "infectious_disease"}],
                                        "sub_themes": [{"id": "2", "name": "respiratory"}],
                                        "topics": [{"id": "3", "name": "COVID-19"}],
                                        "metrics": [{"id": "-1", "name": "* (All)"}]
                                    }
                                ]
                            }
                        }
                    }
                },
                "total_permissions": 1
            },
            response_only=True,
        ),
        OpenApiExample(
            name="Grouped by theme",
            description="Nested structure grouped by theme hierarchy",
            value={
                "permission_sets": {
                    "2": {
                        "theme_name": "infectious_disease",
                        "sub_themes": {
                            "2": {
                                "sub_theme_name": "respiratory",
                                "topics": {
                                    "3": {
                                        "topic_name": "COVID-19",
                                        "geographies": [
                                            {
                                                "geography_types": [{"id": "3", "name": "Nation"}],
                                                "geographies": [{"id": "E92000001", "name": "England"}],
                                                "metrics": [{"id": "-1", "name": "* (All)"}]
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                },
                "total_permissions": 1
            },
            response_only=True,
        ),
    ],
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
