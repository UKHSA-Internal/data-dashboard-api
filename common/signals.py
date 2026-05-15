import logging

from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from metrics.api.middleware.current_user import get_current_user


audit_logger = logging.getLogger("audit")

AUDITABLE_MODELS = ["PermissionSet", "User"]
AUDITABLE_RELATIONSHIPS = ["User_permission_sets"]

# TODO: This fires alongside post_save - what's the best way to handle that?
#       We can just track certain fields in the model, and if changes to those
#       aren't present then ignore and don't log?
# TODO: Tests
@receiver(m2m_changed)
def audit_m2m_relationships_log(sender, instance, action, pk_set, **kwargs):
    if sender.__name__ not in AUDITABLE_RELATIONSHIPS:
        return
    
    if action not in ("post_add", "post_remove", "post_clear"):
        return
    
    user = get_current_user()
    user_id = user.id if user and user.is_authenticated else "anonymous"

    if action == "post_add":
        audit_logger.info("User permission sets relationship added", extra={
            "user": user_id,
            "action": f"ADD {sender.__name__} {pk_set}",
            "target": instance.pk
        })
    elif action == "post_remove":
        audit_logger.info("User permission sets relationship removed", extra={
            "user": user_id,
            "action": f"REMOVE {sender.__name__} {pk_set}",
            "target": instance.pk,
        })
    elif action == "post_clear":
        audit_logger.info("User permission sets relationships cleared", extra={
            "user": user_id,
            "action": f"CLEAR {sender.__name__}",
            "target": instance.pk,
        })


@receiver(post_save)
def audit_save_log(sender, instance, created, **kwargs):
    if sender.__name__ in AUDITABLE_MODELS:
        user = get_current_user()
        user_id = user.id if user else "anonymous"
        action = "CREATED" if created else "UPDATED"

        audit_logger.info("Model saved", extra={
            "user": user_id,
            "action": f"{action} {sender.__name__}",
            "target": f"id={instance.pk}",
        })

@receiver(post_delete)
def audit_delete_log(sender, instance, **kwargs):
    if sender.__name__ in AUDITABLE_MODELS:
        user = get_current_user()
        user_id = user.id if user else "anonymous"

        audit_logger.info("Model deleted", extra={
            "user": user_id,
            "action": f"DELETE {sender.__name__}",
            "target": f"id={instance.pk}",
        })
