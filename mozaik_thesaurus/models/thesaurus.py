# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class Thesaurus(models.Model):

    _name = 'thesaurus'
    _inherit = ['mozaik.abstract.model']
    _description = 'Thesaurus'
    _order = 'name'
    _unicity_keys = 'name'

    name = fields.Char(
        string='Thesaurus',
        required=True,
        track_visibility='onchange',
    )

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Thesaurus name already exists !"),
    ]
