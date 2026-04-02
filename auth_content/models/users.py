from django import forms

from django.db import models
from wagtail.admin.panels import FieldPanel



class User(models.Model):
    user_id = models.UUIDField(unique=True)
    permission_sets = models.ManyToManyField("PermissionSet", blank=True)

    panels = [
        FieldPanel("user_id"),
        FieldPanel("permission_sets", widget=forms.CheckboxSelectMultiple),
    ]
    
    
    def __str__(self):
        return f"User {self.user_id}"
