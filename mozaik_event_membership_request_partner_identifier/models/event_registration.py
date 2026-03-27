# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    @api.depends("associated_partner_id", "partner_id")
    def _compute_partner_identifier(self):
        for rec in self:
            rec.partner_identifier = (
                rec.associated_partner_id.identifier or rec.partner_id.identifier
            )
