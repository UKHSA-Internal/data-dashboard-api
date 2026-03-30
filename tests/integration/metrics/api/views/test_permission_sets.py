from http import HTTPStatus

import pytest
from rest_framework.response import Response
from rest_framework.test import APIClient

from auth_content.models.permission_sets import PermissionSet
from tests.factories.metrics.metric import MetricFactory
from tests.factories.metrics.permission_set import PermissionSetFactory
from tests.factories.metrics.sub_theme import SubThemeFactory
from tests.factories.metrics.topic import TopicFactory


class TestSubThemeByThemeView:
    @property
    def path(self) -> str:
        return "/api/permission-set/subthemes"

    @pytest.mark.django_db
    def test_get_sub_themes_by_theme_id_should_return_tuple_of_id_and_name(self):

        client = APIClient()

        # create subthemes
        respiratorySubTheme = SubThemeFactory.create_with_theme(
            name="respiratory", theme="infectious_disease"
        )
        childhoodVaccinesSubtheme = SubThemeFactory.create_with_theme(
            name="immunisation", theme="childhood_vaccines"
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
            name="immunisation", theme="childhood_vaccines"
        )

        # Retrieve the subthemes
        themeId = -1
        path = f"{self.path}/{themeId}"
        response: Response = client.get(path=path)
        result = response.data

        # Choices length should only contain wildcard option
        assert len(response.data["choices"]) == 1

        # Should return a wildcard choice
        assert result["choices"][0][0] == "-1"
        assert result["choices"][0][1] == "* (All sub-themes)"

    @pytest.mark.django_db
    def test_get_sub_themes_by_theme_id_should_return_an_error(self):

        client = APIClient()

        # create subthemes
        respiratorySubtheme = SubThemeFactory.create_with_theme(
            name="respiratory", theme="infectious_disease"
        )
        childhoodVaccinesSubtheme = SubThemeFactory.create_with_theme(
            name="immunisation", theme="childhood_vaccines"
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
        return "/api/permission-set/topics"

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
        assert result["choices"][0][0] == "-1"
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
        return "/api/permission-set/metrics"

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
        assert result["choices"][0][0] == "-1"
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

class TestPermissionSetChoicesView:
    @property
    def path(self) -> str:
        return "/api/permission-set/all"

    @pytest.mark.django_db
    def test_get_permission_set_choices_returns_expected_shape(self):
        """
        Should return: {"choices": [[id, name], ...]}
        """

        # Given
        ps1 = PermissionSet.objects.create(
            theme="theme1", sub_theme="subtheme1", topic="topic1", metric="metric1", geography_type="g", geography="gg"
        )
        ps2 = PermissionSet.objects.create(
            theme="theme2", sub_theme="subtheme2", topic="topic2", metric="metric2", geography_type="g", geography="gg"
        )

        client = APIClient()

        # When
        response: Response = client.get(self.path)
        
        # Then
        assert response.status_code == HTTPStatus.OK
        assert "choices" in response.data
        assert response.data["choices"] == [
            [str(ps1.id), ps1.name],
            [str(ps2.id), ps2.name],
        ]
    
    @pytest.mark.django_db
    def test_empty_permission_sets_returns_empty_list(self):
        """
        When the DB has no permission sets, return: {"choices": []}
        """
        client = APIClient()

        response = client.get(self.path)

        assert response.status_code == HTTPStatus.OK
        assert response.data == {"choices": []}
        
    @pytest.mark.django_db
    def test_results_are_sorted_by_name(self):
        """
        Should respect .order_by("name") in the view.
        """
        ps1 = PermissionSet.objects.create(
            theme="themeb1", sub_theme="subthemeb1", topic="topicb1", metric="metricb1", geography_type="g", geography="gg"
        )
        ps2 = PermissionSet.objects.create(
            theme="themea2", sub_theme="subthemea2", topic="topica2", metric="metrica2", geography_type="g", geography="gg"
        )

        client = APIClient()

        response = client.get(self.path)
        assert response.status_code == HTTPStatus.OK
        
        # Should be alphabetically sorted: 2 then 1
        assert response.data["choices"] == [
            [str(ps2.id), ps2.name],
            [str(ps1.id), ps1.name],
        ]


