from unittest import mock

import pytest

from cms.whats_new.models.parent import (
    WhatsNewParentMultipleLivePagesError,
    WhatsNewParentPage,
    WhatsNewParentSlugNotValidError,
)
from tests.fakes.factories.cms.whats_new_parent_page_factory import (
    FakeWhatsNewParentPageFactory,
)
from tests.fakes.models.queryset import FakeQuerySet


class TestWhatsNewParentPage:
    @mock.patch.object(WhatsNewParentPage, "_raise_error_if_slug_not_whats_new")
    @mock.patch.object(WhatsNewParentPage, "_raise_error_for_multiple_live_pages")
    def test_clean_delegates_extra_validation_calls(
        self,
        spy_raise_error_for_multiple_live_pages: mock.MagicMock,
        spy_raise_error_if_slug_not_whats_new: mock.MagicMock,
    ):
        """
        Given a `WhatsNewParentPage`
        When `clean()` is called from that model
        Then the extra validation methods are called out to

        Patches:
            `spy_raise_error_for_multiple_live_pages`: To check
                validation is performed for preventing multiple live pages
           `spy_raise_error_if_slug_not_whats_new`: To check
                validation is performed for preventing a slug which
                does not contain `whats-new`

        """
        # Given
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template()
        )

        # When
        fake_whats_new_parent_page.clean()

        # Then
        spy_raise_error_for_multiple_live_pages.assert_called_once()
        spy_raise_error_if_slug_not_whats_new.assert_called_once()

    @mock.patch.object(WhatsNewParentPage, "_raise_error_if_slug_not_whats_new")
    @mock.patch.object(WhatsNewParentPage, "_raise_error_for_multiple_live_pages")
    def test_clean_passes_for_trash_can_slug(
        self,
        spy_raise_error_for_multiple_live_pages: mock.MagicMock,
        spy_raise_error_if_slug_not_whats_new: mock.MagicMock,
    ):
        """
        Given a `WhatsNewParentPage` which has slug prefixed with "trash-"
        When `clean()` is called from that model
        Then the extra validation methods are called out to

        Patches:
            `spy_raise_error_for_multiple_live_pages`: To check
                validation is performed for preventing multiple live pages
            `spy_raise_error_if_slug_not_whats_new`: To check
                validation is performed for preventing a slug which
                does not contain `whats-new`

        """
        # Given
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template()
        )
        fake_whats_new_parent_page.slug = "trash-whats-new"

        # When
        fake_whats_new_parent_page.clean()

        # Then
        spy_raise_error_for_multiple_live_pages.assert_called_once()
        spy_raise_error_if_slug_not_whats_new.assert_called_once()

    def test_raise_error_if_slug_not_whats_new(self):
        """
        Given an invalid slug which is not equal to `whats-new`
        When `_raise_error_if_slug_not_whats_new()` is called
            from an instance of a `WhatNewParentPage`
        Then a `WhatsNewParentSlugNotValidError` is raised
        """
        # Given
        invalid_slug = "not-valid-slug"
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template(slug=invalid_slug)
        )

        # When / Then
        with pytest.raises(WhatsNewParentSlugNotValidError):
            fake_whats_new_parent_page._raise_error_if_slug_not_whats_new()

    def test_raise_error_if_slug_not_whats_new_passes_for_valid_slug(self):
        """
        Given a slug which is equal to `whats-new`
        When `_raise_error_if_slug_not_whats_new()` is called
            from an instance of a `WhatNewParentPage`
        Then no error is raised
        """
        # Given
        valid_slug = "whats-new"
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template(slug=valid_slug)
        )

        # When / Then
        fake_whats_new_parent_page._raise_error_if_slug_not_whats_new()

    @mock.patch.object(WhatsNewParentPage, "objects")
    def test_raise_error_for_multiple_live_pages_passes_for_no_current_live_pages(
        self, spy_whats_new_parent_page_model_manager: mock.MagicMock
    ):
        """
        Given a `WhatsNewParentPage` model manager which returns no live pages
        When `_raise_error_for_multiple_live_pages()` is called
            from an instance of `WhatsNewParentPage`
        Then no error is raised

        Patches:
            `spy_whats_new_parent_page_model_manager`: To isolate the model manager
                and emulate the returned queryset from the database

        """
        # Given
        fake_queryset = FakeQuerySet(instances=[])
        spy_whats_new_parent_page_model_manager.get_live_pages.return_value = (
            fake_queryset
        )
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template()
        )

        # When / Then
        fake_whats_new_parent_page._raise_error_for_multiple_live_pages()

    @mock.patch.object(WhatsNewParentPage, "objects")
    def test_raise_error_for_multiple_live_pages_passes_for_current_page_being_republished(
        self, spy_whats_new_parent_page_model_manager: mock.MagicMock
    ):
        """
        Given a `WhatsNewParentPage` model manager which returns only the current live page
        When `_raise_error_for_multiple_live_pages()` is called
            from an instance of `WhatsNewParentPage`
        Then no error is raised

        Patches:
            `spy_whats_new_parent_page_model_manager`: To isolate the model manager
                and emulate the returned queryset from the database

        """
        # Given
        fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template()
        )
        fake_queryset = FakeQuerySet(instances=[fake_whats_new_parent_page])
        spy_whats_new_parent_page_model_manager.get_live_pages.return_value = (
            fake_queryset
        )

        # When / Then
        fake_whats_new_parent_page._raise_error_for_multiple_live_pages()

    @mock.patch.object(WhatsNewParentPage, "objects")
    def test_raise_error_for_multiple_live_pages_raises_error(
        self, spy_whats_new_parent_page_model_manager: mock.MagicMock
    ):
        """
        Given a `WhatsNewParentPage` model manager which returns
            a different live page from the current page
        When `_raise_error_for_multiple_live_pages()` is called
            from an instance of `WhatsNewParentPage`
        Then a `WhatsNewParentMultipleLivePagesError` is raised

        Patches:
            `spy_whats_new_parent_page_model_manager`: To isolate the model manager
                and emulate the returned queryset from the database

        """
        # Given
        current_fake_whats_new_parent_page = (
            FakeWhatsNewParentPageFactory.build_page_from_template(pk=1)
        )
        fake_queryset = FakeQuerySet(instances=[current_fake_whats_new_parent_page])
        spy_whats_new_parent_page_model_manager.get_live_pages.return_value = (
            fake_queryset
        )

        invalid_duplicate_page = FakeWhatsNewParentPageFactory.build_page_from_template(
            pk=2
        )

        # When / Then
        with pytest.raises(WhatsNewParentMultipleLivePagesError):
            invalid_duplicate_page._raise_error_for_multiple_live_pages()
