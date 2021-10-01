# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields
from odoo.tests.common import TransactionCase


class TestInvolvement(TransactionCase):
    def test_promise(self):
        """
        Check for multi donation payment data propagation when validating
        """
        return  # TODO
        # create an involvement category
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Je promets d" "être fidèle...",
                "involvement_type": "donation",
            }
        )
        # create a partner
        partner = self.env["res.partner"].create(
            {
                "lastname": "Le Saint",
            }
        )
        # create a donation
        inv = self.env["partner.involvement"].new(
            {
                "involvement_category_id": cat.id,
                "partner_id": partner.id,
                "amount": 1.0,
                "effective_time": fields.Datetime.now(),
            }
        )
        # Just a  promise? no it's a real donation
        self.assertFalse(inv.promise)
        inv.reference = "MaBonneFoi"
        # Just a  promise? no it's also a real donation
        self.assertFalse(inv.promise)
        inv.effective_time = False
        # Just a  promise? yes
        self.assertTrue(inv.promise)
