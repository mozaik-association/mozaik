# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AbstractPowerLevel(models.AbstractModel):

    _name = 'abstract.power.level'
    _inherit = ['mozaik.abstract.model']
    _description = 'Abstract Power Level'
    _order = 'sequence, name'
    _unicity_keys = 'name'
    _log_access = True

    name = fields.Char(
        required=True,
        index=True,
        tracking=True,
    )
    sequence = fields.Integer(
        required=True,
        tracking=True,
        group_operator='min',
        default=5,
    )
    assembly_category_ids = fields.One2many(
        'abstract.assembly.category',
        'power_level_id',
        string='Assembly Categories',
        domain=[('active', '=', True)],
    )
    assembly_category_inactive_ids = fields.One2many(
        'abstract.assembly.category',
        'power_level_id',
        string='Assembly Categories',
        domain=[('active', '=', False)],
    )
