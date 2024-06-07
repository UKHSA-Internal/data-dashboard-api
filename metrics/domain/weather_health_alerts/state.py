from dataclasses import dataclass

from metrics.domain.weather_health_alerts.mapping import (
    WeatherHealthAlertsMetricMapping,
)


@dataclass
class WeatherHealthAlarmState:
    metric_value: int
    topic_name: str
    period_start: str | None
    period_end: str | None
    refresh_date: str | None

    @property
    def detailed_data(self) -> dict[str, str]:
        return {
            "status": self.get_associated_status(),
            "text": self.get_associated_text(),
            "period_start": self.period_start,
            "period_end": self.period_end,
            "refresh_date": self.refresh_date,
        }

    @property
    def summary_data(self) -> dict[str, str]:
        return {
            "status": self.get_associated_status(),
            "refresh_date": self.refresh_date,
        }

    def _build_mapping(self) -> WeatherHealthAlertsMetricMapping:
        return WeatherHealthAlertsMetricMapping(
            metric_value=self.metric_value,
            topic_name=self.topic_name,
        )

    def get_associated_status(self) -> str:
        mapping: WeatherHealthAlertsMetricMapping = self._build_mapping()
        return mapping.associated_status_colour

    def get_associated_text(self) -> str:
        mapping: WeatherHealthAlertsMetricMapping = self._build_mapping()
        return "".join(mapping.associated_text.split("\n"))
