from collections import OrderedDict
from unittest import mock

import pytest
from rest_framework.exceptions import ValidationError

from cms.forms.models import FormField
from feedback.api.serializers.questions import (
    SuggestionsV2Serializer,
)


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

    def test_serializes_for_multiline_form_field(self):
        """
        Given form fields returned from the `FormPageManager`
        When a valid payload is serialized
            with the `SuggestionsV2Serializer`
        Then the payload is deemed valid
        """
        # Given
        form_field = FormField(
            clean_name="how_could_we_improve_your_experience_with_the_dashboard",
            label="How could we improve your experience with the dashboard?",
            field_type="multiline",
            required=False,
        )
        mocked_form_page_manager = mock.Mock()
        mocked_form_page_manager.get_feedback_page_form_fields.return_value = [
            form_field
        ]

        payload = {form_field.clean_name: "More data"}
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
