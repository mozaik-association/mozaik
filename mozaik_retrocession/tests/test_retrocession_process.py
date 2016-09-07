# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_retrocession, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_retrocession is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_retrocession is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_retrocession.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from dateutil.relativedelta import relativedelta
from datetime import datetime
import logging
from anybox.testing.openerp import SharedSetupTransactionCase

_logger = logging.getLogger(__name__)


class test_retrocession_with_accounting(object):

    _data_files = (
        '../../l10n_mozaik/data/account_template.xml',
        '../../l10n_mozaik/data/account_chart_template.xml',
        '../../l10n_mozaik/data/account_installer.xml',
        '../../mozaik_base/tests/data/res_partner_data.xml',
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_mandate/tests/data/mandate_data.xml',
        'data/retrocession_data.xml',
    )

    _module_ns = 'mozaik_retrocession'

    def setUp(self):
        super(test_retrocession_with_accounting, self).setUp()
        self.year = (datetime.today() - relativedelta(years=1)).strftime('%Y')
        wiz_id = self.ref('%s.pcmn_mozaik' % self._module_ns)
        self.registry('wizard.multi.charts.accounts').auto_execute(
            self.cr, self.uid, [wiz_id])
        self.registry('retrocession.helper').create_fiscal_year(
            self.cr, self.uid, self.year)
        # members to instanciate by real test
        self.retro = None

    def test_retrocession_process(self):
        '''
            Test retrocessions
        '''
        rule_pool = self.registry('calculation.rule')
        retro_pool = self.registry('retrocession')

        fixed_rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('retrocession_id', '=', self.retro.id),
                ('type', '=', 'fixed'),
                ('is_deductible', '=', False)])
        variable_rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('retrocession_id', '=', self.retro.id),
                ('type', '=', 'variable'),
                ('is_deductible', '=', False)])
        deductible_rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('retrocession_id', '=', self.retro.id),
                ('type', '=', 'variable'),
                ('is_deductible', '=', True)])

        # Check if fixed rules have been copied from mandate to retrocession
        self.assertEqual(len(fixed_rule_ids), 2)

        # Check if variable rules have been copied from method to retrocession
        rule_ids = rule_pool.search(
            self.cr, self.uid, [
                ('retrocession_id', '=', self.retro.id),
                ('type', '=', 'variable')])
        self.assertEqual(len(rule_ids), 2)

        # Setting some amounts on fixed rules should invoke retrocession
        # calculation
        rule_pool.write(self.cr, self.uid, fixed_rule_ids, {'amount': 100})
        amounts = retro_pool.read(
            self.cr, self.uid, self.retro.id, [
                'amount_retrocession', 'amount_total'])
        self.assertEqual(amounts['amount_retrocession'], 3.40)
        self.assertEqual(amounts['amount_total'], 3.40)

        # Setting some amounts on variable rules should invoke retrocession
        # calculation
        rule_pool.write(self.cr, self.uid, variable_rule_ids, {'amount': 100})
        amounts = retro_pool.read(
            self.cr, self.uid, self.retro.id, [
                'amount_retrocession', 'amount_total'])
        self.assertEqual(amounts['amount_retrocession'], 4.15)
        self.assertEqual(amounts['amount_total'], 4.15)

        # Setting some amounts on deductible rules should invoke retrocession
        # calculation
        rule_pool.write(self.cr, self.uid, deductible_rule_ids, {'amount': 1})
        amounts = retro_pool.read(
            self.cr, self.uid, self.retro.id, [
                'amount_retrocession', 'amount_deduction', 'amount_total'])
        self.assertEqual(amounts['amount_retrocession'], 4.15)
        self.assertEqual(amounts['amount_deduction'], -1)
        self.assertEqual(amounts['amount_total'], 3.15)

        # Changing percentage of fixed rules should affect retrocession
        # computation
        rule_pool.write(
            self.cr, self.uid, fixed_rule_ids, {'percentage': 0.25})
        amounts = retro_pool.read(
            self.cr, self.uid, self.retro.id, [
                'amount_retrocession', 'amount_deduction', 'amount_total'])
        self.assertEqual(amounts['amount_retrocession'], 1.25)
        self.assertEqual(amounts['amount_deduction'], -1)
        self.assertEqual(amounts['amount_total'], 0.25)

        # Changing percentage of variable rules should affect retrocession
        # computation
        rule_pool.write(
            self.cr, self.uid, deductible_rule_ids, {
                'percentage': 5})
        amounts = retro_pool.read(self.cr,
                                  self.uid,
                                  self.retro.id,
                                  ['amount_retrocession',
                                   'amount_deduction',
                                   'amount_total',
                                   'amount_reconcilied'])
        self.assertEqual(amounts['amount_retrocession'], 1.25)
        self.assertEqual(amounts['amount_deduction'], -0.05)
        self.assertEqual(amounts['amount_total'], 1.20)
        self.assertEqual(amounts['amount_reconcilied'], 0.00)

        # Validating retrocession
        retro_pool.action_validate(self.cr, self.uid, [self.retro.id])
        retro_state = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['state'])['state']
        self.assertEqual(retro_state, 'validated')

        # Account move should exist
        move_id = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['move_id'])['move_id']
        self.assertNotEqual(move_id, False)

        # Account move should have 3 lines
        line_ids = self.registry('account.move.line').search(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0])])
        self.assertEqual(len(line_ids), 3)

        # Analyse lines generated
        lines = self.registry('account.move.line').search_read(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0]),
                ('account_id', '=', self.retro.default_debit_account.id)],
            fields=[
                'debit', 'credit', 'name'])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['credit'], 0)
        self.assertEqual(lines[0]['debit'], 0.05)
        self.assertEqual(lines[0]['name'], self.retro.unique_id)

        lines = self.registry('account.move.line').search_read(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0]),
                ('account_id', '=', self.retro.default_credit_account.id)],
            fields=[
                'debit', 'credit', 'name'])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['credit'], 1.25)
        self.assertEqual(lines[0]['debit'], 0)
        self.assertEqual(lines[0]['name'], self.retro.unique_id)

        default_debit_account_id = self.registry(
            'account.journal').search_read(
            self.cr, self.uid, [
                ('code', '=', 'RETRO')],
            fields=['default_debit_account_id'])[0]['default_debit_account_id']
        lines = self.registry('account.move.line').search_read(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0]),
                ('account_id', '=', default_debit_account_id[0])],
            fields=[
                'debit', 'credit', 'name'])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['credit'], 0)
        self.assertEqual(lines[0]['debit'], 1.20)
        self.assertEqual(lines[0]['name'], self.retro.unique_id)

        # Reset retrocession
        retro_pool.action_revalidate(self.cr, self.uid, [self.retro.id])
        retro_state = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['state'])['state']
        self.assertEqual(retro_state, 'draft')

        # Account move lines should have been unlinked
        line_ids = self.registry('account.move.line').search(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0])])
        self.assertEqual(len(line_ids), 0)

        # Account move should have been unlinked
        move_id = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['move_id'])['move_id']
        self.assertFalse(move_id)

        # Validating retrocession again
        retro_pool.action_validate(self.cr, self.uid, [self.retro.id])
        retro_state = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['state'])['state']
        self.assertEqual(retro_state, 'validated')

        # Creating bank statement for retrocession
        b_statement_id = self.registry('account.bank.statement').create(
            self.cr, self.uid, {
                'name': (
                    '/%s' %
                    self.retro.unique_id)}, context={
                'journal_type': 'bank'})

        statement_line_vals = {
            'statement_id': b_statement_id,
            'name': self.retro.sta_mandate_id.reference if
            self.retro.sta_mandate_id else self.retro.ext_mandate_id.reference,
            'amount': 1.20,
            'partner_id': self.retro.partner_id.id,
            'ref': self.retro.unique_id,
        }
        self.registry('account.bank.statement.line').create(
            self.cr, self.uid, statement_line_vals)

        # Check provision computation
        if self.retro.retrocession_mode == 'year':
            provision = retro_pool.read(
                self.cr,
                self.uid,
                self.retro.id,
                ['provision'])['provision']
            self.assertEqual(provision, 1.20)

        # Reconcile statement
        self.registry('account.bank.statement').auto_reconcile(
            self.cr,
            self.uid,
            b_statement_id)
        data = retro_pool.read(
            self.cr, self.uid, self.retro.id, [
                'amount_reconcilied', 'state'])
        self.assertEqual(data['amount_reconcilied'], 1.20)
        self.assertEqual(data['state'], 'done')

    def test_negative_retrocession(self):
        rule_pool = self.registry('calculation.rule')
        retro_pool = self.registry('retrocession')

        vals = {'retrocession_id': self.retro.id,
                'type': 'fixed',
                'is_deductible': False,
                'name': 'Test',
                'percentage': -100,
                'amount': 45,
                }
        rule_pool.create(self.cr, self.uid, vals)

        # Validating retrocession
        retro_pool.action_validate(self.cr, self.uid, [self.retro.id])
        retro_state = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['state'])['state']
        self.assertEqual(retro_state, 'validated')

        # Account move should exist
        move_id = retro_pool.read(
            self.cr,
            self.uid,
            self.retro.id,
            ['move_id'])['move_id']
        self.assertTrue(move_id)

        # Account move should have 2 lines
        line_ids = self.registry('account.move.line').search(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0])])
        self.assertEqual(len(line_ids), 2)

        # Analyse lines generated
        lines = self.registry('account.move.line').search_read(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0]),
                ('account_id', '=', self.retro.default_credit_account.id)],
            fields=[
                'debit', 'credit', 'name'])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['credit'], 0)
        self.assertEqual(lines[0]['debit'], 45)
        self.assertEqual(lines[0]['name'], self.retro.unique_id)

        default_debit_account_id = self.registry(
            'account.journal').search_read(
            self.cr, self.uid, [
                ('code', '=', 'RETRO')],
            fields=['default_debit_account_id'])[0]['default_debit_account_id']
        lines = self.registry('account.move.line').search_read(
            self.cr, self.uid, [
                ('move_id', '=', move_id[0]),
                ('account_id', '=', default_debit_account_id[0])],
            fields=[
                'debit', 'credit', 'name'])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0]['credit'], 45)
        self.assertEqual(lines[0]['debit'], 0)
        self.assertEqual(lines[0]['name'], self.retro.unique_id)

        #  Creating bank statement for retrocession
        b_statement_id = self.registry('account.bank.statement').create(
            self.cr, self.uid, {
                'name': (
                    '/%s' %
                    self.retro.unique_id)}, context={
                'journal_type': 'bank'})
        statement_line_vals = {
            'statement_id': b_statement_id,
            'name': self.retro.sta_mandate_id.reference if
            self.retro.sta_mandate_id else
            self.retro.ext_mandate_id.reference,
            'amount': -
            45,
            'partner_id': self.retro.partner_id.id,
            'ref': self.retro.unique_id,
        }
        self.registry('account.bank.statement.line').create(
            self.cr,
            self.uid,
            statement_line_vals)

        # Reconcile statement
        self.registry('account.bank.statement').auto_reconcile(
            self.cr,
            self.uid,
            b_statement_id)
        data = retro_pool.read(
            self.cr, self.uid, self.retro.id, [
                'amount_reconcilied', 'state'])
        self.assertEqual(data['amount_reconcilied'], -45)
        self.assertEqual(data['state'], 'done')


class test_retrocession_ext_mandate_process(
        test_retrocession_with_accounting,
        SharedSetupTransactionCase):

    def setUp(self):
        super(test_retrocession_ext_mandate_process, self).setUp()

        self.retro = self.browse_ref(
            '%s.retro_jacques_ag_mai_20xx' % self._module_ns)

    def test_negative_retrocession(self):
        return


class test_retrocession_sta_mandate_process(
        test_retrocession_with_accounting,
        SharedSetupTransactionCase):

    def setUp(self):
        super(test_retrocession_sta_mandate_process, self).setUp()

        self.retro = self.browse_ref(
            '%s.retro_jacques_bourg_20xx' % self._module_ns)

    def test_negative_retrocession(self):
        return


class test_retrocession_ext_mandate_negative_process(
        test_retrocession_with_accounting,
        SharedSetupTransactionCase):

    def setUp(self):
        super(test_retrocession_ext_mandate_negative_process, self).setUp()

        self.retro = self.browse_ref(
            '%s.retro_paul_december_20xx' % self._module_ns)

    def test_retrocession_process(self):
        return
