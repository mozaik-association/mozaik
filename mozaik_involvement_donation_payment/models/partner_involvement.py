# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    payment_link = fields.Char(compute="_compute_payment_link")
    payment_transaction_ids = fields.One2many("payment.transaction", "involvement_id")

    @api.depends(
        "involvement_category_id",
        "amount",
        "partner_id",
        "involvement_type",
        "reference",
    )
    def _compute_payment_link(self):
        for inv in self:
            if inv.id and inv.involvement_type == "donation" and inv.promise:
                inv.payment_link = (
                    self.env["payment.link.wizard"]
                    .with_context(active_model="partner.involvement", active_id=inv.id)
                    .new()
                    .link
                )
            else:
                inv.payment_link = False

    def _compute_default_donation_reference(self):
        self.ensure_one()
        return self.reference or f"Donation - {self.involvement_category_id.name}"
