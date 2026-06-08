# Audit Logging Guide

## Introduction

This document outlines the approach to audit logging in the project, and how to extend to log for more changes in the future.

---

## Configuration
Audit logs are configured in `metrics/api/settings/default.py` under the audit formatter. The format accepts `user`, `action`, and `target` parameters.

```
[AUDIT_EVENT] %(asctime)s [User:%(user)s - Action:%(action)s - Target:%(target)s]
```

## Logging Model Changes
We utilize Django signals to automatically capture changes to core database models. The logic triggered by the signals is defined in `common/signals.py`.

To extend the audit logging to track new models or relationships, update the configuration lists in the signals file, providing the name of the models or relationships that should be tracked:
```
AUDITABLE_MODELS = ["PermissionSet", "User"]
AUDITABLE_RELATIONSHIPS = ["User_permission_sets"]
```

## Logging Non-Model Changes
For events not tied to specific model lifecycle hooks, use the designated audit logger directly. Provide the user, action, and target fields via the `extra` parameter.
```
import logging

audit_logger = logging.getLogger("audit")
audit_logger.info(
    "Custom event description",
    extra={
        "user": user_id,
        "action": "ACTION_PERFORMED",
        "target": "ID of impacted item if applicable",
    },
)
```

## Storage of Logs
All logs follow a structured path to persistent storage:

- Logs are logged to CloudWatch as standard
- A CloudWatch Subscription Filter identifies logs containing the `[AUDIT_EVENT]` pattern.
- Kinesis Firehose consumes these filtered logs and pushes them to S3.
    - These are pushed to S3 every 5 minutes, or every 5MB of logs.

For more information about the infrastructure for storing logs see the [infra repo](https://github.com/UKHSA-Internal/data-dashboard-infra)
