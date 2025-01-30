from django.db import models


class DatasetGroupMapping(models.Model):

    class Meta:
        db_table = "dataset_group_mappings"
        unique_together = ('dataset_name', 'group')

    id = models.BigAutoField(primary_key=True)
    dataset_name = models.CharField(max_length=255)
    group = models.ForeignKey("DatasetGroup", on_delete=models.CASCADE, related_name='group_mappings')

    def __str__(self):
        return f"(Dataset Name: {self.dataset_name}), (Group: {self.group.name})"
