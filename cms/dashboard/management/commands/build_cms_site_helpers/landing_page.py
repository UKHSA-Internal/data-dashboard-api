from cms.composite.models import CompositePage
from cms.topic.models import TopicPage


def create_landing_page_body_wih_page_links() -> list[dict]:
    respiratory_viruses_index = CompositePage.objects.get(slug="respiratory-viruses")
    covid_page = TopicPage.objects.get(slug="covid-19")
    influenza_page = TopicPage.objects.get(slug="influenza")
    other_respiratory_viruses_page = TopicPage.objects.get(
        slug="other-respiratory-viruses"
    )
    weather_health_alerts_page = CompositePage.objects.get(slug="weather-health-alerts")

    return [
        {
            "type": "section",
            "value": {
                "heading": "Respiratory viruses",
                "page_link": respiratory_viruses_index.id,
                "content": [
                    {
                        "type": "chart_card_section",
                        "value": {
                            "cards": [
                                {
                                    "type": "simplified_chart_with_link",
                                    "value": {
                                        "title": "COVID-19",
                                        "sub_title": "Cases reported",
                                        "tag_manager_event_id": "",
                                        "topic_page": covid_page.id,
                                        "x_axis": "date",
                                        "y_axis": "metric",
                                        "chart": [
                                            {
                                                "type": "plot",
                                                "value": {
                                                    "topic": "COVID-19",
                                                    "metric": "COVID-19_cases_countRollingMean",
                                                    "geography": "England",
                                                    "geography_type": "Nation",
                                                    "sex": "all",
                                                    "age": "all",
                                                    "stratum": "default",
                                                    "chart_type": "line_single_simplified",
                                                    "date_from": "2022-10-14",
                                                    "date_to": "2023-10-14",
                                                },
                                                "id": "0cb2a953-8737-4978-9886-d3943b76820a",
                                            }
                                        ],
                                    },
                                    "id": "8b2ca8aa-7bdb-4c47-835c-dc1c09f767cf",
                                },
                                {
                                    "type": "simplified_chart_with_link",
                                    "value": {
                                        "title": "Influenza",
                                        "sub_title": "Healthcare admission rates",
                                        "tag_manager_event_id": "",
                                        "topic_page": influenza_page.id,
                                        "x_axis": "date",
                                        "y_axis": "metric",
                                        "chart": [
                                            {
                                                "type": "plot",
                                                "value": {
                                                    "topic": "Influenza",
                                                    "metric": "influenza_healthcare_ICUHDUadmissionRateByWeek",
                                                    "geography": "England",
                                                    "geography_type": "Nation",
                                                    "sex": "all",
                                                    "age": "all",
                                                    "stratum": "default",
                                                    "chart_type": "line_single_simplified",
                                                    "date_from": "2022-10-14",
                                                    "date_to": "2023-10-14",
                                                },
                                                "id": "7423460c-aa0c-482d-8fd5-ab9c62396657",
                                            }
                                        ],
                                    },
                                    "id": "b7b37be5-8bc0-4f88-8310-7a91430b7993",
                                },
                                {
                                    "type": "simplified_chart_with_link",
                                    "value": {
                                        "title": "RSV",
                                        "sub_title": "Positivity by week",
                                        "tag_manager_event_id": "",
                                        "topic_page": other_respiratory_viruses_page.id,
                                        "x_axis": "date",
                                        "y_axis": "metric",
                                        "chart": [
                                            {
                                                "type": "plot",
                                                "value": {
                                                    "topic": "RSV",
                                                    "metric": "RSV_testing_positivityByWeek",
                                                    "geography": "England",
                                                    "geography_type": "Nation",
                                                    "sex": "all",
                                                    "age": "all",
                                                    "stratum": "default",
                                                    "chart_type": "line_single_simplified",
                                                    "date_from": "2022-01-01",
                                                    "date_to": "2023-10-14",
                                                },
                                                "id": "f9eb94ff-0d92-4265-a88b-d52bf73532a5",
                                            }
                                        ],
                                    },
                                    "id": "0a830ab5-b232-47f1-a5af-f140e0f07c23",
                                },
                            ]
                        },
                        "id": "40d17855-71e3-424e-a662-2f6930073e59",
                    }
                ],
            },
            "id": "c3ec156e-e58b-4976-b0f2-c08c1e933467",
        },
        {
            "type": "section",
            "value": {
                "heading": "Weather health alerts",
                "page_link": weather_health_alerts_page.id,
                "content": [
                    {
                        "type": "weather_health_alert_card",
                        "value": {
                            "title": "weather health alerts",
                            "sub_title": "Across England",
                            "alert_type": "heat",
                        },
                        "id": "d01c65cb-4cd2-4e07-bd6e-71ea0ec04594",
                    }
                ],
            },
            "id": "be533e25-ba91-4e86-8a45-1314ed395fb9",
        },
    ]
