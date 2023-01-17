# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPayment(models.Model):

    _inherit = "account.payment"

    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        self.ensure_one()
        res = super()._prepare_move_line_default_vals(write_off_line_vals)
        if (
            self.payment_method_id.code == "electronic"
            and self.payment_method_id.payment_type == "inbound"
            and self.company_id.electronic_payment_analytic_account_id
        ):
            for ml_vals in res:
                if (
                    "account_id" in ml_vals
                    and ml_vals["account_id"] == self.destination_account_id.id
                ):
                    ml_vals[
                        "analytic_account_id"
                    ] = self.company_id.electronic_payment_analytic_account_id.id
        return res
