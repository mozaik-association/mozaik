# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestPartnerInvolvement(SavepointCase):
    def setUp(self):
        super().setUp()
        self.paul = self.env["res.partner"].create({"name": "Paul Bocuse"})
        self.ig = self.env["interest.group"].create({"name": "Youths"})
        self.ic = self.env["partner.involvement.category"].create(
            {
                "name": "Involvement Category",
                "res_users_ids": [4, self.browse_ref("base.user_admin").id],
                "interest_group_ids": [(4, self.ig.id)],
            }
        )
        self.ic_2 = self.env["partner.involvement.category"].create(
            {
                "name": "Involvement Category 2",
                "res_users_ids": [4, self.browse_ref("base.user_admin").id],
                "interest_group_ids": [(4, self.ig.id)],
            }
        )
        self.inv_model = self.env["partner.involvement"]
        self.inv = self.inv_model.create(
            {
                "partner_id": self.paul.id,
                "involvement_category_id": self.ic.id,
            }
        )

    def test_add_involvement_with_interest_group(self):
        """
        Check that the interest group is on the partner, after having added
        self.inv in setUp
        """
        self.assertEqual(self.paul.interest_group_ids, self.ig)

    def test_delete_involvement_on_partner(self):
        """
        Add and then delete involvement with interest group
        -> Check that the interest group was removed from the partner
        """
        self.inv.unlink()
        self.assertFalse(self.paul.interest_group_ids)

    def test_delete_involvement_on_partner_2(self):
        """
        Add 2 involvements on partner with the same interest group, and then
        delete one
        -> Check that the interest group is left
        """
        self.inv_model.create(
            {
                "partner_id": self.paul.id,
                "involvement_category_id": self.ic_2.id,
            }
        )
        self.assertEqual(len(self.paul.partner_involvement_ids), 2)
        self.assertEqual(self.paul.interest_group_ids, self.ig)
        self.inv.unlink()
        self.assertEqual(len(self.paul.partner_involvement_ids), 1)
        self.assertEqual(self.paul.interest_group_ids, self.ig)

    def test_remove_interest_group_from_ic(self):
        """
        1. Add an involvement on the partner.
        2. Remove the interest group on the involvement category.
          -> Check that it was removed on the partner.
        """
        self.ic.interest_group_ids = False
        self.assertFalse(self.paul.interest_group_ids)
