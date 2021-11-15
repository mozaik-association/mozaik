# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PartnerInvolvementCategory(models.Model):

    _inherit = "partner.involvement.category"

    name = fields.Char(compute="_compute_name", store=True)

    event_id = fields.Many2one("event.event", string="Related Event")

    involvement_type = fields.Selection(selection_add=[("event", "Event")])

    @api.depends("event_id.name")
    def _compute_name(self):
        for rec in self:
            if rec.event_id:
                rec.name = rec.event_id.name
            else:
                rec.name = rec.name
