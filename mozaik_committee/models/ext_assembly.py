# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ExtAssembly(models.Model):

    _inherit = 'ext.assembly'

    _columns = {
        'selection_committee_ids': fields.one2many(
            'ext.selection.committee',
            'assembly_id',
            'Selection Committees',
            domain=[('active', '=', True)]),
        'selection_committee_inactive_ids': fields.one2many(
            'ext.selection.committee',
            'assembly_id',
            'Selection Committees',
            domain=[('active', '=', False)]),
    }
