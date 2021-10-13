# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

class ElectoralDistrict(models.Model):

    _inherit = 'electoral.district'

    selection_committee_ids = fields.One2many(
        comodel_name="sta.selection.committee",
        inverse_name="electoral_district_id",
        string="Selection Committees",
    )
