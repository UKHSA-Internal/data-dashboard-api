from collections.abc import Iterator
from contextlib import ExitStack, nullcontext
from types import SimpleNamespace
from unittest import mock

import pytest
from django.core.management import CommandParser
from django.core.management.base import CommandError

from metrics.interfaces.management.commands.seed_random import SCALE_CONFIGS, Command

MODULE_PATH = "metrics.interfaces.management.commands.seed_random"
FULL_BATCH_DAYS = 5000
SMALL_GEO_COUNT = 3
LARGE_GEO_COUNT = 7


def _fake_metric_hierarchy() -> SimpleNamespace:
    theme = SimpleNamespace(name="Theme 1")
    sub_theme = SimpleNamespace(name="SubTheme 1", theme=theme)
    topic = SimpleNamespace(name="Topic 1", sub_theme=sub_theme)
    return SimpleNamespace(name="Metric 1", topic=topic)


def _fake_geography() -> SimpleNamespace:
    geography_type = SimpleNamespace(name="Nation")
    return SimpleNamespace(
        name="Area 1",
        geography_code="RND0001",
        geography_type=geography_type,
    )


class TestSeedRandomCommand:
    def test_add_arguments_parses_defaults(self):
        parser = CommandParser(prog="manage.py seed_random")

        Command().add_arguments(parser)
        options = parser.parse_args([])

        assert options.dataset == "both"
        assert options.scale == "small"
        assert options.seed is None
        assert options.truncate_first is False

    @mock.patch(f"{MODULE_PATH}.random.seed")
    @mock.patch(f"{MODULE_PATH}.call_command")
    @mock.patch.object(Command, "_seed_metrics_data")
    @mock.patch.object(Command, "_print_summary")
    @mock.patch(f"{MODULE_PATH}.time.perf_counter")
    def test_handle_metrics_dataset(
        self,
        spy_perf_counter: mock.MagicMock,
        spy_print_summary: mock.MagicMock,
        spy_seed_metrics_data: mock.MagicMock,
        spy_call_command: mock.MagicMock,
        spy_random_seed: mock.MagicMock,
    ):
        spy_perf_counter.side_effect = [10.0, 14.5]
        spy_seed_metrics_data.return_value = {
            "Theme": 3,
            "SubTheme": 6,
            "Topic": 12,
            "Metric": 10,
            "Geography": 5,
            "CoreTimeSeries": 1,
            "APITimeSeries": 1,
        }

        Command().handle(dataset="metrics", scale="small", truncate_first=True, seed=42)

        spy_random_seed.assert_called_once_with(42)
        spy_seed_metrics_data.assert_called_once_with(
            scale_config=SCALE_CONFIGS["small"],
            truncate_first=True,
            progress_callback=mock.ANY,
        )
        spy_call_command.assert_not_called()
        spy_print_summary.assert_called_once_with(
            dataset="metrics",
            scale="small",
            seed=42,
            counts=spy_seed_metrics_data.return_value,
            runtime_seconds=4.5,
        )

    @mock.patch(f"{MODULE_PATH}.random.seed")
    @mock.patch(f"{MODULE_PATH}.call_command")
    @mock.patch.object(Command, "_seed_metrics_data")
    @mock.patch.object(Command, "_print_summary")
    @mock.patch(f"{MODULE_PATH}.time.time")
    @mock.patch(f"{MODULE_PATH}.time.perf_counter")
    def test_handle_cms_dataset_uses_time_seed_and_builds_cms(
        self,
        spy_perf_counter: mock.MagicMock,
        spy_time: mock.MagicMock,
        spy_print_summary: mock.MagicMock,
        spy_seed_metrics_data: mock.MagicMock,
        spy_call_command: mock.MagicMock,
        spy_random_seed: mock.MagicMock,
    ):
        spy_perf_counter.side_effect = [20.0, 22.0]
        spy_time.return_value = 1234

        Command().handle(dataset="cms", scale="large", truncate_first=False, seed=None)

        spy_random_seed.assert_called_once_with(1234)
        spy_seed_metrics_data.assert_not_called()
        spy_call_command.assert_called_once_with("build_cms_site")
        spy_print_summary.assert_called_once_with(
            dataset="cms",
            scale="large",
            seed=1234,
            counts={
                "Theme": 0,
                "SubTheme": 0,
                "Topic": 0,
                "Metric": 0,
                "Geography": 0,
                "CoreTimeSeries": 0,
                "APITimeSeries": 0,
            },
            runtime_seconds=2.0,
        )

    @mock.patch.object(Command, "_truncate_metrics_data")
    @mock.patch.object(Command, "_seed_time_series_rows")
    @mock.patch.object(Command, "_build_geography_seed_values")
    @mock.patch.object(Command, "_build_theme_hierarchy_records")
    @mock.patch.object(Command, "_bulk_create")
    @mock.patch(f"{MODULE_PATH}.Geography")
    @mock.patch(f"{MODULE_PATH}.Metric")
    @mock.patch(f"{MODULE_PATH}.Topic")
    @mock.patch(f"{MODULE_PATH}.SubTheme")
    @mock.patch(f"{MODULE_PATH}.Theme")
    @mock.patch(f"{MODULE_PATH}.GeographyType")
    @mock.patch(f"{MODULE_PATH}.transaction.atomic")
    @mock.patch(f"{MODULE_PATH}.Stratum.objects.create")
    @mock.patch(f"{MODULE_PATH}.Age.objects.create")
    def test_seed_metrics_data_builds_expected_counts_and_calls(
        self,
        spy_age_create: mock.MagicMock,
        spy_stratum_create: mock.MagicMock,
        spy_atomic: mock.MagicMock,
        spy_geography_type: mock.MagicMock,
        spy_theme: mock.MagicMock,
        spy_sub_theme: mock.MagicMock,
        spy_topic: mock.MagicMock,
        spy_metric: mock.MagicMock,
        spy_geography: mock.MagicMock,
        spy_bulk_create: mock.MagicMock,
        spy_build_theme_hierarchy_records: mock.MagicMock,
        spy_build_geography_seed_values: mock.MagicMock,
        spy_seed_time_series_rows: mock.MagicMock,
        spy_truncate: mock.MagicMock,
    ):
        spy_progress_callback = mock.MagicMock()
        spy_atomic.return_value = nullcontext()
        spy_geography_type.side_effect = SimpleNamespace
        spy_theme.side_effect = SimpleNamespace
        spy_sub_theme.side_effect = SimpleNamespace
        spy_topic.side_effect = SimpleNamespace
        spy_metric.side_effect = SimpleNamespace
        spy_geography.side_effect = SimpleNamespace
        spy_stratum_create.return_value = SimpleNamespace(name="All")
        spy_age_create.return_value = SimpleNamespace(name="All ages")
        spy_seed_time_series_rows.return_value = (77, 88)
        spy_build_theme_hierarchy_records.return_value = (
            ["infectious_disease", "climate_and_environment"],
            [
                ("respiratory", "infectious_disease"),
                ("vectors", "climate_and_environment"),
            ],
            [
                ("COVID-19", "respiratory", "infectious_disease"),
                ("ticks", "vectors", "climate_and_environment"),
            ],
        )
        spy_build_geography_seed_values.return_value = [
            {
                "name": "England",
                "geography_code": "E92000001",
                "geography_type": "Nation",
            },
            {
                "name": "Area 2",
                "geography_code": "E09000002",
                "geography_type": "Lower Tier Local Authority",
            },
        ]

        themes = [
            SimpleNamespace(name="infectious_disease"),
            SimpleNamespace(name="climate_and_environment"),
        ]
        sub_themes = [
            SimpleNamespace(name="respiratory", theme=themes[0]),
            SimpleNamespace(name="vectors", theme=themes[1]),
        ]
        topics = [
            SimpleNamespace(
                name="COVID-19",
                sub_theme=sub_themes[0],
            ),
            SimpleNamespace(
                name="ticks",
                sub_theme=sub_themes[1],
            ),
        ]
        metrics = [
            SimpleNamespace(
                name=f"Metric {index + 1}", topic=topics[index % len(topics)]
            )
            for index in range(4)
        ]
        geography_types = [
            SimpleNamespace(name="Nation"),
            SimpleNamespace(name="Lower Tier Local Authority"),
        ]
        geographies = [
            SimpleNamespace(
                name="England",
                geography_code="E92000001",
                geography_type=geography_types[0],
            ),
            SimpleNamespace(
                name="Area 2",
                geography_code="E09000002",
                geography_type=geography_types[1],
            ),
        ]
        spy_bulk_create.side_effect = [
            themes,
            sub_themes,
            topics,
            metrics,
            geography_types,
            geographies,
        ]

        result = Command._seed_metrics_data(
            scale_config={"geographies": 2, "metrics": 4, "days": 9},
            truncate_first=True,
            progress_callback=spy_progress_callback,
        )

        assert result == {
            "Theme": 2,
            "SubTheme": 2,
            "Topic": 2,
            "Metric": 4,
            "Geography": 2,
            "CoreTimeSeries": 77,
            "APITimeSeries": 88,
        }
        spy_truncate.assert_called_once_with()
        spy_seed_time_series_rows.assert_called_once_with(
            metrics=metrics,
            geographies=geographies,
            stratum=spy_stratum_create.return_value,
            age=spy_age_create.return_value,
            days=9,
            progress_callback=spy_progress_callback,
        )
        spy_progress_callback.assert_any_call(
            "Preparing metric taxonomy and geography records..."
        )
        spy_progress_callback.assert_any_call("Generating Core/API time series rows...")

    def test_truncate_metrics_data_deletes_from_all_models(self):
        model_names = [
            "APITimeSeries",
            "CoreTimeSeries",
            "Metric",
            "Topic",
            "SubTheme",
            "Theme",
            "Geography",
            "GeographyType",
            "Age",
            "Stratum",
        ]

        managers: dict[str, mock.MagicMock] = {}
        with ExitStack() as stack:
            for model_name in model_names:
                manager = mock.MagicMock()
                managers[model_name] = manager
                stack.enter_context(
                    mock.patch(f"{MODULE_PATH}.{model_name}.objects", manager)
                )

            Command._truncate_metrics_data()

        for model_name in model_names:
            managers[model_name].all.assert_called_once_with()
            managers[model_name].all.return_value.delete.assert_called_once_with()

    @mock.patch(f"{MODULE_PATH}.APITimeSeries")
    @mock.patch(f"{MODULE_PATH}.CoreTimeSeries")
    def test_seed_time_series_rows_flushes_remainder(
        self,
        spy_core_time_series: mock.MagicMock,
        spy_api_time_series: mock.MagicMock,
    ):
        spy_core_time_series.side_effect = lambda **kwargs: kwargs
        spy_api_time_series.side_effect = lambda **kwargs: kwargs
        spy_progress_callback = mock.MagicMock()

        core_count, api_count = Command._seed_time_series_rows(
            metrics=[_fake_metric_hierarchy()],
            geographies=[_fake_geography()],
            stratum=SimpleNamespace(name="All"),
            age=SimpleNamespace(name="All ages"),
            days=1,
            progress_callback=spy_progress_callback,
        )

        assert core_count == 1
        assert api_count == 1
        spy_core_time_series.objects.bulk_create.assert_called_once()
        spy_api_time_series.objects.bulk_create.assert_called_once()
        progress_messages = [
            call.args[0] for call in spy_progress_callback.call_args_list
        ]
        assert any(
            message.startswith("Processed 1/1 metrics") for message in progress_messages
        )
        assert any(message.startswith("Inserted ") for message in progress_messages)

    @mock.patch(f"{MODULE_PATH}.APITimeSeries")
    @mock.patch(f"{MODULE_PATH}.CoreTimeSeries")
    def test_seed_time_series_rows_flushes_at_batch_size(
        self,
        spy_core_time_series: mock.MagicMock,
        spy_api_time_series: mock.MagicMock,
    ):
        spy_core_time_series.side_effect = lambda **kwargs: kwargs
        spy_api_time_series.side_effect = lambda **kwargs: kwargs

        core_count, api_count = Command._seed_time_series_rows(
            metrics=[_fake_metric_hierarchy()],
            geographies=[_fake_geography()],
            stratum=SimpleNamespace(name="All"),
            age=SimpleNamespace(name="All ages"),
            days=FULL_BATCH_DAYS,
        )

        assert core_count == FULL_BATCH_DAYS
        assert api_count == FULL_BATCH_DAYS
        spy_core_time_series.objects.bulk_create.assert_called_once()
        spy_api_time_series.objects.bulk_create.assert_called_once()

    def test_bulk_create_materialises_iterable_and_delegates(self):
        class FakeModel:
            objects = mock.MagicMock()

        def records_generator() -> Iterator[int]:
            yield 1
            yield 2

        FakeModel.objects.bulk_create.return_value = ["created-records"]

        result = Command._bulk_create(FakeModel, records_generator())

        assert result == ["created-records"]
        FakeModel.objects.bulk_create.assert_called_once_with([1, 2])

    def test_print_summary_writes_expected_output(self):
        command = Command()
        command.stdout = mock.MagicMock()

        command._print_summary(
            dataset="both",
            scale="small",
            seed=123,
            counts={
                "Theme": 3,
                "SubTheme": 6,
                "Topic": 12,
                "Metric": 10,
                "Geography": 5,
                "CoreTimeSeries": 1500,
                "APITimeSeries": 1500,
            },
            runtime_seconds=3.456,
        )

        expected_lines = [
            "",
            "Seed random summary:",
            "  dataset: both",
            "  scale: small",
            "  seed used: 123",
            "  Theme: 3",
            "  SubTheme: 6",
            "  Topic: 12",
            "  Metric: 10",
            "  Geography: 5",
            "  CoreTimeSeries: 1500",
            "  APITimeSeries: 1500",
            "  runtime seconds: 3.46",
        ]
        actual_lines = [call.args[0] for call in command.stdout.write.call_args_list]

        assert actual_lines == expected_lines


def test_add_arguments_rejects_invalid_dataset_value():
    parser = CommandParser(prog="manage.py seed_random")
    Command().add_arguments(parser)

    with pytest.raises(CommandError):
        parser.parse_args(["--dataset", "invalid"])


def test_build_theme_hierarchy_records_contains_expected_real_values():
    theme_names, sub_theme_rows, topic_rows = Command._build_theme_hierarchy_records()

    assert "infectious_disease" in theme_names
    assert any(sub_theme == "respiratory" for sub_theme, _ in sub_theme_rows)
    assert any(
        topic == "COVID-19" and sub_theme == "respiratory"
        for topic, sub_theme, _ in topic_rows
    )


def test_build_theme_hierarchy_records_skips_unmatched_topic_group():
    fake_topic_group = mock.Mock()
    fake_topic_group.name = "DOES_NOT_MATCH_CHILD_THEME"
    fake_topic_group.return_list.return_value = ["dummy-topic"]

    with mock.patch(f"{MODULE_PATH}.validation_enums.Topic", [fake_topic_group]):
        _, _, topic_rows = Command._build_theme_hierarchy_records()

    assert topic_rows == []


def test_build_geography_seed_values_returns_required_count():
    small_geographies = Command._build_geography_seed_values(count=SMALL_GEO_COUNT)
    larger_geographies = Command._build_geography_seed_values(count=LARGE_GEO_COUNT)

    assert len(small_geographies) == SMALL_GEO_COUNT
    assert len(larger_geographies) == LARGE_GEO_COUNT
    assert small_geographies[0]["name"] == "United Kingdom"
    assert larger_geographies[-1]["geography_type"] in {
        "Nation",
        "Lower Tier Local Authority",
    }


def test_format_enum_name_replaces_underscores_and_title_cases():
    assert Command._format_enum_name("LOWER_TIER_LOCAL_AUTHORITY") == (
        "Lower Tier Local Authority"
    )
