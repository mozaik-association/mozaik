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
        track_visibility='onchange',
    )
    power_level_id = fields.Many2one(
        'sta.power.level',
        string='Power Level',
        required=True,
        index=True,
        track_visibility='onchange',
    )
    start_date = fields.Date(
        required=True,
        index=True,
        track_visibility='onchange',
    )
    deadline_date = fields.Date(
        required=True,
        track_visibility='onchange',
    )
    election_date = fields.Date(
        required=True,
        track_visibility='onchange',
    )

    _sql_constraints = [
        ('date_check1', 'CHECK ( start_date <= deadline_date )',
         'The start date must be anterior to the deadline date.'),
        ('date_check2', 'CHECK ( election_date <= start_date )',
         'The election date must be anterior to the start date.'),
    ]

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            display_name = '%s (%s-%s)' % (
                record.name, record.start_date[0:4], record.deadline_date[0:4]
            )
            res.append((record.id, display_name))
        return res
