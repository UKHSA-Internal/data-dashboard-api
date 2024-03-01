from cms.snippets.models.external_button import ExternalButtonIcons, ExternalButtonTypes


class TestExternalButtonTypeTextChoices:

    def test_returns_tuple_of_button_types(self):
        """
        Given a tuple of expected button choices taken from `ExternalButtonTypes` attributes
        When `get_external_button_types()` is called
        Then the expected button types are returned
        """
        # Given
        expected_button_types = tuple(
            (item.value, item.value) for item in ExternalButtonTypes
        )

        # When
        returned_button_types = ExternalButtonTypes.get_external_button_types()

        # Then
        assert returned_button_types == expected_button_types


class TestExternalButtonIconsChoices:

    def test_returns_tuple_of_icons(self):
        """
        Given a tuple of expected icon choices taken from `ExternalButtonIcons` attributes
        When `get_external_button_icons()` is called
        Then the expected button icons are returned
        """
        # Given
        expected_button_icons = tuple(
            (item.value, item.value) for item in ExternalButtonIcons
        )

        # When
        returned_button_icons = ExternalButtonIcons.get_external_button_icons()

        # Then
        assert returned_button_icons == expected_button_icons
