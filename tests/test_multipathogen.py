from datetime import datetime

from tortoise.contrib import test
from tortoise.contrib.test import initializer, finalizer

import wpdb
from wpdb.models import MultiPathogen


class TestModels(test.TestCase):

    def setUp(self) -> None:
        initializer(modules=[wpdb.models], db_url="sqlite:///tmp/test-{}.sqlite")

    def tearDown(self) -> None:
        finalizer()

    async def test_multipathogen_one_item(self):
        """ We can load data into the multipathogen table and it will be returned
        as expected. """
        multipathogen = await MultiPathogen.create(
            week=1,
            year=2022,
            week_key="2022-01",
            publish_date=datetime(2022, 11, 3),
            season="2022-2023",
            influenza_pct=1.1,
            rsv_pct=10.2,
            rhinovirus_pct=2.3,
            parainfluenza_pct=20.4,
            hmpv_pct=3.5,
            adenovirus_pct=30.6,
            sars_cov_pct=4.7,
            influenza_a_h3n2_n_pct=40.8,
            influenza_a_h1n1_pdm09_n_pct=5.9,
            influenza_a_not_subtyped_n_pct=50.0,
            influenza_b_n_pct=6.1,

        )
        await multipathogen.save()
        saved_item = await MultiPathogen.get(season="2022-2023")
        self.assertEqual(1, saved_item.week)
        self.assertEqual(2022, saved_item.year)
        self.assertEqual("2022-01", saved_item.week_key)
        self.assertEqual(datetime(2022, 11, 3),
                         datetime.combine(saved_item.publish_date, datetime.min.time()))
        self.assertEqual("2022-2023", saved_item.season)
        self.assertEqual(4.7, float(saved_item.sars_cov_pct))
        self.assertEqual(10.2, float(saved_item.rsv_pct))
        self.assertEqual(2.3, float(saved_item.rhinovirus_pct))
        self.assertEqual(20.4, float(saved_item.parainfluenza_pct))
        self.assertEqual(3.5, float(saved_item.hmpv_pct))
        self.assertEqual(30.6, float(saved_item.adenovirus_pct))
        self.assertEqual(4.7, float(saved_item.sars_cov_pct))
        self.assertEqual(40.8, float(saved_item.influenza_a_h3n2_n_pct))
        self.assertEqual(5.9, float(saved_item.influenza_a_h1n1_pdm09_n_pct))
        self.assertEqual(50.0, float(saved_item.influenza_a_not_subtyped_n_pct))
        self.assertEqual(6.1, float(saved_item.influenza_b_n_pct))