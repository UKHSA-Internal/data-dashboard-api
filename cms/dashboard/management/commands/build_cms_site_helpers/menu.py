from cms.common.models import CommonPage
from cms.composite.models import CompositePage
from cms.home.models import HomePage
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
    homepage = HomePage.objects.first()
    covid_page = TopicPage.objects.get(slug="covid-19")
    flu_page = TopicPage.objects.get(slug="influenza")
    other_respiratory_viruses_page = TopicPage.objects.get(
        slug="other-respiratory-viruses"
    )

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
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "Homepage",
                                    "body": "",
                                    "page": homepage.id,
                                    "html_url": homepage.full_url,
                                },
                                "secondary_links": [
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "COVID-19",
                                            "body": "",
                                            "page": covid_page.id,
                                            "html_url": covid_page.full_url,
                                        },
                                        "id": "c14de8da-5852-41b2-80bb-aa7ea92ff9b1",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Influenza",
                                            "body": "",
                                            "page": flu_page.id,
                                            "html_url": flu_page.full_url,
                                        },
                                        "id": "ebe1dcf7-bd06-485c-bd56-6b96ed639ef8",
                                    },
                                    {
                                        "type": "secondary_link",
                                        "value": {
                                            "title": "Other respiratory viruses",
                                            "body": "",
                                            "page": other_respiratory_viruses_page.id,
                                            "html_url": other_respiratory_viruses_page.full_url,
                                        },
                                        "id": "8f6fa7aa-8283-48ca-bb73-f8fecf059b78",
                                    },
                                ],
                            },
                        },
                        "id": "9b1ea5e1-3a8e-4600-ac19-9a94ed0de509",
                    }
                ]
            },
            "id": "7c65b301-1226-4db1-8dbd-2a2342f8b523",
        },
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "Weather health alerts",
                                    "body": "",
                                    "page": weather_health_alerts_page.id,
                                    "html_url": weather_health_alerts_page.full_url,
                                },
                                "secondary_links": [],
                            },
                        },
                        "id": "17120416-69d7-4ca7-88f4-f9c4752f0933",
                    }
                ]
            },
            "id": "8fc1b945-0c7d-440d-82df-5135efcd6082",
        },
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "About",
                                    "body": "",
                                    "page": about_page.id,
                                    "html_url": about_page.full_url,
                                },
                                "secondary_links": [],
                            },
                        },
                        "id": "0c3514bb-bbe3-4047-a210-1ecd3e5704df",
                    }
                ]
            },
            "id": "5919756a-b432-4b56-8531-5cd58d00c86d",
        },
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "Metrics documentation",
                                    "body": "",
                                    "page": metrics_docs_page.id,
                                    "html_url": metrics_docs_page.full_url,
                                },
                                "secondary_links": [],
                            },
                        },
                        "id": "6718fbcd-1d0f-457f-ba2a-af3db223000f",
                    }
                ]
            },
            "id": "0c0e6da8-abfe-4141-9145-80c65d1cd427",
        },
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "What's new",
                                    "body": "",
                                    "page": whats_new_page.id,
                                    "html_url": whats_new_page.full_url,
                                },
                                "secondary_links": [],
                            },
                        },
                        "id": "15a86699-851a-48bd-b28b-7af51ac8d771",
                    }
                ]
            },
            "id": "fbf95d3d-e695-488a-a588-2df83bf789a0",
        },
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "What's coming",
                                    "body": "",
                                    "page": whats_coming_page.id,
                                    "html_url": whats_coming_page.full_url,
                                },
                                "secondary_links": [],
                            },
                        },
                        "id": "6feddadb-b1c7-4bbf-8f4d-cafc5e222088",
                    }
                ]
            },
            "id": "6fded286-2cfc-47c8-91d1-a60995581ec0",
        },
        {
            "type": "row",
            "value": {
                "columns": [
                    {
                        "type": "column",
                        "value": {
                            "heading": "",
                            "links": {
                                "primary_link": {
                                    "title": "Access our data",
                                    "body": "",
                                    "page": access_our_data_page.id,
                                    "html_url": access_our_data_page.full_url,
                                },
                                "secondary_links": [],
                            },
                        },
                        "id": "95565e6e-1577-4b4e-a0ec-40b8f416f219",
                    }
                ]
            },
            "id": "7c6579b2-041d-4ef7-b4ca-d4fbe9d3387e",
        },
    ]
