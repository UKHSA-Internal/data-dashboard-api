from typing import List, OrderedDict

import pytest
from rest_framework.exceptions import ValidationError

from feedback.serializers.questions import (
    QuestionAnswerListSerializer,
    QuestionAnswerSerializer,
    SuggestionsSerializer,
)

EXAMPLE_QUESTION = "What would you like to see on the dashboard in the future?"
EXAMPLE_ANSWER = "Location-based on maps, with breakdown of regional filters"


class TestQuestionAnswerSerializer:
    def test_can_serialize_successfully(self):
        """
        Given a payload containing a question and answer pair
        When that payload is serialized with the `QuestionAnswerSerializer`
        Then the data is validated and returned
        """
        # Given
        question = EXAMPLE_QUESTION
        answer = EXAMPLE_ANSWER
        payload = {"question": question, "answer": answer}
        serializer = QuestionAnswerSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: OrderedDict = serializer.validated_data

        # Then
        assert validated_data["question"] == question
        assert validated_data["answer"] == answer

    def test_invalidates_if_an_answer_is_not_provided(self):
        """
        Given a payload only containing a question but not an answer
        When `is_valid()` is called from
            an instance of the `QuestionAnswerSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        question = EXAMPLE_QUESTION
        payload = {"question": question}
        serializer = QuestionAnswerSerializer(data=payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalidates_if_a_question_is_not_provided(self):
        """
        Given a payload only containing an answer but not a question
        When `is_valid()` is called from
            an instance of the `QuestionAnswerSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        answer = EXAMPLE_ANSWER
        payload = {"answer": answer}
        serializer = QuestionAnswerSerializer(data=payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestQuestionAnswerListSerializer:
    def test_validates_successfully(self):
        """
        Given a valid payload containing a list of question answer pairs
        When that payload is serialized with the `QuestionAnswerSerializer`
        Then the data is validated and returned
        """
        # Given
        question = EXAMPLE_QUESTION
        answer = EXAMPLE_ANSWER
        payload = [{"question": question, "answer": answer}]
        serializer = QuestionAnswerListSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: List[OrderedDict] = serializer.validated_data

        # Then
        assert len(validated_data) == len(payload)
        assert validated_data[0]["question"] == question
        assert validated_data[0]["answer"] == answer


class TestSuggestionsSerializer:
    def test_validates_successfully(self):
        """
        Given a valid payload containing a list of question answer pairs
        When that payload is serialized with the `SuggestionsSerializer`
        Then the data is validated and returned
        """
        # Given
        question = EXAMPLE_QUESTION
        answer = EXAMPLE_ANSWER
        payload = {"suggestions": [{"question": question, "answer": answer}]}
        serializer = SuggestionsSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: OrderedDict[List[OrderedDict]] = serializer.validated_data

        # Then
        validated_suggestions = validated_data["suggestions"]
        assert validated_suggestions[0]["question"] == question
        assert validated_suggestions[0]["answer"] == answer
