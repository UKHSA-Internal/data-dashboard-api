from django.core.exceptions import ValidationError
from django.db import models

from metrics.data.managers.rbac_models.rbac_permissions import RBACPermissionManager


class AdminFormThemeSubthemeError(ValidationError):
    def __init__(self):
        message = "You must select a theme & a subtheme."
        super().__init__(message)


class AdminFormSubthemeAssocThemeError(ValidationError):
    def __init__(self):
        message = "The selected subtheme must belong to the selected theme."
        super().__init__(message)


class AdminFormTopicAssocSubthemeError(ValidationError):
    def __init__(self):
        message = "The selected topic's subtheme must have an associated theme."
        super().__init__(message)


class AdminFormSubthemeAssocTopicError(ValidationError):
    def __init__(self):
        message = "The selected subtheme must have an associated topic."
        super().__init__(message)


class AdminFormDuplicatePermissionError(ValidationError):
    def __init__(self):
        message = "A permission with these values already exists."
        super().__init__(message)


class RBACPermission(models.Model):

    class Meta:
        db_table = "rbac_permissions"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "theme",
                    "sub_theme",
                    "topic",
                    "metric",
                    "geography_type",
                    "geography",
                    "age",
                    "stratum",
                ],
                name="unique_permission_fields",
            )
        ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)
    theme = models.ForeignKey(
        "Theme", on_delete=models.CASCADE, related_name="theme_permissions"
    )
    sub_theme = models.ForeignKey(
        "SubTheme", on_delete=models.CASCADE, related_name="sub_theme_permissions"
    )
    topic = models.ForeignKey(
        "Topic",
        on_delete=models.CASCADE,
        related_name="topic_permissions",
        null=True,
        blank=True,
    )
    metric = models.ForeignKey(
        "Metric",
        on_delete=models.CASCADE,
        related_name="metric_permissions",
        null=True,
        blank=True,
    )
    geography_type = models.ForeignKey(
        "GeographyType",
        on_delete=models.CASCADE,
        related_name="geography_type_permissions",
        null=True,
        blank=True,
    )
    geography = models.ForeignKey(
        "Geography",
        on_delete=models.CASCADE,
        related_name="geography_permissions",
        null=True,
        blank=True,
    )
    age = models.ForeignKey(
        "Age",
        on_delete=models.CASCADE,
        related_name="age_permissions",
        null=True,
        blank=True,
    )
    stratum = models.ForeignKey(
        "Stratum",
        on_delete=models.CASCADE,
        related_name="stratum_permissions",
        null=True,
        blank=True,
    )

    objects = RBACPermissionManager()

    def __str__(self):
        model_str = f"name={self.name}, "
        model_str += f"theme={self.theme.name}, "
        model_str += f"sub_theme={self.sub_theme.name}"
        if self.topic is not None:
            model_str += f", topic={self.topic.name}"
        if self.metric is not None:
            model_str += f", metric={self.metric.name}"
        if self.geography_type is not None:
            model_str += f", geography_type={self.geography_type.name}"
        if self.geography is not None:
            model_str += f", geography={self.geography.name}"
        if self.age is not None:
            model_str += f", age={self.age.name}"
        if self.stratum is not None:
            model_str += f", stratum={self.stratum.name}"
        return model_str

    def clean(self):
        super().clean()
        if not getattr(self, "theme", None) or not getattr(self, "sub_theme", None):
            raise AdminFormThemeSubthemeError
        if self.sub_theme.theme != self.theme:
            raise AdminFormSubthemeAssocThemeError
        if self.topic:
            if self.topic.sub_theme.theme != self.theme:
                raise AdminFormTopicAssocSubthemeError
            if self.sub_theme.name != self.topic.sub_theme.name:
                raise AdminFormSubthemeAssocTopicError

        """Validates that there are no duplicate permissions with the same fields."""
        rbac_permissions = RBACPermission.objects.get_existing_permissions(self)
        if rbac_permissions.exists():
            raise AdminFormDuplicatePermissionError

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
