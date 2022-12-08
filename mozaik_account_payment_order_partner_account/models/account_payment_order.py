# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def _prepare_move_line_partner_account(self, bank_line):
        res_vals = super()._prepare_move_line_partner_account(bank_line).copy()
        if (
            not bank_line.payment_line_ids[0].move_line_id
            and self.payment_type == "inbound"
            and self.env.company.debit_order_partner_account_id
        ):
            res_vals["account_id"] = self.env.company.debit_order_partner_account_id.id
        return res_vals
