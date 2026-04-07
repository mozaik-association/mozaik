# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Territory(models.Model):
    _name = "territory"
    _description = "Territory"
    _order = "name"

    name = fields.Char(
        string="Territory",
        required=True,
        index=True,
    )
    active = fields.Boolean(
        default=True,
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            "The name of the territory must be unique!",
        )
    ]
