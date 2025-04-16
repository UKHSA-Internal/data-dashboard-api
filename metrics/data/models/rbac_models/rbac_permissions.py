from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Model

from metrics.data.managers.rbac_models import RBACPermissionQuerySet
from metrics.data.managers.rbac_models.rbac_permissions import RBACPermissionManager


class NoSelectionMadeError(ValidationError):
    def __init__(self):
        message = "You must make some form of selection."
        super().__init__(message=message)


class NoModelSelectedError(ValidationError):
    def __init__(self, category: str):
        message = f"You must select a {category}."
        super().__init__(message=message)


class SelectionInvalidWithParentSelectionError(ValidationError):
    def __init__(self, model: type[Model], parent_model: type[Model]):
        message = f"The selection of '{model.name}' for the {model.__class__.__name__} cannot be paired with '{parent_model.name}' for the {parent_model.__class__.__name__} ."
        super().__init__(message=message)


class DuplicatePermissionError(ValidationError):
    def __init__(self):
        message = "A permission with these values already exists."
        super().__init__(message=message)


class RBACPermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False, unique=True)
    theme = models.ForeignKey(
        "Theme",
        on_delete=models.CASCADE,
        related_name="theme_permissions",
        null=True,
        blank=True,
    )
    sub_theme = models.ForeignKey(
        "SubTheme",
        on_delete=models.CASCADE,
        related_name="sub_theme_permissions",
        null=True,
        blank=True,
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

    objects = RBACPermissionManager()

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
                ],
                name="unique_permission_fields",
            )
        ]

    @property
    def model_types(self) -> list[str]:
        return [
            "theme",
            "sub_theme",
            "topic",
            "metric",
            "geography_type",
            "geography",
        ]

    def __str__(self) -> str:
        attributes = ["name=" + self.name]

        for model_type in self.model_types:
            value = getattr(self, model_type)
            if value is not None:
                attributes.append(f"{model_type}={value.name}")

        return ", ".join(attributes)

    def clean(self):
        super().clean()
        self._validate_a_selection_has_been_made()

        if self.metric:
            self._validate_metric_selection()

        if self.topic:
            self._validate_topic_selection()

        if self.sub_theme:
            self._validate_sub_theme_selection()

        if self.geography:
            self._validate_geography_selection()

        self._check_rbac_permissions_exist()

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def _validate_a_selection_has_been_made(self):
        for model_type in self.model_types:
            if getattr(self, model_type) is not None:
                return
        raise NoSelectionMadeError

    def _get_theme_selection(self) -> type[Model]:
        return self._get_model_selection(model_type="theme")

    def _get_sub_theme_selection(self) -> type[Model]:
        return self._get_model_selection(model_type="sub_theme")

    def _get_topic_selection(self) -> type[Model]:
        return self._get_model_selection(model_type="topic")

    def _get_metric_selection(self) -> type[Model]:
        return self._get_model_selection(model_type="metric")

    def _get_geography_type_selection(self) -> type[Model]:
        return self._get_model_selection(model_type="geography_type")

    def _get_geography_selection(self) -> type[Model]:
        return self._get_model_selection(model_type="geography")

    def _get_model_selection(self, model_type: str) -> type[Model]:
        selected_model = getattr(self, model_type)
        if selected_model is None:
            raise NoModelSelectedError(category=model_type)
        return selected_model

    def _validate_sub_theme_selection(self) -> None:
        theme = self._get_theme_selection()
        sub_theme = self._get_sub_theme_selection()

        if sub_theme.theme != theme:
            raise SelectionInvalidWithParentSelectionError(
                model=sub_theme, parent_model=theme
            )

    def _validate_topic_selection(self) -> None:
        sub_theme = self._get_sub_theme_selection()
        topic = self._get_topic_selection()

        if topic.sub_theme != sub_theme:
            raise SelectionInvalidWithParentSelectionError(
                model=topic, parent_model=sub_theme
            )

    def _validate_metric_selection(self) -> None:
        topic = self._get_topic_selection()
        metric = self._get_metric_selection()

        if metric.topic != topic:
            raise SelectionInvalidWithParentSelectionError(
                model=metric, parent_model=topic
            )

    def _validate_geography_selection(self) -> None:
        geography_type = self._get_geography_type_selection()
        geography = self._get_geography_selection()
        if geography.geography_type != geography_type:
            raise SelectionInvalidWithParentSelectionError(
                model=geography, parent_model=geography_type
            )

    def _get_existing_permissions(self) -> RBACPermissionQuerySet:
        """Validates that there are no duplicate permissions with the same fields."""
        return RBACPermission.objects.get_existing_permissions(instance=self)

    def _check_rbac_permissions_exist(self):
        rbac_permissions = self._get_existing_permissions()
        if rbac_permissions.exists():
            raise DuplicatePermissionError
