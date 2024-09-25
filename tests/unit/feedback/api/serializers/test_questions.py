from collections import OrderedDict
from unittest import mock

import pytest
from rest_framework.exceptions import ValidationError

from cms.forms.models import FormField
from feedback.api.serializers.questions import (
    SuggestionsSerializer,
    SuggestionsV2Serializer,
)


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

    @pytest.mark.parametrize("valid_did_you_find_everything_value", ["", None])
    def test_did_you_find_everything_answer_as_empty_string_is_valid(
        self, valid_did_you_find_everything_value: str | None
    ):
        """
        Given a payload which contains an empty string
            for the *did_you_find_everything* question
        When that payload is serialized with the `SuggestionsSerializer`
        Then the answer is serialized correctly
        """
        # Given
        payload = {self.did_you_find_everything: valid_did_you_find_everything_value}
        serializer = SuggestionsSerializer(data=payload)

        # When
        serializer.is_valid(raise_exception=True)

        # Then
        assert (
            serializer.validated_data["did_you_find_everything"]
            == valid_did_you_find_everything_value
        )

    @pytest.mark.parametrize(
        "invalid_did_you_find_everything_value", ["maybe", "this is invalid"]
    )
    def test_invalid_did_you_find_everything_answer_raises_error(
        self, invalid_did_you_find_everything_value: str
    ):
        """
        Given a payload which contains an invalid answer
            for the *did_you_find_everything* question
        When that payload is serialized with the `SuggestionsSerializer`
        Then a `ValidationError` is raised
        """
        # Given
        payload = {self.did_you_find_everything: invalid_did_you_find_everything_value}
        serializer = SuggestionsSerializer(data=payload)

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)


class TestSuggestionsV2Serializer:
    @property
    def example_form_field(self) -> FormField:
        return FormField(
            clean_name="did_you_find_everything_you_were_looking_for",
            label="Did you find everything you were looking for?",
            field_type="radio",
            required=False,
            choices="Yes\r\nNo",
        )

    def test_serializes_against_feedback_page_form_fields(self):
        """
        Given form fields returned from the `FormPageManager`
        When a valid payload is serialized
            with the `SuggestionsV2Serializer`
        Then the payload is deemed valid
        """
        # Given
        form_field = self.example_form_field
        mocked_form_page_manager = mock.Mock()
        mocked_form_page_manager.get_feedback_page_form_fields.return_value = [
            form_field
        ]

        payload = {form_field.clean_name: "No"}
        serializer = SuggestionsV2Serializer(
            data=payload, context={"form_page_manager": mocked_form_page_manager}
        )

        # When
        serializer.is_valid(raise_exception=True)

        # Then
        assert (
            serializer.validated_data[form_field.clean_name]
            == payload[form_field.clean_name]
        )

    def test_invalidates_against_feedback_page_form_fields(self):
        """
        Given form fields returned from the `FormPageManager`
        When an invalid payload is serialized
            with the `SuggestionsV2Serializer`
        Then a `ValidationError` is raised
        """
        # Given
        form_field = self.example_form_field
        mocked_form_page_manager = mock.Mock()
        mocked_form_page_manager.get_feedback_page_form_fields.return_value = [
            form_field
        ]

        payload = {form_field.clean_name: "invalid-answer"}
        serializer = SuggestionsV2Serializer(
            data=payload, context={"form_page_manager": mocked_form_page_manager}
        )

        # When / Then
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_strips_off_invalid_keys_from_payload(self):
        """
        Given form fields returned from the `FormPageManager`
        When a payload containing no valid keys
            is serialized with the `SuggestionsV2Serializer`
        Then the validated data strips the invalid keys
        """
        # Given
        form_field = self.example_form_field
        mocked_form_page_manager = mock.Mock()
        mocked_form_page_manager.get_feedback_page_form_fields.return_value = [
            form_field
        ]

        payload = {
            "invalid-question": "invalid-answer",
            self.example_form_field.clean_name: "Yes",
        }
        serializer = SuggestionsV2Serializer(
            data=payload, context={"form_page_manager": mocked_form_page_manager}
        )

        # When
        serializer.is_valid(raise_exception=True)

        # Then
        assert "invalid-question" not in serializer.validated_data
        assert form_field.clean_name in serializer.validated_data
