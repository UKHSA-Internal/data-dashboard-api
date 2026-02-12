import pytest
from wagtail.api import APIField

from tests.fakes.factories.cms.whats_new_child_entry_factory import (
    FakeWhatsNewChildEntryFactory,
)


class TestWhatsNewChildEntry:
    def test_parent_page_type_only_allows_for_whats_new_child_entry(self):
        """
        Given a `WhatsNewChildEntry`
        When the `parent_page_type` attribute is called
        Then a list containing the `WhatsNewParentPage` label is returned
        """
        # Given
        fake_whats_new_child_entry = (
            FakeWhatsNewChildEntryFactory.build_page_from_template(pk=1)
        )

        # When
        allowable_parent_page_types: list[str] = (
            fake_whats_new_child_entry.parent_page_type
        )

        # Then
        assert allowable_parent_page_types == ["whats_new.WhatsNewParentPage"]

    @pytest.mark.parametrize(
        "expected_api_field",
        [
            "date_posted",
            "body",
            "last_updated_at",
            "last_published_at",
            "seo_title",
            "search_description",
            "additional_details",
            "badge",
        ],
    )
    def test_has_correct_api_fields(
        self,
        expected_api_field: str,
    ):
        """
        Given a blank `WhatsNewChildEntry` model
        When `api_fields` is called
        Then the expected names are on the returned `APIField` objects
        """
        # Given
        fake_whats_new_child_entry = (
            FakeWhatsNewChildEntryFactory.build_page_from_template()
        )

        # When
        api_fields: list[APIField] = fake_whats_new_child_entry.api_fields

        # Then
        api_field_names: set[str] = {api_field.name for api_field in api_fields}
        assert expected_api_field in api_field_names
