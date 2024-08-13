import pytest

from cms.dashboard.models import UKHSAPage
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.composite_page_factory import FakeCompositePageFactory
from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory
from tests.fakes.factories.cms.metrics_documentation_factory import (
    FakeMetricsDocumentationParentPageFactory,
)
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory
from tests.fakes.factories.cms.whats_new_child_entry_factory import (
    FakeWhatsNewChildEntryFactory,
)
from tests.fakes.factories.cms.whats_new_parent_page_factory import (
    FakeWhatsNewParentPageFactory,
)


class TestUKHSAPage:
    @pytest.mark.parametrize(
        "fake_page",
        [
            FakeHomePageFactory.build_blank_page(),
            FakeTopicPageFactory.build_influenza_page_from_template(),
            FakeCommonPageFactory.build_blank_page(),
            FakeCompositePageFactory.build_page_from_template(
                page_name="access_our_data_getting_started"
            ),
            FakeMetricsDocumentationParentPageFactory.build_page_from_template(),
            FakeWhatsNewChildEntryFactory.build_page_from_template(),
            FakeWhatsNewParentPageFactory.build_page_from_template(),
        ],
    )
    def test_show_in_menus_not_available_in_promote_panel(self, fake_page: UKHSAPage):
        """
        Given a blank page model which inherits from `UKHSAPage`
        When `promote_panels` is called
        Then `show_in_menus` is not available
        """
        # Given
        child_page = fake_page

        # When
        promote_panels = child_page.promote_panels

        # Then
        multi_field_panel = promote_panels[0]
        panel_names: list[str] = [p.clean_name for p in multi_field_panel.children]
        assert "show_in_menus" not in panel_names
