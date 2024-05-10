import datetime

from metrics.domain.weather_health_alerts.mapping import (
    WeatherHealthAlertTopics,
    WeatherHealthAlertStatusColour,
)
from metrics.interfaces.weather_health_alerts.access import (
    WeatherHealthAlertsInterface,
    WEATHER_HEALTH_ALERT_DETAILED_DATA,
)
from tests.fakes.factories.metrics.headline_factory import FakeCoreHeadlineFactory
from tests.fakes.managers.headline_manager import FakeCoreHeadlineManager
from django.utils import timezone
from metrics.domain.weather_health_alerts.text_lookups import HEAT_ALERT_TEXT_LOOKUP

from tests.fakes.models.metrics.headline import FakeCoreHeadline


class TestWeatherHealthAlertsInterfaceBuildDetailedDataForAlert:
    def test_for_non_existent_alert(self):
        """
        Given no matching `CoreHeadline` for a given `geography_code`
        When `build_detailed_data_for_alert()` is called
            from an instance of `WeatherHealthAlertsInterface`
        Then the default fallback data is returned
            stating the alert is green/normal
            with timestamps of None

        Notes:
            We really only expect this to occur,
            when the database has never been sent an alert
            i.e. on day 1 of alerts.

        """
        # Given
        topic_name = WeatherHealthAlertTopics.HEAT_ALERT.value
        metric_name = "heat-alert_headline_matrixNumber"
        geography_code = "E07000115"
        fake_core_headline_manager = FakeCoreHeadlineManager(headlines=[])
        weather_health_alerts_interface = WeatherHealthAlertsInterface(
            core_headline_manager=fake_core_headline_manager
        )

        # When
        detailed_alarm_data: WEATHER_HEALTH_ALERT_DETAILED_DATA = (
            weather_health_alerts_interface.build_detailed_data_for_alert(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_code=geography_code,
            )
        )

        # Then
        assert (
            detailed_alarm_data["status"] == WeatherHealthAlertStatusColour.GREEN.value
        )
        assert detailed_alarm_data["text"] == HEAT_ALERT_TEXT_LOOKUP[1]
        assert detailed_alarm_data["period_end"] is None
        assert detailed_alarm_data["period_start"] is None
        assert detailed_alarm_data["refresh_date"] is None

    def test_for_alert_which_has_expired(self):
        """
        Given a matching `CoreHeadline` for a given `geography_code`
            which has had its `period_end` expired
        When `build_detailed_data_for_alert()` is called
            from an instance of `WeatherHealthAlertsInterface`
        Then the correct data is returned
            stating the alert is green/normal
            with timestamps matching the previous alert

        Notes:
            We expect this to occur whenever an alert has expired/
            In this case, we assume that the status
            can be considered as green/normal

        """
        # Given
        topic_name = WeatherHealthAlertTopics.HEAT_ALERT.value
        metric_name = "heat-alert_headline_matrixNumber"
        geography_code = "E07000115"
        two_weeks_ago = timezone.now() - datetime.timedelta(days=14)
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        red_alert_metric_value = 16
        fake_expired_red_alert: FakeCoreHeadline = FakeCoreHeadlineFactory.build_record(
            topic_name=topic_name,
            metric_name=metric_name,
            metric_value=red_alert_metric_value,
            geography_code=geography_code,
            period_end=one_week_ago,
            refresh_date=two_weeks_ago,
        )

        fake_core_headline_manager = FakeCoreHeadlineManager(
            headlines=[fake_expired_red_alert]
        )
        weather_health_alerts_interface = WeatherHealthAlertsInterface(
            core_headline_manager=fake_core_headline_manager
        )

        # When
        detailed_alarm_data: WEATHER_HEALTH_ALERT_DETAILED_DATA = (
            weather_health_alerts_interface.build_detailed_data_for_alert(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_code=geography_code,
            )
        )

        # Then
        assert (
            detailed_alarm_data["status"] == WeatherHealthAlertStatusColour.GREEN.value
        )
        assert detailed_alarm_data["text"] == HEAT_ALERT_TEXT_LOOKUP[1]
        assert detailed_alarm_data["period_end"] is fake_expired_red_alert.period_end
        assert (
            detailed_alarm_data["period_start"] is fake_expired_red_alert.period_start
        )
        assert detailed_alarm_data["refresh_date"] is fake_expired_red_alert.period_end

    def test_for_alert_which_is_currently_live(self):
        """
        Given a matching `CoreHeadline` for a given `geography_code`
            which is currently live
        When `build_detailed_data_for_alert()` is called
            from an instance of `WeatherHealthAlertsInterface`
        Then the correct data is returned

        Notes:
            We expect this to occur whenever an alert is live
            i.e. the `period_end` is greater than the current time

        """
        # Given
        topic_name = WeatherHealthAlertTopics.HEAT_ALERT.value
        metric_name = "heat-alert_headline_matrixNumber"
        geography_code = "E07000115"
        two_weeks_from_now = timezone.now() + datetime.timedelta(days=14)
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        red_alert_metric_value = 16
        fake_expired_red_alert: FakeCoreHeadline = FakeCoreHeadlineFactory.build_record(
            topic_name=topic_name,
            metric_name=metric_name,
            metric_value=red_alert_metric_value,
            geography_code=geography_code,
            period_end=two_weeks_from_now,
            refresh_date=one_week_ago,
        )

        fake_core_headline_manager = FakeCoreHeadlineManager(
            headlines=[fake_expired_red_alert]
        )
        weather_health_alerts_interface = WeatherHealthAlertsInterface(
            core_headline_manager=fake_core_headline_manager
        )

        # When
        detailed_alarm_data: WEATHER_HEALTH_ALERT_DETAILED_DATA = (
            weather_health_alerts_interface.build_detailed_data_for_alert(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_code=geography_code,
            )
        )

        # Then
        assert detailed_alarm_data["status"] == WeatherHealthAlertStatusColour.RED.value
        assert detailed_alarm_data["text"] == HEAT_ALERT_TEXT_LOOKUP[16]
        assert detailed_alarm_data["period_end"] is fake_expired_red_alert.period_end
        assert (
            detailed_alarm_data["period_start"] is fake_expired_red_alert.period_start
        )
        assert (
            detailed_alarm_data["refresh_date"] is fake_expired_red_alert.refresh_date
        )


class TestWeatherHealthAlertsInterfaceBuildSummaryDataForAlerts:
    def test_for_non_existent_alerts(self):
        """
        Given no matching `CoreHeadline` for given `geography_codes`
        When `build_summary_data_for_alerts()` is called
            from an instance of `WeatherHealthAlertsInterface`
        Then the default fallback data is returned
            stating each alert is green/normal
            with timestamps of None

        Notes:
            We really only expect this to occur,
            when the database has never been sent an alert
            i.e. on day 1 of alerts.

        """
        # Given
        topic_name = WeatherHealthAlertTopics.HEAT_ALERT.value
        metric_name = "heat-alert_headline_matrixNumber"
        first_geography_code = "E07000115"
        second_geography_code = "E07000120"
        geography_codes = [first_geography_code, second_geography_code]

        fake_core_headline_manager = FakeCoreHeadlineManager(headlines=[])
        weather_health_alerts_interface = WeatherHealthAlertsInterface(
            core_headline_manager=fake_core_headline_manager
        )

        # When
        summary_alarm_data: WEATHER_HEALTH_ALERT_DETAILED_DATA = (
            weather_health_alerts_interface.build_summary_data_for_alerts(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_codes=geography_codes,
            )
        )

        # Then
        assert len(summary_alarm_data) == len(geography_codes)
        assert (
            summary_alarm_data[first_geography_code]["status"]
            == WeatherHealthAlertStatusColour.GREEN.value
        )
        assert summary_alarm_data[first_geography_code]["refresh_date"] is None
        assert (
            summary_alarm_data[second_geography_code]["status"]
            == WeatherHealthAlertStatusColour.GREEN.value
        )
        assert summary_alarm_data[second_geography_code]["refresh_date"] is None

    def test_for_alerts_which_have_expired(self):
        """
        Given matching `CoreHeadline` records for given `geography_codes`
            which have expired `period_end` times
        When `build_summary_data_for_alerts()` is called
            from an instance of `WeatherHealthAlertsInterface`
        Then the correct data is returned for each alert
            stating each alert is green/normal
            with timestamps matching the previous alert

        Notes:
            We expect this to occur whenever alerts have expired/
            In this case, we assume that the status
            can be considered as green/normal

        """
        # Given
        topic_name = WeatherHealthAlertTopics.HEAT_ALERT.value
        metric_name = "heat-alert_headline_matrixNumber"
        first_geography_code = "E07000115"
        second_geography_code = "E07000120"
        two_weeks_ago = timezone.now() - datetime.timedelta(days=14)
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        red_alert_metric_value = 16
        fake_expired_red_alert_for_first_geography: FakeCoreHeadline = (
            FakeCoreHeadlineFactory.build_record(
                topic_name=topic_name,
                metric_name=metric_name,
                metric_value=red_alert_metric_value,
                geography_code=first_geography_code,
                period_end=one_week_ago,
                refresh_date=two_weeks_ago,
            )
        )
        fake_expired_red_alert_for_second_geography: FakeCoreHeadline = (
            FakeCoreHeadlineFactory.build_record(
                topic_name=topic_name,
                metric_name=metric_name,
                metric_value=red_alert_metric_value,
                geography_code=second_geography_code,
                period_end=one_week_ago,
                refresh_date=two_weeks_ago,
            )
        )

        fake_core_headline_manager = FakeCoreHeadlineManager(
            headlines=[
                fake_expired_red_alert_for_first_geography,
                fake_expired_red_alert_for_second_geography,
            ]
        )
        weather_health_alerts_interface = WeatherHealthAlertsInterface(
            core_headline_manager=fake_core_headline_manager
        )

        # When
        summary_alarm_data: WEATHER_HEALTH_ALERT_DETAILED_DATA = (
            weather_health_alerts_interface.build_summary_data_for_alerts(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_codes=[first_geography_code, second_geography_code],
            )
        )

        # Then
        assert len(summary_alarm_data) == 2
        assert (
            summary_alarm_data[first_geography_code]["status"]
            == WeatherHealthAlertStatusColour.GREEN.value
        )
        assert (
            summary_alarm_data[first_geography_code]["refresh_date"]
            == fake_expired_red_alert_for_first_geography.period_end
        )
        assert (
            summary_alarm_data[second_geography_code]["status"]
            == WeatherHealthAlertStatusColour.GREEN.value
        )
        assert (
            summary_alarm_data[second_geography_code]["refresh_date"]
            == fake_expired_red_alert_for_second_geography.period_end
        )

    def test_for_alert_which_is_currently_live(self):
        """
        Given matching `CoreHeadline` records for given `geography_codes`
            which are all currently live
        When `build_summary_data_for_alerts()` is called
            from an instance of `WeatherHealthAlertsInterface`
        Then the correct data is returned for each alert

        Notes:
            We expect this to occur whenever alerts are live
            i.e. the `period_end` is greater than the current time

        """
        # Given
        topic_name = WeatherHealthAlertTopics.HEAT_ALERT.value
        metric_name = "heat-alert_headline_matrixNumber"
        first_geography_code = "E07000115"
        second_geography_code = "E07000120"

        two_weeks_from_now = timezone.now() + datetime.timedelta(days=14)
        one_week_ago = timezone.now() - datetime.timedelta(days=7)
        red_alert_metric_value = 16
        fake_expired_red_alert_for_first_geography: FakeCoreHeadline = (
            FakeCoreHeadlineFactory.build_record(
                topic_name=topic_name,
                metric_name=metric_name,
                metric_value=red_alert_metric_value,
                geography_code=first_geography_code,
                period_end=two_weeks_from_now,
                refresh_date=one_week_ago,
            )
        )

        amber_alert_metric_value = 14
        fake_expired_red_alert_for_second_geography: FakeCoreHeadline = (
            FakeCoreHeadlineFactory.build_record(
                topic_name=topic_name,
                metric_name=metric_name,
                metric_value=amber_alert_metric_value,
                geography_code=second_geography_code,
                period_end=two_weeks_from_now,
                refresh_date=one_week_ago,
            )
        )

        fake_core_headline_manager = FakeCoreHeadlineManager(
            headlines=[
                fake_expired_red_alert_for_first_geography,
                fake_expired_red_alert_for_second_geography,
            ]
        )
        weather_health_alerts_interface = WeatherHealthAlertsInterface(
            core_headline_manager=fake_core_headline_manager
        )

        # When
        detailed_alarm_data: WEATHER_HEALTH_ALERT_DETAILED_DATA = (
            weather_health_alerts_interface.build_summary_data_for_alerts(
                topic_name=topic_name,
                metric_name=metric_name,
                geography_codes=[first_geography_code, second_geography_code],
            )
        )

        # Then
        assert len(detailed_alarm_data) == 2

        assert (
            detailed_alarm_data[first_geography_code]["status"]
            == WeatherHealthAlertStatusColour.RED.value
        )
        assert (
            detailed_alarm_data[first_geography_code]["refresh_date"]
            == fake_expired_red_alert_for_first_geography.refresh_date
        )
        assert (
            detailed_alarm_data[second_geography_code]["status"]
            == WeatherHealthAlertStatusColour.AMBER.value
        )
        assert (
            detailed_alarm_data[second_geography_code]["refresh_date"]
            == fake_expired_red_alert_for_first_geography.refresh_date
        )
