# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    territory_ids = fields.Many2many(
        comodel_name="territory",
        relation="partner_territory_rel",
        column1="partner_id",
        column2="territory_id",
        string="Territories",
    )
