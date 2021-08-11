# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtAssemblyCategory(models.Model):

    _name = "ext.assembly.category"
    _inherit = ["abstract.assembly.category"]
    _description = "External Assembly Category"
    _order = "name"
    _unicity_keys = "name"

    # Unused fields
    power_level_id = fields.Many2one(
        comodel_name="int.power.level",
    )
    assembly_ids = fields.One2many(
        comodel_name="int.assembly",
    )
    assembly_inactive_ids = fields.One2many(
        comodel_name="int.assembly",
    )

    def _check_power_level(self):
        """
        Not relevant for external assembly
        """
