# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Legislature(models.Model):

    _name = 'legislature'
    _inherit = ['mozaik.abstract.model']
    _description = 'Legislature'
    _order = 'start_date desc, name'
    _unicity_keys = 'power_level_id, name, start_date'

    name = fields.Char(
        required=True,
        index=True,
        tracking=True,
    )
    power_level_id = fields.Many2one(
        'sta.power.level',
        string='Power Level',
        required=True,
        index=True,
        tracking=True,
    )
    start_date = fields.Date(
        required=True,
        index=True,
        tracking=True,
    )
    deadline_date = fields.Date(
        required=True,
        tracking=True,
    )
    election_date = fields.Date(
        required=True,
        tracking=True,
    )

    _sql_constraints = [
        ('date_check1', 'CHECK ( start_date <= deadline_date )',
         'The start date must be anterior to the deadline date.'),
        ('date_check2', 'CHECK ( election_date <= start_date )',
         'The election date must be anterior to the start date.'),
    ]

    def name_get(self):
        res = []
        for record in self:
            display_name = "%s (%s-%s)" % (
                record.name,
                record.start_date.strftime("%Y"),
                record.deadline_date.strftime("%Y"),
            )
            res.append((record.id, display_name))
        return res
