from rest_framework import serializers

from feedback.api.serializers import help_texts

DID_YOU_FIND_EVERYTHING_CHOICES: tuple[str, str] = ("yes", "no")


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
