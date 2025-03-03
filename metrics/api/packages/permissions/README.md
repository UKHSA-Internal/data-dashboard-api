# FluentPermissions Usage Guide

## Introduction

The `FluentPermissions` class is for handling Role-Based Access Control (RBAC) permissions.
It allows for checking multiple fields against user permissions using a fluent API.

---

## Installation & Setup

Ensure your project includes the necessary imports:

```python
from metrics.data.models.rbac_models import RBACPermission
from metrics.api.packages.permissions import FluentPermissions, FluentPermissionsError
```

---

## Creating FluentPermissions Instance

To create an instance of `FluentPermissions`, pass in the **data** (the object containing the fields to check) 
and the **group_permissions** (a list of `RBACPermission` objects associated with the user).

### Example:
```python
permissions = FluentPermissions(
    data={
        "theme": "infectious_disease",
        "sub_theme": "respiratory",
        "topic": "COVID-19",
    },
    group_permissions=[user_permission_object],
)
```

---

## Adding Fields to Check

You must specify which fields you want to check by calling `.add_field(field_name)`. Multiple fields can be chained.

### Example:
```python
permissions.add_field("theme").add_field("sub_theme").add_field("topic")
```

---

## Executing the Permissions Check

Once the fields are added, call `.execute()` to process the matching logic.

### Example:
```python
permissions.execute()
```

The results are stored in `permissions.match_fields_all`, which is a **read-only property** 
that returns a list of dictionaries indicating whether each field matched.

### Example Output:
```python
[
    {
        "theme": True,
        "sub_theme": True,
        "topic": False,
        "geography_type": False,
        "geography": False,
        "metric": False,
        "age": False,
        "stratum": False,
    }
]
```

---

## Validating the Permissions

To ensure that at least one set of permissions fully matches, call `.validate()`.
If no complete match is found, it raises a `FluentPermissionsError`.

### Example:
```python
try:
    permissions.validate()
except FluentPermissionsError:
    print("Access denied")
```
---

## Integration with `filter_by_permissions` Decorator

The `FluentPermissions` class is used within the `filter_by_permissions()` decorator to automatically enforce permissions when serializing API responses.

### Example:
```python
@filter_by_permissions()
class MySerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = "__all__"
```

When `to_representation()` is called on the serializer, the decorator ensures that unauthorized users cannot see restricted data.

---

## Handling Public Data

If an object contains `is_public = True`, the `FluentPermissions` logic is **bypassed**, and the data is always returned.

### Example:
```python
{ "is_public": True, "theme": "Finance", "sub_theme": "Banking" }
```
The object above will be accessible to all users regardless of permissions.

---

## Summary

| **Method** | **Description** |
|------------|----------------|
| `add_field(field_name)` | Adds a field to be checked in permissions |
| `execute()` | Runs the permission checks and stores results |
| `validate()` | Raises `FluentPermissionsError` if no full match exists |
| `match_fields_all` | Read-only property that stores a list of match results |
