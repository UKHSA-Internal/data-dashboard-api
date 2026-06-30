from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from common.auth.permissions import WILDCARD_ID_VALUE
from tests.factories.metrics.metric import MetricFactory
from tests.factories.metrics.sub_theme import SubThemeFactory
from tests.factories.metrics.topic import TopicFactory


class TestSubThemeByThemeView:
    @property
    def path(self) -> str:
        return "/api/data-hierarchy/subthemes"

    @pytest.mark.django_db
    def test_get_sub_themes_by_theme_id_should_return_tuple_of_id_and_name(self):

        client = APIClient()

        # create subthemes
        respiratorySubTheme = SubThemeFactory.create_with_theme(
            name="respiratory", theme="infectious_disease"
        )
        childhoodVaccinesSubtheme = SubThemeFactory.create_with_theme(
            name="immunisation", theme="childhood-vaccines"
        )

        # Retrieve the subthemes
        themeId = 1
        path = f"{self.path}/{themeId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == str(respiratorySubTheme.id)
        assert result["choices"][0][1] == respiratorySubTheme.name

    @pytest.mark.django_db
    def test_get_sub_themes_by_theme_id_should_return_wildcard(self):

        client = APIClient()

        # create subthemes
        respiratorySubtheme = SubThemeFactory.create_with_theme(
            name="respiratory", theme="infectious_disease"
        )
        childhoodVaccinesSubtheme = SubThemeFactory.create_with_theme(
            name="immunisation", theme="childhood-vaccines"
        )

        # Retrieve the subthemes
        themeId = -1
        path = f"{self.path}/{themeId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == WILDCARD_ID_VALUE
        assert result["choices"][0][1] == "* (All sub-themes)"

    @pytest.mark.django_db
    def test_get_sub_themes_by_theme_id_should_return_an_error(self):

        client = APIClient()

        # create subthemes
        respiratorySubtheme = SubThemeFactory.create_with_theme(
            name="respiratory", theme="infectious_disease"
        )
        childhoodVaccinesSubtheme = SubThemeFactory.create_with_theme(
            name="immunisation", theme="childhood-vaccines"
        )

        # Retrieve the subthemes
        themeId = "string"
        path = f"{self.path}/{themeId}"
        response: Response = client.get(path=path)
        result = response.data

        assert response.status_code == HTTPStatus.BAD_REQUEST

        # data should contain error
        assert str(result["theme_id"][0]) == "theme_id must be a number or '-1'"


class TestTopicBySubThemeView:
    @property
    def path(self) -> str:
        return "/api/data-hierarchy/topics"

    @pytest.mark.django_db
    def test_get_topics_by_sub_theme_id_should_return_tuple_of_id_and_name(self):

        client = APIClient()

        # create subthemes
        covid19Topic = TopicFactory.create_with_sub_theme(
            name="COVID-19", sub_theme="respiratory"
        )

        # Retrieve the topics
        subThemeId = 1
        path = f"{self.path}/{subThemeId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == str(covid19Topic.id)
        assert result["choices"][0][1] == covid19Topic.name

    @pytest.mark.django_db
    def test_get_topics_by_sub_theme_id_should_return_wildcard(self):

        client = APIClient()

        covid19Topic = TopicFactory.create_with_sub_theme(
            name="COVID-19", sub_theme="respiratory"
        )

        # Retrieve the subthemes
        themeId = -1
        path = f"{self.path}/{themeId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == WILDCARD_ID_VALUE
        assert result["choices"][0][1] == "* (All topics)"

    @pytest.mark.django_db
    def test_get_topics_by_sub_theme_id_should_return_an_error(self):

        client = APIClient()

        # create subthemes
        covid19Topic = TopicFactory.create_with_sub_theme(
            name="COVID-19", sub_theme="respiratory"
        )

        # Retrieve the subthemes
        themeId = "string"
        path = f"{self.path}/{themeId}"
        response: Response = client.get(path=path)
        result = response.data

        assert response.status_code == HTTPStatus.BAD_REQUEST

        # data should contain error
        assert str(result["sub_theme_id"][0]) == "sub_theme_id must be a number or '-1'"


class TestMetricByTopicView:
    @property
    def path(self) -> str:
        return "/api/data-hierarchy/metrics"

    @pytest.mark.django_db
    def test_get_metric_by_topic_id_should_return_tuple_of_id_and_name(self):

        client = APIClient()

        # create subthemes
        covid19metric = MetricFactory.create_with_topic(
            name="COVID-19_cases_rateRollingMean", topic="COVID-19"
        )

        # Retrieve the topics
        topicId = 1
        path = f"{self.path}/{topicId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == str(covid19metric.id)
        assert result["choices"][0][1] == covid19metric.name

    @pytest.mark.django_db
    def test_get_metric_by_topic_id_should_return_wildcard(self):

        client = APIClient()

        covid19metric = MetricFactory.create_with_topic(
            name="COVID-19_cases_rateRollingMean", topic="COVID-19"
        )

        # Retrieve the subthemes
        topicId = -1
        path = f"{self.path}/{topicId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == WILDCARD_ID_VALUE
        assert result["choices"][0][1] == "* (All metrics)"

    @pytest.mark.django_db
    def test_get_metric_by_topic_id_should_return_an_error(self):

        client = APIClient()

        # create subthemes
        covid19metric = MetricFactory.create_with_topic(
            name="COVID-19_cases_rateRollingMean", topic="COVID-19"
        )

        # Retrieve the subthemes
        topicId = "string"
        path = f"{self.path}/{topicId}"
        response: Response = client.get(path=path)
        result = response.data

        assert response.status_code == HTTPStatus.BAD_REQUEST

        # data should contain error
        assert str(result["topic_id"][0]) == "topic_id must be a number or '-1'"
