# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class CoordinateCategory(models.Model):
    _name = 'coordinate.category'
    _inherit = 'mozaik.abstract.model'
    _description = 'Coordinate Category'
    _order = 'name'
    _unicity_keys = 'name'

    name = fields.Char(
        required=True,
        index=True,
        track_visibility='onchange',
    )
