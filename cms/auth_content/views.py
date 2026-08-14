from django.http import StreamingHttpResponse

from cms.auth_content.models.users import User
from cms.auth_content.exporters import generate_user_permission_sets_csv_rows


def export_user_permission_sets_csv(request):
    users = User.objects.with_permission_sets()
    response = StreamingHttpResponse(
        generate_user_permission_sets_csv_rows(users),
        content_type="text/csv",
    )
    response["Content-Disposition"] = 'attachment; filename="dashboard_cms_users.csv"'
    return response
