# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import uuid
from datetime import date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


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
        self.partner.reference = self.partner._generate_membership_reference()
        b_statement_id = self.bs_obj.with_context(journal_type='bank')\
            .create({})
        amount = 0.0
        if self.product:
            amount = self.product.list_price
        amount += additional_amount
        statement_line_vals = {'statement_id': b_statement_id.id,
                               'name': self.partner.reference,
                               'amount': amount}
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
        if self.product:
            if self.product.list_price > 0:
                res.append({
                    'account_id': subscription_account.id,
                    'debit': 0,
                    'credit': self.product.list_price,
                    'name': self.partner.reference
                })
        if additional_amount > 0:
            account = None
            if self.product:
                account = other_account
                name = 'Comment'
            else:
                account = subscription_account
                name = self.partner.reference

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
        self.assertEqual(
            self.partner.subscription_product_id, self.product)
        ml_data = self.ml_obj.search_read(
            [('partner_id', '=', self.partner.id), ('active', '=', True)],
            ['price'])[0]

        self.assertEqual(ml_data['price'], bank_s.line_ids.amount)
        self.assertFalse(self.partner.amount)

    def test_accounting_manual_reconcile(self):
        additional_amount = 1999.99
        bank_s = self._generate_payment(
            additional_amount=additional_amount)
        bank_s.auto_reconcile()
        for line in bank_s.line_ids:
            self.assertFalse(line.journal_entry_ids)

        move_dicts = self._get_manual_move_dict(additional_amount)

        bank_s.line_ids[0].process_reconciliation(
            new_aml_dicts=move_dicts)

        self.assertEqual(
            self.partner.membership_state_id.code, 'member_committee')

        if not self.product:
            prod_id = self.env.ref(
                'mozaik_membership.membership_product_undefined')
        else:
            prod_id = self.product

        self.assertEqual(
            self.partner.subscription_product_id, prod_id)

        ml_data = self.ml_obj.search_read(
            [('partner_id', '=', self.partner.id), ('active', '=', True)],
            ['price'])[0]
        price = 0.0
        if self.product:
            price = self.product.list_price
        else:
            price = additional_amount

        self.assertEqual(ml_data['price'], price)
        self.assertFalse(self.partner.amount)

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

        self.assertRaises(ValidationError,
                          bank_s.line_ids[0].process_reconciliation,
                          new_aml_dicts=move_dicts)


class TestAccountingFirstMembershipAccepted(TestAccountingWithProduct,
                                            TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_first')


class TestAccountingFirstMembershipAcceptedWithAnotherAmount(
        TestAccountingWithProduct, TransactionCase):

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
        return bs

    def test_accounting_manual_reconcile_without_partner(self):
        return


class TestAccountingFirstMembershipRefused(TestAccountingWithProduct,
                                           TransactionCase):

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


class TestAccountingIsolated(TestAccountingWithProduct, TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_isolated')


class TestAccountingLiveTogether(TestAccountingWithProduct,
                                 TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_live_together')


class TestAccountingOther(TestAccountingWithProduct, TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env.ref(
            'mozaik_membership.membership_product_other')


class TestAccountingUndefined(TestAccountingWithProduct, TransactionCase):

    def test_accounting_auto_reconcile(self):
        return


class TestAccountingGroupedPayment(TestAccountingWithProduct,
                                   TransactionCase):

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
            if self.product.list_price > 0:
                res.append({
                    'account_id': subscription_account.id,
                    'debit': 0,
                    'credit': self.product.list_price,
                    'name': self.partner.reference
                })

        if additional_amount > 0:
            if self.product.list_price > 0:
                res.append({
                    'account_id': subscription_account.id,
                    'debit': 0,
                    'credit': self.product.list_price,
                    'name': self.partner_2.reference
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
        self.partner_2.reference = self.partner_2\
            ._generate_membership_reference()
        references = {self.partner.id: self.partner.reference,
                      self.partner_2.id: self.partner_2.reference}
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
                partner.subscription_product_id, prod_id)

            ml_data = self.ml_obj.search_read(
                [('partner_id', '=', partner.id),
                 ('active', '=', True)],
                ['price'])[0]
            price = 0.0
            if self.product:
                price = self.product.list_price
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
                                         TransactionCase):

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
