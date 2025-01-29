from django.db import models
"""
-  Create indexes for group_dataset_mapping
"""


class GroupDatasetMapping(models.Model):

    class Meta:
        db_table = "group_dataset_mappings"
        unique_together = ("dataset_group", "dataset")

    dataset_group = models.ForeignKey("DatasetGroup", on_delete=models.CASCADE)
    dataset = models.ForeignKey("Dataset", on_delete=models.CASCADE)

    def __str__(self):
        return (f"<GroupDatasetMapping"
                f"dataset_group={self.dataset_group}"
                f"dataset={self.dataset} />")
