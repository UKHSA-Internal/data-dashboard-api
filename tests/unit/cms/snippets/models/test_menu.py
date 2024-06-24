from unittest import mock

import pytest

from cms.snippets.managers.menu import MenuManager
from cms.snippets.models.menu_builder.menu import Menu, MultipleMenusActiveError


class TestMenu:
    @pytest.mark.parametrize(
        "expected_panel_name",
        [
            "internal_label",
            "is_active",
            "body",
        ],
    )
    def test_panels(self, expected_panel_name: str):
        """
        Given a body, an internal label and an is_active bool
        When a `Menu` instance is created
        Then the correct panels are set
        """
        # Given
        internal_label = "abc"
        is_active = True
        body = {}

        # When
        menu = Menu(
            internal_label=internal_label,
            is_active=is_active,
            body=body,
        )

        # Then
        panel_names: set[str] = {panel.field_name for panel in menu.panels}
        assert expected_panel_name in panel_names

    def test_enabled_set_false_by_default(self):
        """
        Given a `Menu` model
        When the object is initialized
        Then the `is_active` field is set to False by default
        """
        # Given
        internal_label = "abc"
        body = {}

        # When
        menu = Menu(
            internal_label=internal_label,
            body=body,
        )

        # Then
        assert menu.is_active is False

    def test_menu_dunder_str_references_internal_label(self):
        """
        Given a `Menu` model
            which has been given an `internal_label` of True
        When the string representation is produced
        Then the string references the `internal_label`
        """
        # Given
        internal_label = "abc"
        is_active = True
        body = {}

        # When
        menu = Menu(
            internal_label=internal_label,
            body=body,
            is_active=is_active,
        )

        # Then
        assert str(menu) == f"(Active) - {internal_label}"

    def test_inactive_menu_produces_correct_dunder_str(self):
        """
        Given a `Menu` model
            which has been given an `internal_label` of False
        When the string representation is produced
        Then the string references the `internal_label`
        """
        # Given
        internal_label = "abc"
        body = {}
        is_active = False

        # When
        menu = Menu(
            internal_label=internal_label,
            body=body,
            is_active=is_active,
        )

        # Then
        assert str(menu) == f"(Inactive) - {internal_label}"

    @mock.patch.object(MenuManager, "has_active_menu")
    def test_clean_raises_error_if_active_menu_already_exists(
        self, mocked_has_active_menu: mock.MagicMock
    ):
        """
        Given a `Menu` which is being set to active
        And the `MenuManager`
            which says there is already an active menu
        When the `clean()` method is called from the `Menu`
        Then the `MultipleMenusActiveError` is raised
        """
        # Given
        mocked_has_active_menu.return_value = True
        menu = Menu(
            internal_label="abc",
            body={},
            is_active=True,
        )

        # When / Then
        with pytest.raises(MultipleMenusActiveError):
            menu.clean()

    @mock.patch.object(MenuManager, "has_active_menu")
    def test_clean_passes_when_current_menu_is_not_being_activated(
        self, mocked_has_active_menu: mock.MagicMock
    ):
        """
        Given a `Menu` which is not being set to active
        And the `MenuManager`
            which says there is already an active menu
        When the `clean()` method is called from the `Menu`
        Then no error is raised
        """
        # Given
        mocked_has_active_menu.return_value = True
        menu = Menu(
            internal_label="abc",
            body={},
            is_active=False,
        )

        # When / Then
        menu.clean()

    @mock.patch.object(MenuManager, "has_active_menu")
    def test_clean_passes_when_current_menu_is_being_activated_as_only_active_menu(
        self, mocked_has_active_menu: mock.MagicMock
    ):
        """
        Given a `Menu` which is being set to active
        And the `MenuManager`
            which says there is not already an active menu
        When the `clean()` method is called from the `Menu`
        Then no error is raised
        """
        # Given
        mocked_has_active_menu.return_value = False
        menu = Menu(
            internal_label="abc",
            body={},
            is_active=True,
        )

        # When / Then
        menu.clean()

    @mock.patch.object(MenuManager, "has_active_menu")
    def test_clean_passes_when_there_is_no_existing_active_menu(
        self, mocked_has_active_menu: mock.MagicMock
    ):
        """
        Given a `Menu` which is not being set to active
        And the `MenuManager`
            which says there is not already an active menu
        When the `clean()` method is called
            from the `Menu`
        Then no error is raised
        """
        # Given
        mocked_has_active_menu.return_value = False
        menu = Menu(
            internal_label="abc",
            body={},
            is_active=False,
        )

        # When / Then
        menu.clean()
