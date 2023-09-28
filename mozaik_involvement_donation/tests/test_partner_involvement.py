# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import SavepointCase


class TestPartnerInvolvement(SavepointCase):
    def setUp(self):
        super().setUp()
        self.paul = self.env["res.partner"].create({"name": "Paul Bocuse"})
        self.ic_1 = self.browse_ref(
            "mozaik_involvement.partner_involvement_category_demo_1"
        )

    def test_onchange_type(self):
        """
        Check for allow_multiple when changing involvement type
        """
        # create an involvement category
        cat = self.env["partner.involvement.category"].new(
            {
                "name": "Semeur, vaillants du rêve...",
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        cat.involvement_type = "donation"
        cat._onchange_involvement_type()
        self.assertTrue(cat.allow_multi)

    def test_promise(self):
        """
        Check for multi donation payment data propagation when validating
        """
        # create an involvement category
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Je promets d être fidèle...",
                "involvement_type": "donation",
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
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
        # Just a promise? yes, he doesn't pay yet
        self.assertTrue(inv.promise)
        inv.payment_date = fields.Datetime.today()
        # Just a promise? no, he paid
        self.assertFalse(inv.promise)

    def test_is_paid(self):
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Semeur, vaillants du rêve...",
                "involvement_type": "newsletter",
            }
        )
        inv = self.env["partner.involvement"].create(
            {
                "partner_id": self.paul.id,
                "involvement_category_id": cat.id,
            }
        )
        self.assertFalse(inv.is_paid)
        inv.payment_date = fields.Date.today()
        self.assertFalse(inv.is_paid)

        inv.payment_date = False
        cat.involvement_type = "donation"
        self.assertTrue(inv.promise)
        self.assertFalse(inv.is_paid)
        inv.payment_date = fields.Date.today()
        self.assertFalse(inv.promise)
        self.assertTrue(inv.is_paid)
