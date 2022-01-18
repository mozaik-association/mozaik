# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StaAssemblyCategory(models.Model):

    _name = "sta.assembly.category"
    _inherit = ["abstract.assembly.category"]
    _description = "State Assembly Category"
    _order = "name, power_level_id"
    _unicity_keys = "power_level_id, name"

    power_level_id = fields.Many2one(
        comodel_name="sta.power.level",
        required=True,
    )
    is_legislative = fields.Boolean(
        default=False,
    )
    assembly_ids = fields.One2many(
        comodel_name="sta.assembly",
    )
    assembly_inactive_ids = fields.One2many(
        comodel_name="sta.assembly",
    )
