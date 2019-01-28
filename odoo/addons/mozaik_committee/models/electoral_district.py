# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ElectoralDistrict(models.Model):

    _inherit = 'electoral.district'
    _columns = {
        'selection_committee_ids': fields.one2many(
            'sta.selection.committee',
            'electoral_district_id',
            'Selection Committees'),
    }
