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
