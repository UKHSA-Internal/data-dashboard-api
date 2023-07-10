from rest_framework import serializers

from feedback.serializers import help_texts


class QuestionAnswerSerializer(serializers.Serializer):
    question = serializers.CharField(
        help_text=help_texts.QUESTION_FIELD_HELP_TEXT,
        required=True,
        allow_blank=False,
    )
    answer = serializers.CharField(
        help_text=help_texts.ANSWER_FIELD_HELP_TEXT,
        required=True,
        allow_blank=False,
    )


class QuestionAnswerListSerializer(serializers.ListSerializer):
    child = QuestionAnswerSerializer()


class SuggestionsSerializer(serializers.Serializer):
    suggestions = QuestionAnswerListSerializer()
