from cms.snippets.models.menu_builder import Menu
from cms.snippets.serializers import (
    MenuResponseSerializer,
    MenuSerializer,
)
from tests.fakes.managers.cms.menu_manager import FakeMenuManager


class TestMenuResponseSerializer:
    def test_serializes_model_correctly(self):
        """
        Given a `Menu` model instance
        When the model is passed to a `MenuResponseSerializer`
        Then the output `data` contains the correct fields
        """
        # Given
        fake_body = []
        menu = Menu(internal_label="abc", is_active=True, body=fake_body)

        # When
        serializer = MenuResponseSerializer(instance=menu)

        # Then
        expected_data = {"active_menu": fake_body}
        assert serializer.data == expected_data

    def test_data_returns_none_if_no_model_instance_is_provided(self):
        """
        Given no `Menu` model instance is provided
        When this is passed to a `MenuResponseSerializer`
        Then the output `data` returns None
        """
        # Given / When
        serializer = MenuResponseSerializer(instance=None)

        # Then
        assert serializer.data == {"active_menu": None}


class TestMenuSerializer:
    def test_serialized_data_for_active_menu(self):
        """
        Given a `Menu` model instance which is active
        And an inactive `Menu` model instance
        When `data` is called from an instance
            of the `MenuSerializer`
        Then the output `data` contains info
            about the currently active menu
        """
        # Given
        fake_body = []
        active_menu = Menu(internal_label="abc", is_active=True, body=fake_body)
        inactive_menu = Menu(internal_label="abc", is_active=False)
        fake_menu_manager = FakeMenuManager(menus=[active_menu, inactive_menu])

        # When
        serializer = MenuSerializer(context={"menu_manager": fake_menu_manager})

        # Then
        expected_data = {"active_menu": fake_body}
        assert serializer.data == expected_data
