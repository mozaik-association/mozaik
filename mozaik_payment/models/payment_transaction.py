# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PaymentTransaction(models.Model):

    _inherit = "payment.transaction"

    display_reference = fields.Char(compute="_compute_display_reference")

    def _compute_display_reference_depends(self):
        # Intended to be extended
        return ("reference",)

    @api.depends(lambda self: self._compute_display_reference_depends())
    def _compute_display_reference(self):
        # Intended to be extended
        for tx in self:
            tx.display_reference = tx.reference
