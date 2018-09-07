# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class VirtualPartnerInstance(models.Model):
    _inherit = "virtual.partner.instance"

    local_voluntary = fields.Boolean()
    regional_voluntary = fields.Boolean()
    national_voluntary = fields.Boolean()
    local_only = fields.Boolean()
    nationality_id = fields.Many2one(
        'res.country',
        'Nationality',
    )
