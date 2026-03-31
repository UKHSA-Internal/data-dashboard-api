from django import forms

from auth_content.models.permission_sets import PermissionSet
from django.db import models
from wagtail.admin.panels import FieldPanel, WagtailAdminModelForm


def get_permission_set_choices():
    return [(str(obj.id), obj.name) for obj in PermissionSet.objects.all()]



class UserForm(WagtailAdminModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = get_permission_set_choices()

        self.fields["permission_sets"] = forms.MultipleChoiceField(
            required=False,
            choices=choices,
            widget=forms.CheckboxSelectMultiple,
            label="Permission Sets"
        )

        if self.instance and self.instance.pk:
            self.fields["permission_sets"].initial = [
                str(v) for v in self.instance.permission_sets
            ]


class User(models.Model):
    user_id = models.UUIDField(unique=True)
    permission_sets = models.ManyToManyField("PermissionSet", blank=True, help_text="If no permission sets are showing, create one on the Permission Sets page")

    base_form_class = UserForm

    panels = [
        FieldPanel("user_id"),
        FieldPanel("permission_sets"),
    ]
    
    
    def __str__(self):
        return f"User {self.user_id}"

