from django.db import models


class RBACPermissionQuerySet(models.QuerySet):
    """Custom queryset which can be used by the `RBACPermissionManager`."""

    def get_existing_permissions(
        self, *, instance: "RBACPermission"
    ) -> "RBACPermissionQuerySet":
        """Retrieves existing permissions that match the given instance's fields, excluding itself.
        Args:
            instance (RBACPermission): The permission instance to compare against.
        Returns:
            RBACPermissionQuerySet: A queryset containing matching permission instances.
        """
        return (
            self.filter(
                theme=instance.theme,
                sub_theme=instance.sub_theme,
                topic=instance.topic,
                metric=instance.metric,
                geography_type=instance.geography_type,
                geography=instance.geography,
            )
            .exclude(pk=instance.pk)
            .distinct()
        )


class RBACPermissionManager(models.Manager):
    """Custom manager for the `RBACPermission` model."""

    def get_queryset(self) -> RBACPermissionQuerySet:
        """Returns the custom queryset for RBACPermission."""
        return RBACPermissionQuerySet(self.model, using=self._db).select_related(
            "theme", "sub_theme", "topic", "metric", "geography_type", "geography"
        )

    def get_existing_permissions(
        self, *, instance: "RBACPermission"
    ) -> RBACPermissionQuerySet:
        """Proxy method to access `get_existing_permissions` from the queryset."""
        return self.get_queryset().get_existing_permissions(instance=instance)
