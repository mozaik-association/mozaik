# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ExtMandate(models.Model):

    _inherit = 'ext.mandate'

    candidature_id = fields.Many2one(
        comodel_name='ext.candidature',
        string='Candidature')
