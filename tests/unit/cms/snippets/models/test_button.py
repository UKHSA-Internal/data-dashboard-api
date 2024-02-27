from cms.snippets.models import Button, ButtonTypes


class TestButton:
    def test_text_and_type_can_be_provided(self):
        """
        Given a text, loading_text and button_type
        When a `Button` instance is created
        Then the text and type fields on the `button` instance
        """
        # Given
        text = "download"
        loading_text = "downloading"
        endpoint = "/api/bulkdownloads/v1"
        method = "POST"
        button_type = ButtonTypes.DOWNLOAD

        # When
        button = Button(
            text=text,
            loading_text=loading_text,
            endpoint=endpoint,
            method=method,
            button_type=button_type,
        )

        # Then
        assert button.text == text
        assert button.loading_text == loading_text
        assert button.endpoint == endpoint
        assert button.method == method
        assert button.button_type == button_type

    def test_panels(self):
        """
        Given a text, text_loading and button_type
        When a `button` instance is created
        Then the correct panels are set
        """
        # Given
        text = "download"
        loading_text = "downloading"
        button_type = ButtonTypes.DOWNLOAD

        # When
        button = Button(
            text=text,
            loading_text=loading_text,
            button_type=button_type,
        )

        # Then
        panels = button.panels
        panel_names: list[str] = [panel.field_name for panel in panels]

        assert "text" in panel_names
        assert "loading_text" in panel_names
        assert "button_type" in panel_names

    def test_button_is_set_as_a_snippet(self):
        """
        Given a text, loading_text and button_type
        When a `Button` instance is created
        Then a URL is made available for the snippets view

        Notes:
            `snippets` are none-page type components
                which are available in wagtail for items
                which are not explicitly tied to an individual page
            See https://docs.wagtail.org/en/stable/topics/snippets/

        """
        # Given
        text = "download"
        loading_text = "downloading"
        button_type = ButtonTypes.DOWNLOAD

        # When
        button = Button(
            text=text,
            loading_text=loading_text,
            button_type=button_type,
        )

        # Then
        assert button.snippet_viewset.url_prefix == "snippets/snippets/button"
