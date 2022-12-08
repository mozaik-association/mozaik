# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from uuid import uuid4

from odoo import fields
from odoo.tests.common import TransactionCase


class TestMembershipLine(TransactionCase):
    def setUp(self):
        super(TestMembershipLine, self).setUp()
        self.instance = self.env.ref("mozaik_structure.int_instance_03")
        self.partner_marc = self.env.ref("mozaik_membership.res_partner_marc")
        self.product_subscription = self.env.ref(
            "mozaik_membership.membership_product_isolated"
        )
        journal = self.env["account.journal"].search([], limit=1)
        self.move = self.env["account.move"].create(
            {
                "name": "Test move",
                "date": fields.Date.today(),
                "journal_id": journal.id,
                "state": "draft",
            }
        )

    def test_mark_as_unpaid(self):
        """
        Mark as unpaid removes paid, price_paid and move
        """
        values = {
            "date_from": "2015-06-05",
            "partner_id": self.partner_marc.id,
            "state_id": self.partner_marc.membership_state_id.id,
            "int_instance_id": self.instance.id,
            "price": 500,
            "reference": str(uuid4()),
            "product_id": self.product_subscription.id,
        }
        membership = self.env["membership.line"].create(values)
        membership._mark_as_paid(500, self.move)
        self.assertTrue(membership.paid)
        membership.mark_as_unpaid()
        self.assertFalse(membership.paid)
        self.assertFalse(membership.price_paid)
        self.assertFalse(membership.move_id)
        self.assertFalse(membership.bank_account_id)
