# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import uuid
from datetime import date
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm


class test_accounting_with_product(object):
    _data_files = (
        '../../l10n_ficep/data/account_template.xml',
        '../../l10n_ficep/data/account_chart_template.xml',
        '../../l10n_ficep/data/account_installer.xml',
    )

    _module_ns = 'ficep_membership'
    _account_wizard = 'pcmn_mozaik'
    _with_coda = False

    product = None
    bs_obj = None
    bsl_obj = None
    ml_obj = None
    partner_obj = None
    partner = None

    def setUp(self):
        super(test_accounting_with_product, self).setUp()
        wiz_id = self.ref('%s.%s' % (self._module_ns, self._account_wizard))
        self.registry('wizard.multi.charts.accounts').execute(self.cr,
                                                              self.uid,
                                                              [wiz_id])

        self.bs_obj = self.registry('account.bank.statement')
        self.bsl_obj = self.registry('account.bank.statement.line')
        self.ml_obj = self.registry('membership.line')
        self.partner_obj = self.registry('res.partner')
        self.partner = self.get_partner()
        self.assertEquals(self.partner.membership_state_id.code,
                          'without_membership',
                          'Create: should be "without_status"')
        self.partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        self.partner = self.get_partner(self.partner.id)
        self.assertEquals(self.partner.membership_state_id.code,
                          'member_candidate', 'Should be "member_candidate"')

    def get_partner(self, partner_id=False):
        """
        ==========
        get_partner
        ==========
        return a new browse record of partner
        """
        if not partner_id:
            name = uuid.uuid4()
            partner_values = {
                'name': name,
            }
            partner_id = self.partner_obj.create(self.cr, self.uid,
                                                 partner_values)
        # check each time the current state change
        return self.partner_obj.browse(self.cr, self.uid, partner_id)

    def _generate_payment(self, additional_amount=0, with_partner=True):
        wiz_obj = self.registry('generate.reference')
        wiz_id = wiz_obj.create(self.cr, self.uid, {}, context={
                                                    'active_ids':
                                                    [self.partner.id]})
        wiz_obj.generate_reference(self.cr, self.uid, wiz_id)
        self.partner = self.get_partner(self.partner.id)
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
                                            self.cr,
                                            self.uid,
                                            'property_subscription_account',
                                            'product.template')
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
                    })
        if additional_amount > 0:
            account = None
            if self.product:
                account = other_account
            else:
                account = subscription_account
            res.append({
                'account_id': account.id,
                'debit': 0,
                'credit': additional_amount})

        return res

    def test_accounting_auto_reconcile(self):
        b_statement_id = self._generate_payment()
        if not self._with_coda:
            self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)

        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id):
            for line in bank_s.line_ids:
                self.assertNotEqual(line.journal_entry_id, False)

        partner = self.get_partner(self.partner.id)
        self.assertEquals(partner.membership_state_id.code, 'member_committee',
                          'Should be "member_committee"')
        self.assertEquals(partner.subscription_product_id.id,
                          self.product.id,
                          'Wrong product affected')
        ml_data = self.ml_obj.search_read(self.cr,
                                    self.uid,
                                    [('partner_id', '=', partner.id),
                                     ('active', '=', True)],
                                    ['price'])[0]

        self.assertEqual(ml_data['price'], self.product.list_price,
                         'Wrong price specified')

    def test_accounting_manual_reconcile(self):
        additional_amount = 1999.99
        b_statement_id = self._generate_payment(
                                        additional_amount=additional_amount)
        self.bs_obj.auto_reconcile(self.cr, self.uid, b_statement_id)
        for bank_s in self.bs_obj.browse(self.cr, self.uid, b_statement_id):
            for line in bank_s.line_ids:
                self.assertFalse(line.journal_entry_id)

        move_dicts = self._get_manual_move_dict(additional_amount)

        self.bsl_obj.process_reconciliation(
            self.cr, self.uid, bank_s.line_ids[0].id, move_dicts)
        partner = self.get_partner(self.partner.id)
        self.assertEquals(partner.membership_state_id.code, 'member_committee',
                          'Should be "member_committee"')

        if not self.product:
            prod_id = self.ref('%s.membership_product_undefined'
                                  % self._module_ns)
        else:
            prod_id = self.product.id

        self.assertEquals(partner.subscription_product_id.id,
                          prod_id,
                          'Wrong product affected')

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
        self.product = self.browse_ref('%s.membership_product_first'
                                  % self._module_ns)
        super(test_accounting_first_membership_accepted, self).setUp()


class test_accounting_first_membership_refused (test_accounting_with_product,
                                                 SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref('%s.membership_product_first'
                                  % self._module_ns)
        super(test_accounting_first_membership_refused, self).setUp()

    def test_accounting_auto_reconcile(self):
        super(test_accounting_first_membership_refused,
              self).test_accounting_auto_reconcile()
        self.partner_obj.signal_workflow(self.cr, self.uid,
                                         [self.partner.id], 'accept')
        self.partner = self.get_partner(self.partner.id)
        self.assertEquals(self.partner.membership_state_id.code, 'member',
                          'Should be "member"')

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
        self.product = self.browse_ref('%s.membership_product_isolated'
                                  % self._module_ns)
        super(test_accounting_isolated, self).setUp()


class test_accounting_live_together (test_accounting_with_product,
                                                 SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref('%s.membership_product_live_together'
                                  % self._module_ns)
        super(test_accounting_live_together, self).setUp()


class test_accounting_other (test_accounting_with_product,
                                                 SharedSetupTransactionCase):

    def setUp(self):
        self.product = self.browse_ref('%s.membership_product_other'
                                  % self._module_ns)
        super(test_accounting_other, self).setUp()


class test_accounting_undefined(test_accounting_with_product,
                                                 SharedSetupTransactionCase):
    def setUp(self):
        super(test_accounting_undefined, self).setUp()

    def test_accounting_auto_reconcile(self):
        return
