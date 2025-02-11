from django.db import models
from django.core.exceptions import ValidationError


class ApiPermission(models.Model):

    class Meta:
        db_table = "api_permissions"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "theme", "sub_theme", "topic", "metric",
                    "geography_type", "geography", "age", "stratum"
                ],
                name="unique_permission_fields"
            )
        ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)
    theme = models.ForeignKey(
        "data.Theme", on_delete=models.CASCADE, related_name="theme_permissions"
    )
    sub_theme = models.ForeignKey(
        "data.SubTheme", on_delete=models.CASCADE, related_name="sub_theme_permissions"
    )
    topic = models.ForeignKey(
        "data.Topic",
        on_delete=models.CASCADE,
        related_name="topic_permissions",
        null=True,
        blank=True,
    )
    metric = models.ForeignKey(
        "data.Metric",
        on_delete=models.CASCADE,
        related_name="metric_permissions",
        null=True,
        blank=True,
    )
    geography_type = models.ForeignKey(
        "data.GeographyType",
        on_delete=models.CASCADE,
        related_name="geography_type_permissions",
        null=True,
        blank=True,
    )
    geography = models.ForeignKey(
        "data.Geography",
        on_delete=models.CASCADE,
        related_name="geography_permissions",
        null=True,
        blank=True,
    )
    age = models.ForeignKey(
        "data.Age",
        on_delete=models.CASCADE,
        related_name="age_permissions",
        null=True,
        blank=True,
    )
    stratum = models.ForeignKey(
        "data.Stratum",
        on_delete=models.CASCADE,
        related_name="stratum_permissions",
        null=True,
        blank=True,
    )

    def __str__(self):
        model_str = f"name={self.name}, "
        model_str += f"theme={self.theme.name}, "
        model_str += f"sub_theme={self.sub_theme.name}"
        if self.topic is not None:
            model_str += f", topic={self.topic.name}"
        if self.metric is not None:
            model_str += f", metric={self.metric.name}"
        if self.geography_type is not None:
            f", geography_type={self.geography_type.name}"
        if self.geography is not None:
            f", geography={self.geography.name}"
        if self.age is not None:
            f", age={self.geography.name}"
        if self.stratum is not None:
            model_str += f", stratum={self.stratum.name}"
        return model_str

    def clean(self):
        if ApiPermission.objects.filter(
            theme=self.theme,
            sub_theme=self.sub_theme,
            topic=self.topic,
            metric=self.metric,
            geography_type=self.geography_type,
            geography=self.geography,
            age=self.age,
            stratum=self.stratum,
        ).exclude(pk=self.pk).exists():
            raise ValidationError("A permission with these values already exists.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)