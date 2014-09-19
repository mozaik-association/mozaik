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
from openerp.tools.translate import _


class account_bank_statement(orm.Model):
    _inherit = 'account.bank.statement'

    def _reconcile_statement_line(self, cr, uid, bank_line, context=None):
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

        if bank_line.name != move_line['ref']:
            return

        if move_line['debit'] == bank_line.amount:
            move_dicts = [{
                'counterpart_move_line_id': move_line['id'],
                'debit': move_line['credit'],
                'credit': move_line['debit'],
            }]
            bsl_obj.process_reconciliation(
                cr, uid, bank_line.id, move_dicts, context=context)

    def _create_membership_move(self, cr, uid, bank_line, context=None):
        """
        Method to create account move linked to membership payment
        """
        bsl_obj = self.pool.get('account.bank.statement.line')
        product_id, price, credit_account = bsl_obj.get_membership_prod_info(
                                                    cr,
                                                    uid,
                                                    bank_line.amount,
                                                    bank_line.partner_id.id,
                                                    bank_line.name,
                                                    context=context)

        if credit_account:
            move_dicts = [{
                'account_id': credit_account.id,
                'debit': 0,
                'credit': bank_line.amount,
            }]
            bsl_obj.process_reconciliation(
                cr, uid, bank_line.id, move_dicts, context=context,
                prod_id=product_id, price=price)

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


class account_bank_statement_line(orm.Model):
    _inherit = 'account.bank.statement.line'

    def _check_first_membership(self, cr, uid, partner_id, reference,
                                context=None):
        modeldata_obj = self.pool.get('ir.model.data')
        partner_obj = self.pool.get('res.partner')
        first_id = modeldata_obj.get_object_reference(
            cr, uid, 'ficep_membership', 'member_candidate')[1]

        domain = [('id', '=', partner_id),
                  ('reference', '=', reference),
                  ('membership_state_id', '=', first_id)]

        p_ids = partner_obj.search(cr, uid, domain, context=context)

        return len(p_ids) == 1

    def get_membership_prod_info(self, cr, uid,
                                 amount, partner_id, reference, context=None):
        prod_obj = self.pool.get('product.product')
        modeldata_obj = self.pool.get('ir.model.data')
        first_id = modeldata_obj.get_object_reference(
            cr, uid, 'ficep_membership', 'membership_product_first')[1]

        domain = [('membership', '=', True),
                  ('list_price', '>', 0)]

        prod_ids = prod_obj.search(cr, uid, domain, context=context)

        credit_account = False
        product_id = False
        price = False
        for prod in prod_obj.browse(cr, uid, prod_ids, context=context):
            if prod.list_price == amount:
                if prod.id == first_id:
                    if not self._check_first_membership(
                            cr, uid, partner_id, reference,
                            context=context):
                        continue
                credit_account = prod.property_subscription_account
                product_id = prod.id
                price = prod.list_price
                break

        return product_id, price, credit_account

    def process_reconciliation(self, cr, uid, line_id, mv_line_dicts,
                               context=None, prod_id=None, price=None):

        bank_line = self.browse(cr, uid, line_id, context=context)
        if not bank_line.partner_id.id:
            raise orm.except_orm(_('No Partner Defined!'),
                                 _("You must first select a partner!"))
        super(account_bank_statement_line, self).process_reconciliation(
                                                            cr,
                                                            uid,
                                                            line_id,
                                                            mv_line_dicts,
                                                            context=context)

        property_obj = self.pool.get('ir.property')
        subscription_account = property_obj.get(
                                        cr,
                                        uid,
                                        'property_subscription_account',
                                        'product.template')
        if not subscription_account:
            return

        is_membership = False
        amount_paid = bank_line.amount
        for data in mv_line_dicts:
            if data['account_id'] == subscription_account.id:
                is_membership = True
                amount_paid = data['credit']
                break

        if is_membership:
            ml_obj = self.pool.get('membership.line')
            mdata_obj = self.pool.get('ir.model.data')
            partner_obj = self.pool.get('res.partner')
            partner_id = bank_line.partner_id.id

            if not prod_id:
                res = self.get_membership_prod_info(
                                                    cr,
                                                    uid,
                                                    amount_paid,
                                                    bank_line.partner_id.id,
                                                    bank_line.name,
                                                    context=context)
                prod_id, price = res[0], res[1]
            if not prod_id:
                # no matching price found
                prod_id = mdata_obj.get_object_reference(
                                            cr,
                                            uid,
                                            'ficep_membership',
                                            'membership_product_undefined')[1]
                price = amount_paid

            partner_obj.signal_workflow(
                cr, uid, [partner_id], 'paid')

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
