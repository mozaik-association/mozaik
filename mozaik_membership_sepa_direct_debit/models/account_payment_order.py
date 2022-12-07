# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountPaymentOrder(models.Model):

    _inherit = "account.payment.order"

    membership_line_ids = fields.Many2many(
        comodel_name="membership.line", string="Membership Lines"
    )

    def _create_reconcile_move(self, hashcode, blines):
        res = super()._create_reconcile_move(hashcode, blines)
        for order in self:
            for membership_line in order.membership_line_ids:
                move = (
                    self.env["account.move.line"]
                    .search(
                        [
                            ("move_id", "in", order.move_ids.ids),
                            ("partner_id", "=", membership_line.partner_id.id),
                            ("credit", ">", 0),
                        ],
                        limit=1,
                    )
                    .move_id
                )
                membership_line._mark_as_paid(membership_line.price, move)
        return res
