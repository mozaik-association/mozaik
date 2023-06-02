# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from odoo.tests.common import TransactionCase


class TestMembership(TransactionCase):
    def setUp(self):
        super(TestMembership, self).setUp()
        self.harry = self.env["res.partner"].create({"name": "Harry Potter"})
        regional = self.env["int.power.level"].create({"name": "Regional"})
        self.instance_lg = self.env["int.instance"].create(
            {
                "name": "Liège",
                "power_level_id": regional.id,
            }
        )
        self.member = self.env.ref("mozaik_membership.member")

    def test_renew_member_not_paid(self):
        """
        Renew a member that didn't pay
        Check that he became a former member with a price = 0
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "int_instance_id": self.instance_lg.id,
                "state_id": self.member.id,
                "price": 10,
            }
        ).action_add()
        self.assertEqual(self.harry.membership_state_id.code, "member")
        self.assertEqual(self.harry.membership_line_ids.paid, False)
        self.env["membership.renew"].create(
            {
                "membership_line_ids": [(6, 0, self.harry.membership_line_ids.ids)],
                "date_from": date.today().replace(
                    day=1, month=1, year=date.today().year + 1
                ),
            }
        )._action_close_and_renew()
        self.assertEqual(self.harry.membership_state_id.code, "former_member")
        self.assertEqual(self.harry.membership_line_ids.filtered("active").price, 0)
