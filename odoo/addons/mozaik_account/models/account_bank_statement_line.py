# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby
from odoo import api, models, _
from odoo.fields import first
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountBankStatementLine(models.Model):

    _inherit = 'account.bank.statement.line'

    @api.model
    def create(self, vals):
        if not vals.get("partner_id"):
            __, partner = self._get_info_from_reference(vals.get("name"))
            if partner:
                vals["partner_id"] = partner.id
        return super().create(vals)

    @api.model
    def _get_models(self):
        return {
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
    def _propagate_payment(self, vals, amount=False):
        self.ensure_one()
        memb_obj = self.env['membership.line']
        amount_paid = amount or vals.get('credit') or 0.0
        reference = vals.get('name') or ''
        mode, partner = self._get_info_from_reference(reference)
        if mode == 'membership':
            move_id = vals.get('move_id', False)
            membership = memb_obj._get_membership_line_by_ref(reference)
            bank_account_id = self.bank_account_id.id
            membership._mark_as_paid(amount_paid, move_id, bank_account_id)

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

        # try to find if a membership have the same amount for the partner
        partner_id = vals.get('partner_id')
        if not mode and partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            membership = memb_obj._get_membership_line_by_partner_amount(
                partner, amount_paid)
            if membership and not membership.paid:
                move_id = vals.get('move_id', False)
                bank_account_id = self.bank_account_id.id
                membership._mark_as_paid(amount_paid, move_id, bank_account_id)
        return

    @api.multi
    def _create_membership_move_from_partner(self):
        self.ensure_one()
        memb_obj = self.env['membership.line']
        partner = self.partner_id
        amount_paid = self.amount
        membership = memb_obj._get_membership_line_by_partner_amount(
            partner, amount_paid)
        self._reconcile_membership_move(membership)

    @api.multi
    def _create_membership_move(self, reference, include_inactive=True):
        """
        Method to create account move linked to membership payment
        """
        self.ensure_one()
        membership = self.env['membership.line']._get_membership_line_by_ref(
            reference, include_inactive=include_inactive)
        self._reconcile_membership_move(membership)

    @api.multi
    def _reconcile_membership_move(self, membership):
        self.ensure_one()
        if membership.paid:
            return
        product = membership.product_id
        account = product.property_subscription_account
        precision = membership._fields.get('price').digits[1]
        # float_compare return 0 if values are equals
        cmp = float_compare(
            self.amount, membership.price, precision_digits=precision)
        if account and not cmp:
            move_dicts = [{
                'account_id': account.id,
                'debit': 0,
                'credit': self.amount,
                'name': membership.reference,
            }]
            self.process_reconciliation(
                new_aml_dicts=move_dicts)

    @api.multi
    def process_reconciliation(
            self, counterpart_aml_dicts=None, payment_aml_rec=None,
            new_aml_dicts=None):
        if self.filtered(lambda l: not l.partner_id):
            raise ValidationError(_("You must first select a partner!"))

        for aml in new_aml_dicts:
            name = aml.get("name")
            if name:
                aml["name"] = name.strip()

        res = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts)

        if new_aml_dicts:
            # grouped by the move_id (to be sure to have 1 statement line)
            # and by the name, since they can pay for multiple membership
            for key, datas in groupby(
                    sorted(new_aml_dicts,
                           key=lambda s: (s.get("move_id"), s.get("name"))),
                    lambda s: (s.get("move_id"), s.get("name"))):
                # datas is a generator, and we iterate more than 1 time
                datas = list(datas)

                # optimization for automatic reconciliation
                if len(datas) == 1:
                    self._propagate_payment(datas[0])
                    continue

                amount = False
                # they all have the same name
                reference = datas[0].get("name", "")
                mode, partner = self._get_info_from_reference(reference)
                if mode == 'membership':
                    amount = 0
                    for data in datas:
                        amount += data.get('credit') or 0.0
                for data in datas:
                    self._propagate_payment(data, amount=amount)
        return res

    @api.multi
    def _auto_reconcile(self):
        reconciled_lines = self.env["account.bank.statement.line"]
        for bank_line in self.filtered(
                lambda l: not (not l.partner_id or l.journal_entry_ids)):
            mode, __ = bank_line._get_info_from_reference(bank_line.name)
            if mode == 'membership':
                bank_line._create_membership_move(bank_line.name, include_inactive=False)
            elif mode == 'donation':
                bank_line._create_donation_move(bank_line.name)
            elif not mode:
                bank_line._create_membership_move_from_partner()
            if bank_line.journal_entry_ids:
                reconciled_lines += bank_line
        return reconciled_lines

    @api.multi
    def reconciliation_widget_auto_reconcile(
            self, num_already_reconciled_lines):
        reconciled_lines = self._auto_reconcile()
        num_already_reconciled_lines += len(reconciled_lines)
        return super(AccountBankStatementLine, self - reconciled_lines)\
            .reconciliation_widget_auto_reconcile(num_already_reconciled_lines)
