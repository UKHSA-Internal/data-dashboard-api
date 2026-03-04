import random
import time
from collections.abc import Iterable
from datetime import date, timedelta
from decimal import Decimal
from typing import override

from django.core.management import CommandParser, call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from metrics.data.enums import TimePeriod
from metrics.data.models.api_models import APITimeSeries
from metrics.data.models.core_models.supporting import (
    Age,
    Geography,
    GeographyType,
    Metric,
    Stratum,
    SubTheme,
    Theme,
    Topic,
)
from metrics.data.models.core_models.timeseries import CoreTimeSeries

SCALE_CONFIGS = {
    "small": {"geographies": 5, "metrics": 10, "days": 30},
    "medium": {"geographies": 20, "metrics": 50, "days": 180},
    "large": {"geographies": 100, "metrics": 200, "days": 365},
}


class Command(BaseCommand):
    @override
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dataset",
            choices=["cms", "metrics", "both"],
            default="both",
        )
        parser.add_argument(
            "--scale",
            choices=["small", "medium", "large"],
            default="small",
        )
        parser.add_argument(
            "--seed",
            type=int,
            required=False,
            default=None,
        )
        parser.add_argument(
            "--truncate-first",
            action="store_true",
            default=False,
        )

    def handle(self, *args, **options) -> None:
        started_at = time.perf_counter()
        dataset: str = options["dataset"]
        scale: str = options["scale"]
        truncate_first: bool = options["truncate_first"]

        selected_seed = options["seed"] if options["seed"] is not None else int(time.time())
        random.seed(selected_seed)
        self.stdout.write(f"Seed used: {selected_seed}")

        should_seed_cms = dataset in {"cms", "both"}
        should_seed_metrics = dataset in {"metrics", "both"}

        counts: dict[str, int] = {
            "Theme": 0,
            "SubTheme": 0,
            "Topic": 0,
            "Metric": 0,
            "Geography": 0,
            "CoreTimeSeries": 0,
            "APITimeSeries": 0,
        }

        if should_seed_metrics:
            scale_config = SCALE_CONFIGS[scale]
            counts = self._seed_metrics_data(
                scale_config=scale_config,
                truncate_first=truncate_first,
            )

        if should_seed_cms:
            call_command("build_cms_site")

        runtime_seconds = time.perf_counter() - started_at
        self._print_summary(
            dataset=dataset,
            scale=scale,
            seed=selected_seed,
            counts=counts,
            runtime_seconds=runtime_seconds,
        )

    @classmethod
    def _seed_metrics_data(cls, *, scale_config: dict[str, int], truncate_first: bool) -> dict[str, int]:
        if truncate_first:
            cls._truncate_metrics_data()

        with transaction.atomic():
            themes = cls._bulk_create(
                Theme,
                [Theme(name=f"Theme {index + 1}") for index in range(3)],
            )

            sub_themes = cls._bulk_create(
                SubTheme,
                [
                    SubTheme(name=f"SubTheme {index + 1}", theme=themes[index % len(themes)])
                    for index in range(6)
                ],
            )

            topics = cls._bulk_create(
                Topic,
                [
                    Topic(name=f"Topic {index + 1}", sub_theme=sub_themes[index % len(sub_themes)])
                    for index in range(12)
                ],
            )

            metrics = cls._bulk_create(
                Metric,
                [
                    Metric(name=f"Random Metric {index + 1}", topic=topics[index % len(topics)])
                    for index in range(scale_config["metrics"])
                ],
            )

            geography_type = GeographyType.objects.create(name="Nation")

            geographies = cls._bulk_create(
                Geography,
                [
                    Geography(
                        name=f"Area {index + 1}",
                        geography_code=f"RND{index + 1:04d}",
                        geography_type=geography_type,
                    )
                    for index in range(scale_config["geographies"])
                ],
            )

            stratum = Stratum.objects.create(name="All")
            age = Age.objects.create(name="All ages")

            core_count, api_count = cls._seed_time_series_rows(
                metrics=metrics,
                geographies=geographies,
                stratum=stratum,
                age=age,
                days=scale_config["days"],
            )

        return {
            "Theme": len(themes),
            "SubTheme": len(sub_themes),
            "Topic": len(topics),
            "Metric": len(metrics),
            "Geography": len(geographies),
            "CoreTimeSeries": core_count,
            "APITimeSeries": api_count,
        }

    @classmethod
    def _truncate_metrics_data(cls) -> None:
        APITimeSeries.objects.all().delete()
        CoreTimeSeries.objects.all().delete()
        Metric.objects.all().delete()
        Topic.objects.all().delete()
        SubTheme.objects.all().delete()
        Theme.objects.all().delete()
        Geography.objects.all().delete()
        GeographyType.objects.all().delete()
        Age.objects.all().delete()
        Stratum.objects.all().delete()

    @classmethod
    def _seed_time_series_rows(
        cls,
        *,
        metrics: list[Metric],
        geographies: list[Geography],
        stratum: Stratum,
        age: Age,
        days: int,
    ) -> tuple[int, int]:
        frequency = TimePeriod.Weekly.value
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        batch_size = 5000
        core_rows: list[CoreTimeSeries] = []
        api_rows: list[APITimeSeries] = []
        core_count = 0
        api_count = 0

        for metric in metrics:
            topic = metric.topic
            sub_theme = topic.sub_theme
            theme = sub_theme.theme

            for geography in geographies:
                for day_offset in range(days):
                    current_date = start_date + timedelta(days=day_offset)
                    base_value = random.uniform(5.0, 250.0)  # noqa: S311
                    metric_value = round(base_value + random.uniform(-10.0, 10.0), 2)  # noqa: S311
                    epidemiological_week = current_date.isocalendar().week

                    core_rows.append(
                        CoreTimeSeries(
                            metric=metric,
                            metric_frequency=frequency,
                            geography=geography,
                            stratum=stratum,
                            age=age,
                            sex=None,
                            year=current_date.year,
                            month=current_date.month,
                            epiweek=epidemiological_week,
                            date=current_date,
                            metric_value=Decimal(str(metric_value)),
                            is_public=True,
                        )
                    )

                    if len(core_rows) >= batch_size:
                        CoreTimeSeries.objects.bulk_create(core_rows, batch_size=batch_size)
                        core_count += len(core_rows)
                        core_rows = []

                    api_rows.append(
                        APITimeSeries(
                            metric_frequency=frequency,
                            age=age.name,
                            month=current_date.month,
                            geography_code=geography.geography_code,
                            metric_group=None,
                            theme=theme.name,
                            sub_theme=sub_theme.name,
                            topic=topic.name,
                            geography_type=geography.geography_type.name,
                            geography=geography.name,
                            metric=metric.name,
                            stratum=stratum.name,
                            sex=None,
                            year=current_date.year,
                            epiweek=epidemiological_week,
                            date=current_date,
                            metric_value=float(metric_value),
                            is_public=True,
                        )
                    )

                    if len(api_rows) >= batch_size:
                        APITimeSeries.objects.bulk_create(api_rows, batch_size=batch_size)
                        api_count += len(api_rows)
                        api_rows = []

        if core_rows:
            CoreTimeSeries.objects.bulk_create(core_rows, batch_size=batch_size)
            core_count += len(core_rows)

        if api_rows:
            APITimeSeries.objects.bulk_create(api_rows, batch_size=batch_size)
            api_count += len(api_rows)

        return core_count, api_count

    @staticmethod
    def _bulk_create(model, records: Iterable):
        return model.objects.bulk_create(list(records))

    def _print_summary(
        self,
        *,
        dataset: str,
        scale: str,
        seed: int,
        counts: dict[str, int],
        runtime_seconds: float,
    ) -> None:
        self.stdout.write("")
        self.stdout.write("Seed random summary:")
        self.stdout.write(f"  dataset: {dataset}")
        self.stdout.write(f"  scale: {scale}")
        self.stdout.write(f"  seed used: {seed}")
        self.stdout.write(f"  Theme: {counts['Theme']}")
        self.stdout.write(f"  SubTheme: {counts['SubTheme']}")
        self.stdout.write(f"  Topic: {counts['Topic']}")
        self.stdout.write(f"  Metric: {counts['Metric']}")
        self.stdout.write(f"  Geography: {counts['Geography']}")
        self.stdout.write(f"  CoreTimeSeries: {counts['CoreTimeSeries']}")
        self.stdout.write(f"  APITimeSeries: {counts['APITimeSeries']}")
        self.stdout.write(f"  runtime seconds: {runtime_seconds:.2f}")
