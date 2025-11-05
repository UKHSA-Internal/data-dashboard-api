from cms.snippets.models import WeatherAlertButton


class TestWeatherAlertButton:
    def test_attributes_can_be_provided(self):
        """
        Given a text, button_type and geography_code
        When an `WeatherAlertButton` instance is created
        Then the text and button_type fields
            on the `WeatherAlertButton` are created.
        """
        # Given
        text = "view map on weather health alerts"
        button_type = "Heat"

        # When
        weather_alert_button = WeatherAlertButton(text=text, button_type=button_type)

        # Then
        assert weather_alert_button.text == text
        assert weather_alert_button.button_type == button_type

    def test_panels(self):
        """
        Given a text, button_type and geography_code
        When a `WeatherAlertButton` instance is created
        Then the correct panels are set
        """
        # Given
        text = "view map on weather health alerts"
        button_type = "Heat"

        # When
        weather_alert_button = WeatherAlertButton(text=text, button_type=button_type)

        # Then
        panels = weather_alert_button.panels
        panel_names: list[str] = [panel.field_name for panel in panels]

        assert "text" in panel_names
        assert "button_type" in panel_names

    def test_button_is_set_as_snippet(self):
        """
        Given a valid text, button_type and geography_code
        When a `WeatherAlertButton` instance is created
        Then a URL is made available for the snippets view

        Notes:
            `snippets` are none-page type components
                which are available in wagtail for items
                which are not explicitly tied to an individual page
            See https://docs.wagtail.org/en/stable/topics/snippets/

        """
        # Given
        text = "view map on weather health alerts"
        button_type = "Heat"

        # When
        weather_alert_button = WeatherAlertButton(text=text, button_type=button_type)

        # Then
        assert (
            weather_alert_button.snippet_viewset.url_prefix
            == "snippets/snippets/weatheralertbutton"
        )
