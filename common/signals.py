import datetime
import logging
from decimal import Decimal

from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver

from metrics.api.middleware.current_user import get_current_user

audit_logger = logging.getLogger("audit")

AUDITABLE_MODELS = ["PermissionSet", "User", "APIApplication"]
AUDITABLE_RELATIONSHIPS = ["User_permission_sets", "APIApplication_permission_sets"]


def _concrete_field_names(instance):
    """Return attnames of all concrete (non-M2M) fields on this instance."""
    return [f.attname for f in instance._meta.concrete_fields]  # noqa: E261 SLF001


def _serialize_value(value):
    """Make values JSON/log-safe (dates, Decimals, model instances, etc.)."""
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, models.Model):
        return value.pk
    return value


@receiver(pre_save)
def track_concrete_field_changes(sender, instance, update_fields=None, **kwargs):
    """
    Stamp _audit_fields_changed on the instance before saving so that
    audit_save_log can skip updates that only touched M2M relationships.
    """
    if sender.__name__ not in AUDITABLE_MODELS:
        return

    if not instance.pk:
        instance.audit_fields_changed = True
        instance.audit_field_diff = {}
        return

    try:
        stored = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance.audit_fields_changed = True
        instance.audit_field_diff = {}
        return

    fields_to_check = _concrete_field_names(instance)

    if update_fields is not None:
        m2m_names = {
            f.name
            for f in instance._meta.get_fields()  # noqa: E261 SLF001
            if f.many_to_many
        }
        relevant = set(update_fields) - m2m_names
        fields_to_check = [
            f.attname
            for f in instance._meta.concrete_fields  # noqa: E261 SLF001
            if f.name in relevant
        ]

    diff = {}
    for attname in fields_to_check:
        old = getattr(stored, attname)
        new = getattr(instance, attname)
        if old != new:
            diff[attname] = (_serialize_value(old), _serialize_value(new))

    instance.audit_field_diff = diff
    instance.audit_fields_changed = bool(diff)


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
                "target": instance.pk,
            },
        )
    elif action == "post_remove":
        audit_logger.info(
            "User permission sets relationship removed",
            extra={
                "user": user_id,
                "action": f"REMOVE {sender.__name__} {pk_set}",
                "target": instance.pk,
            },
        )
    elif action == "post_clear":
        audit_logger.info(
            "User permission sets relationships cleared",
            extra={
                "user": user_id,
                "action": f"CLEAR {sender.__name__}",
                "target": instance.pk,
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

    extra = {
        "user": user_id,
        "action": f"{action} {sender.__name__}",
        "target": f"id={instance.pk}",
    }

    if not created:
        diff = getattr(instance, "audit_field_diff", {})
        changes = {
            field: {"old": old, "new": new} for field, (old, new) in diff.items()
        }
        extra["target"] += f", Changes: {changes}"

    audit_logger.info("Model saved", extra=extra)


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
            "action": f"DELETE {sender.__name__}",
            "target": f"id={instance.pk}",
        },
    )
