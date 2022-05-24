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
        if vals.get("state") == "done" and self.membership_request_ids:
            # may update the result state
            self.membership_request_ids.onchange_partner_id()
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
        for pt in self:
            for m in pt.membership_ids:
                m._mark_as_paid(pt.amount, pt.payment_id.move_id.id)
