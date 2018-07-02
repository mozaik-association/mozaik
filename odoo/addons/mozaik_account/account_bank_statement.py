# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_account, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_account is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_account is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_account.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import orm
from openerp.tools.translate import _

from openerp import api


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def _reconcile_statement_line(self, cr, uid, bank_line, reference,
                                  context=None):
        """
        Method to auto reconcile all bank statement lines related to
        retrocession
        """
        bsl_obj = self.pool.get('account.bank.statement.line')
        ret = bsl_obj.get_reconciliation_proposition(
            cr, uid, bank_line, context=context)
        if ret:
            move_line = ret[0]
        else:
            return

        if reference != move_line['ref']:
            return

        if move_line['debit'] == bank_line.amount \
           or move_line['credit'] == -bank_line.amount:
            move_dicts = [{
                'counterpart_move_line_id': move_line['id'],
                'debit': move_line['credit'],
                'credit': move_line['debit'],
            }]
            bsl_obj.process_reconciliation(
                cr, uid, bank_line.id, move_dicts, context=context)

    def _create_membership_move(self, cr, uid, bank_line, reference,
                                context=None):
        """
        Method to create account move linked to membership payment
        """
        bsl_obj = self.pool.get('account.bank.statement.line')
        line_count = bsl_obj.search_count(cr, uid, [('id', '!=', bank_line.id),
                                                    ('name', '=', reference)],
                                          context=context)
        if line_count > 0:
            # do not auto reconcile if reference has been used previously
            return
        pobj = self.pool.get('res.partner')
        product_id, credit_account = pobj._get_membership_prod_info(
            cr, uid, bank_line.partner_id.id, bank_line.amount, reference,
            context=context)

        if credit_account:
            move_dicts = [{
                'account_id': credit_account.id,
                'debit': 0,
                'credit': bank_line.amount,
                'name': reference,
            }]
            bsl_obj.process_reconciliation(
                cr, uid, bank_line.id, move_dicts, context=context,
                prod_id=product_id)


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    @api.cr_uid_id_context
    def process_reconciliation(self, cr, uid, line_id, mv_line_dicts,
                               context=None, prod_id=None):

        bank_line = self.browse(cr, uid, line_id, context=context)
        if not bank_line.partner_id.id:
            raise orm.except_orm(_('No Partner Defined!'),
                                 _("You must first select a partner!"))

        for line in mv_line_dicts:
            mode, partner_id = self._get_info_from_reference(
                cr, uid, line.get('name', False), context=context)[0:2]
            if mode == "membership" and partner_id:
                line['partner_id'] = partner_id

        super(account_bank_statement_line, self).process_reconciliation(
            cr, uid, line_id, mv_line_dicts, context=context)

        for data in mv_line_dicts:
            self._propagate_payment(
                cr, uid, [line_id], prod_id, data['credit'],
                data.get('name', False), context=context)
