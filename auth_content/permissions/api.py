
from django.http import JsonResponse
from auth_content.models.permission_sets import PermissionSet
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def permission_sets_api(request):
    data = [
        {"id": str(p.id), "name": p.name}
        for p in PermissionSet.objects.all()
    ]
    return JsonResponse(data, safe=False)
