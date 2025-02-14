from django.db import models


class RBACGroupPermission(models.Model):

    class Meta:
        db_table = "rbac_group_permissions"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(
        "RBACPermission", related_name="rbac_group_permissions"
    )

    def __str__(self):
        return self.name
