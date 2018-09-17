# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid
import random
from datetime import date
from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError
from odoo.fields import first


class TestAccountingWithProduct(object):

    product = None
    bs_obj = None
    bsl_obj = None
    ml_obj = None
    partner_obj = None
    partner = None
    partner_2 = None

    def setUp(self):
        super().setUp()

        self.bs_obj = self.env['account.bank.statement']
        self.bsl_obj = self.env['account.bank.statement.line']
        self.ml_obj = self.env['membership.line']
        self.partner_obj = self.env['res.partner']
        self.partner = self._get_partner()
        self.partner.write({
            'accepted_date': date.today().strftime('%Y-%m-%d'),
            'free_member': False,
        })

    def _get_partner(self):
        """
        return a new browse record of partner
        """
        name = uuid.uuid4()
        partner_values = {
            'lastname': name,
        }
        partner = self.partner_obj.create(partner_values)
        partner.member_candidate()
        return partner

    def _generate_payment(self, additional_amount=0, with_partner=True):
        instance = first(self.partner.int_instance_ids)
        reference = self.partner._generate_membership_reference(instance)
        b_statement_id = self.bs_obj.with_context(
            journal_type='bank').create({})
        if self.product:
            amount = self.product.list_price
        else:
            amount = random.uniform(10, 100)
        if not self.partner.membership_line_ids.filtered(
                lambda l: l.reference == reference):
            values = self.partner.membership_line_ids._build_membership_values(
                self.partner, instance, price=amount, product=self.product)
            values.update({
                'reference': reference,
            })
            self.partner.membership_line_ids.create(values)
        amount += additional_amount
        statement_line_vals = {
            'statement_id': b_statement_id.id,
            'name': reference,
            'amount': amount,
        }
        if with_partner:
            statement_line_vals['partner_id'] = self.partner.id

        self.bsl_obj.create(statement_line_vals)

        return b_statement_id

    def _get_manual_move_dict(self, additional_amount):
        property_obj = self.env['ir.property']
        res = []
        subscription_account = property_obj.get(
            'property_subscription_account', 'product.template')
        other_account = self.env["account.account"].search(
            [("id", "not in", subscription_account.ids)], limit=1)
        reference = self.partner.membership_line_ids.reference
        if self.product:
            if self.product.list_price > 0:
                res.append({
                    'account_id': subscription_account.id,
                    'debit': 0,
                    'credit': self.product.list_price,
                    'name': reference
                })
        if additional_amount > 0:
            if self.product:
                account = other_account
                name = 'Comment'
            else:
                account = subscription_account
                name = reference

            res.append({
                'account_id': account.id,
                'debit': 0,
                'credit': additional_amount,
                'name': name})

        return res

    def test_accounting_auto_reconcile(self):
        bank_s = self._generate_payment()
        bank_s.auto_reconcile()

        for line in bank_s.line_ids:
            self.assertTrue(line.journal_entry_ids)

        self.assertEqual(
            self.partner.membership_state_id.code, 'member_committee')
        ml_data = self.ml_obj.search([
            ('partner_id', '=', self.partner.id),
            ('active', '=', True),
        ], limit=1)

        self.assertAlmostEqual(ml_data.price, bank_s.line_ids.amount)
        self.assertTrue(ml_data.paid)

    def test_accounting_manual_reconcile(self):
        additional_amount = 1999.99
        if not self.product:
            prod_id = self.env['membership.line']._get_subscription_product(
                partner=self.partner,
                instance=first(self.partner.int_instance_ids))
        else:
            prod_id = self.product
        bank_s = self._generate_payment(
            additional_amount=additional_amount)
        price = self.partner.membership_line_ids.price
        bank_s.auto_reconcile()
        for line in bank_s.line_ids:
            self.assertFalse(line.journal_entry_ids)

        move_dicts = self._get_manual_move_dict(additional_amount)

        first(bank_s.line_ids).process_reconciliation(
            new_aml_dicts=move_dicts)

        self.assertEqual(
            self.partner.membership_state_id.code, 'member_committee')

        self.assertEqual(self.partner.membership_line_ids.product_id, prod_id)

        ml_data = self.ml_obj.search([
            ('partner_id', '=', self.partner.id),
            ('active', '=', True),
        ], limit=1)

        self.assertAlmostEqual(ml_data.price, price)
        self.assertTrue(ml_data.paid)

    def test_accounting_manual_reconcile_without_partner(self):
        additional_amount = 1999.99
        bank_s = self._generate_payment(
            additional_amount=additional_amount,
            with_partner=False)
        bank_s.auto_reconcile()
        for bank_st in bank_s:
            for line in bank_st.line_ids:
                self.assertFalse(line.journal_entry_ids)

        move_dicts = self._get_manual_move_dict(additional_amount)
        with self.assertRaises(ValidationError):
            first(bank_s.line_ids).process_reconciliation(
                new_aml_dicts=move_dicts)


class TestAccountingFirstMembershipAccepted(TestAccountingWithProduct,
                                            SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_first')


class TestAccountingFirstMembershipAcceptedWithAnotherAmount(
        TestAccountingWithProduct, SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_first')
        self.partner.amount = 7.0

    def _generate_payment(self, additional_amount=0, with_partner=True):
        bs = super()._generate_payment(
            additional_amount=additional_amount, with_partner=with_partner)
        if with_partner and not additional_amount:
            bs.line_ids.amount = self.partner.amount
            self.partner.membership_line_ids.write({
                'price': self.partner.amount,
            })
        return bs

    def test_accounting_manual_reconcile_without_partner(self):
        return


class TestAccountingFirstMembershipRefused(TestAccountingWithProduct,
                                           SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_first')

    def test_accounting_auto_reconcile(self):
        res = super().test_accounting_auto_reconcile()
        self.partner.accept()
        self.assertEqual(self.partner.membership_state_id.code, 'member')

        bank_s = self._generate_payment()
        bank_s.auto_reconcile()
        for bank_st in bank_s:
            for line in bank_st.line_ids:
                self.assertFalse(line.journal_entry_ids)
        return res

    def test_accounting_manual_reconcile(self):
        return


class TestAccountingIsolated(TestAccountingWithProduct, SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_isolated')


class TestAccountingLiveTogether(TestAccountingWithProduct,
                                 SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_live_together')


class TestAccountingOther(TestAccountingWithProduct, SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_other')


class TestAccountingUndefined(TestAccountingWithProduct, SavepointCase):

    def test_accounting_auto_reconcile(self):
        return


class TestAccountingGroupedPayment(TestAccountingWithProduct,
                                   SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_live_together')
        self.partner_2 = self._get_partner()
        self.partner_2.write({
            'accepted_date': date.today().strftime('%Y-%m-%d'),
            'free_member': False,
        })

    def _get_manual_move_dict(self, additional_amount):
        property_obj = self.env['ir.property']
        res = []
        subscription_account = property_obj.get(
            'property_subscription_account',
            'product.template')
        if self.product:
            if self.partner.membership_line_ids.price > 0:
                res.append({
                    'account_id': subscription_account.id,
                    'debit': 0,
                    'credit': self.partner.membership_line_ids.price,
                    'name': self.partner.membership_line_ids.reference
                })

        if additional_amount > 0:
            if self.partner.membership_line_ids.price > 0:
                res.append({
                    'account_id': subscription_account.id,
                    'debit': 0,
                    'credit': self.partner_2.membership_line_ids.price,
                    'name': self.partner_2.membership_line_ids.reference
                })
        return res

    def test_accounting_auto_reconcile(self):
        return

    def test_accounting_manual_reconcile_without_partner(self):
        return

    def test_accounting_manual_reconcile(self):
        additional_amount = self.product.list_price
        b_statement_id = self._generate_payment(
            additional_amount=additional_amount)
        instance = first(self.partner_2.int_instance_ids)
        partner2_ref = self.partner_2._generate_membership_reference(
            instance=instance)
        values = self.partner_2.membership_line_ids._build_membership_values(
            self.partner_2, instance, price=additional_amount,
            product=self.product)
        values.update({
            'reference': partner2_ref,
        })
        self.partner_2.membership_line_ids.create(values)
        partner1_ref = self.partner.membership_line_ids.reference
        references = {
            self.partner.id: partner1_ref,
            self.partner_2.id: partner2_ref,
        }
        b_statement_id.auto_reconcile()
        for bank_s in b_statement_id:
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_ids)

        move_dicts = self._get_manual_move_dict(additional_amount)

        b_statement_id.line_ids[0].process_reconciliation(
            new_aml_dicts=move_dicts)

        for partner in [self.partner, self.partner_2]:
            self.assertEqual(
                partner.membership_state_id.code, 'member_committee')

            if not self.product:
                prod_id = self.env.ref(
                    'mozaik_membership.membership_product_undefined')
            else:
                prod_id = self.product

            self.assertEqual(
                partner.membership_line_ids.product_id, prod_id)

            ml_data = self.ml_obj.search_read(
                [('partner_id', '=', partner.id),
                 ('active', '=', True)],
                ['price'])[0]
            if self.product:
                price = partner.membership_line_ids.price
            else:
                price = additional_amount

            self.assertEqual(ml_data['price'], price,
                             'Wrong price specified')

            mv_lines = self.env['account.move.line'].search(
                [('partner_id', '=', partner.id),
                 ('name', '=', references[partner.id]),
                 ('credit', '=', price)])
            self.assertEqual(len(mv_lines), 1,
                             'No account move lines created for partner')


class TestAccountingProtectAutoReconcile(TestAccountingWithProduct,
                                         SavepointCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_live_together')

    def test_accounting_auto_reconcile(self):
        '''
        Auto reconcile should not occur if reference has been already
        used previously
        '''
        b_statement_id = self._generate_payment()
        b_statement_id.auto_reconcile()
        for bank_s in b_statement_id:
            for line in bank_s.line_ids:
                self.assertTrue(line.journal_entry_ids)
        b_statement_id2 = b_statement_id.copy()
        b_statement_id2.auto_reconcile()
        for bank_s in b_statement_id2:
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_ids)

    def test_accounting_manual_reconcile(self):
        return

    def test_accounting_manual_reconcile_without_partner(self):
        return
