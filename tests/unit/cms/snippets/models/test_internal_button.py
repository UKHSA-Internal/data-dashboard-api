from cms.snippets.models import InternalButton, InternalButtonTypes


class TestInternalButton:
    def test_text_and_type_can_be_provided(self):
        """
        Given a text and button_type
        When an `InternalButton` instance is created
        Then the text and type fields on the `InternalButton` instance.
        """
        # Given
        text = "bulk download"
        button_type = InternalButtonTypes.BULK_DOWNLOAD
        endpoint = "/api/bulkdownloads/v1"
        method = "POST"

        # When
        internal_button = InternalButton(
            text=text,
            button_type=button_type,
            endpoint=endpoint,
            method=method,
        )

        # Then
        assert internal_button.text == text
        assert internal_button.button_type == button_type

    def test_panels(self):
        """
        Given a text and button_type
        When an `InternalButton` instance is created
        Then the correct panels are set
        """
        # Given
        text = "bulk download"
        button_type = InternalButtonTypes.BULK_DOWNLOAD

        # When
        internal_button = InternalButton(
            text=text,
            button_type=button_type,
        )

        # Then
        panels = internal_button.panels
        panel_names: list[str] = [panel.field_name for panel in panels]

        assert "text" in panel_names
        assert "button_type" in panel_names

    def test_button_is_set_as_a_snippet(self):
        """
        Given a valid text and button_type
        When an `InternalButton` instance is created
        Then a URL is made available for the snippets view

        Notes:
            `snippets` are none-page type components
                which are available in wagtail for items
                which are not explicitly tied to an individual page
            See https://docs.wagtail.org/en/stable/topics/snippets/

        """
        # Given
        text = "bulk download"
        button_type = InternalButtonTypes.BULK_DOWNLOAD

        # When
        internal_button = InternalButton(
            text=text,
            button_type=button_type,
        )

        # Then
        assert (
            internal_button.snippet_viewset.url_prefix
            == "snippets/snippets/internalbutton"
        )
