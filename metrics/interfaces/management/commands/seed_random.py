import random
import time
from collections.abc import Callable, Iterable
from datetime import date, timedelta
from decimal import Decimal
from operator import itemgetter
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
from validation import enums as validation_enums
from validation.geography_code import (
    NATION_GEOGRAPHY_CODES,
    UNITED_KINGDOM_GEOGRAPHY_CODE,
)

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
            help="Which dataset to seed: CMS, metrics, or both.",
        )
        parser.add_argument(
            "--scale",
            choices=["small", "medium", "large"],
            default="small",
            help="Size of the random metrics dataset to generate.",
        )
        parser.add_argument(
            "--seed",
            type=int,
            required=False,
            default=None,
            help="Optional random seed for reproducible metric values.",
        )
        parser.add_argument(
            "--truncate-first",
            action="store_true",
            default=False,
            help="Clear existing metrics tables before seeding to avoid duplicates.",
        )

    def handle(self, *args, **options) -> None:
        started_at = time.perf_counter()
        dataset: str = options["dataset"]
        scale: str = options["scale"]
        truncate_first: bool = options["truncate_first"]

        selected_seed = (
            options["seed"] if options["seed"] is not None else int(time.time())
        )
        random.seed(selected_seed)  # nosec B311
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
            self.stderr.write("Seeding metrics dataset...")
            counts = self._seed_metrics_data(
                scale_config=scale_config,
                truncate_first=truncate_first,
                progress_callback=self.stderr.write,
            )
            self.stderr.write("Metrics dataset seeding complete.")

        if should_seed_cms:
            self.stderr.write("Building CMS site data...")
            call_command("build_cms_site")
            self.stderr.write("CMS site build complete.")

        runtime_seconds = time.perf_counter() - started_at
        self._print_summary(
            dataset=dataset,
            scale=scale,
            seed=selected_seed,
            counts=counts,
            runtime_seconds=runtime_seconds,
        )

    @classmethod
    def _seed_metrics_data(
        cls,
        *,
        scale_config: dict[str, int],
        truncate_first: bool,
        progress_callback: Callable[[str], None] | None = None,
    ) -> dict[str, int]:  # noqa: PLR0914
        """Seed supporting metric models and time series rows for the selected scale."""
        if progress_callback is not None:
            progress_callback("Preparing metric taxonomy and geography records...")

        with transaction.atomic():
            if truncate_first:
                cls._truncate_metrics_data()

            (
                theme_names,
                sub_theme_rows,
                topic_rows,
            ) = cls._build_theme_hierarchy_records()
            themes = cls._bulk_create(
                Theme,
                [Theme(name=name) for name in theme_names],
            )
            themes_by_name = {theme.name: theme for theme in themes}

            sub_themes = cls._bulk_create(
                SubTheme,
                [
                    SubTheme(name=name, theme=themes_by_name[theme_name])
                    for name, theme_name in sub_theme_rows
                ],
            )
            sub_themes_by_key = {
                (sub_theme.name, sub_theme.theme.name): sub_theme
                for sub_theme in sub_themes
            }

            topics = cls._bulk_create(
                Topic,
                [
                    Topic(
                        name=topic_name,
                        sub_theme=sub_themes_by_key[(sub_theme_name, theme_name)],
                    )
                    for topic_name, sub_theme_name, theme_name in topic_rows
                ],
            )

            metrics = cls._bulk_create(
                Metric,
                [
                    Metric(
                        name=f"Random Metric {index + 1}",
                        topic=topics[index % len(topics)],
                    )
                    for index in range(scale_config["metrics"])
                ],
            )

            geography_seed_values = cls._build_geography_seed_values(
                count=scale_config["geographies"]
            )
            geography_type_names = {
                record["geography_type"] for record in geography_seed_values
            }
            geography_types = cls._bulk_create(
                GeographyType,
                [GeographyType(name=name) for name in sorted(geography_type_names)],
            )
            geography_types_by_name = {
                geography_type.name: geography_type
                for geography_type in geography_types
            }

            geographies = cls._bulk_create(
                Geography,
                [
                    Geography(
                        name=record["name"],
                        geography_code=record["geography_code"],
                        geography_type=geography_types_by_name[
                            record["geography_type"]
                        ],
                    )
                    for record in geography_seed_values
                ],
            )

            stratum = Stratum.objects.create(name="All")
            age = Age.objects.create(name="All ages")

            if progress_callback is not None:
                progress_callback("Generating Core/API time series rows...")
            core_count, api_count = cls._seed_time_series_rows(
                metrics=metrics,
                geographies=geographies,
                stratum=stratum,
                age=age,
                days=scale_config["days"],
                progress_callback=progress_callback,
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
        """Delete all seeded metrics-related rows in dependency-safe order."""
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
        progress_callback: Callable[[str], None] | None = None,
    ) -> tuple[int, int]:  # noqa: PLR0914
        frequency = TimePeriod.Weekly.value
        today = date.today()
        start_date = today - timedelta(days=days - 1)
        batch_size = 5000
        core_rows: list[CoreTimeSeries] = []
        api_rows: list[APITimeSeries] = []
        core_count = 0
        api_count = 0
        total_metrics = len(metrics)
        total_row_count = total_metrics * len(geographies) * days
        log_interval = max(1, total_metrics // 10) if total_metrics else 1

        for metric_index, metric in enumerate(metrics, start=1):
            topic = metric.topic
            sub_theme = topic.sub_theme
            theme = sub_theme.theme

            for geography in geographies:
                for day_offset in range(days):
                    current_date = start_date + timedelta(days=day_offset)
                    base_value = random.uniform(5.0, 250.0)  # noqa: S311  # nosec B311
                    metric_value = round(
                        base_value
                        + random.uniform(-10.0, 10.0),  # noqa: S311  # nosec B311
                        2,
                    )
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
                        CoreTimeSeries.objects.bulk_create(
                            core_rows, batch_size=batch_size
                        )
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
                        APITimeSeries.objects.bulk_create(
                            api_rows, batch_size=batch_size
                        )
                        api_count += len(api_rows)
                        api_rows = []

            if (
                progress_callback is not None
                and (
                    metric_index == total_metrics
                    or metric_index % log_interval == 0
                )
            ):
                processed_row_count = metric_index * len(geographies) * days
                progress_callback(
                    f"Processed {metric_index}/{total_metrics} metrics "
                    f"({processed_row_count:,}/{total_row_count:,} row groups)."
                )

        if core_rows:
            CoreTimeSeries.objects.bulk_create(core_rows, batch_size=batch_size)
            core_count += len(core_rows)

        if api_rows:
            APITimeSeries.objects.bulk_create(api_rows, batch_size=batch_size)
            api_count += len(api_rows)

        if progress_callback is not None:
            progress_callback(
                "Inserted "
                f"{core_count:,} CoreTimeSeries rows and "
                f"{api_count:,} APITimeSeries rows."
            )

        return core_count, api_count

    @staticmethod
    def _bulk_create(model, records: Iterable):
        """Materialise and bulk insert a sequence of model instances."""
        return model.objects.bulk_create(list(records))

    @classmethod
    def _build_theme_hierarchy_records(
        cls,
    ) -> tuple[list[str], list[tuple[str, str]], list[tuple[str, str, str]]]:
        child_to_parent: dict[str, str] = {}
        normalised_to_child: dict[str, str] = {}
        parent_by_name = validation_enums.ParentTheme.__members__

        for child_theme_group in validation_enums.ChildTheme:
            resolved_parent = (
                parent_by_name[child_theme_group.name].value
                if child_theme_group.name in parent_by_name
                else validation_enums.ParentTheme.INFECTIOUS_DISEASE.value
            )
            for sub_theme_name in child_theme_group.return_list():
                child_to_parent[sub_theme_name] = resolved_parent
                normalised_to_child[cls._normalise_key(sub_theme_name)] = (
                    sub_theme_name
                )

        topic_rows: list[tuple[str, str, str]] = []
        sub_theme_pairs: set[tuple[str, str]] = set()
        for topic_group in validation_enums.Topic:
            normalised_topic_group = cls._normalise_key(topic_group.name)
            sub_theme_name = normalised_to_child.get(normalised_topic_group)
            if sub_theme_name is None:
                continue

            parent_theme_name = child_to_parent[sub_theme_name]
            sub_theme_pairs.add((sub_theme_name, parent_theme_name))
            topic_rows.extend(
                (topic_value, sub_theme_name, parent_theme_name)
                for topic_value in topic_group.return_list()
            )

        theme_names = sorted({parent_name for _, parent_name in sub_theme_pairs})
        sub_theme_rows = sorted(
            sub_theme_pairs,
            key=itemgetter(1, 0),
        )
        return theme_names, sub_theme_rows, topic_rows

    @classmethod
    def _build_geography_seed_values(cls, *, count: int) -> list[dict[str, str]]:
        geographies: list[dict[str, str]] = [
            {
                "name": "United Kingdom",
                "geography_code": UNITED_KINGDOM_GEOGRAPHY_CODE,
                "geography_type": (
                    validation_enums.GeographyType.UNITED_KINGDOM.value
                ),
            }
        ]

        geographies.extend(
            {
                "name": name,
                "geography_code": code,
                "geography_type": validation_enums.GeographyType.NATION.value,
            }
            for name, code in NATION_GEOGRAPHY_CODES.items()
        )

        if len(geographies) >= count:
            return geographies[:count]

        extra_required = count - len(geographies)
        geographies.extend(
            {
                "name": cls._format_enum_name(ltla.name),
                "geography_code": ltla.value,
                "geography_type": (
                    validation_enums.GeographyType.LOWER_TIER_LOCAL_AUTHORITY.value
                ),
            }
            for ltla in list(validation_enums.LTLAs)[:extra_required]
        )
        return geographies[:count]

    @staticmethod
    def _normalise_key(value: str) -> str:
        return value.lower().replace("-", "_")

    @staticmethod
    def _format_enum_name(value: str) -> str:
        return value.replace("_", " ").title()

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
