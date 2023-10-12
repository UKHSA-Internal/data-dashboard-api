from cms.whats_new.colour_scheme import BadgeColours
from cms.whats_new.models import Badge


class TestBadge:
    def test_text_and_colour_can_be_provided(self):
        """
        Given a text and a colour
        When a `Badge` instance is created
        Then the text and colour are set on the `Badge` instance
        """
        # Given
        text = "DATA ISSUE"
        colour = BadgeColours.GREY

        # When
        badge = Badge(text=text, colour=colour)

        # Then
        assert badge.text == text
        assert badge.colour == colour

    def test_panels(self):
        """
        Given a text and a colour
        When a `Badge` instance is created
        Then the correct panels are set
        """
        # Given
        text = "DATA_ISSUE"
        colour = BadgeColours.GREY

        # When
        badge = Badge(text=text, colour=colour)

        # Then
        panels = badge.panels
        panel_names: list[str] = [panel.field_name for panel in panels]

        assert "text" in panel_names
        assert "colour" in panel_names

    def test_api_fields(self):
        """
        Given a text and a colour
        When a `Badge` instance is created
        Then the correct API fields are set
        """
        # Given
        text = "DATA_ISSUE"
        colour = BadgeColours.GREY

        # When
        badge = Badge(text=text, colour=colour)

        # Then
        api_fields = badge.api_fields
        api_field_names: list[str] = [api_field.name for api_field in api_fields]

        assert "text" in api_field_names
        assert "colour" in api_field_names

    def test_badge_is_set_as_a_snippet(self):
        """
        Given a text and a colour
        When a `Badge` instance is created
        Then a URL is made available for the snippets view

        Notes:
            `snippets` are none-page type components
                which are available in wagtail for items
                which are not explicitly tied to an individual page
            See https://docs.wagtail.org/en/stable/topics/snippets/

        """
        # Given
        text = "DATA_ISSUE"
        colour = BadgeColours.GREY

        # When
        badge = Badge(text=text, colour=colour)

        # Then
        assert badge.snippet_viewset.url_prefix == "snippets/whats_new/badge"
