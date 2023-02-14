from django.db import models


class WeeklyTimeSeries(models.Model):
    parent_theme = models.CharField(max_length=30)
    child_theme = models.CharField(max_length=30)
    topic = models.CharField(max_length=30)
    geography_type = models.CharField(max_length=30)
    geography = models.CharField(max_length=30)
    metric = models.CharField(max_length=30)
    stratum = models.CharField(max_length=30)
    year = models.IntegerField()
    epiweek = models.IntegerField()
    start_date = models.DateField(max_length=30)
    metric_value = models.FloatField(max_length=30)

    def __str__(self):
        return f"Data for {self.start_date}, metric '{self.metric}', stratum '{self.stratum}', value: {self.metric_value}"


