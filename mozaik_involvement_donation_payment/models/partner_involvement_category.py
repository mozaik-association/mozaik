# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PartnerInvolvementCategory(models.Model):

    _inherit = "partner.involvement.category"

    payment_acquirer_id = fields.Many2one(
        "payment.acquirer", compute="_compute_acquirer", store=True, readonly=False
    )

    @api.constrains("involvement_type", "payment_acquirer_id")
    def _check_required_payment_acquirer(self):
        """
        Payment acquirer is mandatory for donations
        """
        if self.filtered(
            lambda ic: ic.involvement_type == "donation" and not ic.payment_acquirer_id
        ):
            raise UserError(
                _(
                    "A payment acquirer is required for involvement "
                    "categories of type 'donation'"
                )
            )

    @api.depends("involvement_type")
    def _compute_acquirer(self):
        """
        For donation involvements, set a default acquirer.
        For other involvement types, remove the acquirer.
        """
        default_acquirer_id = self.env["payment.acquirer"]._get_default_acquirer()
        for rec in self:
            if rec.involvement_type == "donation":
                rec.payment_acquirer_id = default_acquirer_id
            else:
                rec.payment_acquirer_id = False
