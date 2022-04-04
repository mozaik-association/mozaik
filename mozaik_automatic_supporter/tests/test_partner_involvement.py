# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestPartnerInvolvement(TransactionCase):
    def test_automatic_supporter(self):
        """
        Check for automatic supporter
        """
        # create an involvement category
        vals = {
            "name": "Le projet Okavango",
            "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
        }
        ic = self.env["partner.involvement.category"].create(vals)
        # create a partner
        vals = {
            "name": "Nicolas HULOT",
        }
        p = self.env["res.partner"].create(vals)
        # create an involvement
        vals = {
            "partner_id": p.id,
            "involvement_category_id": ic.id,
        }
        inv = self.env["partner.involvement"].create(vals)
        # the partner is without status
        self.assertEqual("without_membership", p.membership_state_code)
        # unlink the involvement and update the category
        inv.unlink()
        ic.automatic_supporter = True
        # recreate the involvement
        self.env["partner.involvement"].create(vals)
        # the partner is now a supporter
        self.assertEqual("supporter", p.membership_state_code)
