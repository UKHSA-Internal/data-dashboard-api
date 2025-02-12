from django.db import models


class ApiGroup(models.Model):

    class Meta:
        db_table = "api_groups"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    permissions = models.ManyToManyField(
        "data.ApiPermission", related_name="api_groups"
    )

    def __str__(self):
        return self.name
