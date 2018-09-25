# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.fields import first
from odoo.exceptions import ValidationError


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    def _get_models(self):
        return {
            'res.partner': {'mode': 'membership', 'map': lambda s: s},
            'membership.line': {'mode': 'membership', 'map': 'partner_id'},
            'partner.involvement': {'mode': 'donation', 'map': 'partner_id'},
        }

    @api.model
    def _get_info_from_reference(self, reference):
        '''
        Get the mode and the partner associated to a given reference
        '''
        if not reference:
            return False, False

        domain = [
            ('reference', '=', reference),
            ('active', '<=', True),
        ]

        models_mode = self._get_models()
        for model in models_mode:
            obj = self.env[model].search(
                domain).mapped(models_mode[model]['map'])
            if obj:
                res = first(obj)
                return models_mode[model]['mode'], res

        return False, False

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

        account = prod_id.product_tmpl_id._get_product_accounts()["income"]
        if account:
            move_dicts = [{
                'account_id': account.id,
                'debit': 0,
                'credit': self.amount,
                'name': reference,
            }]
            self.process_reconciliation(new_aml_dicts=move_dicts)

    @api.multi
    def _propagate_payment(self, prod_id, amount_paid, reference):
        self.ensure_one()

        mode, partner = self._get_info_from_reference(reference)

        if mode == 'membership':

            if not prod_id:
                prod_id = partner._get_membership_prod_info(
                    amount_paid, reference)[0]

            if not prod_id:
                # no matching price found
                prod_id = self.env.ref(
                    'mozaik_membership.membership_product_undefined').id

            partner.paid()

            ml_ids = self.env['membership.line'].search([
                ('partner_id', '=', partner.id),
                ('active', '=', True)])
            if ml_ids:
                vals = {
                    'product_id': prod_id,
                    'price': amount_paid,
                }
                ml_ids.write(vals)

        if mode == 'donation':
            inv_ids = self.env['partner.involvement'].search([
                ('partner_id', '=', partner.id),
                ('reference', '=', reference),
                ('active', '<=', True)])
            if inv_ids:
                vals = {
                    'effective_time': self.date,
                    'amount': amount_paid,
                }
                inv_ids.write(vals)

        return

    @api.multi
    def _create_membership_move(self, reference):
        """
        Method to create account move linked to membership payment
        """
        self.ensure_one()
        bsl_obj = self.env['account.bank.statement.line']
        line_count = bsl_obj.search_count([('id', '!=', self.id),
                                           ('name', '=', reference)])
        if line_count > 0:
            # do not auto reconcile if reference has been used previously
            return
        product_id, credit_account = self.partner_id._get_membership_prod_info(
            self.amount, reference)

        if credit_account:
            move_dicts = [{
                'account_id': credit_account.id,
                'debit': 0,
                'credit': self.amount,
                'name': reference,
            }]
            self.process_reconciliation(
                new_aml_dicts=move_dicts, prod_id=product_id)

    @api.multi
    def process_reconciliation(
            self, counterpart_aml_dicts=None, payment_aml_rec=None,
            new_aml_dicts=None, prod_id=None):
        if not all((r.partner_id for r in self)):
            raise ValidationError(_("You must first select a partner!"))

        res = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts)

        for data in new_aml_dicts or {}:
            self._propagate_payment(
                prod_id, data['credit'], data.get('name', False))
        return res
