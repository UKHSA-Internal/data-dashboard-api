from typing import OrderedDict

import pytest
from rest_framework.exceptions import ValidationError

from feedback.serializers.questions import SuggestionsSerializer


class TestSuggestionsSerializer:
    reason = "reason"
    improve_experience = "improve_experience"
    like_to_see = "like_to_see"
    did_you_find_everything = "did_you_find_everything"

    @pytest.mark.parametrize(
        "question, answer",
        (
            [
                "reason",
                "I wanted to find out the infection rates of Disease X in my area",
            ],
            ["improve_experience", "More context around metrics and figures"],
            [
                "like_to_see",
                "I'd like to see more consistency across charts and graphs",
            ],
        ),
    )
    def test_other_questions_with_valid_answers_can_be_successfully_serialized(
        self, question: str, answer: str
    ):
        """
        Given a valid payload containing a valid question answer pair
        And the mandatory "did_you_find_everything" question answer pair
        When that payload is serialized with the `SuggestionsSerializer`
        Then the data is validated and returned
        """
        # Given
        payload = {self.did_you_find_everything: "yes", question: answer}
        serializer = SuggestionsSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: OrderedDict = serializer.validated_data

        # Then
        assert validated_data[self.did_you_find_everything] == "yes"
        assert validated_data[question] == answer

    @pytest.mark.parametrize(
        "question",
        (["reason", "improve_experience", "like_to_see"]),
    )
    def test_other_questions_with_none_answer_can_be_successfully_serialized(
        self, question: str
    ):
        """
        Given a valid payload containing an answer of None
            for one of the optional question answer pairs
        And the mandatory "did_you_find_everything" question answer pair
        When that payload is serialized with the `SuggestionsSerializer`
        Then the data is validated and returned
        """
        # Given
        payload = {self.did_you_find_everything: "yes", question: None}
        serializer = SuggestionsSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: OrderedDict = serializer.validated_data

        # Then
        assert validated_data[self.did_you_find_everything] == "yes"
        assert validated_data[question] is None

    @pytest.mark.parametrize(
        "question",
        (["reason", "improve_experience", "like_to_see"]),
    )
    def test_other_questions_with_empty_string_answer_can_be_successfully_serialized(
        self, question: str
    ):
        """
        Given a valid payload containing an answer of an empty string
            for one of the optional question answer pairs
        And the mandatory "did_you_find_everything" question answer pair
        When that payload is serialized with the `SuggestionsSerializer`
        Then the data is validated and returned
        """
        # Given
        payload = {self.did_you_find_everything: "yes", question: ""}
        serializer = SuggestionsSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: OrderedDict = serializer.validated_data

        # Then
        assert validated_data[self.did_you_find_everything] == "yes"
        assert validated_data[question] == ""

    @pytest.mark.parametrize("answer", ["yes", "no"])
    def test_only_did_you_find_everything_answer_is_required(self, answer: str):
        """
        Given a payload which only contains a valid answer
            for the "did_you_find_everything" question
        When that payload is serialized with the `SuggestionsSerializer`
        Then the data is validated and returned
        """
        # Given
        # Only the "did_you_find_everything" question is required
        payload = {self.did_you_find_everything: answer}
        serializer = SuggestionsSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)
        validated_data: OrderedDict = serializer.validated_data

        # Then
        assert validated_data[self.did_you_find_everything] == answer

    @pytest.mark.parametrize(
        "did_you_find_everything_value", ["", "maybe", "this is invalid"]
    )
    def test_invalid_did_you_find_everything_answer(
        self, did_you_find_everything_value: str
    ):
        """
        Given a payload which contains an invalid answer
            for the *did_you_find_everything* question
        When that payload is serialized with the `SuggestionsSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        payload = {self.did_you_find_everything: did_you_find_everything_value}
        serializer = SuggestionsSerializer(data=payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
