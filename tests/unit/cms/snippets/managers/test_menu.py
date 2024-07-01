from unittest import mock

from cms.snippets.managers.menu import MenuManager
from cms.snippets.models import Menu


class TestMenuManager:
    @mock.patch.object(MenuManager, "has_active_menu")
    def test_is_menu_overriding_currently_active_menu_returns_false_for_no_active_menu(
        self, mocked_has_active_menu: mock.MagicMock
    ):
        """
        Given the `has_active_menu()` method returns False
        When `is_menu_overriding_currently_active_menu()` is called
            from the `MenuManager`
        Then False is returned
        """
        # Given
        mocked_has_active_menu.return_value = False
        menu_manager = Menu.objects

        # When
        menu_is_overriding: bool = (
            menu_manager.is_menu_overriding_currently_active_menu(menu=mock.Mock())
        )

        # Then
        assert menu_is_overriding is False

    @mock.patch.object(MenuManager, "has_active_menu")
    @mock.patch.object(MenuManager, "get_active_menu")
    def test_is_menu_overriding_currently_active_menu_returns_false_for_new_inactive_menu(
        self,
        mocked_get_active_menu: mock.MagicMock,
        mocked_has_active_menu: mock.MagicMock,
    ):
        """
        Given the `has_active_menu()` method returns True
        And a new `Menu` object which is inactive
        When `is_menu_overriding_currently_active_menu()` is called
            from the `MenuManager`
        Then False is returned
        """
        # Given
        mocked_get_active_menu.return_value = mock.Mock()
        mocked_has_active_menu.return_value = True
        menu_manager = Menu.objects
        mocked_new_menu = mock.Mock(is_active=False)

        # When
        menu_is_overriding: bool = (
            menu_manager.is_menu_overriding_currently_active_menu(menu=mocked_new_menu)
        )

        # Then
        assert menu_is_overriding is False

    @mock.patch.object(MenuManager, "has_active_menu")
    @mock.patch.object(MenuManager, "get_active_menu")
    def test_is_menu_overriding_currently_active_menu_returns_false_when_active_menu_is_being_updated(
        self,
        mocked_get_active_menu: mock.MagicMock,
        mocked_has_active_menu: mock.MagicMock,
    ):
        """
        Given the `has_active_menu()` method returns True
        And that same `Menu` object which is just being updated
        When `is_menu_overriding_currently_active_menu()` is called
            from the `MenuManager`
        Then False is returned
        """
        # Given
        mocked_has_active_menu.return_value = True
        mocked_menu = mock.Mock(is_active=True)
        mocked_get_active_menu.return_value = mocked_menu
        menu_manager = Menu.objects

        # When
        menu_is_overriding: bool = (
            menu_manager.is_menu_overriding_currently_active_menu(menu=mocked_menu)
        )

        # Then
        assert menu_is_overriding is False

    @mock.patch.object(MenuManager, "has_active_menu")
    @mock.patch.object(MenuManager, "get_active_menu")
    def test_is_menu_overriding_currently_active_menu_returns_true_when_active_menu_is_being_overriden(
        self,
        mocked_get_active_menu: mock.MagicMock,
        mocked_has_active_menu: mock.MagicMock,
    ):
        """
        Given the `has_active_menu()` method returns True
        And a new `Menu` object which is active
        When `is_menu_overriding_currently_active_menu()` is called
            from the `MenuManager`
        Then True is returned
        """
        # Given
        mocked_has_active_menu.return_value = True
        mocked_existing_active_menu = mock.Mock(is_active=True)
        mocked_get_active_menu.return_value = mocked_existing_active_menu
        new_mocked_menu = mock.Mock(is_active=True)
        menu_manager = Menu.objects

        # When
        menu_is_overriding: bool = (
            menu_manager.is_menu_overriding_currently_active_menu(menu=new_mocked_menu)
        )

        # Then
        assert menu_is_overriding is True
