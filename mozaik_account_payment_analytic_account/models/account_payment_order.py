# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def generated2uploaded(self):
        debit_order_analytic_account = self.company_id.debit_order_analytic_account_id
        if debit_order_analytic_account:
            self.filtered(lambda o: o.payment_type == "inbound").mapped(
                "payment_ids.move_id.line_ids"
            ).filtered(lambda ml: ml.credit > 0).write(
                {"analytic_account_id": debit_order_analytic_account.id}
            )
        return super().generated2uploaded()
