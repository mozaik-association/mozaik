# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    def _create_reconcile_move(self, hashcode, blines):
        res = super()._create_reconcile_move(hashcode, blines)
        for order in self:
            for move_line in order.mapped("move_ids.line_ids"):
                membership_lines = move_line.bank_payment_line_id.mapped(
                    "payment_line_ids.membership_line_id"
                )
                for membership_line in membership_lines:
                    membership_line._mark_as_paid(
                        membership_line.price, move_line.move_id
                    )
        return res
