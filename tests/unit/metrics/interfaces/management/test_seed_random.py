from collections.abc import Iterator
from contextlib import ExitStack, nullcontext
from types import SimpleNamespace
from typing import cast
from unittest import mock

import pytest
from django.core.management import CommandParser
from django.core.management.base import CommandError

from metrics.data.models.core_models.supporting import Age, Stratum
from metrics.interfaces.management.commands.seed_random import SCALE_CONFIGS, Command

MODULE_PATH = "metrics.interfaces.management.commands.seed_random"
FULL_BATCH_DAYS = 5000
SMALL_GEO_COUNT = 3
LARGE_GEO_COUNT = 7
EXPECTED_BULK_CREATE_CALLS = 2
EXPECTED_NEXT_METRIC_INDEX = 11
EXPECTED_TIME_SERIES_POINTS = 2
EXPECTED_METRIC_VALUE = 123.45


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


def _fake_stratum() -> Stratum:
    return cast(Stratum, SimpleNamespace(name="All"))


def _fake_age() -> Age:
    return cast(Age, SimpleNamespace(name="All ages"))


def _assert_progress_messages(progress_messages: list[str]) -> None:
    assert any(message.startswith("Processed 1/1 metrics") for message in progress_messages)
    assert any(message.startswith("Inserted ") for message in progress_messages)


class TestSeedRandomCommand:
    def test_add_arguments_parses_defaults(self):
        parser = CommandParser(prog="manage.py seed_random")

        Command().add_arguments(parser)
        options = parser.parse_args([])

        assert options.dataset == "both"
        assert options.scale == "small"
        assert options.seed is None
        assert options.truncate_first is False
        assert options.delivery == "db"
        assert options.non_public is False

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

        Command().handle(
            dataset="metrics",
            scale="small",
            truncate_first=True,
            seed=42,
            delivery="db",
            non_public=False,
        )

        spy_random_seed.assert_called_once_with(42)
        spy_seed_metrics_data.assert_called_once_with(
            scale_config=SCALE_CONFIGS["small"],
            truncate_first=True,
            is_public=True,
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

        Command().handle(
            dataset="cms",
            scale="large",
            truncate_first=False,
            seed=None,
            delivery="db",
            non_public=False,
        )

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

    @mock.patch(f"{MODULE_PATH}.random.seed")
    @mock.patch.object(Command, "_seed_metrics_data")
    @mock.patch.object(Command, "_seed_metrics_data_to_s3")
    @mock.patch.object(Command, "_print_summary")
    @mock.patch(f"{MODULE_PATH}.time.perf_counter")
    def test_handle_metrics_dataset_s3_delivery(
        self,
        spy_perf_counter: mock.MagicMock,
        spy_print_summary: mock.MagicMock,
        spy_seed_metrics_data_to_s3: mock.MagicMock,
        spy_seed_metrics_data: mock.MagicMock,
        spy_random_seed: mock.MagicMock,
    ):
        spy_perf_counter.side_effect = [11.0, 13.0]
        spy_seed_metrics_data_to_s3.return_value = {
            "Theme": 1,
            "SubTheme": 1,
            "Topic": 1,
            "Metric": 1,
            "Geography": 1,
            "CoreTimeSeries": 10,
            "APITimeSeries": 10,
        }

        Command().handle(
            dataset="metrics",
            scale="small",
            truncate_first=False,
            seed=99,
            delivery="s3",
            non_public=True,
        )

        spy_random_seed.assert_called_once_with(99)
        spy_seed_metrics_data.assert_not_called()
        spy_seed_metrics_data_to_s3.assert_called_once_with(
            scale_config=SCALE_CONFIGS["small"],
            is_public=False,
            progress_callback=mock.ANY,
        )
        spy_print_summary.assert_called_once_with(
            dataset="metrics",
            scale="small",
            seed=99,
            counts=spy_seed_metrics_data_to_s3.return_value,
            runtime_seconds=2.0,
        )

    @mock.patch.object(Command, "_truncate_metrics_data")
    @mock.patch.object(Command, "_seed_time_series_rows")
    @mock.patch.object(Command, "_seed_geographies")
    @mock.patch.object(Command, "_seed_theme_hierarchy")
    @mock.patch.object(Command, "_get_next_random_metric_index")
    @mock.patch.object(Command, "_bulk_create")
    @mock.patch(f"{MODULE_PATH}.Metric")
    @mock.patch(f"{MODULE_PATH}.transaction.atomic")
    @mock.patch(f"{MODULE_PATH}.Stratum.objects.get_or_create")
    @mock.patch(f"{MODULE_PATH}.Age.objects.get_or_create")
    def test_seed_metrics_data_builds_expected_counts_and_calls(
        self,
        spy_age_get_or_create: mock.MagicMock,
        spy_stratum_get_or_create: mock.MagicMock,
        spy_atomic: mock.MagicMock,
        spy_metric: mock.MagicMock,
        spy_bulk_create: mock.MagicMock,
        spy_get_next_random_metric_index: mock.MagicMock,
        spy_seed_theme_hierarchy: mock.MagicMock,
        spy_seed_geographies: mock.MagicMock,
        spy_seed_time_series_rows: mock.MagicMock,
        spy_truncate: mock.MagicMock,
    ):
        spy_progress_callback = mock.MagicMock()
        spy_atomic.return_value = nullcontext()
        spy_metric.side_effect = SimpleNamespace
        spy_get_next_random_metric_index.return_value = 1
        spy_stratum_get_or_create.return_value = (SimpleNamespace(name="All"), False)
        spy_age_get_or_create.return_value = (SimpleNamespace(name="All ages"), False)
        spy_seed_time_series_rows.return_value = (77, 88)

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
        metrics = [SimpleNamespace(name=f"Metric {index + 1}", topic=topics[index % len(topics)]) for index in range(4)]
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
        spy_seed_theme_hierarchy.return_value = (themes, sub_themes, topics)
        spy_seed_geographies.return_value = geographies
        spy_bulk_create.return_value = metrics

        result = Command._seed_metrics_data(
            scale_config={"geographies": 2, "metrics": 4, "days": 9},
            truncate_first=True,
            is_public=False,
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
            stratum=spy_stratum_get_or_create.return_value[0],
            age=spy_age_get_or_create.return_value[0],
            days=9,
            is_public=False,
            progress_callback=spy_progress_callback,
        )
        spy_progress_callback.assert_any_call("Preparing metric taxonomy and geography records...")
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
                stack.enter_context(mock.patch(f"{MODULE_PATH}.{model_name}.objects", manager))

            Command._truncate_metrics_data()

        for model_name in model_names:
            managers[model_name].all.assert_called_once_with()
            managers[model_name].all.return_value.delete.assert_called_once_with()

    @mock.patch(f"{MODULE_PATH}.APITimeSeries")
    @mock.patch(f"{MODULE_PATH}.CoreTimeSeries")
    @mock.patch(f"{MODULE_PATH}.random.choice")
    def test_seed_time_series_rows_flushes_remainder(
        self,
        spy_random_choice: mock.MagicMock,
        spy_core_time_series: mock.MagicMock,
        spy_api_time_series: mock.MagicMock,
    ):
        spy_random_choice.return_value = "f"
        spy_core_time_series.side_effect = lambda **kwargs: kwargs
        spy_api_time_series.side_effect = lambda **kwargs: kwargs
        spy_progress_callback = mock.MagicMock()

        core_count, api_count = Command._seed_time_series_rows(
            metrics=[_fake_metric_hierarchy()],
            geographies=[_fake_geography()],
            stratum=_fake_stratum(),
            age=_fake_age(),
            days=1,
            is_public=False,
            progress_callback=spy_progress_callback,
        )

        assert core_count == 1
        assert api_count == 1
        spy_core_time_series.objects.bulk_create.assert_called_once()
        spy_api_time_series.objects.bulk_create.assert_called_once()
        assert spy_core_time_series.call_args.kwargs["sex"] == "f"
        assert spy_api_time_series.call_args.kwargs["sex"] == "f"
        assert spy_core_time_series.call_args.kwargs["is_public"] is False
        assert spy_api_time_series.call_args.kwargs["is_public"] is False
        progress_messages = [call.args[0] for call in spy_progress_callback.call_args_list]
        _assert_progress_messages(progress_messages)

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
            stratum=_fake_stratum(),
            age=_fake_age(),
            days=FULL_BATCH_DAYS,
            is_public=True,
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
    assert any(topic == "COVID-19" and sub_theme == "respiratory" for topic, sub_theme, _ in topic_rows)


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
    assert Command._format_enum_name("LOWER_TIER_LOCAL_AUTHORITY") == ("Lower Tier Local Authority")


@mock.patch.object(Command, "_upsert_topics")
@mock.patch.object(Command, "_upsert_sub_themes")
@mock.patch.object(Command, "_upsert_themes")
@mock.patch.object(Command, "_build_theme_hierarchy_records")
def test_seed_theme_hierarchy_delegates_to_upsert_helpers(
    spy_build_theme_hierarchy_records: mock.MagicMock,
    spy_upsert_themes: mock.MagicMock,
    spy_upsert_sub_themes: mock.MagicMock,
    spy_upsert_topics: mock.MagicMock,
):
    theme_names = ["theme_1"]
    sub_theme_rows = [("sub_1", "theme_1")]
    topic_rows = [("topic_1", "sub_1", "theme_1")]
    themes = [SimpleNamespace(name="theme_1")]
    sub_themes = [SimpleNamespace(name="sub_1", theme=themes[0])]
    sub_theme_map = {("sub_1", "theme_1"): sub_themes[0]}
    topics = [SimpleNamespace(name="topic_1", sub_theme=sub_themes[0])]
    themes_by_name = {"theme_1": themes[0]}

    spy_build_theme_hierarchy_records.return_value = (
        theme_names,
        sub_theme_rows,
        topic_rows,
    )
    spy_upsert_themes.return_value = (themes, themes_by_name)
    spy_upsert_sub_themes.return_value = (sub_themes, sub_theme_map)
    spy_upsert_topics.return_value = topics

    result = Command._seed_theme_hierarchy()

    assert result == (themes, sub_themes, topics)
    spy_upsert_themes.assert_called_once_with(theme_names=theme_names)
    spy_upsert_sub_themes.assert_called_once_with(
        theme_names=theme_names,
        sub_theme_rows=sub_theme_rows,
        themes_by_name=themes_by_name,
    )
    spy_upsert_topics.assert_called_once_with(
        topic_rows=topic_rows,
        sub_themes_by_key=sub_theme_map,
    )


@mock.patch.object(Command, "_bulk_create")
@mock.patch(f"{MODULE_PATH}.Theme")
def test_upsert_themes_creates_missing_and_returns_requested_order(
    spy_theme: mock.MagicMock,
    spy_bulk_create: mock.MagicMock,
):
    existing_theme = SimpleNamespace(name="theme_1")
    created_theme = SimpleNamespace(name="theme_2")
    spy_theme.side_effect = SimpleNamespace
    spy_theme.objects.filter.side_effect = [[existing_theme], [created_theme]]

    themes, themes_by_name = Command._upsert_themes(theme_names=["theme_1", "theme_2"])

    assert [theme.name for theme in themes] == ["theme_1", "theme_2"]
    assert themes_by_name == {"theme_1": existing_theme, "theme_2": created_theme}
    spy_bulk_create.assert_called_once()


@mock.patch.object(Command, "_bulk_create")
@mock.patch(f"{MODULE_PATH}.SubTheme")
def test_upsert_sub_themes_creates_missing_and_returns_requested_order(
    spy_sub_theme: mock.MagicMock,
    spy_bulk_create: mock.MagicMock,
):
    theme_1 = SimpleNamespace(name="theme_1")
    theme_2 = SimpleNamespace(name="theme_2")
    existing_sub_theme = SimpleNamespace(name="sub_1", theme=theme_1)
    created_sub_theme = SimpleNamespace(name="sub_2", theme=theme_2)

    spy_sub_theme.side_effect = SimpleNamespace
    spy_sub_theme.objects.select_related.return_value.filter.side_effect = [
        [existing_sub_theme],
        [created_sub_theme],
    ]

    sub_themes, sub_theme_map = Command._upsert_sub_themes(
        theme_names=["theme_1", "theme_2"],
        sub_theme_rows=[("sub_1", "theme_1"), ("sub_2", "theme_2")],
        themes_by_name={"theme_1": theme_1, "theme_2": theme_2},
    )

    assert [(sub_theme.name, sub_theme.theme.name) for sub_theme in sub_themes] == [
        ("sub_1", "theme_1"),
        ("sub_2", "theme_2"),
    ]
    assert sub_theme_map == {
        ("sub_1", "theme_1"): existing_sub_theme,
        ("sub_2", "theme_2"): created_sub_theme,
    }
    spy_bulk_create.assert_called_once()


@mock.patch.object(Command, "_bulk_create")
@mock.patch(f"{MODULE_PATH}.Topic")
def test_upsert_topics_creates_missing_and_returns_requested_order(
    spy_topic: mock.MagicMock,
    spy_bulk_create: mock.MagicMock,
):
    sub_theme_1 = SimpleNamespace(id=1, name="sub_1")
    sub_theme_2 = SimpleNamespace(id=2, name="sub_2")
    existing_topic = SimpleNamespace(name="topic_1", sub_theme_id=1)
    created_topic = SimpleNamespace(name="topic_2", sub_theme_id=2)

    spy_topic.side_effect = lambda **kwargs: SimpleNamespace(
        name=kwargs["name"],
        sub_theme=kwargs["sub_theme"],
        sub_theme_id=kwargs["sub_theme"].id,
    )
    spy_topic.objects.filter.side_effect = [[existing_topic], [created_topic]]

    topics = Command._upsert_topics(
        topic_rows=[("topic_1", "sub_1", "theme_1"), ("topic_2", "sub_2", "theme_2")],
        sub_themes_by_key={
            ("sub_1", "theme_1"): sub_theme_1,
            ("sub_2", "theme_2"): sub_theme_2,
        },
    )

    assert [(topic.name, topic.sub_theme_id) for topic in topics] == [
        ("topic_1", 1),
        ("topic_2", 2),
    ]
    spy_bulk_create.assert_called_once()


@mock.patch.object(Command, "_build_geography_seed_values")
@mock.patch.object(Command, "_bulk_create")
@mock.patch(f"{MODULE_PATH}.Geography")
@mock.patch(f"{MODULE_PATH}.GeographyType")
def test_seed_geographies_creates_missing_types_and_geographies(
    spy_geography_type: mock.MagicMock,
    spy_geography: mock.MagicMock,
    spy_bulk_create: mock.MagicMock,
    spy_build_geography_seed_values: mock.MagicMock,
):
    nation_type = SimpleNamespace(name="Nation")
    ltla_type = SimpleNamespace(name="Lower Tier Local Authority")
    existing_geography = SimpleNamespace(
        name="England",
        geography_type=nation_type,
        geography_code="E92000001",
    )
    created_geography = SimpleNamespace(
        name="Area 2",
        geography_type=ltla_type,
        geography_code="E09000002",
    )
    spy_geography_type.side_effect = SimpleNamespace
    spy_geography.side_effect = SimpleNamespace
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
    spy_geography_type.objects.filter.side_effect = [[nation_type], [ltla_type]]
    spy_geography.objects.select_related.return_value.filter.side_effect = [
        [existing_geography],
        [created_geography],
    ]

    result = Command._seed_geographies(count=2)

    assert [(geography.name, geography.geography_type.name) for geography in result] == [
        ("England", "Nation"),
        ("Area 2", "Lower Tier Local Authority"),
    ]
    assert spy_bulk_create.call_count == EXPECTED_BULK_CREATE_CALLS


@mock.patch.object(Command, "_build_geography_seed_values")
@mock.patch.object(Command, "_bulk_create")
@mock.patch(f"{MODULE_PATH}.Geography")
@mock.patch(f"{MODULE_PATH}.GeographyType")
def test_seed_geographies_reuses_existing_without_creating(
    spy_geography_type: mock.MagicMock,
    spy_geography: mock.MagicMock,
    spy_bulk_create: mock.MagicMock,
    spy_build_geography_seed_values: mock.MagicMock,
):
    nation_type = SimpleNamespace(name="Nation")
    ltla_type = SimpleNamespace(name="Lower Tier Local Authority")
    england = SimpleNamespace(
        name="England",
        geography_type=nation_type,
        geography_code="E92000001",
    )
    area_2 = SimpleNamespace(
        name="Area 2",
        geography_type=ltla_type,
        geography_code="E09000002",
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
    spy_geography_type.objects.filter.return_value = [nation_type, ltla_type]
    spy_geography.objects.select_related.return_value.filter.return_value = [
        england,
        area_2,
    ]

    result = Command._seed_geographies(count=2)

    assert result == [england, area_2]
    spy_bulk_create.assert_not_called()


@mock.patch(f"{MODULE_PATH}.Metric.objects.filter")
def test_get_next_random_metric_index_ignores_non_matching_names(
    spy_metric_filter: mock.MagicMock,
):
    spy_metric_filter.return_value.values_list.return_value = [
        "Random Metric 2",
        "Random Metric x",
        "Some Other Metric",
        "Random Metric 10",
    ]

    result = Command._get_next_random_metric_index()

    assert result == EXPECTED_NEXT_METRIC_INDEX


@mock.patch(f"{MODULE_PATH}.Metric.objects.filter")
def test_get_next_random_metric_index_defaults_to_one_when_no_matches(
    spy_metric_filter: mock.MagicMock,
):
    spy_metric_filter.return_value.values_list.return_value = ["Some Other Metric"]

    result = Command._get_next_random_metric_index()

    assert result == 1


@mock.patch(f"{MODULE_PATH}.AWSClient")
@mock.patch.object(Command, "_build_s3_object_key")
@mock.patch.object(Command, "_build_geography_seed_values")
@mock.patch.object(Command, "_build_theme_hierarchy_records")
@mock.patch.object(Command, "_build_timeseries_ingestion_payloads")
def test_seed_metrics_data_to_s3_uploads_payloads_and_returns_counts(
    spy_build_payloads: mock.MagicMock,
    spy_build_theme_hierarchy_records: mock.MagicMock,
    spy_build_geography_seed_values: mock.MagicMock,
    spy_build_s3_object_key: mock.MagicMock,
    spy_aws_client: mock.MagicMock,
):
    spy_progress_callback = mock.MagicMock()
    payload = {
        "topic": "COVID-19",
        "metric": "COVID-19_cases_randomByDay_1",
        "geography_code": "E92000001",
        "age": "all",
        "sex": "all",
        "stratum": "default",
    }
    spy_build_payloads.return_value = [payload]
    spy_build_s3_object_key.return_value = "in/key.json"
    spy_build_theme_hierarchy_records.return_value = (
        [],
        [],
        [("COVID-19", "respiratory", "infectious_disease")],
    )
    spy_build_geography_seed_values.return_value = [
        {
            "name": "England",
            "geography_code": "E92000001",
            "geography_type": "Nation",
        }
    ]

    result = Command._seed_metrics_data_to_s3(
        scale_config={"geographies": 1, "metrics": 2, "days": 3},
        is_public=False,
        progress_callback=spy_progress_callback,
    )

    assert result == {
        "Theme": 1,
        "SubTheme": 1,
        "Topic": 1,
        "Metric": 2,
        "Geography": 1,
        "CoreTimeSeries": 6,
        "APITimeSeries": 6,
    }
    spy_aws_client.return_value.upload_json_to_inbound.assert_called_once_with(
        key="in/key.json",
        payload=payload,
    )
    spy_progress_callback.assert_any_call("Generating ingestion payloads for S3 upload...")
    spy_progress_callback.assert_any_call("Uploaded 1 files to ingest bucket in/.")


@mock.patch(f"{MODULE_PATH}.random.choice")
@mock.patch(f"{MODULE_PATH}.random.uniform")
@mock.patch.object(Command, "_build_geography_seed_values")
@mock.patch.object(Command, "_build_theme_hierarchy_records")
def test_build_timeseries_ingestion_payloads_builds_expected_shape(
    spy_build_theme_hierarchy_records: mock.MagicMock,
    spy_build_geography_seed_values: mock.MagicMock,
    spy_random_uniform: mock.MagicMock,
    spy_random_choice: mock.MagicMock,
):
    spy_build_theme_hierarchy_records.return_value = (
        [],
        [],
        [("COVID-19", "respiratory", "infectious_disease")],
    )
    spy_build_geography_seed_values.return_value = [
        {
            "name": "England",
            "geography_code": "E92000001",
            "geography_type": "Nation",
        }
    ]
    spy_random_uniform.return_value = EXPECTED_METRIC_VALUE
    spy_random_choice.return_value = "all"

    payloads = Command._build_timeseries_ingestion_payloads(
        scale_config={"geographies": 1, "metrics": 1, "days": 2},
        is_public=True,
    )

    assert len(payloads) == 1
    payload = payloads[0]
    assert payload["parent_theme"] == "infectious_disease"
    assert payload["child_theme"] == "respiratory"
    assert payload["topic"] == "COVID-19"
    assert payload["metric_group"] == "cases"
    assert payload["geography"] == "England"
    assert payload["geography_code"] == "E92000001"
    assert payload["age"] == "all"
    assert payload["sex"] == "all"
    assert payload["stratum"] == "default"
    assert len(payload["time_series"]) == EXPECTED_TIME_SERIES_POINTS
    assert payload["time_series"][0]["metric_value"] == EXPECTED_METRIC_VALUE
    assert payload["time_series"][0]["is_public"] is True


def test_build_s3_object_key_builds_expected_file_name():
    payload = {
        "topic": "COVID-19",
        "metric": "COVID-19_cases_randomByDay_1",
        "geography_code": "E92000001",
        "age": "all",
        "sex": "f",
        "stratum": "default",
    }

    result = Command._build_s3_object_key(payload=payload, payload_index=7)

    assert result == ("in/covid_19_cases_covid_19_cases_randombyday_1_E92000001_all_f_default_7.json")
