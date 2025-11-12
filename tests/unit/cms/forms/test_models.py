from unittest import mock

from wagtail.contrib.forms.models import AbstractFormField
import pytest
from cms.forms.models import FormField


class TestFormField:

    @pytest.mark.parametrize(
        "valid_field_type",
        [
            "singleline",
            "multiline",
            "email",
            "number",
            "url",
            "checkbox",
            "checkbox",
            "checkboxes",
            "dropdown",
            "radio",
            "date",
            "datetime",
            "hidden",
        ],
    )
    def test_form_field_supports_expected_field_types(self, valid_field_type: str):
        """
        Given the list of supported `FormField` `field_type` choices
        When a valid field name is provided
        Then the field name is found in the choices list.
        """
        # Given
        choices_list: list[str] = FormField._meta.get_field("field_type").choices

        # When / Then
        assert valid_field_type in [choices[0] for choices in choices_list]

    @pytest.mark.parametrize(
        "invalid_field_type",
        [
            "multiselect",
        ],
    )
    def test_unsupported_field_types_not_included_in_form_field(
        self, invalid_field_type: str
    ):
        """
        Given the list of supported `FormField` `field_type` choices
        When an invalid field name is provided
        Then the field name is not found in the choices list.
        """
        # Given
        choices_list: list[str] = FormField._meta.get_field("field_type").choices

        # When / Then
        assert invalid_field_type not in [choices[0] for choices in choices_list]

    @mock.patch.object(AbstractFormField, "save")
    def test_save_sets_clean_name_for_new_field(
        self, mocked_save_from_parent_class: mock.MagicMock
    ):
        """
        Given a new `FormField` with a `label`
        When the `save()` method is called from the `FormField` object
        Then the `clean_name` is set to snake_case version of the `label`
        """
        # Given
        form = FormField(
            label="Did you find everything you were looking for?",
            field_type="radio",
            required=False,
            choices="Yes\r\nNo",
        )

        # When
        form.save()

        # Then
        assert form.clean_name == "did_you_find_everything_you_were_looking_for"
        mocked_save_from_parent_class.assert_called_once()

    @mock.patch.object(AbstractFormField, "save")
    def test_save_updates_clean_name_for_existing_field(
        self, mocked_save_from_parent_class: mock.MagicMock
    ):
        """
        Given a `FormField` with an existing `label` and `clean_name`
        When the `label` is updated and the `save()` method is called
        Then the `FormField` object updates the `clean_name`
            in place to match the new `label` value
        """
        # Given
        original_clean_name = "did_you_find_everything_you_were_looking_for"
        form = FormField(
            label="Did you find everything you were looking for?",
            field_type="radio",
            required=False,
            choices="Yes\r\nNo",
        )
        form.save()
        mocked_save_from_parent_class.assert_called_once()

        # When
        form.label = "Would you like to join our research panel?"
        form.save()
        assert mocked_save_from_parent_class.call_count == 2

        # Then
        assert (
            form.clean_name
            == "would_you_like_to_join_our_research_panel"
            != original_clean_name
        )
