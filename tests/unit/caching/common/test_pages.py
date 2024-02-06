from unittest import mock

from caching.common.pages import (
    collect_all_pages,
    extract_area_selectable_pages,
    get_pages_for_area_selector,
)
from tests.fakes.factories.cms.common_page_factory import FakeCommonPageFactory
from tests.fakes.factories.cms.home_page_factory import FakeHomePageFactory
from tests.fakes.factories.cms.topic_page_factory import FakeTopicPageFactory
from tests.fakes.factories.cms.whats_new_child_entry_factory import (
    FakeWhatsNewChildEntryFactory,
)
from tests.fakes.factories.cms.whats_new_parent_page_factory import (
    FakeWhatsNewParentPageFactory,
)
from tests.fakes.managers.cms.common_page_manager import FakeCommonPageManager
from tests.fakes.managers.cms.home_page_manager import FakeHomePageManager
from tests.fakes.managers.cms.topic_page_manager import FakeTopicPageManager
from tests.fakes.managers.cms.whats_new_child_entry_manager import (
    FakeWhatsNewChildEntryManager,
)
from tests.fakes.managers.cms.whats_new_parent_page_manager import (
    FakeWhatsNewParentPageManager,
)

MODULE_PATH = "caching.common.pages"


class TestCollectAllPages:
    def test_all_pages_collected(self):
        """
        Given a `HomePage` with a slug of "dashboard"
        And a number of live `TopicPages` and a `CommonPage`
        When `collect_all_pages()` is called
        Then the correct pages are returned
        """
        # Given
        # HomePage of slug "dashboard" which should be collected
        published_home_page = FakeHomePageFactory.build_blank_page(slug="dashboard")
        fake_home_page_manager = FakeHomePageManager(pages=[published_home_page])

        # Published `TopicPages` which should be collected
        published_covid_page = FakeTopicPageFactory.build_covid_19_page_from_template()
        published_influenza_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )
        fake_topic_page_manager = FakeTopicPageManager(
            pages=[published_covid_page, published_influenza_page]
        )

        # Published `CommonPage` which should be collected
        published_about_page = FakeCommonPageFactory.build_blank_page(
            slug="about", live=True
        )
        fake_common_page_manager = FakeCommonPageManager(pages=[published_about_page])

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
            common_page_manager=fake_common_page_manager,
            whats_new_parent_page_manager=FakeWhatsNewParentPageManager(pages=[]),
            whats_new_child_entry_manager=FakeWhatsNewChildEntryManager(pages=[]),
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert published_influenza_page in collected_pages
        assert published_about_page in collected_pages

    def test_all_whats_new_type_pages_collected(self):
        """
        Given a `WhatsNewParentPage` and `WhatsNewChildEntry`
        When `collect_all_pages()` is called
        Then the correct pages are returned
        """
        # Given
        # Published `WhatsNewParentPage` which should be collected
        published_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template(
                live=True,
            )
        )
        fake_whats_new_parent_page_manager = FakeWhatsNewParentPageManager(
            pages=[published_whats_new_parent_page]
        )
        # Published `WhatsNewChildEntry` which should be collected
        published_whats_new_child_entry = (
            FakeWhatsNewChildEntryFactory.build_page_from_template(
                live=True,
            )
        )
        # Unpublished `WhatsNewChildEntry` which should not be collected
        unpublished_whats_new_child_entry = (
            FakeWhatsNewChildEntryFactory.build_page_from_template(
                live=False,
            )
        )
        fake_whats_new_child_entry_manager = FakeWhatsNewChildEntryManager(
            pages=[published_whats_new_child_entry, unpublished_whats_new_child_entry]
        )

        # When
        collected_pages = collect_all_pages(
            home_page_manager=FakeHomePageManager(pages=[]),
            topic_page_manager=FakeTopicPageManager(pages=[]),
            common_page_manager=FakeCommonPageManager(pages=[]),
            whats_new_child_entry_manager=fake_whats_new_child_entry_manager,
            whats_new_parent_page_manager=fake_whats_new_parent_page_manager,
        )

        # Then
        assert published_whats_new_parent_page in collected_pages
        assert published_whats_new_child_entry in collected_pages
        assert unpublished_whats_new_child_entry not in collected_pages

    def test_non_dashboard_home_pages_not_collected(self):
        """
        Given a `HomePage` with a slug which is not "dashboard"
        When `collect_all_pages()` is called
        Then no pages are returned
        """
        # Given
        # HomePage which has a different slug then "dashboard" which should not be collected
        non_dashboard_page = FakeHomePageFactory.build_blank_page(
            slug="respiratory-viruses"
        )
        fake_home_page_manager = FakeHomePageManager(pages=[non_dashboard_page])
        fake_topic_page_manager = FakeTopicPageManager(pages=[])

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
            common_page_manager=FakeCommonPageManager(pages=[]),
            whats_new_parent_page_manager=FakeWhatsNewParentPageManager(pages=[]),
            whats_new_child_entry_manager=FakeWhatsNewChildEntryManager(pages=[]),
        )

        # Then
        assert non_dashboard_page not in collected_pages

    def test_unpublished_pages_not_collected(self):
        """
        Given a `HomePage` with a slug of "dashboard"
        And an unpublished `TopicPage`
        When `collect_all_pages()` is called
        Then the correct pages are returned
        """
        # Given
        published_home_page = FakeHomePageFactory.build_blank_page(slug="dashboard")
        fake_home_page_manager = FakeHomePageManager(pages=[published_home_page])

        # A mixture of unpublished and live pages
        # Whereby only the live pages should be collected
        unpublished_page = (
            FakeTopicPageFactory.build_other_respiratory_viruses_page_from_template(
                live=False
            )
        )
        published_covid_page = FakeTopicPageFactory.build_covid_19_page_from_template()
        fake_topic_page_manager = FakeTopicPageManager(
            pages=[unpublished_page, published_covid_page]
        )

        # When
        collected_pages = collect_all_pages(
            home_page_manager=fake_home_page_manager,
            topic_page_manager=fake_topic_page_manager,
            common_page_manager=FakeCommonPageManager(pages=[]),
            whats_new_parent_page_manager=FakeWhatsNewParentPageManager(pages=[]),
            whats_new_child_entry_manager=FakeWhatsNewChildEntryManager(pages=[]),
        )

        # Then
        assert published_home_page in collected_pages
        assert published_covid_page in collected_pages
        assert unpublished_page not in collected_pages


class TestExtractAreaSelectablePages:
    def test_returns_for_topic_pages_only(self):
        """
        Given a list of pages of different types
            including a `TopicPage` which is valid for the area selector
        When `extract_area_selectable_pages()` is called
        Then only the valid `TopicPage` model is returned
        """
        # Given
        valid_topic_page = FakeTopicPageFactory.build_covid_19_page_from_template()
        valid_topic_page.enable_area_selector = True

        # The topic page was not selected so should be excluded
        unselected_topic_page = (
            FakeTopicPageFactory.build_influenza_page_from_template()
        )
        unselected_topic_page.enable_area_selector = False

        # Although the build other viruses page was selected
        # It contains more than 1 topic and therefore is not included
        invalid_topic_page = (
            FakeTopicPageFactory.build_other_respiratory_viruses_page_from_template()
        )
        invalid_topic_page.enable_area_selector = True

        # Other page types do not implement the `is_valid_for_area_selector`
        # property and therefore should return False by default
        # and will be excluded
        other_pages = [
            FakeHomePageFactory.build_blank_page(slug="dashboard"),
            FakeWhatsNewParentPageFactory.build_page_from_template(live=True),
        ]
        all_pages = other_pages + [
            valid_topic_page,
            unselected_topic_page,
            invalid_topic_page,
        ]

        # When
        area_selectable_pages = extract_area_selectable_pages(all_pages=all_pages)

        # Then
        assert area_selectable_pages == [valid_topic_page]


class TestGetPagesForAreaSelector:
    @mock.patch(f"{MODULE_PATH}.collect_all_pages")
    def test_returns_correct_pages(self, spy_collect_all_pages: mock.MagicMock):
        """
        Given the `collect_all_pages()` function
            which returns a list of pages
        When `get_pages_for_area_selector()` is called
        Then
        """
        # Given
        mocked_valid_pages = [mock.Mock(is_valid_for_area_selector=True)] * 4
        # To simulate valid topic pages
        invalid_pages = [mock.Mock(is_valid_for_area_selector=False)] * 2
        # To simulate invalid topic pages

        fake_home_page = FakeHomePageFactory.build_blank_page()
        invalid_pages.append(fake_home_page)
        # To simulate an invalid page which
        # does not implement the `is_valid_for_area_selector` property

        all_pages = mocked_valid_pages + invalid_pages
        spy_collect_all_pages.return_value = all_pages

        # When
        pages = get_pages_for_area_selector()

        # Then
        assert set(pages) == set(mocked_valid_pages)
