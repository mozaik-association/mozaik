# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class StaAssembly(models.Model):

    _inherit = 'sta.assembly'
    _columns = {
        'selection_committee_ids': fields.one2many(
            'sta.selection.committee',
            'assembly_id',
            'Selection Committees',
            domain=[('active', '=', True)]),
        'selection_committee_inactive_ids': fields.one2many(
            'sta.selection.committee',
            'assembly_id',
            'Selection Committees',
            domain=[('active', '=', False)]),
    }
