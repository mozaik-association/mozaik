# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IntAssemblyCategory(models.Model):

    _name = "int.assembly.category"
    _inherit = ["abstract.assembly.category"]
    _description = "Internal Assembly Category"

    is_secretariat = fields.Boolean(
        default=False,
        tracking=True,
    )
    power_level_id = fields.Many2one(
        comodel_name="int.power.level",
        required=True,
    )
    assembly_ids = fields.One2many(
        comodel_name="int.assembly",
    )
    assembly_inactive_ids = fields.One2many(
        comodel_name="int.assembly",
    )
