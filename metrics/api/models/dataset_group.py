from django.db import models


class DatasetGroup(models.Model):

    class Meta:
        db_table = "dataset_groups"

    group_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
