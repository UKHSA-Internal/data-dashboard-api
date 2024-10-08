from cms.topic.models import TopicPage


def create_respiratory_viruses_index_page() -> list[dict]:
    covid_page = TopicPage.objects.get(slug="covid-19")
    influenza_page = TopicPage.objects.get(slug="influenza")
    other_respiratory_viruses_page = TopicPage.objects.get(
        slug="other-respiratory-viruses"
    )

    return [
        {
            "type": "internal_page_links",
            "value": [
                {
                    "type": "page_link",
                    "value": {
                        "title": "COVID-19",
                        "sub_title": "COVID-19 is a respiratory infection caused by the SARS-CoV-2-virus",
                        "page": covid_page.id,
                    },
                    "id": "c36d19c1-3a5e-4fcf-b696-91468c609369",
                },
                {
                    "type": "page_link",
                    "value": {
                        "title": "Influenza",
                        "sub_title": "Influenza (commonly known as flu) is a respiratory infection",
                        "page": influenza_page.id,
                    },
                    "id": "b3375764-0829-494e-9060-a65df5dd53bd",
                },
                {
                    "type": "page_link",
                    "value": {
                        "title": "Other respiratory viruses",
                        "sub_title": "RSV is one of the common viruses that cause coughs and colds in winter",
                        "page": other_respiratory_viruses_page.id,
                    },
                    "id": "99c01f1d-0280-4cf4-bd96-39543a6c1ac9",
                },
            ],
        }
    ]
