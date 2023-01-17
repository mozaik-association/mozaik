# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def generated2uploaded(self):
        if self.company_id.debit_order_partner_account_id:
            self.filtered(lambda o: o.payment_type == "inbound").mapped(
                "payment_ids.move_id.line_ids"
            ).filtered(lambda ml: ml.credit > 0).write(
                {"account_id": self.company_id.debit_order_partner_account_id.id}
            )
        return super().generated2uploaded()
