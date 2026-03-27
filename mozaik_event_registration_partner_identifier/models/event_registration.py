# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    partner_identifier = fields.Char(compute="_compute_partner_identifier", store=True)

    @api.depends("partner_id")
    def _compute_partner_identifier(self):
        for rec in self:
            rec.partner_identifier = rec.partner_id.identifier
