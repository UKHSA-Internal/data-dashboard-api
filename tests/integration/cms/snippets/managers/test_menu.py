import pytest

from cms.snippets.models.menu_builder import Menu, SimpleMenu
from tests.factories.cms.snippets.menu import MenuFactory, SimpleMenuFactory


class TestMenuManager:
    @pytest.mark.django_db
    def test_has_active_menu(self):
        """
        Given a number of `Menu` records
            of which 1 has `is_active` set to True
        When `has_active_menu()` is called
            from the `MenuManager`
        Then True is returned
        """
        # Given
        MenuFactory.create(is_active=True)
        MenuFactory.create(is_active=False)

        # When
        has_active_menu: bool = Menu.objects.has_active_menu()

        # Then
        assert has_active_menu is True

    @pytest.mark.django_db
    def test_get_active_menu(self):
        """
        Given a number of `Menu` records
            of which 1 has `is_active` set to True
        When `get_active_menu()` is called
            from the `MenuManager`
        Then the correct `Menu` record is returned
        """
        # Given
        active_menu = MenuFactory.create(is_active=True)
        inactive_menu = MenuFactory.create(is_active=False)

        # When
        retrieved_menu: bool = Menu.objects.get_active_menu()

        # Then
        assert retrieved_menu == active_menu != inactive_menu


class TestSimpleMenuManager:
    @pytest.mark.django_db
    def test_has_active_menu(self):
        """
        Given a number of `SimpleMenu` records
            of which 1 has `is_active` set to True
        When `has_active_menu()` is called
            from the `SimpleMenuManager`
        Then True is returned
        """
        # Given
        SimpleMenuFactory.create(is_active=True)
        SimpleMenuFactory.create(is_active=False)

        # When
        has_active_menu: bool = SimpleMenu.objects.has_active_menu()

        # Then
        assert has_active_menu is True

    @pytest.mark.django_db
    def test_get_active_menu(self):
        """
        Given a number of `SimpleMenu` records
            of which 1 has `is_active` set to True
        When `get_active_menu()` is called
            from the `SimpleMenuManager`
        Then the correct `SimpleMenu` record is returned
        """
        # Given
        active_menu = SimpleMenuFactory.create(is_active=True)
        inactive_menu = SimpleMenuFactory.create(is_active=False)

        # When
        retrieved_menu: bool = SimpleMenu.objects.get_active_menu()

        # Then
        assert retrieved_menu == active_menu != inactive_menu
