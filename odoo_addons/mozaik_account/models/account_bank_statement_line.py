# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models

MODELS = {
    'res.partner': {'mode': 'membership', 'map': lambda s: s},
    'membership.line': {'mode': 'membership', 'map': 'partner_id'},
    'sta.mandate': {'mode': 'retrocession', 'map': 'partner_id'},
    'ext.mandate': {'mode': 'retrocession', 'map': 'partner_id'},
    'partner.involvement': {'mode': 'donation', 'map': 'partner_id'},
}


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    def _get_info_from_reference(self, reference):
        '''
        Get the mode and the partner associated to a given reference
        '''
        if not reference:
            return False, False, False

        domain = [
            ('reference', '=', reference),
            ('active', '<=', True),
        ]

        for model in MODELS.keys():
            obj = self.env[model].search(
                domain).mapped(MODELS[model]['map'])
            if obj:
                res = obj[0]
                return MODELS[model]['mode'], res.id, reference

        return False, False, False

    @api.multi
    def _create_donation_move(self, reference):
        """
        Create an account move related to a donation
        """
        self.ensure_one()
        line_count = self.search_count([('name', '=', reference)])
        if line_count > 1:
            # do not auto reconcile if reference has already been used
            return

        prod_id = self.env.ref('mozaik_account.product_template_donation')

        if prod_id.property_account_income:
            move_dicts = [{
                'account_id': prod_id.property_account_income.id,
                'debit': 0,
                'credit': self.amount,
                'name': reference,
            }]
            self.process_reconciliation(move_dicts)

    @api.multi
    def _propagate_payment(self, prod_id, amount_paid, reference):
        self.ensure_one()

        mode, partner_id, reference = self._get_info_from_reference(reference)

        if mode == 'membership':
            partner = self.env['res.partner'].browse(partner_id)

            if not prod_id:
                prod_id = partner._get_membership_prod_info(
                    amount_paid, reference)[0]

            if not prod_id:
                # no matching price found
                prod_id = self.env.ref(
                    'mozaik_membership.membership_product_undefined').id

            # save current state to be able to compare it later
            current_state = partner.membership_state_id.code
            partner.signal_workflow('paid')
            next_state = partner.membership_state_id.code

            ml_ids = self.env['membership.line'].search([
                ('partner_id', '=', partner_id),
                ('active', '=', True)])
            if ml_ids:
                vals = {
                    'product_id': prod_id,
                    'price': amount_paid,
                }
                ml_ids.write(vals)
                # if state does not change after payment force a notification
                if next_state == current_state:
                    subtype = 'mozaik_membership.no_state_change_notification'
                    partner._message_post(subtype=subtype)

        if mode == 'donation':
            inv_ids = self.env['partner.involvement'].search([
                ('partner_id', '=', partner_id),
                ('reference', '=', reference),
                ('active', '<=', True)])
            if inv_ids:
                vals = {
                    'effective_time': self.date,
                    'amount': amount_paid,
                }
                inv_ids.write(vals)

        return
