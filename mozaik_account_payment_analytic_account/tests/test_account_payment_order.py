# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestAccountPaymentOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        bank_journal = self.env["account.journal"].search(
            [("name", "=", "Bank")], limit=1
        )
        self.company = bank_journal.company_id
        payment_method_in = self.env.ref("account.account_payment_method_manual_in")
        self.payment_mode_in = self.env["account.payment.mode"].create(
            {
                "name": "Test",
                "payment_method_id": payment_method_in.id,
                "bank_account_link": "fixed",
                "fixed_journal_id": bank_journal.id,
                "company_id": self.company.id,
            }
        )
        self.debit_order = self.env["account.payment.order"].create(
            {
                "payment_mode_id": self.payment_mode_in.id,
                "batch_booking": True,
                "payment_type": "inbound",
            }
        )
        self.partner = self.env["res.partner"].create({"name": "Test"})
        self.env["account.payment.line"].create(
            {
                "order_id": self.debit_order.id,
                "amount_currency": 10.0,
                "partner_id": self.partner.id,
                "communication": "Test comm",
            }
        )
        self.analytic_account = self.env.ref("analytic.analytic_asustek")

    def test_force_partner_account(self):
        """
        Credit move lines must be linked to account set on company
        """
        self.company.debit_order_analytic_account_id = self.analytic_account.id
        self.debit_order.draft2open()
        self.debit_order.open2generated()
        self.debit_order.generated2uploaded()
        credit_ml = self.debit_order.move_ids[0].line_ids.filtered(
            lambda ml: ml.credit == 10.0
        )
        self.assertEqual(self.analytic_account.id, credit_ml.analytic_account_id.id)

    def test_electronic_payment_analytic_account(self):
        """
        Credit move lines must be linked to analytic account set on company
        """
        self.company.electronic_payment_analytic_account_id = self.analytic_account.id
        payment_method_in = self.env.ref("payment.account_payment_method_electronic_in")
        payment = self.env["account.payment"].create(
            {
                "amount": 50.0,
                "payment_method_id": payment_method_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
            }
        )
        credit_ml = payment.move_id.mapped("line_ids").filtered("credit")
        self.assertEqual(credit_ml.analytic_account_id, self.analytic_account)
