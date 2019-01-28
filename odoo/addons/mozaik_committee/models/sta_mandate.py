# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StaMandate(models.Model):

    _inherit = 'sta.mandate'
    candidature_id = fields.Many2one(
        comodel_name='sta.candidature',
        string='Candidature')
