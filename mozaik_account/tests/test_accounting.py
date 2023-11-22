# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import random
import uuid

from odoo.fields import first
from odoo.tests.common import SavepointCase


class TestAccounting(object):

    product = None
    partner_2 = None

    def setUp(self):
        super().setUp()

        self.bs_obj = self.env["account.bank.statement"]
        self.bsl_obj = self.env["account.bank.statement.line"]
        self.ml_obj = self.env["membership.line"]
        self.partner_obj = self.env["res.partner"]
        self.partner = self._get_partner()
        self.member_state = self.env.ref("mozaik_membership.member")

    def _get_partner(self):
        """
        return a new browse record of partner
        """
        name = uuid.uuid4()
        partner_values = {
            "lastname": name,
        }
        partner = self.partner_obj.create(partner_values)
        return partner

    def _generate_payment(self, additional_amount=0, with_partner=True):
        instance = first(self.partner.int_instance_ids)
        reference = self.ml_obj._generate_membership_reference(self.partner, instance)
        b_statement_id = self.bs_obj.with_context(journal_type="bank").create({})
        if self.product:
            amount = self.product.list_price
        else:
            amount = random.uniform(10, 100)
        if not self.partner.membership_line_ids.filtered(
            lambda line: line.reference == reference
        ):
            values = self.partner.membership_line_ids._build_membership_values(
                self.partner,
                instance,
                self.member_state,
                price=amount,
                product=self.product,
            )
            values.update(
                {
                    "reference": reference,
                }
            )
            self.partner.membership_line_ids.create(values)
        amount += additional_amount
        statement_line_vals = {
            "statement_id": b_statement_id.id,
            "amount": amount,
            "payment_ref": "%s" % b_statement_id.id,
        }
        if with_partner:
            statement_line_vals.update(
                {
                    "partner_id": self.partner.id,
                    "name": reference,
                }
            )

        self.bsl_obj.create(statement_line_vals)

        return b_statement_id

    def _get_manual_move_dict(self, additional_amount):
        property_obj = self.env["ir.property"]
        res = []
        subscription_account = property_obj._get(
            "property_subscription_account", "product.template"
        )
        other_account = self.env["account.account"].search(
            [("id", "not in", subscription_account.ids)], limit=1
        )
        reference = self.partner.membership_line_ids.reference
        if self.product:
            if self.product.list_price > 0:
                res.append(
                    {
                        "account_id": subscription_account.id,
                        "debit": 0,
                        "credit": self.product.list_price,
                        "name": reference,
                    }
                )
        if additional_amount > 0:
            if self.product:
                account = other_account
                name = "Comment"
            else:
                account = subscription_account
                name = reference

            res.append(
                {
                    "account_id": account.id,
                    "debit": 0,
                    "credit": additional_amount,
                    "name": name,
                }
            )

        return res

    def test_accounting_auto_reconcile(self):
        bank_s = self._generate_payment()
        bank_s.auto_reconcile()

        for line in bank_s.line_ids:
            self.assertTrue(line.is_reconciled)

        self.assertTrue(self.partner.membership_line_ids.paid)
        self.assertAlmostEqual(
            self.partner.membership_line_ids.price_paid, bank_s.line_ids.amount
        )
        self.assertEqual(
            bank_s.line_ids.move_id,
            self.partner.membership_line_ids.move_id,
        )

    def test_accounting_manual_reconcile(self):
        additional_amount = 1999.99
        bank_s = self._generate_payment(additional_amount=additional_amount)
        if self.product:
            price = self.product.list_price
        else:
            price = additional_amount
        bank_s.auto_reconcile()
        for line in bank_s.line_ids:
            self.assertFalse(line.is_reconciled)

        if not self.product:
            move_dicts = self._get_manual_move_dict(bank_s.line_ids.amount)
        else:
            move_dicts = self._get_manual_move_dict(additional_amount)

        first(bank_s.line_ids).process_reconciliation(new_aml_dicts=move_dicts)

        self.assertTrue(self.partner.membership_line_ids.paid)
        if not self.product:
            self.assertAlmostEqual(
                self.partner.membership_line_ids.price_paid, bank_s.line_ids.amount
            )
        else:

            self.assertAlmostEqual(self.partner.membership_line_ids.price_paid, price)
        self.assertEqual(
            bank_s.line_ids.move_id,
            self.partner.membership_line_ids.move_id,
        )


class TestAccountingWithProduct(TestAccounting, SavepointCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref("mozaik_membership.membership_product_first")


class TestAccountingWithProductWithAnotherAmount(TestAccounting, SavepointCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref("mozaik_membership.membership_product_first")

    def _generate_payment(self, additional_amount=0, with_partner=True):
        bs = super()._generate_payment(
            additional_amount=additional_amount, with_partner=with_partner
        )
        if with_partner and not additional_amount:
            bs.line_ids.amount = 7.0
            self.partner.membership_line_ids.write(
                {
                    "price": 7.0,
                }
            )
        return bs

    def test_accounting_manual_reconcile_without_partner(self):
        return


class TestAccountingPayTwice(TestAccounting, SavepointCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref("mozaik_membership.membership_product_first")

    def test_accounting_auto_reconcile(self):
        res = super().test_accounting_auto_reconcile()

        bank_s = self._generate_payment()
        bank_s.auto_reconcile()
        for bank_st in bank_s:
            for line in bank_st.line_ids:
                self.assertFalse(line.is_reconciled)
        return res

    def test_accounting_manual_reconcile(self):
        return


class TestAccountingNoProduct(TestAccounting, SavepointCase):
    def test_accounting_auto_reconcile(self):
        return


class TestAccountingGroupedPayment(TestAccounting, SavepointCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            "mozaik_membership.membership_product_live_together"
        )
        self.partner_2 = self._get_partner()

    def _get_manual_move_dict(self, additional_amount):
        property_obj = self.env["ir.property"]
        subscription_account = property_obj._get(
            "property_subscription_account", "product.template"
        )
        res = [
            {
                "account_id": subscription_account.id,
                "debit": 0,
                "credit": self.product.list_price,
                "name": self.partner.membership_line_ids.reference,
            },
            {
                "account_id": subscription_account.id,
                "debit": 0,
                "credit": additional_amount,
                "name": self.partner_2.membership_line_ids.reference,
            },
        ]
        return res

    def test_accounting_auto_reconcile(self):
        return

    def test_accounting_manual_reconcile_without_partner(self):
        return

    def test_accounting_manual_reconcile(self):
        additional_amount = self.product.list_price
        b_statement_id = self._generate_payment(additional_amount=additional_amount)
        instance = first(self.partner_2.int_instance_ids)
        partner2_ref = self.ml_obj._generate_membership_reference(
            self.partner_2, instance
        )
        values = self.partner_2.membership_line_ids._build_membership_values(
            self.partner_2, instance, self.member_state, product=self.product
        )
        values.update(
            {
                "reference": partner2_ref,
            }
        )
        self.partner_2.membership_line_ids.create(values)
        partner1_ref = self.partner.membership_line_ids.reference
        references = {
            self.partner.id: partner1_ref,
            self.partner_2.id: partner2_ref,
        }
        b_statement_id.auto_reconcile()
        for line in b_statement_id.line_ids:
            self.assertFalse(line.is_reconciled)

        move_dicts = self._get_manual_move_dict(additional_amount)

        b_statement_id.line_ids[0].process_reconciliation(new_aml_dicts=move_dicts)

        for partner in [self.partner, self.partner_2]:
            self.assertTrue(partner.membership_line_ids.paid)
            self.assertAlmostEqual(
                partner.membership_line_ids.price_paid, self.product.list_price
            )
            self.assertEqual(
                b_statement_id.line_ids.move_id,
                partner.membership_line_ids.move_id,
            )

            mv_lines = self.env["account.move.line"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("name", "=", references[partner.id]),
                    ("credit", "=", self.product.list_price),
                ]
            )
            self.assertEqual(len(mv_lines), 1)


class TestAccountingProtectAutoReconcile(TestAccounting, SavepointCase):
    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            "mozaik_membership.membership_product_live_together"
        )

    def test_accounting_auto_reconcile(self):
        """
        Auto reconcile should not occur if reference has been already
        used previously
        """
        b_statement_id = self._generate_payment()
        b_statement_id.auto_reconcile()
        for bank_s in b_statement_id:
            for line in bank_s.line_ids:
                self.assertTrue(line.is_reconciled)
        b_statement_id2 = b_statement_id.copy()
        b_statement_id2.line_ids.move_id.line_ids[
            1
        ].account_id = b_statement_id2.line_ids.journal_id.suspense_account_id
        b_statement_id2.auto_reconcile()
        for bank_s in b_statement_id2:
            for line in bank_s.line_ids:
                self.assertFalse(line.is_reconciled)

    def test_accounting_manual_reconcile(self):
        return

    def test_accounting_manual_reconcile_without_partner(self):
        return
