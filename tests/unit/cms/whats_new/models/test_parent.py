import pytest

from tests.fakes.factories.cms.whats_new_parent_page_factory import (
    FakeWhatsNewParentPageFactory,
)


class TestWhatsNewParentPage:
    @pytest.mark.parametrize(
        "subpage_type", (["whats_new.WhatsNewChildEntry", "common.CommonPage"])
    )
    def test_subpage_types_only_allows_for_whats_new_child_entry(
        self, subpage_type: str
    ):
        """
        Given a `WhatsNewParentPage`
        When the `subpage_types` attribute is called
        Then a list containing the `WhatsNewChildEntry` label is returned
        """
        # Given
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template(pk=1)
        )

        # When
        allowable_subpage_types: list[str] = fake_whats_new_parent_page.subpage_types

        # Then
        assert subpage_type in allowable_subpage_types
