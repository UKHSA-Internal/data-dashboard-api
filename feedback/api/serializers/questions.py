from rest_framework import serializers
from rest_framework.fields import Field

from feedback.cms_interface.interface import CMSInterface


class SuggestionsSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generate_fields()

    @property
    def form_page_manager(self):
        return self.context.get(
            "form_page_manager", CMSInterface().get_form_page_manager()
        )

    def _generate_fields(self) -> None:
        form_fields = self.form_page_manager.get_feedback_page_form_fields()

        for field in form_fields:
            self.fields[field.clean_name] = self._construct_serializer_field(
                field=field
            )

    @classmethod
    def _construct_serializer_field(cls, field: "FormField") -> Field:
        if field.choices:
            choices = field.choices.split("\r\n")
            return serializers.ChoiceField(
                choices=choices,
                allow_blank=not field.required,
                required=field.required,
                default=field.default_value,
                label=field.label,
            )

        return serializers.CharField(
            allow_blank=not field.required,
            required=field.required,
            default=field.default_value,
            label=field.label,
        )
