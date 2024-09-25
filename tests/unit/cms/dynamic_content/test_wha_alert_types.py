from cms.dynamic_content.cards import WHAlerts


class TestWHAlertsTextChoices:
    def test_returns_tuple_of_alert_types(self):
        """
        Given a tuple of expected alerts taken from `WHAlerts` attributes
        When `get_alerts()` is called
        Then the expected alerts are returned
        """
        # Given
        expected_alerts = tuple((item.value, item.value) for item in WHAlerts)

        # When
        returned_alerts = WHAlerts.get_alerts()

        # Then
        assert returned_alerts == expected_alerts
