# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    partner_identifier = fields.Char(
        string="Partner Identifier", related="partner_id.identifier", store=True
    )
