from django.db import models


class DatasetGroup(models.Model):

    class Meta:
        db_table = "data_groups"

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    datasets = models.ManyToManyField(
        "Dataset",
        through="GroupDatasetMapping",
        related_name="groups",
    )

    def __str__(self):
        return (f"<DatasetGroup "
                f"dataset_group_id={self.id} "
                f"name={self.name} />")
