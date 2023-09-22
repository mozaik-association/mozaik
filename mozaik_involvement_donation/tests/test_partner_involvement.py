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
        # Just a promise? no it's a real donation
        self.assertFalse(inv.promise)
        inv.reference = "MaBonneFoi"
        # Just a promise? no it's also a real donation
        self.assertFalse(inv.promise)
        inv.effective_time = False
        # Just a promise? yes
        self.assertTrue(inv.promise)
