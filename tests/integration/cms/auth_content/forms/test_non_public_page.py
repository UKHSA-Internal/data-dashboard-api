from unittest.mock import MagicMock, patch

import pytest
from wagtail.admin.panels import get_form_for_model
from wagtail.models import Page

from cms.auth_content.forms.non_public_page import (
    NonPublicPageAdminForm,
    SUB_THEME_FIELD,
)
from cms.auth_content.models.non_public_page import (
    DataClassificationLevels,
    get_non_public_page_types,
)
from cms.topic.models import TopicPage


class TestNonPublicPageAdminForm:

    @pytest.mark.django_db
    @pytest.mark.parametrize("non_public_subclass", get_non_public_page_types())
    def test_binding_to_non_public_page_classes(self, non_public_subclass):
        """
        When a new form is instantiated for a non-public page subclass
        Then a form field is added to `fields` for each expected non-pub field
        """
        # bind the subclass to the form
        page_form = get_form_for_model(
            non_public_subclass,
            form_class=NonPublicPageAdminForm,
        )
        # create the form
        form = page_form()

        # check we've got what we expected
        for field in ["page_theme", "page_sub_theme", "page_topic"]:
            assert (
                field in form.fields
            ), f"{field} is missing when bound to {non_public_subclass.__name__}"

    @pytest.mark.django_db
    @pytest.mark.parametrize("non_public_subclass", get_non_public_page_types())
    def test_non_public_pages_are_using_form(self, non_public_subclass):
        """
        When a new form is instantiated for a non-public page subclass
        Then a form field is added to `fields` for each expected field
        """
        # instantiate the actual form in use by the page
        form = non_public_subclass().get_edit_handler().get_form_class()()
        # check we've got what we expected
        for field in ["page_theme", "page_sub_theme", "page_topic"]:
            assert (
                field in form.fields
            ), f"{field} is missing from {non_public_subclass.__name__}'s form"

    @pytest.mark.django_db
    def test_dependent_fields_initialised_for_saved_instance(self):
        """
        Given a saved page (i.e. has a pk)
        When its form is initialised
        Then `_initialize_dependent_fields` is called
        """
        home = Page.objects.get(id=2)
        page = TopicPage(
            title="A test topic page",
            page_description="test",
            slug="a-test-topic-page",
            seo_title="a-test-topic-page-seo-title",
            is_public=False,
            page_classification=DataClassificationLevels.OFFICIAL_SENSITIVE.value,
            page_theme="3",
            page_sub_theme="5",
            page_topic="7",
        )
        page = home.add_child(instance=page)
        mock__initialize_dependent_fields = MagicMock()
        with patch.object(
            page.base_form_class,
            "_initialize_dependent_fields",
            mock__initialize_dependent_fields,
        ):
            _form = page.get_edit_handler().get_form_class()(instance=page)
            mock__initialize_dependent_fields.assert_called_once()

    @pytest.mark.django_db
    def test_dependent_fields_not_initialised_for_new_instance(self):
        """
        Given a saved page (i.e. has a pk)
        When its form is initialised
        Then `_initialize_dependent_fields` is not called
        """
        page = TopicPage()
        mock__initialize_dependent_fields = MagicMock()
        with patch.object(
            page.base_form_class,
            "_initialize_dependent_fields",
            mock__initialize_dependent_fields,
        ):
            _form = page.get_edit_handler().get_form_class()(instance=page)
            mock__initialize_dependent_fields.assert_not_called()

    @pytest.mark.django_db
    def test_widget_choices_set_when_sub_theme_has_value(self):
        """
        Given a page with a page_sub_theme value set and its form
        When `_initialize_dependent_fields` is called
        Then the sub_theme choices are set
        """
        # create an empty page
        page = TopicPage()
        form = page.get_edit_handler().get_form_class()(instance=page)
        # set a sub-theme on the page
        page_sub_theme = "10"
        page.page_sub_theme = page_sub_theme

        form._initialize_dependent_fields()

        assert form.fields["page_sub_theme"].widget.choices == [
            ("", "Select theme first"),
            (page_sub_theme, f"Loading... (ID: {page_sub_theme})"),
        ]

    @pytest.mark.django_db
    def test_widget_choices_not_set_when_value_is_none(self):
        """
        Given a page without a page_sub_theme value set and its form
        When `_initialize_dependent_fields` is called
        Then the sub_theme choices remain the default
        """
        page = TopicPage()
        form = page.get_edit_handler().get_form_class()(instance=page)
        page.page_sub_theme = ""

        form._initialize_dependent_fields()

        assert form.fields["page_sub_theme"].widget.choices == [
            ("", SUB_THEME_FIELD.choice_default)
        ]
