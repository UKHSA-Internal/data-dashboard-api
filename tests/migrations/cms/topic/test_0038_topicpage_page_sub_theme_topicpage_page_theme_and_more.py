import pytest

from tests.migrations.helper import MigrationTests


@pytest.mark.django_db(transaction=True)
class Test0038_topicpage_page_sub_theme_topicpage_page_theme_and_more(MigrationTests):
    previous_migration_name = "0037_add_dual_cat_chart_date_prefix"
    current_migration_name = (
        "0038_topicpage_page_sub_theme_topicpage_page_theme_and_more"
    )
    current_django_app = "topic"

    @pytest.mark.parametrize(
        "theme, sub_theme, topic",
        [
            (None, None, None),
            (None, None, ""),
            (None, "", ""),
            ("", "", ""),
            ("", None, None),
            ("", "", None),
        ],
    )
    def test_is_public_true_field_values(
        self, theme: str | None, sub_theme: str | None, topic: str | None
    ):
        # Given
        self.migrate_backward()

        ContentType = self.get_model("ContentType", app="contenttypes")
        Locale = self.get_model("Locale", app="wagtailcore")
        TopicPage = self.get_model("TopicPage")

        locale, _ = Locale.objects.get_or_create(language_code="en")
        topic_page_content_type, _ = ContentType.objects.get_or_create(
            app_label="topic",
            model="topicpage",
        )

        TopicPage.objects.create(
            title="Topic 1",
            draft_title="Topic 1",
            slug="topic-1",
            path="90010001",
            depth=2,
            numchild=0,
            url_path="/topic-1/",
            content_type_id=topic_page_content_type.id,
            locale_id=locale.id,
            page_description="A test",
            seo_title="topic-1",
            is_public=True,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
        )

        topic_page = TopicPage.objects.get(title="Topic 1")
        assert topic_page.theme == theme
        assert topic_page.sub_theme == sub_theme
        assert topic_page.topic == topic

        # When
        self.migrate_forward()

        # Then
        topic_page = self.get_model("TopicPage").objects.get(title="Topic 1")
        assert topic_page.page_theme == ""
        assert topic_page.page_sub_theme == ""
        assert topic_page.page_topic == ""
        assert topic_page.page_classification == ""

        # When
        self.migrate_backward()

        # Then
        topic_page = self.get_model("TopicPage").objects.get(title="Topic 1")
        assert topic_page.theme == theme
        assert topic_page.sub_theme == sub_theme
        assert topic_page.topic == topic

    def test_is_public_false_field_values(self):
        # Given
        self.migrate_backward()

        ContentType = self.get_model("ContentType", app="contenttypes")
        Locale = self.get_model("Locale", app="wagtailcore")
        TopicPage = self.get_model("TopicPage")

        locale, _ = Locale.objects.get_or_create(language_code="en")
        topic_page_content_type, _ = ContentType.objects.get_or_create(
            app_label="topic",
            model="topicpage",
        )

        page_classification = "super-secret-classification"
        theme = "1"
        sub_theme = "2"
        topic = "3"

        TopicPage.objects.create(
            title="Topic 1",
            draft_title="Topic 1",
            slug="topic-1",
            path="90010001",
            depth=2,
            numchild=0,
            url_path="/topic-1/",
            content_type_id=topic_page_content_type.id,
            locale_id=locale.id,
            page_description="A test",
            seo_title="topic-1",
            is_public=False,
            page_classification=page_classification,
            theme=theme,
            sub_theme=sub_theme,
            topic=topic,
        )

        topic_page = TopicPage.objects.get(title="Topic 1")
        assert topic_page.theme == theme
        assert topic_page.sub_theme == sub_theme
        assert topic_page.topic == topic
        assert topic_page.page_classification == page_classification

        # When
        self.migrate_forward()

        # Then
        topic_page = self.get_model("TopicPage").objects.get(title="Topic 1")
        assert topic_page.page_theme == theme
        assert topic_page.page_sub_theme == sub_theme
        assert topic_page.page_topic == topic
        assert topic_page.page_classification == page_classification

        # When
        self.migrate_backward()

        # Then
        topic_page = self.get_model("TopicPage").objects.get(title="Topic 1")
        assert topic_page.theme == theme
        assert topic_page.sub_theme == sub_theme
        assert topic_page.topic == topic
