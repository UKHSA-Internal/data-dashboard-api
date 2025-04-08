from django.db import models

from metrics.data.managers.rbac_models.rbac_group_permissions import (
    RBACGroupPermissionManager,
)
from metrics.data.models.rbac_models import help_texts


class RBACGroupPermission(models.Model):

    class Meta:
        db_table = "rbac_group_permissions"

    id = models.BigAutoField(primary_key=True)
    group_id = models.UUIDField(
        help_text=help_texts.RBAC_GROUP_ID,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(
        "RBACPermission", related_name="rbac_group_permissions"
    )

    objects = RBACGroupPermissionManager()

    def __str__(self):
        return f"{self.name} : ({self.group_id})"
