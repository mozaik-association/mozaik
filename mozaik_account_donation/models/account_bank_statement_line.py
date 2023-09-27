# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountBankStatementLine(models.Model):

    _inherit = "account.bank.statement.line"

    @api.model
    def _get_models(self):
        res = super()._get_models()
        res["partner.involvement"] = {"mode": "donation", "map": "partner_id"}
        return res

    def _create_donation_move(self, reference):
        """
        Create an account move related to a donation
        """
        self.ensure_one()
        line_count = self.search_count([("payment_ref", "=", reference)])
        if line_count > 1:
            # do not auto reconcile if reference has already been used
            return

        prod_id = self.env.ref("mozaik_account_donation.product_product_donation")

        account = prod_id.product_tmpl_id._get_product_accounts().get("income")
        if account:
            move_dicts = [
                {
                    "account_id": account.id,
                    "debit": 0,
                    "credit": self.amount,
                    "name": reference,
                }
            ]
            self.process_reconciliation(new_aml_dicts=move_dicts)

    def _execute_specific_mode_actions(
        self, mode, partner, reference, amount_paid, vals
    ):
        super()._execute_specific_mode_actions(
            mode, partner, reference, amount_paid, vals
        )
        if mode == "donation":
            involvements = self.env["partner.involvement"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("reference", "=", reference),
                    ("active", "<=", True),
                ]
            )
            if involvements:
                vals = {
                    "payment_date": self.date,
                    "amount": amount_paid,
                }
                involvements.write(vals)

    @api.model
    def _get_available_account_reconciliation(self):
        subscription_accounts = super()._get_available_account_reconciliation()
        donation_p = self.env.ref("mozaik_account_donation.product_product_donation")
        return subscription_accounts | donation_p.property_account_income_id

    def _auto_reconcile(self):
        reconciled_lines = super()._auto_reconcile()
        for bank_line in self.filtered(
            lambda l: not (not l.partner_id or l.is_reconciled)
        ):
            mode, __ = bank_line._get_info_from_reference(bank_line.payment_ref)
            if mode == "donation":
                bank_line._create_donation_move(bank_line.payment_ref)
            if bank_line.is_reconciled:
                reconciled_lines |= bank_line
        return reconciled_lines
