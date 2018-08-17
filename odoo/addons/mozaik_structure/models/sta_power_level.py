# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StaPowerLevel(models.Model):

    _name = 'sta.power.level'
    _inherit = ['abstract.power.level']
    _description = 'State Power Level'

    assembly_category_ids = fields.One2many(
        comodel_name='sta.assembly.category',
        string='State Assembly Categories',
        domain=[('active', '=', True)],
    )
    assembly_category_inactive_ids = fields.One2many(
        comodel_name='sta.assembly.category',
        string='State Assembly Categories',
        domain=[('active', '=', False)],
    )
