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
        fake_whats_new_parent_page = (
            FakeWhatsNewChildEntryFactory.build_page_from_template(pk=1)
        )

        # When
        allowable_parent_page_types: list[
            str
        ] = fake_whats_new_parent_page.parent_page_type

        # Then
        assert allowable_parent_page_types == ["whats_new.WhatsNewParentPage"]
