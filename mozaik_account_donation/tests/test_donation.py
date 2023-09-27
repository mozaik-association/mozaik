# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestDonation(object):
    def setUp(self):
        super().setUp()

        self.involvement = self._create_involvement()
        self.partner = self.involvement.partner_id

    def _create_involvement(self):
        """
        return a new involvement related to a new partner
        """
        # create a partner
        partner = self.env["res.partner"].create(
            {
                "lastname": uuid.uuid4(),
            }
        )
        # create an involvement category
        cat = self.env["partner.involvement.category"].create(
            {
                "name": "Protégons nos arrières...",
                "code": "PA",
                "involvement_type": "donation",
                "allow_multi": True,
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        # create an involvement
        involvement = self.env["partner.involvement"].create(
            {
                "partner_id": partner.id,
                "involvement_category_id": cat.id,
                "effective_time": fields.Datetime.now().replace(
                    hour=0, minute=0, second=0
                ),
                "amount": 12.0,
                "reference": "DONKAMYO",
            }
        )
        return involvement

    def _generate_payment(self, additional_amount=0.0, with_partner=True):
        statement = (
            self.env["account.bank.statement"]
            .with_context(journal_type="bank")
            .create({})
        )
        amount = 12.0
        amount += additional_amount
        vals = {
            "statement_id": statement.id,
            "payment_ref": self.involvement.reference,
            "amount": amount,
        }
        if with_partner:
            vals["partner_id"] = self.partner.id

        self.env["account.bank.statement.line"].create(vals)

        return statement

    def _get_manual_move_dict(self, additional_amount):
        res = []
        donation_account = self.env["ir.property"].get(
            "property_account_income", "product.template"
        )
        res.append(
            {
                "account_id": donation_account.id,
                "debit": 0,
                "credit": self.involvement.amount,
                "name": self.involvement.reference,
            }
        )
        if additional_amount > 0:
            res.append(
                {
                    "account_id": donation_account.id,
                    "debit": 0,
                    "credit": additional_amount,
                    "name": "Comment",
                }
            )
        return res

    def test_accounting_auto_reconcile(self):
        statement = self._generate_payment()
        statement.auto_reconcile()

        for line in statement.line_ids:
            self.assertTrue(line.journal_entry_id.id)

        # now without seconds
        about_now = fields.Datetime.now()[0:16]
        self.assertEqual(about_now, self.involvement.effective_time[0:16])
        self.assertEqual(12.0, self.involvement.amount)
        self.assertEqual(statement.line_ids.amount, self.involvement.amount)

    def test_accounting_manual_reconcile(self):
        additional_amount = 20.0
        statement = self._generate_payment(additional_amount=additional_amount)

        statement.auto_reconcile()

        for line in statement.line_ids:
            self.assertFalse(line.journal_entry_id)

        move_dicts = self._get_manual_move_dict(additional_amount)

        statement.process_reconciliation(move_dicts)

        # now without seconds
        about_now = fields.Datetime.now()[0:16]
        self.assertEqual(about_now, self.involvement.effective_time[0:16])
        self.assertEqual(12.0 + 20.0, self.involvement.amount)
        self.assertEqual(statement.line_ids.amount, self.involvement.amount)

    def test_accounting_manual_reconcile_without_partner(self):
        additional_amount = 30.0
        statement = self._generate_payment(
            additional_amount=additional_amount, with_partner=False
        )

        statement.auto_reconcile()

        for line in statement.line_ids:
            self.assertFalse(line.journal_entry_id)

        move_dicts = self._get_manual_move_dict(additional_amount)

        self.assertRaises(ValidationError, statement.process_reconciliation, move_dicts)


class TestAccountingProtectAutoReconcile(TestDonation, SavepointCase):
    def test_accounting_auto_reconcile(self):
        """
        Auto reconcile does not work when a reference is used twice
        """
        statement = self._generate_payment()
        statement.auto_reconcile()

        for line in statement.line_ids:
            self.assertTrue(line.is_reconciled)

        statement2 = statement.copy()
        statement2.line_ids.move_id.line_ids[
            1
        ].account_id = statement2.line_ids.journal_id.suspense_account_id
        statement2.auto_reconcile()
        for line in statement2.line_ids:
            self.assertFalse(line.is_reconciled)

    def test_accounting_manual_reconcile(self):
        return

    def test_accounting_manual_reconcile_without_partner(self):
        return
