# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.addons.mozaik_involvement.models.partner_involvement import CATEGORY_TYPE


class VirtualPartnerInvolvement(models.Model):
    _inherit = "virtual.partner.involvement"

    local_voluntary = fields.Boolean()
    regional_voluntary = fields.Boolean()
    national_voluntary = fields.Boolean()
    local_only = fields.Boolean()
    nationality_id = fields.Many2one(
        'res.country',
        'Nationality',
    )
    involvement_type = fields.Selection(
        CATEGORY_TYPE,
    )
    effective_time = fields.Datetime(
        'Involvement Date',
    )
    promise = fields.Boolean()
