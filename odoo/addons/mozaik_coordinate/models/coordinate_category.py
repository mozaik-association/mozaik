# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class CoordinateCategory(models.Model):

    _name = 'coordinate.category'
    _inherit = 'mozaik.abstract.model'
    _description = 'Coordinate Category'

    name = fields.Char('Name', size=128, required=True, index=True,
                       track_visibility='onchange')

    _order = 'name'

# constraints

    _unicity_keys = 'name'
