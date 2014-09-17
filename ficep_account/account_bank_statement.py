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
from openerp.osv import orm


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def _check_first_membership(self, cr, uid, partner_id, reference,
                                context=None):
        modeldata_obj = self.pool.get('ir.model.data')
        ml_obj = self.pool.get('membership.membership_line')
        first_id = modeldata_obj.get_object_reference(cr,
                                                    uid,
                                                    'ficep_membership',
                                                    'member_candidate')

        domain = [('partner', '=', partner_id),
                  ('date_to', '=', False),
                  ('reference', '=', reference)
                  ('active', '=', True),
                  ('membership_state_id', '=', first_id)]

        ml_ids = ml_obj.search(cr, uid, domain, context=context)

        return len(ml_ids) == 1

    def _reconcile_statement_line(self, cr, uid, bank_line, context=None):
        """
        Method to auto reconcile all bank statement lines related to
        retrocession
        """
        bsl_obj = self.pool.get('account.bank.statement.line')
        ret = bsl_obj.get_reconciliation_proposition(cr,
                                                     uid,
                                                     bank_line,
                                                     context=context)
        if ret:
            move_line = ret[0]
        else:
            return

        if bank_line.name != move_line['ref']:
            return

        if move_line['debit'] == bank_line.amount:
            move_dicts = [{'counterpart_move_line_id': move_line['id'],
                           'debit': move_line['credit'],
                           'credit': move_line['debit'],
                          }]
            bsl_obj.process_reconciliation(cr,
                                           uid,
                                           bank_line.id,
                                           move_dicts,
                                           context=context)

    def _create_membership_move(self, cr, uid, bank_line, context=None):
        """
        Method to create account move linked to membership payment
        """
        bsl_obj = self.pool.get('account.bank.statement.line')
        prod_obj = self.pool.get('product.product')
        modeldata_obj = self.pool.get('ir.model.data')
        partner_obj = self.pool.get('res.partner')
        first_id = modeldata_obj.get_object_reference(cr,
                                                    uid,
                                                    'ficep_membership',
                                                    'membership_product_first')

        domain = [('membership', '=', True),
                  ('list_price', '>', 0)]
        prod_ids = prod_obj.search(cr, uid, domain, context=context)

        credit_account = False
        product_id = False
        for prod in prod_obj.browse(cr, uid, prod_ids, context=context):
            if prod.list_price == bank_line.amount:
                if prod.id == first_id:
                    if not self._check_first_membership(
                            cr, uid, bank_line.partner_id.id, bank_line.name,
                            context=context):
                        continue
                credit_account = prod.property_subscription_account
                product_id = prod.id
                break

        if credit_account:
            move_dicts = [{
                'account_id': credit_account.id,
                'debit': 0,
                'credit': bank_line.amount,
            }]
            bsl_obj.process_reconciliation(
                cr, uid, bank_line.id, move_dicts, context=context)
            partner_obj.signal_workflow(
                cr, uid, [bank_line.partner_id.id], 'paid')
            vals = {
                'subscription_product_id': product_id,
            }
            partner_obj.write(
                cr, uid, vals, context=context)

    def auto_reconcile(self, cr, uid, ids, context=None):
        for bank_s in self.browse(cr, uid, ids, context=context):
            for bank_line in bank_s.line_ids:
                is_retrocession = bank_line.name.startswith('+++8')
                is_membership = bank_line.name.startswith('+++9')

                if not bank_line.partner_id:
                    continue

                if is_retrocession:
                    self._reconcile_statement_line(cr, uid, bank_line,
                                                   context=context)
                elif is_membership:
                    self._create_membership_move(cr, uid, bank_line,
                                                 context=context)
