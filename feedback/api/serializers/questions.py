from rest_framework import serializers
from rest_framework.fields import Field

from feedback.api.serializers import help_texts
from feedback.cms_interface.interface import CMSInterface

DID_YOU_FIND_EVERYTHING_CHOICES: tuple[str, str] = ("yes", "no")


class SuggestionsV2Serializer(serializers.Serializer):
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


class SuggestionsSerializer(serializers.Serializer):
    reason = serializers.CharField(
        help_text=help_texts.QUESTION_REASON_HELP_TEXT,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    improve_experience = serializers.CharField(
        help_text=help_texts.QUESTION_IMPROVE_EXPERIENCE_HELP_TEXT,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    like_to_see = serializers.CharField(
        help_text=help_texts.QUESTION_LIKE_TO_SEE_HELP_TEXT,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    did_you_find_everything = serializers.ChoiceField(
        help_text=help_texts.QUESTION_DID_YOU_FIND_EVERYTHING_HELP_TEXT,
        required=False,
        allow_blank=True,
        allow_null=True,
        choices=DID_YOU_FIND_EVERYTHING_CHOICES,
    )
