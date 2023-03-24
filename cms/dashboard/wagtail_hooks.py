from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks, signals
from wagtail.models import Page

import config
from integrations import frontend


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" type="text/css" href="{}">', static("css/theme.css")
    )


def revalidate_frontend_cache(sender, **kwargs):
    instance: Page = kwargs["instance"]

    frontend.revalidate_page_via_api_client(config=config, slug=instance.slug)


# Register the receiver to the dispatched `page_published` signal
signals.page_published.connect(revalidate_frontend_cache)
