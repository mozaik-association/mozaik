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
        product_id, price, credit_account = pobj._get_membership_prod_info(
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
                prod_id=product_id, price=price)

    def auto_reconcile(self, cr, uid, ids, context=None):
        bsl_obj = self.pool.get('account.bank.statement.line')
        for bank_s in self.browse(cr, uid, ids, context=context):
            for bank_line in bank_s.line_ids:
                if not bank_line.partner_id or bank_line.journal_entry_id.id:
                    continue

                mode, _, reference = bsl_obj.search_partner_id_with_reference(
                    cr, uid, bank_line.name, context=context)

                if mode == 'membership':
                    self._create_membership_move(
                        cr, uid, bank_line, reference, context=context)
                elif mode == 'retrocession':
                    self._reconcile_statement_line(
                        cr, uid, bank_line, reference, context=context)


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    def process_reconciliation(self, cr, uid, line_id, mv_line_dicts,
                               context=None, prod_id=None, price=None):

        bank_line = self.browse(cr, uid, line_id, context=context)
        for line in mv_line_dicts:
            mode, partner_id = self.search_partner_id_with_reference(
                cr, uid, line.get('name', False), context=context)[0:2]
            if mode == "membership" and partner_id:
                line['partner_id'] = partner_id

        if not bank_line.partner_id.id:
            raise orm.except_orm(_('No Partner Defined!'),
                                 _("You must first select a partner!"))
        super(account_bank_statement_line, self).process_reconciliation(
            cr, uid, line_id, mv_line_dicts, context=context)

        for data in mv_line_dicts:
            self.manage_membership_payment(cr,
                                           uid,
                                           bank_line.partner_id.id,
                                           data.get('name', False),
                                           prod_id,
                                           data['credit'],
                                           context)

    def manage_membership_payment(self, cr, uid, partner_id,
                                  reference, prod_id, amount_paid,
                                  context=None):
        context = context or {}
        ml_obj = self.pool.get('membership.line')
        mdata_obj = self.pool.get('ir.model.data')
        partner_obj = self.pool.get('res.partner')

        mode, partner_id, reference = self.search_partner_id_with_reference(
            cr, uid, reference, context=context)

        if mode != 'membership':
            return

        price = amount_paid
        if not prod_id:
            res = partner_obj._get_membership_prod_info(
                cr, uid, partner_id, amount_paid, reference, context=context)
            prod_id, price = res[0], res[1]

        if not prod_id:
            # no matching price found
            prod_id = mdata_obj.get_object_reference(
                cr,
                uid,
                'mozaik_membership',
                'membership_product_undefined')[1]
            price = amount_paid

        partner = partner_obj.browse(cr, uid, partner_id, context)

        # save current state to be able to compare it later
        current_state = partner.membership_state_id.code
        partner_obj.signal_workflow(
            cr, uid, [partner_id], 'paid')
        next_state = partner.membership_state_id.code

        vals = {
            'product_id': prod_id,
            'price': price,
        }
        ml_ids = ml_obj.search(
            cr, uid, [('partner_id', '=', partner_id),
                      ('active', '=', True)])
        if ml_ids:
            self.pool['membership.line'].write(
                cr, uid, ml_ids, vals, context=context)
            # if state does not change after payment force a notification
            if next_state == current_state:
                subtype = 'mozaik_membership.no_state_change_notification'
                partner_obj._message_post(
                    cr, uid, partner_id, subtype=subtype, context=context)

    def search_partner_id_with_reference(self, cr, uid, reference,
                                         context=None):
        '''
        Get the mode and the partner id associated to a given reference
        '''
        if not reference:
            return False, False, False

        models = []
        if self.pool.get('membership.line'):
            models += ['res.partner', 'membership.line', ]
        if self.pool.get('retrocession'):
            models += ['ext.mandate', 'sta.mandate', ]
        domain = [
            ('reference', '=', reference),
            ('active', '<=', True),
        ]

        for model in models:
            column = 'id' if model == 'res.partner' else 'partner_id'

            data = self.pool.get(model).search_read(
                cr, uid, domain, [column], context=context)
            if data:
                res = data[0][column]
                if isinstance(res, (list, tuple)):
                    res = res[0]
                mode = model.endswith('mandate') and \
                    'retrocession' or 'membership'
                return mode, res, reference

        return False, False, False
