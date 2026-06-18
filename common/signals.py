import logging

from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver

from metrics.api.middleware.current_user import get_current_user

audit_logger = logging.getLogger("audit")

AUDIT_EXCLUDED_FIELDS: dict[str, set[str]] = {
    "User": {"last_login", "password"},
    "PermissionSet": set(),
}
AUDITABLE_MODELS = ["PermissionSet", "User"]
AUDITABLE_RELATIONSHIPS = ["User_permission_sets"]


def _concrete_field_names(instance):
    """Return attnames of all concrete (non-M2M) fields on this instance."""
    return [f.attname for f in instance._meta.concrete_fields]  # noqa: E261 SLF001


@receiver(pre_save)
def track_concrete_field_changes(sender, instance, update_fields=None, **kwargs):
    """
    Stamp _audit_fields_changed on the instance before saving so that
    audit_save_log can skip updates that only touched M2M relationships.
    """
    if sender.__name__ not in AUDITABLE_MODELS:
        return

    excluded = AUDIT_EXCLUDED_FIELDS.get(sender.__name__, set())

    if not instance.pk:
        instance.audit_fields_changed = True
        return

    if update_fields is not None:
        m2m_names = {
            f.name
            for f in instance._meta.get_fields()  # noqa: E261 SLF001
            if f.many_to_many
        }
        auditable_fields = set(update_fields) - m2m_names - excluded
        instance.audit_fields_changed = bool(auditable_fields)
        return

    try:
        stored = sender.objects.get(pk=instance.pk)
        instance.audit_fields_changed = any(
            getattr(instance, f) != getattr(stored, f)
            for f in _concrete_field_names(instance)
            if f not in excluded
        )
    except sender.DoesNotExist:
        instance.audit_fields_changed = True


@receiver(m2m_changed)
def audit_m2m_relationships_log(sender, instance, action, pk_set, **kwargs):
    if sender.__name__ not in AUDITABLE_RELATIONSHIPS:
        return

    if action not in {"post_add", "post_remove", "post_clear"}:
        return

    user = get_current_user()
    user_id = user.id if user and user.is_authenticated else "anonymous"

    if action == "post_add":
        audit_logger.info(
            "User permission sets relationship added",
            extra={
                "user": user_id,
                "action": f"ADD {sender.__name__} {pk_set}",
                "target": f"pk={instance.pk}, id={instance.user_id}",
            },
        )
    elif action == "post_remove":
        audit_logger.info(
            "User permission sets relationship removed",
            extra={
                "user": user_id,
                "action": f"REMOVE {sender.__name__} {pk_set}",
                "target": f"pk={instance.pk}, id={instance.user_id}",
            },
        )
    elif action == "post_clear":
        audit_logger.info(
            "User permission sets relationships cleared",
            extra={
                "user": user_id,
                "action": f"CLEAR {sender.__name__}",
                "target": f"pk={instance.pk}, user_id={instance.user_id}",
            },
        )


@receiver(post_save)
def audit_save_log(sender, instance, created, **kwargs):
    if sender.__name__ not in AUDITABLE_MODELS:
        return

    if not created and not getattr(instance, "audit_fields_changed", True):
        return

    user = get_current_user()
    user_id = user.id if user else "anonymous"
    action = "CREATED" if created else "UPDATED"

    audit_logger.info(
        "Model saved",
        extra={
            "user": user_id,
            "action": f"{action} {sender.__name__}",
            "target": f"pk={instance.pk}, id={instance.user_id}",
        },
    )


@receiver(post_delete)
def audit_delete_log(sender, instance, **kwargs):
    if sender.__name__ not in AUDITABLE_MODELS:
        return

    user = get_current_user()
    user_id = user.id if user else "anonymous"

    audit_logger.info(
        "Model deleted",
        extra={
            "user": user_id,
            "action": f"pk={instance.pk}, DELETE {sender.__name__}",
            "target": f"pk={instance.pk}, id={instance.user_id}",
        },
    )
