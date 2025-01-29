from django.db import models


class Dataset(models.Model):

    class Meta:
        db_table = "datasets"

    dataset_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return (f"<Dataset"
                f" dataset_id={self.dataset_id}"
                f" name={self.name} />")
