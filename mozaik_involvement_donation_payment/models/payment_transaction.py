# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PaymentTransaction(models.Model):

    _inherit = "payment.transaction"

    involvement_id = fields.Many2one(
        "partner.involvement", domain="[('involvement_type', '=', 'donation')]"
    )

    def _compute_display_reference_depends(self):
        res = super()._compute_display_reference_depends()
        return res + ("involvement_id", "involvement_id.reference")

    def _compute_display_reference(self):
        super()._compute_display_reference()
        for tx in self.filtered("involvement_id"):
            tx.display_reference = (
                tx.involvement_id._compute_default_donation_reference() or tx.reference
            )

    def _update_involvement_payment_date(self):
        self.filtered(lambda tr: tr.state == "done").mapped("involvement_id").filtered(
            lambda inv: not inv.payment_date
        ).write({"payment_date": fields.Date.today()})

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._update_involvement_payment_date()
        return res

    def write(self, vals):
        res = super().write(vals)
        if "involvement_id" in vals or "state" in vals:
            self._update_involvement_payment_date()
        if "payment_id" in vals:
            # Normally we should always write a given account.payment on a single transaction.
            if len(self) == 1 and self.involvement_id:
                # Update the account set on the related credit account move line.
                # The account to take is configured by the user.
                credit_line = (
                    self.env["account.payment"]
                    .browse(vals["payment_id"])
                    .mapped("move_id.line_ids")
                    .filtered(lambda t: t.credit > 0)
                )
                donation_account = self.env.user.company_id.donation_account_id
                if donation_account:
                    credit_line.account_id = donation_account
        return res
