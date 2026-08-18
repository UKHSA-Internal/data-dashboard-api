import logging
from datetime import datetime

from django.http import StreamingHttpResponse
from django.views.decorators.http import require_http_methods

from cms.auth_content.exporters import generate_user_permission_sets_csv_rows
from cms.auth_content.models.users import User

audit_logger = logging.getLogger("audit")


@require_http_methods(["GET"])
def export_user_permission_sets_csv(request):
    user_id = (
        request.user.id
        if request.user and request.user.is_authenticated
        else "anonymous"
    )
    audit_logger.info(
        "User permission sets relationships cleared",
        extra={
            "user": user_id,
            "action": "CSV EXPORT",
            "target": "Users and permissions",
        },
    )

    users = User.objects.with_permission_sets()
    response = StreamingHttpResponse(
        generate_user_permission_sets_csv_rows(users),
        content_type="text/csv",
    )
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    response["Content-Disposition"] = (
        f'attachment; filename="dashboard_cms_users_{timestamp}.csv"'
    )
    return response
