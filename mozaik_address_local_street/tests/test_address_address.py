# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestAddressAddress(TransactionCase):
    def setUp(self):
        super().setUp()

        self.model_address = self.env["address.address"]

    def test_create_address(self):

        vals = {
            "country_id": self.env.ref("base.be").id,
            "city_id": self.env.ref("mozaik_address.res_city_1").id,
            "address_local_street_id": self.env.ref(
                "mozaik_address_local_street.local_street_1"
            ).id,
            "box": "4b",
        }
        adr = self.model_address.create(vals)
        self.assertEqual(
            adr.name,
            "Grand-Place -/4b - 4500 Huy",
            "Create address fails with wrong name",
        )
        self.assertEqual(
            adr.zip, "4500", "Create address fails with wrong zip"
        )
        self.assertEqual(
            adr.street,
            "Grand-Place -/4b",
            "Create address fails with wrong street",
        )
