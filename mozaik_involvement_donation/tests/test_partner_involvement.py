# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


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
