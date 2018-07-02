# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import uuid
from datetime import date
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm


class test_accounting_with_product(object):
    _data_files = (
        '../../l10n_mozaik/data/account_template.xml',
        '../../l10n_mozaik/data/account_chart_template.xml',
        '../../l10n_mozaik/data/account_installer.xml',
    )

    _module_ns = 'mozaik_account'
    _account_wizard = 'pcmn_mozaik'
    _with_coda = False

    product = None
    bs_obj = None
    bsl_obj = None
    ml_obj = None
    partner_obj = None
    partner = None
    partner_2 = None

    def setUp(self):
        super(test_accounting_with_product, self).setUp()

        self.bs_obj = self.registry('account.bank.statement')
        self.bsl_obj = self.registry('account.bank.statement.line')
        self.ml_obj = self.registry('membership.line')
        self.partner_obj = self.registry('res.partner')
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
        partner_id = self.partner_obj.create(
            self.cr, self.uid, partner_values)
        return self.partner_obj.browse(self.cr, self.uid, partner_id)

    def _generate_payment(self, additional_amount=0, with_partner=True):
        pobj = self.partner_obj
        self.partner.reference = pobj._generate_membership_reference(
            self.cr, self.uid, self.partner.id)
        b_statement_id = self.bs_obj.create(self.cr,
                                            self.uid,
                                            {},
                                            context={'journal_type': 'bank'})
        amount = 0.0
        if self.product:
            amount = self.product.list_price
        amount += additional_amount
        statement_line_vals = {'statement_id': b_statement_id,
                               'name': self.partner.reference,
                               'amount': amount,
                               }
        if with_partner:
            statement_line_vals['partner_id'] = self.partner.id

        self.bsl_obj.create(self.cr, self.uid, statement_line_vals)

        return b_statement_id

    def _get_manual_move_dict(self, additional_amount):
        property_obj = self.registry('ir.property')
        res = []
        subscription_account = property_obj.get(
            self.cr, self.uid,
            'property_subscription_account', 'product.template')
        other_account = property_obj.get(
            self.cr,
            self.uid,
            'property_retrocession_cost_account',
            'mandate.category')
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
        b_statement_id = self._generate_payment()
        if not self._with_coda:
            self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)

        bank_s = self.bs_obj.browse(self.cr, self.uid, b_statement_id)
        for line in bank_s.line_ids:
            self.assertNotEqual(line.journal_entry_id.id, False)

        self.assertEqual(
            self.partner.membership_state_id.code, 'member_committee')
        self.assertEqual(
            self.partner.subscription_product_id.id, self.product.id)
        ml_data = self.ml_obj.search_read(
            self.cr, self.uid,
            [('partner_id', '=', self.partner.id), ('active', '=', True)],
            ['price'])[0]

        self.assertEqual(ml_data['price'], bank_s.line_ids.amount)
        self.assertFalse(self.partner.amount)

    def test_accounting_manual_reconcile(self):
        additional_amount = 1999.99
        b_statement_id = self._generate_payment(
            additional_amount=additional_amount)
        self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)
        bank_s = self.bs_obj.browse(self.cr, self.uid, b_statement_id)
        for line in bank_s.line_ids:
            self.assertFalse(line.journal_entry_id)

        move_dicts = self._get_manual_move_dict(additional_amount)

        self.bsl_obj.process_reconciliation(
            self.cr, self.uid, bank_s.line_ids[0].id, move_dicts)

        self.assertEqual(
            self.partner.membership_state_id.code, 'member_committee')

        if not self.product:
            prod_id = self.ref(
                'mozaik_membership.membership_product_undefined')
        else:
            prod_id = self.product.id

        self.assertEqual(
            self.partner.subscription_product_id.id, prod_id)

        ml_data = self.ml_obj.search_read(
            self.cr, self.uid,
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
        b_statement_id = self._generate_payment(
            additional_amount=additional_amount,
            with_partner=False)
        self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)
        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id):
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_id)

        move_dicts = self._get_manual_move_dict(additional_amount)

        self.assertRaises(orm.except_orm, self.bsl_obj.process_reconciliation,
                          self.cr, self.uid, bank_s.line_ids[0].id, move_dicts)


class test_accounting_first_membership_accepted (test_accounting_with_product,
                                                 SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_first')
        super(test_accounting_first_membership_accepted, self).setUp()


class test_accounting_first_membership_accepted_with_another_amount(
        test_accounting_with_product, SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_first')
        super(test_accounting_first_membership_accepted_with_another_amount,
              self).setUp()
        self.partner.amount = 7.0

    def _generate_payment(self, additional_amount=0, with_partner=True):
        b_statement_id = super(
            test_accounting_first_membership_accepted_with_another_amount,
            self)._generate_payment(
                additional_amount=additional_amount, with_partner=with_partner)
        if with_partner and not additional_amount:
            bs = self.bs_obj.browse(self.cr, self.uid, b_statement_id)
            bs.line_ids.amount = self.partner.amount
        return b_statement_id

    def test_accounting_manual_reconcile_without_partner(self):
        return


class test_accounting_first_membership_refused(
        test_accounting_with_product, SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_first')
        super(test_accounting_first_membership_refused, self).setUp()

    def test_accounting_auto_reconcile(self):
        super(test_accounting_first_membership_refused,
              self).test_accounting_auto_reconcile()
        self.partner_obj.signal_workflow(self.cr, self.uid,
                                         [self.partner.id], 'accept')
        self.assertEqual(self.partner.membership_state_id.code, 'member')

        b_statement_id = self._generate_payment()
        self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)
        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id):
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_id)

    def test_accounting_manual_reconcile(self):
        return


class test_accounting_isolated (test_accounting_with_product,
                                SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_isolated')
        super(test_accounting_isolated, self).setUp()


class test_accounting_live_together (test_accounting_with_product,
                                     SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_live_together')
        super(test_accounting_live_together, self).setUp()


class test_accounting_other (test_accounting_with_product,
                             SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_other')
        super(test_accounting_other, self).setUp()


class test_accounting_undefined(test_accounting_with_product,
                                SharedSetupTransactionCase):

    def setUp(self):
        super(test_accounting_undefined, self).setUp()

    def test_accounting_auto_reconcile(self):
        return


class test_accounting_grouped_payment(test_accounting_with_product,
                                      SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_live_together')
        super(test_accounting_grouped_payment, self).setUp()
        self.partner_2 = self._get_partner()
        self.partner_2.write({
            'accepted_date': date.today().strftime('%Y-%m-%d'),
            'free_member': False,
        })

    def _get_manual_move_dict(self, additional_amount):
        property_obj = self.registry('ir.property')
        res = []
        subscription_account = property_obj.get(
            self.cr,
            self.uid,
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
        pobj = self.partner_obj
        additional_amount = self.product.list_price
        b_statement_id = self._generate_payment(
            additional_amount=additional_amount)
        self.partner_2.reference = pobj._generate_membership_reference(
            self.cr, self.uid, self.partner_2.id)
        references = {self.partner.id: self.partner.reference,
                      self.partner_2.id: self.partner_2.reference}
        self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)
        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id):
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_id)

        move_dicts = self._get_manual_move_dict(additional_amount)

        self.bsl_obj.process_reconciliation(
            self.cr, self.uid, bank_s.line_ids[0].id, move_dicts)

        for partner in [self.partner, self.partner_2]:
            self.assertEqual(
                partner.membership_state_id.code, 'member_committee')

            if not self.product:
                prod_id = self.ref(
                    'mozaik_membership.membership_product_undefined')
            else:
                prod_id = self.product.id

            self.assertEqual(
                partner.subscription_product_id.id, prod_id)

            ml_data = self.ml_obj.search_read(self.cr,
                                              self.uid,
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

            mv_lines = self.registry('account.move.line').search(
                self.cr, self.uid, [('partner_id', '=', partner.id),
                                    ('name', '=', references[partner.id]),
                                    ('credit', '=', price)])
            self.assertEqual(len(mv_lines), 1,
                             'No account move lines created for partner')


class test_accounting_protect_auto_reconcile(test_accounting_with_product,
                                             SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref(
            'mozaik_membership.membership_product_live_together')
        super(test_accounting_protect_auto_reconcile, self).setUp()

    def test_accounting_auto_reconcile(self):
        '''
            Auto reconcile should not occur if reference has been already
            used previously
        '''
        b_statement_id = self._generate_payment()
        if not self._with_coda:
            self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)
        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id):
            for line in bank_s.line_ids:
                self.assertNotEqual(line.journal_entry_id.id, False)
        b_statement_id2 = self.bs_obj.copy(self.cr, self.uid, b_statement_id)
        self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id2)
        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id2):
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_id.id)

    def test_accounting_manual_reconcile(self):
        return

    def test_accounting_manual_reconcile_without_partner(self):
        return
