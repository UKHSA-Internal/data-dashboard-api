from datetime import datetime
from django.http import StreamingHttpResponse
import logging

from cms.auth_content.models.users import User
from cms.auth_content.exporters import generate_user_permission_sets_csv_rows

from metrics.api.middleware.current_user import get_current_user


audit_logger = logging.getLogger("audit")


def export_user_permission_sets_csv(request):
    user = get_current_user()
    user_id = user.id if user and user.is_authenticated else "anonymous"
    audit_logger.info(
        "User permission sets relationships cleared",
        extra={
            "user": user_id,
            "action": "CSV EXPORT",
            "target": "Users and permissions"
        },
    )

    users = User.objects.with_permission_sets()
    response = StreamingHttpResponse(
        generate_user_permission_sets_csv_rows(users),
        content_type="text/csv",
    )
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    response["Content-Disposition"] = f'attachment; filename="dashboard_cms_users_{timestamp}.csv"'
    return response
