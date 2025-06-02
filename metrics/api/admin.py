from django.contrib import admin

from metrics.data.models.rbac_models import RBACGroupPermission, RBACPermission

admin.site.register(RBACPermission)
admin.site.register(RBACGroupPermission)
