from cms.topic.models import TopicPage


def create_respiratory_viruses_index_page_body() -> list[dict]:
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


def create_cover_index_page_body() -> list[dict]:
    childhood_vaccinations_topic_page = TopicPage.objects.get(
        slug="childhood-vaccinations"
    )
    return [
        {
            "type": "text",
            "value": '<p data-block-key="mlj9y">Childhood vaccinations include data collected through the Cover of Vaccination Evaluation Rapidly (COVER) programme. The data allows the comparison of vaccination uptake across time and geography. <br/></p><p data-block-key="5ms82">This includes statistics collected for routine vaccinations offered between the ages of 12 months and 5 years for England up to the years 2022-23. <br/></p><p data-block-key="85n9a">The data show the number of children vaccinated as a proportion of the eligible population (coverage) and are derived from information collected by the UK Health Security Agency (UKHSA) through the COVER programme.</p>',
            "id": "38c0fb4d-7374-4c15-9eb9-f307fa4cac15",
        },
        {
            "type": "text",
            "value": '<h2 data-block-key="4o3cw">Vaccination and coverage</h2><p data-block-key="ejgqr">Vaccination uptake is reported for the following age groups and vaccines:</p><h3 data-block-key="13qrp">12 months</h3><ul><li data-block-key="7da2p">6-in-1 (DTaP-IPV-Hib-(HepB))</li><li data-block-key="aa580">PCV (Pneumococcal conjugate vaccine)</li><li data-block-key="8oi3q">Rota (Rotavirus vaccine)</li><li data-block-key="fa822">MenB (Meningococcal group B)</li></ul><h3 data-block-key="183io">24 months</h3><ul><li data-block-key="3f8pk">6-in-1 booster (DTaP-IPV-Hib)</li><li data-block-key="2cvhe">4-in-1 booster (DTaP-IPV booster)</li><li data-block-key="fpjk4">MMR1 (Measles, mumps and rubella first dose)</li><li data-block-key="5o8a9">MMR2 (Measles, mumps and rubella second dose)</li><li data-block-key="5k8dm">Hib/MenC (Hib/Meningitis C booster)</li></ul><h3 data-block-key="f4vhg">5 years</h3><ul><li data-block-key="6t1j4">6-in-1 booster (DTaP-IPV-Hib)</li><li data-block-key="a80iv">4-in-1 booster (DTaP-IPV booster)</li><li data-block-key="7i7ub">MMR1 (Measles, mumps and rubella first dose)</li><li data-block-key="f68pp">MMR2 (Measles, mumps and rubella second dose)</li><li data-block-key="kkdc">Hib/MenC (Hib/Meningitis C booster)</li></ul>',
            "id": "b3fd4f2e-1ccf-4e0b-ba7e-1748dce84869",
        },
        {
            "type": "text",
            "value": '<h2 data-block-key="4o3cw">Geographic coverage and data availability</h2><h3 data-block-key="1o0fe">Countries of the UK</h3><p data-block-key="csink">The United Kingdom (UK) is composed of four countries: England, Scotland, Wales and Northern Ireland. Data is available from 2009-10 onwards.</p><h3 data-block-key="28rtn">Regions in England</h3><p data-block-key="c0eap">England is divided into nine regions for statistical purposes. These regions are: London, North East, North West, Yorkshire and The Humber, East Midlands, West Midlands, East of England, South East and South West. Data is available from 2009-10 onwards.</p><h3 data-block-key="2envu">Upper Tier Local Authorities</h3><p data-block-key="9q1h0">There are 152 upper-tier local authorities in England. These include unitary authorities, metropolitan districts, London boroughs, and counties. Data is available from 2013 - 14 onwards.</p>',
            "id": "6f976d03-0bc9-42c1-96c4-d8a34121fb1c",
        },
        {
            "type": "text",
            "value": '<h2 data-block-key="4o3cw">About the statistics</h2><p data-block-key="9pi3h">These are National Statistics which means they meet the highest standards of trustworthiness, quality and public value as assessed by Code of Practice for Statistics.</p>',
            "id": "92aa5e34-a874-4998-8578-c48e22aed95a",
        },
        {
            "type": "internal_page_links",
            "value": [
                {
                    "type": "page_link",
                    "value": {
                        "title": "Childhood vaccinations",
                        "sub_title": "Data about annual childhood vaccination statistics for England up to 2022-2023 and relates to routine vaccinations offered to all children up to the age of 5 years.",
                        "page": childhood_vaccinations_topic_page.id,
                    },
                    "id": "c36d19c1-3a5e-4fcf-b696-91468c609369",
                }
            ],
            "id": "41948072-024e-4566-85b5-b02706838b97",
        },
    ]
