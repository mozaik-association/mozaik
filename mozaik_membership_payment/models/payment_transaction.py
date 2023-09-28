# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


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

    def write(self, vals):
        if vals.get("state") == "done" and self.membership_ids:
            self._mark_membership_as_paid(vals.get("acquirer_reference"))
        res = super().write(vals)
        if vals.get("state") == "done" and self.membership_request_ids:
            # may update the result state
            self.membership_request_ids.onchange_partner_id()
        return res

    def _post_process_after_done(self):
        res = super(PaymentTransaction, self)._post_process_after_done()
        tx_done = self.filtered(
            lambda s: s.state == "done" and s.membership_request_ids
        )
        if tx_done:
            # auto-validate after payment, if asked
            for mr in tx_done.mapped("membership_request_ids").filtered(
                lambda s: s.auto_validate_after_payment
            ):
                failure_reason = mr._auto_validate(True)
                if failure_reason:
                    mr._create_note(
                        _("Autovalidation after payment failed"),
                        _("Autovalidation after payment failed. Reason of failure: %s")
                        % failure_reason,
                    )
        return res

    def _compute_display_reference_depends(self):
        res = super()._compute_display_reference_depends()
        return res + ("membership_ids", "membership_ids.reference")

    def _compute_display_reference(self):
        super()._compute_display_reference()
        for tx in self:
            if tx.membership_ids and tx.membership_ids.mapped("reference"):
                tx.display_reference = tx.membership_ids.mapped("reference")[
                    0
                ]  # should be only one
            elif tx.membership_request_ids and tx.membership_request_ids.mapped(
                "reference"
            ):
                tx.display_reference = tx.membership_request_ids.mapped("reference")[
                    0
                ]  # should be only one

    def _mark_membership_as_paid(self, acquirer_reference=False):
        for pt in self:
            for m in pt.membership_ids:
                m._mark_as_paid(pt.amount, pt.payment_id.move_id.id)
