# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, _
from odoo.fields import first
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


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
            obj = self.env[model].search(domain).mapped(
                models_mode.get(model, {}).get('map'))
            if obj:
                return models_mode.get(model, {}).get('mode'), first(obj)

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

        account = prod_id.product_tmpl_id._get_product_accounts().get("income")
        if account:
            move_dicts = [{
                'account_id': account.id,
                'debit': 0,
                'credit': self.amount,
                'name': reference,
            }]
            self.process_reconciliation(new_aml_dicts=move_dicts)

    @api.multi
    def _propagate_payment(self, amount_paid, reference):
        self.ensure_one()
        memb_obj = self.env['membership.line']
        mode, partner = self._get_info_from_reference(reference)
        if mode == 'membership':
            membership = memb_obj._get_membership_line_by_ref(reference)
            # ??? still necessary ??
            partner.paid()
            membership._mark_as_paid()

        if mode == 'donation':
            involvements = self.env['partner.involvement'].search([
                ('partner_id', '=', partner.id),
                ('reference', '=', reference),
                ('active', '<=', True),
            ])
            if involvements:
                vals = {
                    'effective_time': self.date,
                    'amount': amount_paid,
                }
                involvements.write(vals)
        return

    @api.multi
    def _create_membership_move(self, reference):
        """
        Method to create account move linked to membership payment
        """
        self.ensure_one()
        bsl_obj = self.env['account.bank.statement.line']
        # Search if already exist
        domain = [
            ('id', '!=', self.id),
            ('name', '=', reference),
        ]
        if bsl_obj.search_count(domain):
            # do not auto reconcile if reference has been used previously
            return
        membership = self.env['membership.line']._get_membership_line_by_ref(
            reference)
        product = membership.product_id
        account = product.property_subscription_account
        precision = membership._fields.get('price').digits[1]
        # float_compare return 0 is values are equals
        if account and not float_compare(self.amount, membership.price, precision_digits=precision):
            move_dicts = [{
                'account_id': account.id,
                'debit': 0,
                'credit': self.amount,
                'name': reference,
            }]
            self.process_reconciliation(
                new_aml_dicts=move_dicts, prod_id=product)

    @api.multi
    def process_reconciliation(
            self, counterpart_aml_dicts=None, payment_aml_rec=None,
            new_aml_dicts=None, prod_id=None):
        if self.filtered(lambda l: not l.partner_id):
            raise ValidationError(_("You must first select a partner!"))

        res = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts)

        for data in new_aml_dicts or []:
            self._propagate_payment(data.get('credit'), data.get('name'))
        return res
