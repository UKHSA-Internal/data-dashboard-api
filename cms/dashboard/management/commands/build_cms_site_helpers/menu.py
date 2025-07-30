from cms.common.models import CommonPage
from cms.composite.models import CompositePage
from cms.home.models import LandingPage
from cms.metrics_documentation.models import MetricsDocumentationParentPage
from cms.snippets.models import Menu
from cms.topic.models import TopicPage
from cms.whats_new.models import WhatsNewParentPage


def create_menu_snippet():
    Menu.objects.create(
        internal_label="Primary navigation",
        is_active=True,
        body=_create_menu_data(),
    )


def _create_menu_data() -> list[dict]:
    landing_page = LandingPage.objects.first()
    covid_page = TopicPage.objects.get(slug="covid-19")
    flu_page = TopicPage.objects.get(slug="influenza")
    other_respiratory_viruses_page = TopicPage.objects.get(
        slug="other-respiratory-viruses"
    )
    childhood_vaccinations_index_page = CompositePage.objects.get(slug="cover")

    weather_health_alerts_page = CompositePage.objects.get(slug="weather-health-alerts")
    about_page = CommonPage.objects.get(slug="about")
    metrics_docs_page = MetricsDocumentationParentPage.objects.first()
    whats_new_page = WhatsNewParentPage.objects.first()
    whats_coming_page = CommonPage.objects.get(slug="whats-coming")
    access_our_data_page = CompositePage.objects.get(slug="access-our-data")

    return [
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "Health topics",
                            "links": {
                                "primary_link": {
                                    "title": "COVID-19",
                                    "body": '<p data-block-key="o0pz4">COVID-19 respiratory infection statistics</p>',
                                    "page": covid_page.id,
                                    "html_url": covid_page.full_url,
                                },
                                "secondary_links": [
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Influenza",
                                            "body": '<p data-block-key="fnj00">Flu ICU and HDU admissions and other statistics</p>',
                                            "page": flu_page.id,
                                            "html_url": flu_page.full_url,
                                        },
                                        "id": "0f41af0a-c4b7-4c68-9cf7-eddd18ceecae",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Other respiratory viruses",
                                            "body": '<p data-block-key="fnj00">Other common respiratory viruses including adenovirus, hMPV &amp; parainfluenza</p>',
                                            "page": other_respiratory_viruses_page.id,
                                            "html_url": other_respiratory_viruses_page.full_url,
                                        },
                                        "id": "acd7c46f-b871-48ae-943f-9e95656bde6e",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Childhood vaccinations",
                                            "body": '<p data-block-key="ap3f6">Cover of vaccination enhanced rapidly</p>',
                                            "page": childhood_vaccinations_index_page.id,
                                            "html_url": childhood_vaccinations_index_page.full_url,
                                        },
                                        "id": "9764fedd-4543-41fd-969f-c38a1ca2e559",
                                    },
                                ],
                            },
                        },
                        "id": "2758ae51-c976-46d2-8e38-c566bf6661b6",
                    },
                    {
                        "type": "column",
                        "value": {
                            "heading": "Services and information",
                            "links": {
                                "primary_link": {
                                    "title": "Homepage",
                                    "body": '<p data-block-key="o0pz4">The UKHSA data dashboard</p>',
                                    "page": landing_page.id,
                                    "html_url": landing_page.full_url,
                                },
                                "secondary_links": [
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Weather health alerts",
                                            "body": '<p data-block-key="fnj00">Weather health alerting system provided by UKHSA</p>',
                                            "page": weather_health_alerts_page.id,
                                            "html_url": weather_health_alerts_page.full_url,
                                        },
                                        "id": "5e595a50-1ef9-48cc-9208-9d02d9ba6006",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "About",
                                            "body": '<p data-block-key="fnj00">About the dashboard</p>',
                                            "page": about_page.id,
                                            "html_url": about_page.full_url,
                                        },
                                        "id": "8409731d-c41c-4cba-8e4c-2685fbcdd9de",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Metrics documentation",
                                            "body": '<p data-block-key="fnj00">See all available metrics</p>',
                                            "page": metrics_docs_page.id,
                                            "html_url": metrics_docs_page.full_url,
                                        },
                                        "id": "31f49d81-37fe-403b-a169-3f7c89c05db8",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Access our data",
                                            "body": '<p data-block-key="fnj00">API developer&#x27;s guide</p>',
                                            "page": access_our_data_page.id,
                                            "html_url": access_our_data_page.full_url,
                                        },
                                        "id": "e651e6cb-5de3-412e-90d2-813d88584e44",
                                    },
                                ],
                            },
                        },
                        "id": "f5e762e6-15c6-4058-8913-7a4e4edbff4d",
                    },
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "What's new",
                                    "body": '<p data-block-key="o0pz4">Timeline of changes</p>',
                                    "page": whats_new_page.id,
                                    "html_url": whats_new_page.full_url,
                                },
                                "secondary_links": [
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "What's coming",
                                            "body": "",
                                            "page": whats_coming_page.id,
                                            "html_url": whats_coming_page.full_url,
                                        },
                                        "id": "110d74f3-3bb3-478a-9385-71e2600a8490",
                                    }
                                ],
                            },
                        },
                        "id": "0816b736-312c-46ce-8b6e-98d18a0ce463",
                    },
                ]
            },
            "id": "dcd6d76c-a3b3-4b44-8326-8177d609b50b",
        }
    ]
