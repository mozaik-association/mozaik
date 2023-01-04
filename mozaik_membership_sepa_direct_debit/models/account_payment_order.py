# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def generated2uploaded(self):
        res = super().generated2uploaded()
        for payment in self.mapped("payment_ids"):
            for membership_line in payment.mapped(
                "payment_line_ids.membership_line_id"
            ):
                membership_line._mark_as_paid(membership_line.price, payment.move_id.id)
        return res
