# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class IntPowerLevel(models.Model):

    _name = 'int.power.level'
    _inherit = ['abstract.power.level']
    _description = 'Internal Power Level'

    assembly_category_ids = fields.One2many(
        comodel_name='int.assembly.category',
        string='Internal Assembly Categories',
        domain=[('active', '=', True)],
    )
    assembly_category_inactive_ids = fields.One2many(
        comodel_name='int.assembly.category',
        string='Internal Assembly Categories (Inactive)',
        domain=[('active', '=', False)],
    )
    level_for_followers = fields.Boolean(default=False)

    @api.model
    def _get_default_int_power_level(self):
        """
        Returns the default Internal Power Level
        """
        res_id = self.env.ref('mozaik_structure.int_power_level_01')
        return res_id
