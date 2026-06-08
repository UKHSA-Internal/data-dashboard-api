from contextlib import ExitStack
from unittest.mock import patch

import pytest

from common.auth.permissions import (
    check_chart_permissions,
    check_chart_permissions_by_name,
    check_page_permissions,
)


class TestCheckPermissionsByName:
    THEME = "Infectious disease"
    SUB_THEME = "Respiratory"
    TOPIC = "COVID-19"
    METRIC = "COVID-19_metric"
    GEOGRAPHY_TYPE = "Nation"
    GEOGRAPHY = "England"

    THEME_ID = 1
    SUB_THEME_ID = 2
    TOPIC_ID = 3
    METRIC_ID = 4
    GEOGRAPHY_TYPE_ID = 5
    GEOGRAPHY_ID = 6

    def _permissions_by_id(self) -> dict:
        return {
            "theme": {"id": str(self.THEME_ID)},
            "sub_theme": {"id": str(self.SUB_THEME_ID)},
            "topic": {"id": str(self.TOPIC_ID)},
            "metric": {"id": str(self.METRIC_ID)},
            "geography_type": {"id": str(self.GEOGRAPHY_TYPE_ID)},
            "geography": {"id": str(self.GEOGRAPHY_ID)},
        }

    def _build_permission_sets(
        self, permission_rows: list[dict], has_global_access: bool = False
    ) -> dict:
        return {
            "permission_sets": permission_rows,
            "summary": {"has_global_access": has_global_access},
        }

    def _check_permissions_by_name(self, permission_sets: dict) -> bool:
        return check_chart_permissions_by_name(
            permission_sets=permission_sets,
            theme_name=self.THEME,
            sub_theme_name=self.SUB_THEME,
            topic_name=self.TOPIC,
            metric_name=self.METRIC,
            geography_type=self.GEOGRAPHY_TYPE,
            geography_name=self.GEOGRAPHY,
        )

    def _patch_lookups(
        self,
        topic_result=None,
        metric_result=None,
        geography_type_result=None,
        geography_result=None,
    ):
        """Return patches for all four DB manager methods."""

        topic_result = topic_result or (self.THEME_ID, self.SUB_THEME_ID, self.TOPIC_ID)
        metric_result = metric_result or self.METRIC_ID
        geography_type_result = geography_type_result or self.GEOGRAPHY_TYPE_ID
        geography_result = geography_result or self.GEOGRAPHY_ID

        stack = ExitStack()
        stack.enter_context(
            patch(
                "metrics.data.managers.core_models.topic.TopicQuerySet.get_id_by_name",
                return_value=topic_result,
            )
        )
        stack.enter_context(
            patch(
                "metrics.data.managers.core_models.metric.MetricQuerySet.get_id_by_name",
                return_value=metric_result,
            )
        )
        stack.enter_context(
            patch(
                "metrics.data.managers.core_models.geography_type.GeographyTypeQuerySet.get_id_by_name",
                return_value=geography_type_result,
            )
        )
        stack.enter_context(
            patch(
                "metrics.data.managers.core_models.geography.GeographyQuerySet.get_id_by_name",
                return_value=geography_result,
            )
        )

        return stack

    @pytest.mark.parametrize(
        "request_kwargs",
        [
            {
                "theme_name": "",
                "sub_theme_name": SUB_THEME,
                "topic_name": TOPIC,
                "metric_name": METRIC,
                "geography_type": GEOGRAPHY_TYPE,
                "geography_name": GEOGRAPHY,
            },
            {
                "theme_name": THEME,
                "sub_theme_name": "",
                "topic_name": TOPIC,
                "metric_name": METRIC,
                "geography_type": GEOGRAPHY_TYPE,
                "geography_name": GEOGRAPHY,
            },
            {
                "theme_name": THEME,
                "sub_theme_name": SUB_THEME,
                "topic_name": "",
                "metric_name": METRIC,
                "geography_type": GEOGRAPHY_TYPE,
                "geography_name": GEOGRAPHY,
            },
            {
                "theme_name": THEME,
                "sub_theme_name": SUB_THEME,
                "topic_name": TOPIC,
                "metric_name": "",
                "geography_type": GEOGRAPHY_TYPE,
                "geography_name": GEOGRAPHY,
            },
            {
                "theme_name": THEME,
                "sub_theme_name": SUB_THEME,
                "topic_name": TOPIC,
                "metric_name": METRIC,
                "geography_type": "",
                "geography_name": GEOGRAPHY,
            },
            {
                "theme_name": THEME,
                "sub_theme_name": SUB_THEME,
                "topic_name": TOPIC,
                "metric_name": METRIC,
                "geography_type": GEOGRAPHY_TYPE,
                "geography_name": "",
            },
        ],
    )
    def test_returns_false_for_empty_required_name_fields_without_mocks(
        self, request_kwargs
    ):
        assert not check_chart_permissions_by_name(
            permission_sets=self._build_permission_sets([self._permissions_by_id()]),
            **request_kwargs,
        )

    def test_returns_false_when_topic_lookup_fails(self):
        with (
            patch(
                "metrics.data.managers.core_models.topic.TopicQuerySet.get_id_by_name",
                return_value=(None, None, None),
            ),
            patch(
                "metrics.data.managers.core_models.metric.MetricQuerySet.get_id_by_name",
                return_value=self.METRIC_ID,
            ),
            patch(
                "metrics.data.managers.core_models.geography_type.GeographyTypeQuerySet.get_id_by_name",
                return_value=self.GEOGRAPHY_TYPE_ID,
            ),
            patch(
                "metrics.data.managers.core_models.geography.GeographyQuerySet.get_id_by_name",
                return_value=self.GEOGRAPHY_ID,
            ),
        ):
            assert not self._check_permissions_by_name(
                self._build_permission_sets([self._permissions_by_id()])
            )

    def test_returns_false_when_metric_lookup_fails(self):
        with (
            patch(
                "metrics.data.managers.core_models.topic.TopicQuerySet.get_id_by_name",
                return_value=(self.THEME_ID, self.SUB_THEME_ID, self.TOPIC_ID),
            ),
            patch(
                "metrics.data.managers.core_models.metric.MetricQuerySet.get_id_by_name",
                return_value=None,
            ),
            patch(
                "metrics.data.managers.core_models.geography_type.GeographyTypeQuerySet.get_id_by_name",
                return_value=self.GEOGRAPHY_TYPE_ID,
            ),
            patch(
                "metrics.data.managers.core_models.geography.GeographyQuerySet.get_id_by_name",
                return_value=self.GEOGRAPHY_ID,
            ),
        ):
            assert not self._check_permissions_by_name(
                self._build_permission_sets([self._permissions_by_id()])
            )

    def test_returns_false_when_geography_type_lookup_fails(self):
        with (
            patch(
                "metrics.data.managers.core_models.topic.TopicQuerySet.get_id_by_name",
                return_value=(self.THEME_ID, self.SUB_THEME_ID, self.TOPIC_ID),
            ),
            patch(
                "metrics.data.managers.core_models.metric.MetricQuerySet.get_id_by_name",
                return_value=self.METRIC_ID,
            ),
            patch(
                "metrics.data.managers.core_models.geography_type.GeographyTypeQuerySet.get_id_by_name",
                return_value=None,
            ),
            patch(
                "metrics.data.managers.core_models.geography.GeographyQuerySet.get_id_by_name",
                return_value=self.GEOGRAPHY_ID,
            ),
        ):
            assert not self._check_permissions_by_name(
                self._build_permission_sets([self._permissions_by_id()])
            )

    def test_returns_false_when_geography_lookup_fails(self):
        with (
            patch(
                "metrics.data.managers.core_models.topic.TopicQuerySet.get_id_by_name",
                return_value=(self.THEME_ID, self.SUB_THEME_ID, self.TOPIC_ID),
            ),
            patch(
                "metrics.data.managers.core_models.metric.MetricQuerySet.get_id_by_name",
                return_value=self.METRIC_ID,
            ),
            patch(
                "metrics.data.managers.core_models.geography_type.GeographyTypeQuerySet.get_id_by_name",
                return_value=self.GEOGRAPHY_TYPE_ID,
            ),
            patch(
                "metrics.data.managers.core_models.geography.GeographyQuerySet.get_id_by_name",
                return_value=None,
            ),
        ):
            assert not self._check_permissions_by_name(
                self._build_permission_sets([self._permissions_by_id()])
            )

    def test_returns_true_when_global_access_is_true(self):
        with self._patch_lookups():
            assert self._check_permissions_by_name(
                self._build_permission_sets([], has_global_access=True)
            )

    @pytest.mark.parametrize(
        "permission_sets",
        [
            pytest.param(
                None,
                id="test_none_permission_sets_denies_access",
            ),
        ],
    )
    def test_returns_false_when_permission_sets_is_not_a_dict(self, permission_sets):
        assert not check_chart_permissions_by_name(
            permission_sets=permission_sets,
            theme_name=self.THEME,
            sub_theme_name=self.SUB_THEME,
            topic_name=self.TOPIC,
            metric_name=self.METRIC,
            geography_type=self.GEOGRAPHY_TYPE,
            geography_name=self.GEOGRAPHY,
        )

    def test_returns_false_when_permission_sets_key_is_not_a_list(self):
        assert not check_chart_permissions_by_name(
            permission_sets={"permission_sets": "not_a_list", "summary": {}},
            theme_name=self.THEME,
            sub_theme_name=self.SUB_THEME,
            topic_name=self.TOPIC,
            metric_name=self.METRIC,
            geography_type=self.GEOGRAPHY_TYPE,
            geography_name=self.GEOGRAPHY,
        )

    def test_returns_false_when_summary_is_not_a_dict(self):
        assert not check_chart_permissions_by_name(
            permission_sets={"permission_sets": [], "summary": "not_a_dict"},
            theme_name=self.THEME,
            sub_theme_name=self.SUB_THEME,
            topic_name=self.TOPIC,
            metric_name=self.METRIC,
            geography_type=self.GEOGRAPHY_TYPE,
            geography_name=self.GEOGRAPHY,
        )

    def test_returns_false_when_has_global_access_is_not_a_bool(self):
        assert not check_chart_permissions_by_name(
            permission_sets={
                "permission_sets": [],
                "summary": {"has_global_access": "yes"},
            },
            theme_name=self.THEME,
            sub_theme_name=self.SUB_THEME,
            topic_name=self.TOPIC,
            metric_name=self.METRIC,
            geography_type=self.GEOGRAPHY_TYPE,
            geography_name=self.GEOGRAPHY,
        )

    def test_returns_true_when_lookups_succeed_and_permission_matches(self):
        permission_sets = self._build_permission_sets([self._permissions_by_id()])
        with self._patch_lookups():
            assert self._check_permissions_by_name(permission_sets)


class TestCheckPermissions:
    @pytest.mark.parametrize(
        (
            "permission_sets, theme_id, sub_theme_id, topic_id, "
            "metric_id, geography_type, geography_id"
        ),
        [
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_all_6_permission_resources_matching_grants_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "-1"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "-1"},
                        "geography": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_theme_wildcard_with_wildcards_following_grants_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "-1"},
                        "geography": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_sub_theme_wildcard_with_wildcards_following_grants_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "-1"},
                        "geography": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_topic_wildcard_with_wildcards_following_grants_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "-1"},
                        "geography": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_metric_wildcard_with_wildcards_following_grants_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "-1"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_theme_wildcard_with_geography_type_and_geography_match_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_sub_theme_wildcard_with_geography_type_and_geography_match_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_topic_wildcard_with_geography_type_and_geography_match_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_metric_wildcard_with_geography_type_and_geography_match_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "-1"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_first_4_matching_permissions_with_geography_type_wildcard_and_geography_match_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_first_4_matching_permissions_with_geography_type_match_and_geography_wildcard_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "-1"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "-1"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_first_4_permissions_wildcards_with_geography_type_wildcard_and_geography_match_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "-1"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_first_4_permissions_wildcards_with_geography_type_match_and_geography_wildcard_grants_access"
                ),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "5"},
                        "sub_theme": {"id": "-1"},
                        "topic": {"id": "-1"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "2"},
                        "geography": {"id": "-1"},
                    },
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    },
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=(
                    "test_matching_permission_row_grants_access_even_if_a_prior_row_does_not_match"
                ),
            ),
        ],
    )
    def test_check_chart_permissions_valid_access(
        self,
        permission_sets,
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type,
        geography_id,
    ):
        assert (
            check_chart_permissions(
                permission_sets=permission_sets,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
                metric_id=metric_id,
                geography_type=geography_type,
                geography_id=geography_id,
            )
            == True
        )

    @pytest.mark.parametrize(
        (
            "permission_sets, theme_id, sub_theme_id, topic_id, "
            "metric_id, geography_type, geography_id"
        ),
        [
            pytest.param(
                [
                    {
                        "theme": {"id": "99"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_theme_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "99"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_sub_theme_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "99"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_topic_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "99"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_metric_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "6"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_geography_type_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "99"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_geography_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "999",
                "60",
                id=("test_geography_type_match_with_geography_mismatch_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "-1"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "999"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_geography_type_mismatch_with_geography_match_denies_access"),
            ),
            pytest.param(
                [],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_permission_set_list_denies_access"),
            ),
        ],
    )
    def test_check_chart_permissions_invalid_access(
        self,
        permission_sets,
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type,
        geography_id,
    ):
        assert (
            check_chart_permissions(
                permission_sets=permission_sets,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
                metric_id=metric_id,
                geography_type=geography_type,
                geography_id=geography_id,
            )
            == False
        )

    @pytest.mark.parametrize(
        (
            "permission_sets, theme_id, sub_theme_id, topic_id, "
            "metric_id, geography_type, geography_id"
        ),
        [
            pytest.param(
                [{}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_permission_row_denies_access"),
            ),
            pytest.param(
                None,
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_non_list_permission_sets_denies_access"),
            ),
            pytest.param(
                [{"sub_theme": {"id": "-1"}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_missing_theme_denies_access"),
            ),
            pytest.param(
                [{"theme": {}, "sub_theme": {"id": "-1"}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_theme_id_in_chart_permissions_denies_access"),
            ),
            pytest.param(
                [{"theme": {"id": "10"}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_missing_sub_theme_denies_access"),
            ),
            pytest.param(
                [{"theme": {"id": "10"}, "sub_theme": {}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_sub_theme_denies_access"),
            ),
            pytest.param(
                [{"theme": {"id": "10"}, "sub_theme": {"id": "20"}}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_missing_topic_denies_access"),
            ),
            pytest.param(
                [{"theme": {"id": "10"}, "sub_theme": {"id": "20"}, "topic": {}}],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_topic_id_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_metric_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_missing_metric_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_missing_geography_type_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {},
                        "geography": {"id": "60"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_geography_type_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_missing_geography_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography": {"id": "50"},
                        "geography_type": {},
                    }
                ],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_empty_geography_denies_access"),
            ),
            pytest.param(
                [123],
                "10",
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_non_dict_item_in_permission_sets_list_denies_access"),
            ),
            pytest.param(
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                        "metric": {"id": "40"},
                        "geography_type": {"id": "50"},
                        "geography": {"id": "60"},
                    }
                ],
                None,
                "20",
                "30",
                "40",
                "50",
                "60",
                id=("test_none_theme_resource_id_denies_access"),
            ),
        ],
    )
    def test_check_chart_permissions_with_missing_values(
        self,
        permission_sets,
        theme_id,
        sub_theme_id,
        topic_id,
        metric_id,
        geography_type,
        geography_id,
    ):
        assert (
            check_chart_permissions(
                permission_sets=permission_sets,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
                metric_id=metric_id,
                geography_type=geography_type,
                geography_id=geography_id,
            )
            == False
        )


class TestCheckPagePermissions:
    @pytest.mark.parametrize(
        "user_permissions, theme_id, sub_theme_id, topic_id",
        [
            ([{"theme": {"id": "-1"}}], "10", "20", "30"),
            ([{"theme": {"id": "10"}, "sub_theme": {"id": "-1"}}], "10", "20", "30"),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            (
                [
                    {"theme": {"id": "5"}, "sub_theme": {"id": "-1"}},
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "30"},
                    },
                ],
                "10",
                "20",
                "30",
            ),
        ],
    )
    def test_check_page_permissions_valid_access(
        self, user_permissions, theme_id, sub_theme_id, topic_id
    ):
        """
        Given a permission set that does grant access to the provided ids
        When the `check_page_permissions` function is called
        Then the function returns true
        """
        assert (
            check_page_permissions(
                permission_sets=user_permissions,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
            )
            == True
        )

    @pytest.mark.parametrize(
        "user_permissions, theme_id, sub_theme_id, topic_id",
        [
            ([{"theme": {"id": "99"}, "sub_theme": {"id": "-1"}}], "10", "20", "30"),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "99"},
                        "topic": {"id": "-1"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            (
                [
                    {
                        "theme": {"id": "10"},
                        "sub_theme": {"id": "20"},
                        "topic": {"id": "99"},
                    }
                ],
                "10",
                "20",
                "30",
            ),
            ([], "10", "20", "30"),
        ],
    )
    def test_check_page_permissions_invalid_access(
        self, user_permissions, theme_id, sub_theme_id, topic_id
    ):
        """
        Given a permission set that does not grant access to the provided ids
        When the `check_page_permissions` function is called
        Then the function returns false
        """
        assert (
            check_page_permissions(
                permission_sets=user_permissions,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
            )
            == False
        )

    @pytest.mark.parametrize(
        "user_permissions, theme_id, sub_theme_id, topic_id",
        [
            ([{}], "10", "20", "30"),
            (None, "10", "20", "30"),
            ([{"sub_theme": {"id": "-1"}, "topic": {"id": "-1"}}], "10", "20", "30"),
            (
                [{"theme": {}, "sub_theme": {"id": "-1"}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
            ),
            ([{"theme": {"id": "10"}, "topic": {"id": "-1"}}], "10", "20", "30"),
            (
                [{"theme": {"id": "10"}, "sub_theme": {}, "topic": {"id": "-1"}}],
                "10",
                "20",
                "30",
            ),
            ([{"theme": {"id": "10"}, "sub_theme": {"id": "20"}}], "10", "20", "30"),
            (
                [{"theme": {"id": "10"}, "sub_theme": {"id": "20"}, "topic": {}}],
                "10",
                "20",
                "30",
            ),
        ],
    )
    def test_check_page_permissions_with_missing_values(
        self, user_permissions, theme_id, sub_theme_id, topic_id
    ):
        """
        Given a permission set that is missing values
        When the `check_page_permissions` function is called
        Then the function returns false
        """
        assert (
            check_page_permissions(
                permission_sets=user_permissions,
                theme_id=theme_id,
                sub_theme_id=sub_theme_id,
                topic_id=topic_id,
            )
            == False
        )
