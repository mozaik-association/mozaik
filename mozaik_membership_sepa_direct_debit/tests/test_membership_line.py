# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.account_banking_sepa_direct_debit.tests.test_sdd import TestSDDBase


class TestMembershipLineBase(TestSDDBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.debit_order = cls.env["account.payment.order"].create(
            {
                "payment_mode_id": cls.payment_mode.id,
                "batch_booking": True,
                "payment_type": "inbound",
            }
        )
        cls.membership_state = cls.env.ref("mozaik_membership.member")
        cls.partner_1 = cls.mandate12.partner_id
        cls.partner_1.is_company = False
        cls.partner_2 = cls.mandate2.partner_id
        cls.partner_2.is_company = False


class TestMembershipLine(TestMembershipLineBase):
    def test_get_draft_sepa_debit_order(self):
        """
        Find existing draft sepa debit order
        """
        self.assertEqual(
            self.env["membership.line"].get_draft_sepa_debit_order(), self.debit_order
        )

    def test_get_unpaid_sepa_membership_lines(self):
        """
        Find active unpaid membership lines not already in an open debit order
        """
        partner_1 = self.env["res.partner"].create({"name": "Partner1"})
        # Not found because paid
        ml_1 = self.env["membership.line"].create(
            {
                "partner_id": partner_1.id,
                "state_id": self.membership_state.id,
                "paid": True,
            }
        )
        partner_2 = self.env["res.partner"].create({"name": "Partner2"})
        # Not found because partner has no active mandate
        ml_2 = self.env["membership.line"].create(
            {
                "partner_id": partner_2.id,
                "state_id": self.membership_state.id,
                "price": 10.0,
                "reference": "testref",
            }
        )
        # Not found because already in an open debit order
        ml_3 = self.env["membership.line"].create(
            {
                "partner_id": self.partner_1.id,
                "state_id": self.membership_state.id,
                "price": 10.0,
                "reference": "testref2",
                "payment_order_ids": [self.debit_order.id],
            }
        )
        # Found !
        canceled_payment_order = self.env["account.payment.order"].create(
            {
                "payment_mode_id": self.payment_mode.id,
                "batch_booking": True,
                "payment_type": "inbound",
                "state": "cancel",
            }
        )
        ml_4 = self.env["membership.line"].create(
            {
                "partner_id": self.partner_2.id,
                "state_id": self.membership_state.id,
                "price": 10.0,
                "reference": "testref3",
                "payment_order_ids": [canceled_payment_order.id],
            }
        )
        found_membership_lines = self.env[
            "membership.line"
        ].get_unpaid_sepa_membership_lines()
        self.assertFalse(
            any([ml.id in found_membership_lines.ids for ml in (ml_1 | ml_2 | ml_3)])
        )
        self.assertEqual(ml_4.id, found_membership_lines.ids[0])

    def test_add_unpaid_memberships_to_debit_order_and_upload(self):
        """
        Add line to debit order for unpaid membership line and upload the order
        """
        ml = self.env["membership.line"].create(
            {
                "partner_id": self.partner_1.id,
                "state_id": self.membership_state.id,
                "price": 10.0,
                "reference": "testref",
            }
        )
        self.env["membership.line"].add_unpaid_memberships_to_debit_order()
        self.assertEqual(ml.payment_order_ids.ids, [self.debit_order.id])
        self.assertEqual(self.debit_order.payment_line_ids[0].amount_currency, 10.0)
        self.debit_order.draft2open()
        self.debit_order.open2generated()
        self.debit_order.generated2uploaded()
        self.assertTrue(ml.paid)
        self.assertEqual(ml.price_paid, 10.0)
        self.assertEqual([ml.move_id.id], self.debit_order.move_ids.ids)
