# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PaymentTransaction(models.Model):

    _inherit = "payment.transaction"

    membership_ids = fields.Many2many(
        string="Memberships",
        comodel_name="membership.line",
    )
    membership_request_ids = fields.Many2many(
        string="Membership Requests",
        comodel_name="membership.request",
    )
    display_reference = fields.Char(compute="_compute_display_reference")

    def write(self, vals):
        if vals.get("state") == "done" and self.membership_ids:
            self._mark_membership_as_paid(vals.get("acquirer_reference"))
        res = super().write(vals)
        return res

    @api.depends("reference", "membership_ids", "membership_ids.reference")
    def _compute_display_reference(self):
        for tx in self:
            reference = tx.reference
            if tx.membership_ids and tx.membership_ids.mapped("reference"):
                reference = tx.membership_ids.mapped("reference")[
                    0
                ]  # should be only one
            elif tx.membership_request_ids and tx.membership_request_ids.mapped(
                "reference"
            ):
                reference = tx.membership_request_ids.mapped("reference")[
                    0
                ]  # should be only one
            tx.display_reference = reference

    def _mark_membership_as_paid(self, acquirer_reference=False):
        am = self.env["account.move"]
        for pt in self:
            move = am.create(
                {
                    "journal_id": pt.acquirer_id.journal_id.id,
                    "ref": pt.reference,
                }
            )

            move_line_values = []
            for m in pt.membership_ids:
                move_line_values.append(
                    (
                        0,
                        0,
                        {
                            "name": m.reference,
                            "move_id": move.id,
                            "account_id": m.product_id.property_subscription_account.id,
                            "credit": m.price,
                            "partner_id": pt.partner_id.id,
                        },
                    )
                )

                m._mark_as_paid(m.price, move.id)

            move_line_values.append(
                (
                    0,
                    0,
                    {
                        "name": acquirer_reference or pt.acquirer_reference,
                        "move_id": move.id,
                        "account_id": pt.acquirer_id.journal_id.default_account_id.id,
                        "debit": pt.amount,
                        "partner_id": pt.partner_id.id,
                    },
                )
            )
            move.write({"line_ids": move_line_values})
