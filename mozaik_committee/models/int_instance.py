# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class IntInstance(models.Model):

    _inherit = 'int.instance'

    def _compute_candidature_count(self):
        """
        This method will set the value for
        * sta_mandate_count
        * sta_candidature_count
        * ext_mandate_count
        * int_mandate_count
        """
        self.sta_candidature_count = len(
            self._get_model_ids('sta.candidature'))

    sta_candidature_count = fields.Integer(
        compute='_compute_candidature_count', type='integer',
        string='State Candidatures')
