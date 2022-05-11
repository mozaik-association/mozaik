# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestMembershipRequest(TransactionCase):
    def setUp(self):
        super().setUp()
        address_1 = self.browse_ref("mozaik_address.address_1")
        self.last_postal_failure_date = datetime.now()
        self.partner = self.env["res.partner"].create(
            {
                "lastname": "Sy",
                "firstname": "Omar",
                "email": "o.s@test.com",
                "address_address_id": address_1.id,
                "last_postal_failure_date": self.last_postal_failure_date,
            }
        )

    def test_last_postal_failure_date_same_address(self):
        """
        Create a membership request without changing the address
        -> last postal failure date shouldn't change
        """
        self.partner.button_modification_request()
        mr = self.env["membership.request"].search(
            [("partner_id", "=", self.partner.id), ("state", "=", "draft")]
        )
        self.assertEqual(len(mr), 1)
        mr.validate_request()
        self.assertEqual(
            self.partner.last_postal_failure_date, self.last_postal_failure_date
        )

    def test_last_postal_failure_date_change_address(self):
        """
        Create a membership request and change the address
        -> last postal failure date reset to False
        """
        self.partner.button_modification_request()
        mr = self.env["membership.request"].search(
            [("partner_id", "=", self.partner.id), ("state", "=", "draft")]
        )
        self.assertEqual(len(mr), 1)
        mr.number = "10"
        mr.validate_request()
        self.assertFalse(self.partner.last_postal_failure_date)
