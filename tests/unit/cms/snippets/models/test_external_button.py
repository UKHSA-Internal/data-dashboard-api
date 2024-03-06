from cms.snippets.models import ExternalButton, ExternalButtonIcons, ExternalButtonTypes


class TestExternalButton:

    def test_button_fields_can_be_provided(self):
        """
        Given a text, url, button_type and button_icon
        When an `ExternalButton` instance is created
        Then the expected fields are on the `ExternalButton` instance
        """
        # Given
        text = "download"
        url = "https://www.example.com"
        button_type = ExternalButtonTypes.PRIMARY.value
        icon = ExternalButtonIcons.DOWNLOAD.value

        # When
        button = ExternalButton(
            text=text,
            url=url,
            button_type=button_type,
            icon=icon,
        )

        # Then
        assert button.text == text
        assert button.url == url
        assert button.button_type == button_type
        assert button.icon == icon

    def test_panels(self):
        """
        Given text, url, button_type and icon field
        When an `ExternalButton` instance is created
        Then the correct panels are set
        """
        # Given
        text = "download"
        url = "https://www.google.com"
        button_type = ExternalButtonTypes.PRIMARY.value
        icon = ExternalButtonIcons.DOWNLOAD.value

        # When
        button = ExternalButton(
            text=text,
            url=url,
            button_type=button_type,
            icon=icon,
        )

        # Then
        panels = button.panels
        panel_names: list[str] = [panel.field_name for panel in panels]

        assert "text" in panel_names
        assert "url" in panel_names
        assert "button_type" in panel_names
        assert "icon" in panel_names

    def test_external_button_is_set_as_a_snippet(self):
        """
        Given a text, url, button_type and icon
        When an `ExternalButton` instance is created
        Then a URL is made available for the snippets view
        """
        # Given
        text = "download"
        url = "https://www.google.com"
        button_type = ExternalButtonTypes.PRIMARY.value
        icon = ExternalButtonIcons.DOWNLOAD.value

        # When
        button = ExternalButton(
            text=text,
            url=url,
            button_type=button_type,
            icon=icon,
        )

        # Then
        assert button.snippet_viewset.url_prefix == "snippets/snippets/externalbutton"
